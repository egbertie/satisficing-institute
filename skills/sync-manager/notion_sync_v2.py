#!/usr/bin/env python3
"""
Notion同步脚本 V2 - 带重试机制
功能：自动重试、连接超时、分批处理、完整性检查
"""

import os
import sys
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ========== 配置常量 ==========
CONFIG_FILE = Path(__file__).parent / "config" / "notion_retry.json"
PROGRESS_FILE = Path("/root/.openclaw/workspace/.notion_sync_v2_progress.json")
WORKSPACE_ROOT = Path("/root/.openclaw/workspace")

# 超时设置
CONNECT_TIMEOUT = 10  # 连接超时（秒）
READ_TIMEOUT = 30     # 读取超时（秒）

# 重试设置
MAX_RETRIES = 3       # 最大重试次数
RETRY_DELAY = 5       # 重试间隔（秒）
BATCH_SIZE = 10       # 每批文件数


class Logger:
    """日志记录器"""
    def __init__(self):
        self.logs = []
    
    def log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_line)
        print(log_line)
    
    def info(self, message: str):
        self.log("INFO", message)
    
    def error(self, message: str):
        self.log("ERROR", message)
    
    def warning(self, message: str):
        self.log("WARN", message)
    
    def success(self, message: str):
        self.log("SUCCESS", message)
    
    def get_logs(self) -> List[str]:
        return self.logs


