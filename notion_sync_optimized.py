#!/usr/bin/env python3
"""
Notion同步脚本 - 优化版 V4
特性：
- 断点续传（保存进度，随时恢复）
- 智能重试（指数退避，自动恢复）
- 连接池复用（提高稳定性）
- 批量处理（每批10个文件）
- 网络故障自动恢复
"""
import os
import sys
import time
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "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")
PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "31fa8a0e-2bba-81fa-b98a-d61da835051e")
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/root/.openclaw/workspace")

# 文件路径配置
PROGRESS_FILE = os.path.join(WORKSPACE_DIR, ".notion_sync_v4_progress.json")
REPORT_PATH = os.path.join(WORKSPACE_DIR, "docs/NOTION_SYNC_V4_REPORT.md")
LOG_PATH = os.path.join(WORKSPACE_DIR, "logs/notion_sync_v4.log")
FAILED_LOG = os.path.join(WORKSPACE_DIR, "logs/notion_sync_failed.json")

# 同步参数
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
FILE_INTERVAL = float(os.getenv("FILE_INTERVAL", "2.0"))
BATCH_INTERVAL = float(os.getenv("BATCH_INTERVAL", "10.0"))
CONNECT_TIMEOUT = int(os.getenv("CONNECT_TIMEOUT", "30"))
READ_TIMEOUT = int(os.getenv("READ_TIMEOUT", "120"))

# 重试策略
BACKOFF_FACTOR = float(os.getenv("BACKOFF_FACTOR", "2.0"))
STATUS_FORCELIST = [429, 500, 502, 503, 504]

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


class ConnectionPool:
    """管理HTTP连接池，提高连接稳定性"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=STATUS_FORCELIST,
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PATCH"]
        )
        
        # 配置连接池
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy
        )
        
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # 设置默认headers
        self.session.headers.update({
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        })
    
    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """发送请求，自动处理重试"""
        kwargs.setdefault('timeout', (CONNECT_TIMEOUT, READ_TIMEOUT))
        return self.session.request(method, url, **kwargs)
    
    def close(self):
        """关闭连接池"""
        self.session.close()


class ProgressManager:
    """管理同步进度，支持断点续传"""
    
    def __init__(self, progress_file: str):
        self.progress_file = progress_file
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """加载进度文件"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载进度文件失败: {e}，将创建新进度")
        
        return {
            "started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "total_files": 0,
            "completed_files": [],
            "failed_files": {},  # file_path -> {error, retries, last_attempt}
            "current_batch": 0,
            "total_batches": 0,
            "version": "4.0"
        }
    
    def save(self):
        """保存进度"""
        self.progress["updated_at"] = datetime.now().isoformat()
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存进度失败: {e}")
    
    def is_completed(self, file_path: str) -> bool:
        """检查文件是否已完成"""
        return file_path in self.progress["completed_files"]
    
    def mark_completed(self, file_path: str, page_id: str, page_url: str):
        """标记文件为已完成"""
        if file_path not in self.progress["completed_files"]:
            self.progress["completed_files"].append({
                "path": file_path,
                "page_id": page_id,
                "page_url": page_url,
                "synced_at": datetime.now().isoformat()
            })
            # 从失败列表中移除
            if file_path in self.progress["failed_files"]:
                del self.progress["failed_files"][file_path]
            self.save()
    
    def mark_failed(self, file_path: str, error: str, retry_count: int = 0):
        """标记文件为失败"""
        self.progress["failed_files"][file_path] = {
            "error": error,
            "retries": retry_count,
            "last_attempt": datetime.now().isoformat()
        }
        self.save()
    
    def get_retry_count(self, file_path: str) -> int:
        """获取文件的重试次数"""
        if file_path in self.progress["failed_files"]:
            return self.progress["failed_files"][file_path].get("retries", 0)
        return 0
    
    def get_pending_files(self, all_files: List[str]) -> List[str]:
        """获取待处理的文件列表"""
        completed = {item["path"] if isinstance(item, dict) else item 
                    for item in self.progress["completed_files"]}
        pending = []
        
        for file_path in all_files:
            if file_path not in completed:
                # 检查是否超过最大重试次数
                retry_count = self.get_retry_count(file_path)
                if retry_count < MAX_RETRIES:
                    pending.append(file_path)
                else:
                    logger.warning(f"跳过 {file_path}，已达到最大重试次数")
        
        return pending
    
    def get_stats(self) -> Dict:
        """获取进度统计"""
        total = self.progress["total_files"]
        completed = len(self.progress["completed_files"])
        failed = len(self.progress["failed_files"])
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": total - completed,
            "progress_pct": (completed / total * 100) if total > 0 else 0
        }


