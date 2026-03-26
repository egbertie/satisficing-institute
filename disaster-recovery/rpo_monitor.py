#!/usr/bin/env python3
"""
RPO/RTO监控脚本
"""
import json
import sys
import subprocess
from datetime import datetime, timedelta
import os

def get_last_git_commit_time():
    """获取最后一次Git提交时间"""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            capture_output=True,
            text=True,
            cwd="/root/.openclaw/workspace"
        )
        if result.returncode == 0:
            timestamp = int(result.stdout.strip())
            return datetime.fromtimestamp(timestamp)
    except Exception as e:
        print(f"Error getting git commit time: {e}", file=sys.stderr)
    return None

def get_last_backup_time():
    """获取最后一次备份时间"""
    state_file = "/tmp/last_backup_time.txt"
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                timestamp = float(f.read().strip())
                return datetime.fromtimestamp(timestamp)
        except:
            pass
    return None

def calculate_rpo():
    """计算当前RPO（分钟）"""
    last_commit = get_last_git_commit_time()
    if not last_commit:
        return None, "无法获取Git提交时间"
    
    now = datetime.now()
    rpo_minutes = (now - last_commit).total_seconds() / 60
    return int(rpo_minutes), last_commit.isoformat()

def check_rpo_status(rpo_minutes, target=120):
    """检查RPO状态"""
    ratio = rpo_minutes / target if target > 0 else 0
    
    if ratio < 0.5:
        return "normal", "🟢"
    elif ratio < 0.8:
        return "warning", "🟡"
    elif ratio < 1.0:
        return "critical", "🟠"
    else:
        return "breach", "🔴"

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "--check"
    
    if action == "--check":
        rpo, details = calculate_rpo()
        if rpo is None:
            print(json.dumps({"error": details}, indent=2))
            sys.exit(1)
        
        status, emoji = check_rpo_status(rpo)
        target = 120
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "rpo_minutes": rpo,
            "rpo_target_minutes": target,
            "rpo_status": status,
            "last_commit": details,
            "remaining_minutes": max(0, target - rpo)
        }
        
        print(json.dumps(result, indent=2))
        
        # 输出简洁状态
        print(f"\n📊 RPO监控: {emoji} {rpo}分钟 / 目标{target}分钟 (状态: {status})", file=sys.stderr)
        
    elif action == "--status":
        rpo, details = calculate_rpo()
        print(f"RPO监控运行中")
        print(f"当前RPO: {rpo}分钟" if rpo else "无法计算RPO")
        print(f"目标: 120分钟")
        
    elif action == "--report":
        print("📊 RPO/RTO报告生成...")
        rpo, _ = calculate_rpo()
        print(f"当前RPO: {rpo}分钟" if rpo else "无法计算")
        
    else:
        print(f"Unknown action: {action}")
        print("Usage: rpo_monitor.py [--check|--status|--report]")

if __name__ == "__main__":
    main()
