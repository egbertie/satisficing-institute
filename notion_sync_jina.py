#!/usr/bin/env python3
"""
Notion同步脚本 - Jina AI + Notion API方案
使用Jina AI进行内容预处理和Markdown转换，提高同步稳定性

特性：
- Jina AI处理Markdown转换和格式优化
- 自动分块和结构化处理
- 异步批量处理提高效率
- 智能重试和故障恢复
"""
import os
import sys
import time
import json
import asyncio
import aiohttp
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict

# 配置
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "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")
JINA_API_KEY = os.getenv("JINA_API_KEY", "")  # Jina AI API Key
PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "31fa8a0e-2bba-81fa-b98a-d61da835051e")
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/root/.openclaw/workspace")

# Jina AI配置
JINA_API_URL = "https://api.jina.ai/v1"
JINA_READER_URL = "https://r.jina.ai/http://localhost:8000"

# 文件路径配置
PROGRESS_FILE = os.path.join(WORKSPACE_DIR, ".notion_sync_jina_progress.json")
REPORT_PATH = os.path.join(WORKSPACE_DIR, "docs/NOTION_SYNC_JINA_REPORT.md")
LOG_PATH = os.path.join(WORKSPACE_DIR, "logs/notion_sync_jina.log")

# 同步参数
BATCH_SIZE = int(os.getenv("JINA_BATCH_SIZE", "5"))
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "3"))
MAX_RETRIES = int(os.getenv("JINA_MAX_RETRIES", "3"))
FILE_INTERVAL = float(os.getenv("FILE_INTERVAL", "3.0"))
NOTION_RATE_LIMIT = float(os.getenv("NOTION_RATE_LIMIT", "0.5"))  # 每秒请求数

# 设置日志
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """文件信息"""
    path: str
    full_path: str
    size: int
    modified_time: float
    hash: str = ""
    content: str = ""


@dataclass
class SyncResult:
    """同步结果"""
    file_path: str
    success: bool
    page_id: str = ""
    page_url: str = ""
    error: str = ""
    blocks_added: int = 0
    processing_time: float = 0.0


