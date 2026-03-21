#!/usr/bin/env python3
"""
Kimi CLI Task Queue Manager
任务队列管理器
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

TASKS_DIR = Path(__file__).parent.parent / "tasks"

def ensure_dirs():
    """确保任务目录存在"""
    for subdir in ["pending", "running", "completed", "failed"]:
        (TASKS_DIR / subdir).mkdir(parents=True, exist_ok=True)

def add_task(task_file):
    """添加任务到队列"""
    task_path = Path(task_file)
    if not task_path.exists():
        print(f"❌ 任务文件不存在: {task_file}")
        return False
    
    with open(task_path) as f:
        task = json.load(f)
    
    task_id = task.get("id", f"task_{int(time.time())}")
    task["id"] = task_id
    task["status"] = "pending"
    task["created_at"] = datetime.now().isoformat()
    
    target_path = TASKS_DIR / "pending" / f"{task_id}.json"
    with open(target_path, "w") as f:
        json.dump(task, f, indent=2)
    
    print(f"✅ 任务已添加: {task_id}")
    print(f"   类型: {task.get('type', 'unknown')}")
    print(f"   超时: {task.get('timeout', 300)}秒")
    return True

def list_tasks():
    """列出所有任务状态"""
    ensure_dirs()
    
    print("📋 任务队列状态")
    print("=" * 50)
    
    for status in ["pending", "running", "completed", "failed"]:
        dir_path = TASKS_DIR / status
        tasks = list(dir_path.glob("*.json"))
        
        icon = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌"
        }.get(status, "❓")
        
        print(f"\n{icon} {status.upper()}: {len(tasks)}")
        
        for task_file in sorted(tasks)[:5]:  # 最多显示5个
            with open(task_file) as f:
                task = json.load(f)
            print(f"   - {task.get('id', 'unknown')} ({task.get('type', 'unknown')})")

def get_status():
    """获取队列状态摘要"""
    ensure_dirs()
    
    stats = {}
    for status in ["pending", "running", "completed", "failed"]:
        dir_path = TASKS_DIR / status
        stats[status] = len(list(dir_path.glob("*.json")))
    
    return stats

def main():
    parser = argparse.ArgumentParser(description="Kimi CLI Task Queue Manager")
    parser.add_argument("action", choices=["add", "list", "status"])
    parser.add_argument("task_file", nargs="?")
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    if args.action == "add":
        if not args.task_file:
            print("❌ 请提供任务文件路径")
            sys.exit(1)
        add_task(args.task_file)
    elif args.action == "list":
        list_tasks()
    elif args.action == "status":
        stats = get_status()
        print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