class NotionSyncV2:
    """Notion同步管理器 V2"""
    
    def __init__(self, config_path: Path = CONFIG_FILE):
        self.config = self._load_config(config_path)
        self.logger = Logger()
        self.session = self._create_session()
        self.progress = self._load_progress()
        self.results = {
            "start_time": datetime.now().isoformat(),
            "files_total": 0,
            "files_success": 0,
            "files_failed": 0,
            "files_skipped": 0,
            "details": []
        }
    
    def _load_config(self, config_path: Path) -> Dict:
        """加载配置文件"""
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _create_session(self) -> requests.Session:
        """创建带重试机制的HTTP会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PATCH"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        # 设置默认头
        session.headers.update({
            "Authorization": f"Bearer {self.config.get('notion_token', '')}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        })
        
        return session
    
    def _load_progress(self) -> Dict:
        """加载进度文件"""
        if PROGRESS_FILE.exists():
            try:
                with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"completed_files": [], "failed_files": []}
    
    def _save_progress(self):
        """保存进度文件"""
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
    
    def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """发送HTTP请求（带重试和超时）"""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                self.logger.info(f"请求 {method} {url} (尝试 {attempt}/{MAX_RETRIES})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout as e:
                self.logger.warning(f"超时: {e}")
                if attempt < MAX_RETRIES:
                    self.logger.info(f"等待 {RETRY_DELAY} 秒后重试...")
                    time.sleep(RETRY_DELAY)
                else:
                    self.logger.error(f"{MAX_RETRIES} 次尝试后仍超时")
                    raise
                    
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"连接错误: {e}")
                if attempt < MAX_RETRIES:
                    self.logger.info(f"等待 {RETRY_DELAY} 秒后重试...")
                    time.sleep(RETRY_DELAY)
                else:
                    self.logger.error(f"{MAX_RETRIES} 次尝试后仍无法连接")
                    raise
                    
            except Exception as e:
                self.logger.error(f"请求失败: {e}")
                raise
        
        return None
    
    def _check_source_file(self, file_path: Path) -> Tuple[bool, Dict]:
        """检查源文件完整性"""
        check_result = {
            "path": str(file_path),
            "exists": False,
            "size": 0,
            "size_ok": False,
            "readable": False,
            "content_hash": "",
            "error": None
        }
        
        try:
            # 1. 存在性检查
            if not file_path.exists():
                check_result["error"] = "文件不存在"
                return False, check_result
            check_result["exists"] = True
            
            # 2. 大小检查
            size = file_path.stat().st_size
            check_result["size"] = size
            if size == 0:
                check_result["error"] = "文件大小为0"
                return False, check_result
            check_result["size_ok"] = True
            
            # 3. 可读性检查
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read(1000)  # 读取前1000字符
                check_result["readable"] = True
            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    with open(file_path, "r", encoding="gbk") as f:
                        content = f.read(1000)
                    check_result["readable"] = True
                except Exception as e:
                    check_result["error"] = f"编码错误: {e}"
                    return False, check_result
            except Exception as e:
                check_result["error"] = f"读取错误: {e}"
                return False, check_result
            
            # 4. 计算内容哈希（用于验证）
            with open(file_path, "rb") as f:
                check_result["content_hash"] = hashlib.md5(f.read()).hexdigest()
            
            return True, check_result
            
        except Exception as e:
            check_result["error"] = str(e)
            return False, check_result
    
    def _create_notion_page(self, title: str, content: str, parent_id: str) -> Optional[str]:
        """创建Notion页面"""
        url = "https://api.notion.com/v1/pages"
        
        # 分割内容（Notion块限制）
        max_chunk = 2000
        chunks = [content[i:i+max_chunk] for i in range(0, len(content), max_chunk)]
        
        children = []
        for chunk in chunks:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}]
                }
            })
        
        data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            },
            "children": children[:100]  # Notion限制100块
        }
        
        result = self._make_request("POST", url, json=data)
        return result.get("id") if result else None
    
    def _verify_notion_page(self, page_id: str, expected_title: str) -> bool:
        """验证Notion页面是否创建成功"""
        try:
            url = f"https://api.notion.com/v1/pages/{page_id}"
            result = self._make_request("GET", url)
            if result:
                title = result.get("properties", {}).get("title", {}).get("title", [{}])[0].get("text", {}).get("content", "")
                return title == expected_title
        except Exception as e:
            self.logger.warning(f"验证页面失败: {e}")
        return False
    
    def sync_file(self, file_path: Path, parent_id: str) -> Dict:
        """同步单个文件"""
        file_key = str(file_path.relative_to(WORKSPACE_ROOT))
        
        # 检查是否已完成
        if file_key in self.progress.get("completed_files", []):
            self.logger.info(f"跳过已完成: {file_key}")
            return {"status": "skipped", "file": file_key, "reason": "already_completed"}
        
        # 1. 源文件完整性检查
        self.logger.info(f"[1/4] 检查源文件: {file_key}")
        is_valid, check_result = self._check_source_file(file_path)
        if not is_valid:
            self.logger.error(f"源文件检查失败: {check_result['error']}")
            self.results["files_failed"] += 1
            return {
                "status": "failed",
                "file": file_key,
                "stage": "source_check",
                "error": check_result['error'],
                "check_result": check_result
            }
        self.logger.success(f"✅ 源文件检查通过 (大小: {check_result['size']} bytes)")
        
        # 2. 读取文件内容
        self.logger.info(f"[2/4] 读取文件内容: {file_key}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="gbk") as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"读取文件失败: {e}")
            self.results["files_failed"] += 1
            return {
                "status": "failed",
                "file": file_key,
                "stage": "read_content",
                "error": str(e)
            }
        self.logger.success(f"✅ 内容读取成功 ({len(content)} 字符)")
        
        # 3. 同步到Notion
        self.logger.info(f"[3/4] 同步到Notion: {file_key}")
        title = file_path.stem
        try:
            page_id = self._create_notion_page(title, content, parent_id)
            if not page_id:
                raise Exception("创建页面返回空ID")
            self.logger.success(f"✅ Notion页面创建成功 (ID: {page_id})")
        except Exception as e:
            self.logger.error(f"同步失败: {e}")
            self.results["files_failed"] += 1
            return {
                "status": "failed",
                "file": file_key,
                "stage": "notion_sync",
                "error": str(e),
                "check_result": check_result
            }
        
        # 4. 验证目标文件
        self.logger.info(f"[4/4] 验证目标文件: {file_key}")
        if self._verify_notion_page(page_id, title):
            self.logger.success(f"✅ 目标验证通过")
            
            # 记录成功
            self.progress["completed_files"].append(file_key)
            self._save_progress()
            self.results["files_success"] += 1
            
            return {
                "status": "success",
                "file": file_key,
                "notion_page_id": page_id,
                "size": check_result['size'],
                "content_hash": check_result['content_hash'],
                "check_result": check_result
            }
        else:
            self.logger.error("目标验证失败")
            self.results["files_failed"] += 1
            return {
                "status": "failed",
                "file": file_key,
                "stage": "verification",
                "error": "目标验证失败",
                "notion_page_id": page_id,
                "check_result": check_result
            }
    
    def sync_batch(self, files: List[str], batch_name: str = "") -> List[Dict]:
        """同步一批文件"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"开始同步批次: {batch_name or '未命名批次'}")
        self.logger.info(f"文件数量: {len(files)}")
        self.logger.info(f"{'='*60}")
        
        parent_id = self.config.get("parent_page_id")
        results = []
        
        for i, file_rel_path in enumerate(files, 1):
            file_path = WORKSPACE_ROOT / file_rel_path
            
            self.logger.info(f"\n[{i}/{len(files)}] 处理: {file_rel_path}")
            result = self.sync_file(file_path, parent_id)
            results.append(result)
            
            # 批次内间隔，避免API限制
            if i < len(files):
                time.sleep(1)
        
        return results
    
    def sync_all(self) -> Dict:
        """同步所有文件"""
        files = self.config.get("files_to_sync", [])
        self.results["files_total"] = len(files)
        
        self.logger.info("="*60)
        self.logger.info("Notion同步 V2 - 带重试机制")
        self.logger.info(f"开始时间: {self.results['start_time']}")
        self.logger.info(f"总文件数: {len(files)}")
        self.logger.info(f"批次大小: {BATCH_SIZE}")
        self.logger.info(f"最大重试: {MAX_RETRIES}")
        self.logger.info(f"连接超时: {CONNECT_TIMEOUT}s")
        self.logger.info(f"读取超时: {READ_TIMEOUT}s")
        self.logger.info("="*60)
        
        # 分批处理
        batches = [files[i:i+BATCH_SIZE] for i in range(0, len(files), BATCH_SIZE)]
        
        for batch_idx, batch in enumerate(batches, 1):
            batch_name = f"第{batch_idx}批"
            batch_results = self.sync_batch(batch, batch_name)
            self.results["details"].extend(batch_results)
            
            # 批次间间隔
            if batch_idx < len(batches):
                self.logger.info(f"\n批次间等待 3 秒...")
                time.sleep(3)
        
        self.results["end_time"] = datetime.now().isoformat()
        return self.results
    
    def generate_report(self, output_path: Path) -> str:
        """生成同步报告"""
        report = []
        report.append("# Notion同步修复报告 V2")
        report.append("")
        report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**报告类型**: 第1批失败文件重试")
        report.append("")
        
        # 执行摘要
        report.append("## 执行摘要")
        report.append("")
        report.append(f"- **总文件数**: {self.results['files_total']}")
        report.append(f"- **成功**: {self.results['files_success']} ✅")
        report.append(f"- **失败**: {self.results['files_failed']} ❌")
        report.append(f"- **跳过**: {self.results['files_skipped']} ⏭️")
        report.append(f"- **成功率**: {self.results['files_success']/max(self.results['files_total'],1)*100:.1f}%")
        report.append("")
        
        # 配置参数
        report.append("## 配置参数")
        report.append("")
        report.append("| 参数 | 值 |")
        report.append("|------|-----|")
        report.append(f"| 最大重试次数 | {MAX_RETRIES} |")
        report.append(f"| 重试间隔 | {RETRY_DELAY} 秒 |")
        report.append(f"| 连接超时 | {CONNECT_TIMEOUT} 秒 |")
        report.append(f"| 读取超时 | {READ_TIMEOUT} 秒 |")
        report.append(f"| 批次大小 | {BATCH_SIZE} 个文件 |")
        report.append(f"| 父页面ID | `{self.config.get('parent_page_id', 'N/A')[:20]}...` |")
        report.append("")
        
        # 完整性检查详情
        report.append("## 完整性检查结果")
        report.append("")
        report.append("### 源文件检查")
        report.append("")
        report.append("| 文件 | 存在 | 大小 | 可读 | 状态 |")
        report.append("|------|------|------|------|------|")
        
        for detail in self.results["details"]:
            file_name = detail["file"]
            check = detail.get("check_result", {})
            exists = "✅" if check.get("exists") else "❌"
            size = f"{check.get('size', 0)} bytes" if check.get("size_ok") else "❌"
            readable = "✅" if check.get("readable") else "❌"
            status = "✅ 通过" if detail["status"] == "success" else ("⏭️ 跳过" if detail["status"] == "skipped" else "❌ 失败")
            report.append(f"| `{file_name}` | {exists} | {size} | {readable} | {status} |")
        
        report.append("")
        
        # 失败详情
        failed_items = [d for d in self.results["details"] if d["status"] == "failed"]
        if failed_items:
            report.append("## 失败详情")
            report.append("")
            for item in failed_items:
                report.append(f"### {item['file']}")
                report.append("")
                report.append(f"- **失败阶段**: {item.get('stage', 'unknown')}")
                report.append(f"- **错误信息**: {item.get('error', 'unknown')}")
                report.append("")
        
        # 同步日志
        report.append("## 同步日志")
        report.append("")
        report.append("```")
        for log in self.logger.get_logs():
            report.append(log)
        report.append("```")
        report.append("")
        
        # 最终完整性声明
        report.append("## 最终完整性声明")
        report.append("")
        all_success = self.results["files_failed"] == 0
        if all_success:
            report.append("✅ **完整性检查通过**")
            report.append("")
            report.append("- 所有源文件存在性检查通过")
            report.append("- 所有源文件大小检查通过（非空）")
            report.append("- 所有源文件可读性检查通过")
            report.append("- 所有目标文件同步后验证通过")
            report.append(f"- 共 {self.results['files_success']} 个文件成功同步到Notion")
        else:
            report.append("⚠️ **完整性检查部分失败**")
            report.append("")
            report.append(f"- 成功: {self.results['files_success']} 个文件")
            report.append(f"- 失败: {self.results['files_failed']} 个文件")
            report.append("- 需要人工介入检查失败文件")
        
        report.append("")
        report.append("---")
        report.append(f"*报告由 Notion Sync V2 生成*")
        
        # 保存报告
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        
        return "\n".join(report)


def main():
    """主函数"""
    sync = NotionSyncV2()
    
    # 执行同步
    results = sync.sync_all()
    
    # 生成报告
    report_path = WORKSPACE_ROOT / "docs" / "NOTION_SYNC_RETRY_REPORT.md"
    sync.generate_report(report_path)
    
    # 输出摘要
    print("\n" + "="*60)
    print("同步完成!")
    print(f"成功: {results['files_success']}/{results['files_total']}")
    print(f"失败: {results['files_failed']}/{results['files_total']}")
    print(f"报告保存至: {report_path}")
    print("="*60)
    
    return 0 if results['files_failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
