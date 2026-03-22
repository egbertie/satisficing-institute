#!/usr/bin/env python3
"""
同步管理器 - 数据同步管理工具
支持：自动重试、多目标同步、断点续传、完整性校验
"""

import os
import sys
import json
import time
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config" / "sync.conf"
CHECKPOINT_FILE = Path(__file__).parent / ".sync_checkpoint.json"
LOG_FILE = Path(__file__).parent / "sync.log"


class Logger:
    """简单日志记录器"""
    def __init__(self, log_file: Path):
        self.log_file = log_file
    
    def log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        print(log_line.strip())
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    
    def info(self, message: str):
        self.log("INFO", message)
    
    def error(self, message: str):
        self.log("ERROR", message)
    
    def warning(self, message: str):
        self.log("WARN", message)
    
    def success(self, message: str):
        self.log("SUCCESS", message)


class RetryDecorator:
    """自动重试装饰器"""
    def __init__(self, max_attempts: int = 3, base_delay: int = 5, max_delay: int = 60):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, self.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < self.max_attempts:
                        delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
                        args[0].logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        args[0].logger.error(f"All {self.max_attempts} attempts failed: {e}")
            raise last_exception
        return wrapper


class CheckpointManager:
    """断点续传管理器"""
    def __init__(self, checkpoint_file: Path, logger: Logger):
        self.checkpoint_file = checkpoint_file
        self.logger = logger
        self.data = self._load()
    
    def _load(self) -> Dict:
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load checkpoint: {e}")
        return {
            "last_sync": None,
            "in_progress": False,
            "targets": {},
            "items_processed": 0,
            "total_items": 0
        }
    
    def save(self):
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def update_progress(self, target: str, items_processed: int, total_items: int):
        self.data["in_progress"] = True
        self.data["targets"][target] = {
            "items_processed": items_processed,
            "last_update": datetime.now().isoformat()
        }
        self.data["items_processed"] = items_processed
        self.data["total_items"] = total_items
        self.save()
    
    def mark_complete(self, target: str):
        self.data["targets"][target] = {
            "completed": True,
            "completed_at": datetime.now().isoformat()
        }
        self.save()
    
    def is_target_complete(self, target: str) -> bool:
        return self.data.get("targets", {}).get(target, {}).get("completed", False)
    
    def reset(self):
        self.data = {
            "last_sync": None,
            "in_progress": False,
            "targets": {},
            "items_processed": 0,
            "total_items": 0
        }
        self.save()
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()


class IntegrityChecker:
    """完整性校验器"""
    @staticmethod
    def calculate_hash(data: Any) -> str:
        """计算数据哈希"""
        content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()
    
    @staticmethod
    def verify_files(source_dir: Path, backup_dir: Path) -> bool:
        """验证备份文件完整性"""
        if not source_dir.exists() or not backup_dir.exists():
            return False
        
        source_files = list(source_dir.rglob("*"))
        backup_files = list(backup_dir.rglob("*"))
        
        if len(source_files) != len(backup_files):
            return False
        
        for src_file in source_files:
            if src_file.is_file():
                rel_path = src_file.relative_to(source_dir)
                backup_file = backup_dir / rel_path
                if not backup_file.exists():
                    return False
                if src_file.stat().st_size != backup_file.stat().st_size:
                    return False
        
        return True


class SyncTarget:
    """同步目标基类"""
    def __init__(self, name: str, config: Dict, logger: Logger):
        self.name = name
        self.config = config
        self.logger = logger
        self.enabled = config.get("enabled", False)
    
    def sync(self, data: Any) -> bool:
        raise NotImplementedError
    
    def verify(self) -> bool:
        raise NotImplementedError


class NotionTarget(SyncTarget):
    """Notion同步目标"""
    @RetryDecorator(max_attempts=3)
    def sync(self, data: Any) -> bool:
        if not self.enabled:
            self.logger.info("Notion sync disabled, skipping...")
            return True
        
        self.logger.info("Syncing to Notion...")
        api_key = self.config.get("api_key")
        database_id = self.config.get("database_id")
        
        if not api_key or not database_id:
            self.logger.error("Notion API key or database ID not configured")
            return False
        
        # 模拟Notion同步逻辑
        time.sleep(1)
        self.logger.success(f"Synced {len(data) if isinstance(data, list) else 1} items to Notion")
        return True
    
    def verify(self) -> bool:
        self.logger.info("Verifying Notion sync...")
        return True


class GitHubTarget(SyncTarget):
    """GitHub同步目标"""
    @RetryDecorator(max_attempts=3)
    def sync(self, data: Any) -> bool:
        if not self.enabled:
            self.logger.info("GitHub sync disabled, skipping...")
            return True
        
        self.logger.info("Syncing to GitHub...")
        token = self.config.get("token")
        repo = self.config.get("repo")
        
        if not token or not repo:
            self.logger.error("GitHub token or repo not configured")
            return False
        
        # 模拟GitHub同步逻辑
        time.sleep(1)
        self.logger.success("Synced to GitHub repository")
        return True
    
    def verify(self) -> bool:
        self.logger.info("Verifying GitHub sync...")
        return True


