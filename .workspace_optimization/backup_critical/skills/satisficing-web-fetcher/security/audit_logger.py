#!/usr/bin/env python3
"""
审计日志模块

功能：
1. 记录所有抓取请求
2. 日志轮转和归档
3. 支持日志查询

安全要求：
- 所有请求必须记录
- 日志本地存储，不上传
- 保留30天
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class AuditEntry:
    """审计日志条目"""
    timestamp: float
    url: str
    fetcher_type: str
    success: bool
    error: Optional[str]
    source_ip: str = "127.0.0.1"
    user_agent: str = ""
    request_size: int = 0
    response_size: int = 0
    duration_ms: int = 0


class AuditLogger:
    """审计日志记录器"""
    
    DEFAULT_LOG_DIR = Path(__file__).parent.parent / ".audit_logs"
    RETENTION_DAYS = 30
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Args:
            log_dir: 日志目录，默认使用 .audit_logs
        """
        self.log_dir = log_dir or self.DEFAULT_LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._current_date = datetime.now().date()
        self._current_file = self._get_log_file()
    
    def log(self, entry_data: Dict[str, Any]):
        """
        记录日志条目
        
        Args:
            entry_data: 日志数据字典
        """
        # 检查是否需要切换日志文件（跨天）
        today = datetime.now().date()
        if today != self._current_date:
            self._current_date = today
            self._current_file = self._get_log_file()
            self._cleanup_old_logs()
        
        # 确保有时间戳
        if "timestamp" not in entry_data:
            entry_data["timestamp"] = time.time()
        
        # 写入日志
        with open(self._current_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry_data, ensure_ascii=False) + '\n')
    
    def query(self, 
              start_time: Optional[float] = None,
              end_time: Optional[float] = None,
              url_pattern: Optional[str] = None,
              success_only: Optional[bool] = None,
              limit: int = 100) -> List[Dict[str, Any]]:
        """
        查询日志
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            url_pattern: URL匹配模式
            success_only: 仅成功请求
            limit: 返回条数限制
            
        Returns:
            List[Dict]: 匹配的日志条目
        """
        results = []
        
        # 获取所有日志文件
        log_files = sorted(self.log_dir.glob("audit_*.log"), reverse=True)
        
        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    # 时间过滤
                    if start_time and entry.get("timestamp", 0) < start_time:
                        continue
                    if end_time and entry.get("timestamp", 0) > end_time:
                        continue
                    
                    # URL过滤
                    if url_pattern and url_pattern not in entry.get("url", ""):
                        continue
                    
                    # 成功状态过滤
                    if success_only is not None and entry.get("success") != success_only:
                        continue
                    
                    results.append(entry)
                    
                    if len(results) >= limit:
                        return results
        
        return results
    
    def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            days: 统计最近N天
            
        Returns:
            Dict: 统计信息
        """
        cutoff = time.time() - (days * 24 * 3600)
        entries = self.query(start_time=cutoff, limit=10000)
        
        total = len(entries)
        successful = sum(1 for e in entries if e.get("success"))
        failed = total - successful
        
        # 按域名统计
        domains: Dict[str, int] = {}
        for entry in entries:
            url = entry.get("url", "")
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                domains[domain] = domains.get(domain, 0) + 1
            except:
                pass
        
        return {
            "period_days": days,
            "total_requests": total,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "N/A",
            "top_domains": sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10],
        }
    
    def _get_log_file(self) -> Path:
        """获取当前日期的日志文件路径"""
        date_str = self._current_date.strftime("%Y%m%d")
        return self.log_dir / f"audit_{date_str}.log"
    
    def _cleanup_old_logs(self):
        """清理过期日志"""
        cutoff = datetime.now() - timedelta(days=self.RETENTION_DAYS)
        
        for log_file in self.log_dir.glob("audit_*.log"):
            try:
                # 从文件名解析日期
                date_str = log_file.stem.replace("audit_", "")
                file_date = datetime.strptime(date_str, "%Y%m%d").date()
                
                if file_date < cutoff.date():
                    log_file.unlink()
                    print(f"[AuditLogger] Removed old log: {log_file}")
            except:
                pass


# 便捷函数

def log_request(url: str, success: bool, error: Optional[str] = None, **kwargs):
    """便捷记录请求日志"""
    logger = AuditLogger()
    logger.log({
        "url": url,
        "success": success,
        "error": error,
        **kwargs
    })


def get_recent_audit(limit: int = 50) -> List[Dict[str, Any]]:
    """获取最近审计日志"""
    logger = AuditLogger()
    return logger.query(limit=limit)