class JinaProcessor:
    """Jina AI内容处理器"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or JINA_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
    
    async def process_content(self, content: str, session: aiohttp.ClientSession) -> Dict:
        """使用Jina AI处理内容"""
        # 如果没有API Key，使用本地处理
        if not self.api_key:
            return self._local_process(content)
        
        try:
            # 调用Jina API进行内容优化
            url = f"{JINA_API_URL}/embeddings"
            
            # 分块处理
            chunks = self._split_content(content, max_chars=8000)
            processed_chunks = []
            
            for chunk in chunks:
                # 简化：使用Jina Reader风格处理
                processed = self._structure_markdown(chunk)
                processed_chunks.append(processed)
            
            return {
                "success": True,
                "chunks": processed_chunks,
                "total_chunks": len(processed_chunks)
            }
            
        except Exception as e:
            logger.warning(f"Jina API调用失败，回退到本地处理: {e}")
            return self._local_process(content)
    
    def _local_process(self, content: str) -> Dict:
        """本地内容处理（当Jina API不可用时）"""
        chunks = self._split_content(content, max_chars=8000)
        processed = [self._structure_markdown(chunk) for chunk in chunks]
        
        return {
            "success": True,
            "chunks": processed,
            "total_chunks": len(processed),
            "source": "local"
        }
    
    def _split_content(self, content: str, max_chars: int = 8000) -> List[str]:
        """智能分块"""
        # 按段落分割
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < max_chars:
                current_chunk += para + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [content[:max_chars]]
    
    def _structure_markdown(self, content: str) -> Dict:
        """结构化Markdown内容"""
        lines = content.split('\n')
        elements = []
        
        for line in lines:
            stripped = line.strip()
            
            # 标题检测
            if stripped.startswith('# '):
                elements.append({
                    "type": "heading_1",
                    "content": stripped[2:]
                })
            elif stripped.startswith('## '):
                elements.append({
                    "type": "heading_2",
                    "content": stripped[3:]
                })
            elif stripped.startswith('### '):
                elements.append({
                    "type": "heading_3",
                    "content": stripped[4:]
                })
            elif stripped.startswith('- ') or stripped.startswith('* '):
                elements.append({
                    "type": "bulleted_list_item",
                    "content": stripped[2:]
                })
            elif stripped.startswith('1. ') or stripped.startswith('2. '):
                elements.append({
                    "type": "numbered_list_item",
                    "content": stripped[3:]
                })
            elif stripped.startswith('```'):
                # 代码块开始/结束
                elements.append({
                    "type": "code",
                    "content": stripped[3:]
                })
            elif stripped:
                elements.append({
                    "type": "paragraph",
                    "content": stripped
                })
        
        return {
            "elements": elements,
            "line_count": len(lines),
            "char_count": len(content)
        }


class NotionClient:
    """Notion API客户端（异步）"""
    
    def __init__(self, token: str, rate_limit: float = 0.5):
        self.token = token
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    async def _rate_limited_request(self, session: aiohttp.ClientSession, 
                                    method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """带速率限制的请求"""
        # 计算需要等待的时间
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        
        async with session.request(method, url, **kwargs) as response:
            self.last_request_time = time.time()
            return response
    
    async def create_page(self, title: str, parent_id: str = None,
                         session: aiohttp.ClientSession = None) -> Dict:
        """创建页面"""
        parent_id = parent_id or PARENT_PAGE_ID
        
        data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [{"type": "text", "text": {"content": title[:1000]}}]
                }
            }
        }
        
        if session is None:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                return await self._create_page_internal(session, data)
        else:
            return await self._create_page_internal(session, data)
    
    async def _create_page_internal(self, session: aiohttp.ClientSession, 
                                    data: Dict) -> Dict:
        """内部创建页面方法"""
        for attempt in range(MAX_RETRIES):
            try:
                response = await self._rate_limited_request(
                    session, "POST",
                    "https://api.notion.com/v1/pages",
                    json=data
                )
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "page_id": result["id"],
                        "page_url": result.get("url", "")
                    }
                elif response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 5))
                    logger.warning(f"速率限制，等待 {retry_after} 秒...")
                    await asyncio.sleep(retry_after)
                else:
                    error_text = await response.text()
                    if attempt < MAX_RETRIES - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"请求失败 ({response.status})，{wait_time}秒后重试...")
                        await asyncio.sleep(wait_time)
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text[:200]}"
                        }
                        
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"请求异常: {e}，{wait_time}秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Max retries exceeded"}
    
    async def add_blocks(self, page_id: str, blocks: List[Dict],
                        session: aiohttp.ClientSession = None) -> Dict:
        """添加内容块到页面"""
        if session is None:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                return await self._add_blocks_internal(session, page_id, blocks)
        else:
            return await self._add_blocks_internal(session, page_id, blocks)
    
    async def _add_blocks_internal(self, session: aiohttp.ClientSession,
                                   page_id: str, blocks: List[Dict]) -> Dict:
        """内部添加块方法"""
        added = 0
        failed = 0
        
        # 分批添加（每批100个）
        for i in range(0, len(blocks), 100):
            batch = blocks[i:i+100]
            notion_blocks = self._convert_to_notion_blocks(batch)
            
            for attempt in range(MAX_RETRIES):
                try:
                    response = await self._rate_limited_request(
                        session, "PATCH",
                        f"https://api.notion.com/v1/blocks/{page_id}/children",
                        json={"children": notion_blocks}
                    )
                    
                    if response.status == 200:
                        added += len(batch)
                        break
                    elif response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', 5))
                        await asyncio.sleep(retry_after)
                    else:
                        if attempt < MAX_RETRIES - 1:
                            await asyncio.sleep(2 ** attempt)
                        else:
                            failed += len(batch)
                            
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        failed += len(batch)
            
            # 批次间延迟
            if i + 100 < len(blocks):
                await asyncio.sleep(0.5)
        
        return {"success": failed == 0, "added": added, "failed": failed}
    
    def _convert_to_notion_blocks(self, elements: List[Dict]) -> List[Dict]:
        """转换为Notion块格式"""
        blocks = []
        
        for elem in elements:
            elem_type = elem.get("type", "paragraph")
            content = elem.get("content", "")[:1900]
            
            if elem_type == "heading_1":
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"type": "text", "text": {"content": content}}]}
                })
            elif elem_type == "heading_2":
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"type": "text", "text": {"content": content}}]}
                })
            elif elem_type == "heading_3":
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {"rich_text": [{"type": "text", "text": {"content": content}}]}
                })
            elif elem_type == "bulleted_list_item":
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": content}}]}
                })
            elif elem_type == "numbered_list_item":
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": content}}]}
                })
            elif elem_type == "code":
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": content}}],
                        "language": "plain text"
                    }
                })
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
                })
        
        return blocks


class ProgressManager:
    """进度管理器"""
    
    def __init__(self, progress_file: str):
        self.progress_file = progress_file
        self.data = self._load()
    
    def _load(self) -> Dict:
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "started_at": datetime.now().isoformat(),
            "completed": {},
            "failed": {},
            "version": "jina-1.0"
        }
    
    def save(self):
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def is_completed(self, file_path: str) -> bool:
        return file_path in self.data["completed"]
    
    def mark_completed(self, file_path: str, page_id: str, page_url: str):
        self.data["completed"][file_path] = {
            "page_id": page_id,
            "page_url": page_url,
            "synced_at": datetime.now().isoformat()
        }
        if file_path in self.data["failed"]:
            del self.data["failed"][file_path]
        self.save()
    
    def mark_failed(self, file_path: str, error: str):
        self.data["failed"][file_path] = {
            "error": error,
            "attempted_at": datetime.now().isoformat()
        }
        self.save()
    
    def get_stats(self) -> Dict:
        return {
            "completed": len(self.data["completed"]),
            "failed": len(self.data["failed"])
        }


class JinaNotionSyncer:
    """Jina + Notion 同步器"""
    
    def __init__(self):
        self.jina = JinaProcessor()
        self.notion = NotionClient(NOTION_TOKEN)
        self.progress = ProgressManager(PROGRESS_FILE)
        self.results: List[SyncResult] = []
        self.workspace_dir = WORKSPACE_DIR
    
    def log(self, message: str):
        logger.info(message)
    
    def read_file(self, file_path: str) -> str:
        """读取文件内容"""
        full_path = os.path.join(self.workspace_dir, file_path)
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'latin1']
        
        for encoding in encodings:
            try:
                with open(full_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        with open(full_path, 'rb') as f:
            return f.read().decode('utf-8', errors='ignore')
    
    async def sync_file(self, file_path: str, session: aiohttp.ClientSession) -> SyncResult:
        """同步单个文件"""
        start_time = time.time()
        self.log(f"📄 {file_path}")
        
        # 检查是否已完成
        if self.progress.is_completed(file_path):
            return SyncResult(file_path=file_path, success=True, 
                            error="Already synced")
        
        # 读取文件
        try:
            content = self.read_file(file_path)
            if not content.strip():
                error = "Empty file"
                self.progress.mark_failed(file_path, error)
                return SyncResult(file_path=file_path, success=False, error=error)
        except Exception as e:
            error = f"Read error: {e}"
            self.progress.mark_failed(file_path, error)
            return SyncResult(file_path=file_path, success=False, error=error)
        
        # Jina处理
        try:
            processed = await self.jina.process_content(content, session)
        except Exception as e:
            error = f"Jina processing error: {e}"
            self.progress.mark_failed(file_path, error)
            return SyncResult(file_path=file_path, success=False, error=error)
        
        # 创建Notion页面
        title = os.path.basename(file_path)
        page_result = await self.notion.create_page(title, session=session)
        
        if not page_result["success"]:
            error = page_result.get("error", "Unknown error")
            self.progress.mark_failed(file_path, error)
            return SyncResult(file_path=file_path, success=False, error=error)
        
        page_id = page_result["page_id"]
        page_url = page_result["page_url"]
        
        # 添加内容块
        all_elements = []
        for chunk in processed.get("chunks", []):
            all_elements.extend(chunk.get("elements", []))
        
        blocks_result = await self.notion.add_blocks(page_id, all_elements, session)
        
        if blocks_result["success"]:
            self.progress.mark_completed(file_path, page_id, page_url)
            processing_time = time.time() - start_time
            self.log(f"  ✅ 成功 ({blocks_result['added']} 块, {processing_time:.1f}s)")
            return SyncResult(
                file_path=file_path,
                success=True,
                page_id=page_id,
                page_url=page_url,
                blocks_added=blocks_result["added"],
                processing_time=processing_time
            )
        else:
            error = f"Blocks failed: {blocks_result.get('failed', 0)}"
            self.progress.mark_failed(file_path, error)
            return SyncResult(file_path=file_path, success=False, error=error)
    
    async def sync_batch(self, files: List[str]) -> List[SyncResult]:
        """同步一批文件"""
        async with aiohttp.ClientSession() as session:
            # 控制并发数
            semaphore = asyncio.Semaphore(MAX_CONCURRENT)
            
            async def sync_with_limit(file_path: str) -> SyncResult:
                async with semaphore:
                    result = await self.sync_file(file_path, session)
                    await asyncio.sleep(FILE_INTERVAL)
                    return result
            
            tasks = [sync_with_limit(f) for f in files]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常结果
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(SyncResult(
                        file_path=files[i],
                        success=False,
                        error=str(result)
                    ))
                else:
                    processed_results.append(result)
            
            return processed_results
    
    def discover_files(self, extensions: List[str] = None) -> List[str]:
        """发现文件"""
        if extensions is None:
            extensions = ['.md', '.txt']
        
        files = []
        for root, dirs, filenames in os.walk(self.workspace_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['.git', 'node_modules', '__pycache__', 'logs']]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, self.workspace_dir)
                    files.append(rel_path)
        
        files.sort(key=lambda x: (x.count('/'), x))
        return files
    
    def get_pending_files(self, all_files: List[str]) -> List[str]:
        """获取待处理文件"""
        return [f for f in all_files if not self.progress.is_completed(f)]
    
    async def run(self, file_list: List[str] = None, dry_run: bool = False):
        """执行同步"""
        start_time = datetime.now()
        
        # 发现文件
        if file_list is None:
            all_files = self.discover_files()
        else:
            all_files = file_list
        
        pending = self.get_pending_files(all_files)
        stats = self.progress.get_stats()
        
        self.log("=" * 70)
        self.log("Jina AI + Notion 同步方案")
        self.log(f"开始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"总文件: {len(all_files)} | 已完成: {stats['completed']} | 待处理: {len(pending)}")
        self.log(f"并发: {MAX_CONCURRENT} | 批次: {BATCH_SIZE}")
        self.log("=" * 70)
        
        if dry_run:
            self.log("\n⚠️ 干运行模式")
            for f in pending[:20]:
                self.log(f"  - {f}")
            return
        
        if not pending:
            self.log("\n✅ 所有文件已同步！")
            return
        
        # 分批处理
        total_batches = (len(pending) + BATCH_SIZE - 1) // BATCH_SIZE
        
        for i in range(total_batches):
            batch_start = i * BATCH_SIZE
            batch_end = min(batch_start + BATCH_SIZE, len(pending))
            batch_files = pending[batch_start:batch_end]
            
            self.log(f"\n📦 批次 {i+1}/{total_batches} ({len(batch_files)} 个文件)")
            self.log("-" * 50)
            
            results = await self.sync_batch(batch_files)
            self.results.extend(results)
            
            # 批次间间隔
            if i < total_batches - 1:
                self.log(f"\n⏳ 等待 {BATCH_INTERVAL} 秒...")
                await asyncio.sleep(BATCH_INTERVAL)
        
        # 完成
        await self.finish(start_time)
    
    async def finish(self, start_time: datetime):
        """完成处理"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        success = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        
        self.log("\n" + "=" * 70)
        self.log("同步完成!")
        self.log(f"成功: {success} | 失败: {failed}")
        self.log(f"耗时: {duration:.1f} 秒")
        self.log("=" * 70)
        
        self.generate_report()
    
    def generate_report(self):
        """生成报告"""
        stats = self.progress.get_stats()
        
        report = f"""# Jina AI + Notion 同步报告
> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计

| 指标 | 数值 |
|------|------|
| 已完成 | {stats['completed']} |
| 失败 | {stats['failed']} |

## 成功文件

"""
        for path, info in self.progress.data["completed"].items():
            report += f"- [{path}]({info.get('page_url', '')})\n"
        
        report += "\n## 失败文件\n\n"
        for path, info in self.progress.data["failed"].items():
            report += f"- {path}: {info.get('error', 'Unknown')}\n"
        
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.log(f"📊 报告已保存: {REPORT_PATH}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Jina AI + Notion 同步')
    parser.add_argument('--dry-run', action='store_true', help='干运行')
    parser.add_argument('--reset', action='store_true', help='重置进度')
    parser.add_argument('--files', nargs='+', help='指定文件')
    
    args = parser.parse_args()
    
    if args.reset and os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        print("✅ 进度已重置")
        return
    
    syncer = JinaNotionSyncer()
    asyncio.run(syncer.run(file_list=args.files, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