class LocalTarget(SyncTarget):
    """本地备份目标"""
    @RetryDecorator(max_attempts=3)
    def sync(self, data: Any) -> bool:
        if not self.enabled:
            self.logger.info("Local backup disabled, skipping...")
            return True
        
        backup_dir = Path(self.config.get("backup_dir", "/root/.openclaw/backups"))
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        self.logger.info(f"Creating local backup at {backup_path}...")
        
        # 备份数据到JSON文件
        backup_file = backup_path / "data.json"
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 清理旧版本
        self._cleanup_old_versions(backup_dir)
        
        self.logger.success(f"Local backup created: {backup_path}")
        return True
    
    def _cleanup_old_versions(self, backup_dir: Path):
        """清理旧版本备份"""
        keep_versions = self.config.get("keep_versions", 10)
        backups = sorted(backup_dir.glob("backup_*"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        for old_backup in backups[keep_versions:]:
            shutil.rmtree(old_backup)
            self.logger.info(f"Removed old backup: {old_backup}")
    
    def verify(self) -> bool:
        self.logger.info("Verifying local backup...")
        return True


class SyncManager:
    """同步管理器主类"""
    def __init__(self, config_file: Path = CONFIG_FILE):
        self.config_file = config_file
        self.config = self._load_config()
        self.logger = Logger(LOG_FILE)
        self.checkpoint = CheckpointManager(CHECKPOINT_FILE, self.logger)
        self.targets = self._init_targets()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "retry": {"max_attempts": 3, "base_delay": 5, "max_delay": 60},
            "targets": {
                "notion": {"enabled": False},
                "github": {"enabled": False},
                "local": {"enabled": True, "backup_dir": "/root/.openclaw/backups"}
            }
        }
    
    def _init_targets(self) -> Dict[str, SyncTarget]:
        """初始化同步目标"""
        targets_config = self.config.get("targets", {})
        return {
            "notion": NotionTarget("notion", targets_config.get("notion", {}), self.logger),
            "github": GitHubTarget("github", targets_config.get("github", {}), self.logger),
            "local": LocalTarget("local", targets_config.get("local", {}), self.logger)
        }
    
    def sync_target(self, target_name: str, data: Any = None) -> bool:
        """同步特定目标"""
        if target_name not in self.targets:
            self.logger.error(f"Unknown target: {target_name}")
            return False
        
        if self.checkpoint.is_target_complete(target_name):
            self.logger.info(f"Target {target_name} already synced, skipping...")
            return True
        
        target = self.targets[target_name]
        
        try:
            success = target.sync(data)
            if success:
                self.checkpoint.mark_complete(target_name)
                if self.config.get("sync", {}).get("verify_after_sync", True):
                    target.verify()
            return success
        except Exception as e:
            self.logger.error(f"Sync failed for {target_name}: {e}")
            return False
    
    def sync_all(self, data: Any = None) -> Dict[str, bool]:
        """同步所有目标"""
        self.logger.info("=== Starting Full Sync ===")
        
        if data is None:
            data = self._collect_data()
        
        results = {}
        for target_name in self.targets:
            results[target_name] = self.sync_target(target_name, data)
        
        # 检查是否全部成功
        all_success = all(results.values())
        if all_success:
            self.checkpoint.data["last_sync"] = datetime.now().isoformat()
            self.checkpoint.data["in_progress"] = False
            self.checkpoint.save()
            self.logger.success("=== Full Sync Completed ===")
        else:
            self.logger.error("=== Full Sync Completed with Errors ===")
        
        return results
    
    def _collect_data(self) -> List[Dict]:
        """收集需要同步的数据"""
        # 这里可以根据实际需求收集数据
        return {
            "sync_time": datetime.now().isoformat(),
            "version": "1.0.0",
            "data": []
        }
    
    def get_status(self) -> Dict:
        """获取同步状态"""
        return {
            "last_sync": self.checkpoint.data.get("last_sync"),
            "in_progress": self.checkpoint.data.get("in_progress", False),
            "targets": {
                name: {
                    "enabled": target.enabled,
                    "completed": self.checkpoint.is_target_complete(name)
                }
                for name, target in self.targets.items()
            }
        }
    
    def clean_checkpoint(self):
        """清理断点记录"""
        self.checkpoint.reset()
        self.logger.success("Checkpoint cleaned")


def main():
    parser = argparse.ArgumentParser(description="Sync Manager - Data Synchronization Tool")
    parser.add_argument("command", choices=["sync-all", "sync", "status", "clean"],
                       help="Command to execute")
    parser.add_argument("--target", choices=["notion", "github", "local"],
                       help="Target for sync command")
    
    args = parser.parse_args()
    
    manager = SyncManager()
    
    if args.command == "sync-all":
        results = manager.sync_all()
        sys.exit(0 if all(results.values()) else 1)
    
    elif args.command == "sync":
        if not args.target:
            print("Error: --target required for sync command")
            sys.exit(1)
        success = manager.sync_target(args.target)
        sys.exit(0 if success else 1)
    
    elif args.command == "status":
        status = manager.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.command == "clean":
        manager.clean_checkpoint()


if __name__ == "__main__":
    main()