class NotionSyncer:
    """Notion同步器 - 优化版"""
    
    def __init__(self):
        self.pool = ConnectionPool()
        self.progress = ProgressManager(PROGRESS_FILE)
        self.results = []
        self.start_time = None
        
    def log(self, message: str, level: str = "info"):
        """记录日志"""
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)
    
    def get_file_hash(self, file_path: str) -> str:
        """计算文件哈希，用于检测变更"""
        full_path = os.path.join(WORKSPACE_DIR, file_path)
        if not os.path.exists(full_path):
            return ""
        
        hasher = hashlib.md5()
        with open(full_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def read_file_content(self, file_path: str) -> str:
        """读取文件内容，支持多种编码"""
        full_path = os.path.join(WORKSPACE_DIR, file_path)
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'latin1']
        
        for encoding in encodings:
            try:
                with open(full_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # 最后尝试忽略错误
        with open(full_path, 'rb') as f:
            return f.read().decode('utf-8', errors='ignore')
    
    def content_to_blocks(self, content: str, max_block_size: int = 1900) -> List[Dict]:
        """将内容转换为Notion块，优化处理"""
        blocks = []
        
        # 按行分割，保留换行
        lines = content.split('\n')
        current_para = ""
        
        for line in lines:
            # 处理标题
            if line.startswith('# '):
                if current_para:
                    blocks.append(self._create_paragraph_block(current_para))
                    current_para = ""
                blocks.append(self._create_heading_block(line[2:], 1))
            elif line.startswith('## '):
                if current_para:
                    blocks.append(self._create_paragraph_block(current_para))
                    current_para = ""
                blocks.append(self._create_heading_block(line[3:], 2))
            elif line.startswith('### '):
                if current_para:
                    blocks.append(self._create_paragraph_block(current_para))
                    current_para = ""
                blocks.append(self._create_heading_block(line[4:], 3))
            elif line.strip() == '':
                # 空行，结束当前段落
                if current_para:
                    blocks.append(self._create_paragraph_block(current_para))
                    current_para = ""
            else:
                # 普通文本
                if current_para:
                    current_para += '\n' + line
                else:
                    current_para = line
                
                # 检查段落长度
                if len(current_para.encode('utf-8')) > max_block_size:
                    blocks.append(self._create_paragraph_block(current_para))
                    current_para = ""
        
        # 处理剩余内容
        if current_para:
            blocks.append(self._create_paragraph_block(current_para))
        
        # 限制块数（Notion限制每页1000块）
        return blocks[:990]
    
    def _create_paragraph_block(self, text: str) -> Dict:
        """创建段落块"""
        # 分割超长文本
        if len(text.encode('utf-8')) > 1900:
            chunks = self._split_text(text, 1900)
            return {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunks[0]}}]
                }
            }
        
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        }
    
    def _create_heading_block(self, text: str, level: int) -> Dict:
        """创建标题块"""
        level = min(max(level, 1), 3)
        heading_types = {1: "heading_1", 2: "heading_2", 3: "heading_3"}
        
        return {
            "object": "block",
            "type": heading_types[level],
            heading_types[level]: {
                "rich_text": [{"type": "text", "text": {"content": text[:1900]}}]
            }
        }
    
    def _split_text(self, text: str, max_bytes: int) -> List[str]:
        """按字节长度安全分割文本"""
        chunks = []
        current = ""
        
        for char in text:
            if len((current + char).encode('utf-8')) > max_bytes:
                chunks.append(current)
                current = char
            else:
                current += char
        
        if current:
            chunks.append(current)
        
        return chunks
    
    def create_page(self, title: str, content: str, retry_count: int = 0) -> Dict:
        """创建Notion页面，带重试机制"""
        try:
            # 步骤1：创建空页面
            data = {
                "parent": {"page_id": PARENT_PAGE_ID},
                "properties": {
                    "title": {
                        "title": [{"type": "text", "text": {"content": title[:1000]}}]
                    }
                }
            }
            
            response = self.pool.request(
                "POST",
                "https://api.notion.com/v1/pages",
                json=data
            )
            
            if response.status_code != 200:
                error_msg = response.text[:300] if response.text else f"HTTP {response.status_code}"
                
                # 特定错误处理
                if response.status_code == 429:  # 速率限制
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self.log(f"  ⚠️ 触发速率限制，等待 {retry_after} 秒...")
                    time.sleep(retry_after)
                    if retry_count < MAX_RETRIES:
                        return self.create_page(title, content, retry_count + 1)
                
                return {"success": False, "error": f"Create page failed: {error_msg}"}
            
            result = response.json()
            page_id = result["id"]
            page_url = result.get("url", "")
            
            # 步骤2：添加内容块
            blocks = self.content_to_blocks(content)
            
            # 分批添加（每批100个）
            for i in range(0, len(blocks), 100):
                batch = blocks[i:i+100]
                
                patch_response = self.pool.request(
                    "PATCH",
                    f"https://api.notion.com/v1/blocks/{page_id}/children",
                    json={"children": batch}
                )
                
                if patch_response.status_code != 200:
                    self.log(f"  ⚠️ 添加内容块 {i+1}-{i+len(batch)} 失败: {patch_response.text[:100]}")
                
                # 批次间短暂等待
                if i + 100 < len(blocks):
                    time.sleep(0.3)
            
            return {
                "success": True,
                "page_id": page_id,
                "page_url": page_url,
                "blocks_added": len(blocks)
            }
            
        except requests.exceptions.Timeout:
            if retry_count < MAX_RETRIES:
                wait_time = BACKOFF_FACTOR ** retry_count
                self.log(f"  ⚠️ 请求超时，{wait_time:.1f}秒后重试 ({retry_count+1}/{MAX_RETRIES})...")
                time.sleep(wait_time)
                return self.create_page(title, content, retry_count + 1)
            return {"success": False, "error": "Max retries exceeded (timeout)"}
            
        except requests.exceptions.ConnectionError as e:
            if retry_count < MAX_RETRIES:
                wait_time = BACKOFF_FACTOR ** retry_count
                self.log(f"  ⚠️ 连接错误，{wait_time:.1f}秒后重试 ({retry_count+1}/{MAX_RETRIES})...")
                time.sleep(wait_time)
                return self.create_page(title, content, retry_count + 1)
            return {"success": False, "error": f"Connection failed after {MAX_RETRIES} retries: {str(e)[:100]}"}
            
        except Exception as e:
            if retry_count < MAX_RETRIES:
                wait_time = BACKOFF_FACTOR ** retry_count
                self.log(f"  ⚠️ 错误: {str(e)[:50]}，{wait_time:.1f}秒后重试...")
                time.sleep(wait_time)
                return self.create_page(title, content, retry_count + 1)
            return {"success": False, "error": str(e)[:200]}
    
    def verify_page(self, page_id: str) -> bool:
        """验证页面是否存在"""
        try:
            response = self.pool.request(
                "GET",
                f"https://api.notion.com/v1/pages/{page_id}"
            )
            return response.status_code == 200
        except:
            return False
    
    def sync_file(self, file_path: str) -> Dict:
        """同步单个文件"""
        self.log(f"📄 {file_path}")
        
        # 检查源文件
        full_path = os.path.join(WORKSPACE_DIR, file_path)
        if not os.path.exists(full_path):
            error = "源文件不存在"
            self.progress.mark_failed(file_path, error)
            return {"success": False, "error": error}
        
        # 读取内容
        try:
            content = self.read_file_content(file_path)
            if not content.strip():
                error = "文件内容为空"
                self.progress.mark_failed(file_path, error)
                return {"success": False, "error": error}
        except Exception as e:
            error = f"读取失败: {str(e)[:50]}"
            self.progress.mark_failed(file_path, error)
            return {"success": False, "error": error}
        
        # 创建页面
        title = os.path.basename(file_path)
        result = self.create_page(title, content)
        
        if result.get("success"):
            page_id = result.get("page_id")
            page_url = result.get("page_url")
            
            # 验证
            time.sleep(0.5)
            verified = self.verify_page(page_id)
            
            if verified:
                self.progress.mark_completed(file_path, page_id, page_url)
                self.log(f"  ✅ 成功 ({result.get('blocks_added', 0)} 块)")
                return {
                    "success": True,
                    "page_id": page_id,
                    "page_url": page_url,
                    "blocks": result.get("blocks_added", 0)
                }
            else:
                error = "页面验证失败"
                self.progress.mark_failed(file_path, error)
                return {"success": False, "error": error}
        else:
            error = result.get("error", "Unknown error")
            retry_count = self.progress.get_retry_count(file_path) + 1
            self.progress.mark_failed(file_path, error, retry_count)
            self.log(f"  ❌ {error[:80]}", "error")
            return {"success": False, "error": error}
    
    def discover_files(self, extensions: List[str] = None) -> List[str]:
        """发现工作区中的所有文档文件"""
        if extensions is None:
            extensions = ['.md', '.txt', '.mdx']
        
        files = []
        for root, dirs, filenames in os.walk(WORKSPACE_DIR):
            # 跳过隐藏目录和特定目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ['.git', 'node_modules', '__pycache__', 'logs']]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, WORKSPACE_DIR)
                    files.append(rel_path)
        
        # 排序：先根目录，后子目录
        files.sort(key=lambda x: (x.count('/'), x))
        return files
    
    def run(self, file_list: List[str] = None, dry_run: bool = False):
        """执行同步"""
        self.start_time = datetime.now()
        
        # 发现文件
        if file_list is None:
            all_files = self.discover_files()
        else:
            all_files = file_list
        
        self.progress.progress["total_files"] = len(all_files)
        pending_files = self.progress.get_pending_files(all_files)
        
        # 显示状态
        stats = self.progress.get_stats()
        self.log("=" * 70)
        self.log("Notion同步 V4 - 优化版")
        self.log(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"总文件: {stats['total']} | 已完成: {stats['completed']} | 待处理: {len(pending_files)}")
        self.log(f"批次大小: {BATCH_SIZE} | 最大重试: {MAX_RETRIES}")
        self.log("=" * 70)
        
        if dry_run:
            self.log("\n⚠️ 干运行模式 - 不会实际同步")
            self.log(f"待处理文件 ({len(pending_files)}):")
            for f in pending_files[:20]:
                self.log(f"  - {f}")
            if len(pending_files) > 20:
                self.log(f"  ... 还有 {len(pending_files) - 20} 个文件")
            return
        
        if not pending_files:
            self.log("\n✅ 所有文件已同步完成！")
            self.generate_report()
            return
        
        # 分批处理
        total_batches = (len(pending_files) + BATCH_SIZE - 1) // BATCH_SIZE
        success_count = 0
        fail_count = 0
        
        for batch_idx in range(total_batches):
            batch_start = batch_idx * BATCH_SIZE
            batch_end = min(batch_start + BATCH_SIZE, len(pending_files))
            batch_files = pending_files[batch_start:batch_end]
            
            self.log(f"\n📦 批次 {batch_idx + 1}/{total_batches} ({len(batch_files)} 个文件)")
            self.log("-" * 50)
            
            for idx, file_path in enumerate(batch_files, 1):
                result = self.sync_file(file_path)
                
                if result["success"]:
                    success_count += 1
                else:
                    fail_count += 1
                
                self.results.append({
                    "file": file_path,
                    "success": result["success"],
                    "error": result.get("error", ""),
                    "page_id": result.get("page_id", ""),
                    "page_url": result.get("page_url", "")
                })
                
                # 文件间间隔
                if idx < len(batch_files):
                    time.sleep(FILE_INTERVAL)
            
            # 批次间间隔
            if batch_idx < total_batches - 1:
                self.log(f"\n⏳ 批次间隔 {BATCH_INTERVAL} 秒...")
                time.sleep(BATCH_INTERVAL)
        
        # 完成
        self.finish(success_count, fail_count)
    
    def finish(self, success_count: int, fail_count: int):
        """完成同步，生成报告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.log("\n" + "=" * 70)
        self.log("同步完成!")
        self.log(f"成功: {success_count} | 失败: {fail_count}")
        self.log(f"总耗时: {duration:.1f} 秒")
        self.log("=" * 70)
        
        self.generate_report()
        
        # 关闭连接池
        self.pool.close()
    
    def generate_report(self):
        """生成详细报告"""
        stats = self.progress.get_stats()
        
        report = f"""# Notion同步报告 V4
> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 同步统计

| 指标 | 数值 |
|------|------|
| 总文件数 | {stats['total']} |
| 已完成 | {stats['completed']} |
| 失败 | {stats['failed']} |
| 进度 | {stats['progress_pct']:.1f}% |

## 失败文件

"""
        
        if self.progress.progress["failed_files"]:
            report += "| 文件 | 错误 | 重试次数 | 最后尝试 |\n"
            report += "|------|------|----------|----------|\n"
            
            for file_path, info in self.progress.progress["failed_files"].items():
                error = info.get("error", "Unknown")[:50]
                retries = info.get("retries", 0)
                last = info.get("last_attempt", "-")
                report += f"| {file_path} | {error} | {retries} | {last} |\n"
        else:
            report += "✅ 无失败文件\n"
        
        report += f"""

## 配置文件

```
BATCH_SIZE={BATCH_SIZE}
MAX_RETRIES={MAX_RETRIES}
FILE_INTERVAL={FILE_INTERVAL}
BATCH_INTERVAL={BATCH_INTERVAL}
BACKOFF_FACTOR={BACKOFF_FACTOR}
```

---
*报告由 notion_sync_optimized.py V4 生成*
"""
        
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.log(f"📊 报告已保存: {REPORT_PATH}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Notion同步 V4 - 优化版')
    parser.add_argument('--dry-run', action='store_true', help='干运行模式')
    parser.add_argument('--reset', action='store_true', help='重置进度')
    parser.add_argument('--files', nargs='+', help='指定文件列表')
    parser.add_argument('--batch-size', type=int, default=None, help='批次大小')
    
    args = parser.parse_args()
    
    # 更新全局批次大小
    global BATCH_SIZE
    if args.batch_size is not None:
        BATCH_SIZE = args.batch_size
    
    # 重置进度
    if args.reset:
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            print("✅ 进度已重置")
        return
    
    # 执行同步
    syncer = NotionSyncer()
    
    try:
        syncer.run(file_list=args.files, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断，进度已保存")
        syncer.progress.save()
        sys.exit(1)


if __name__ == "__main__":
    main()
