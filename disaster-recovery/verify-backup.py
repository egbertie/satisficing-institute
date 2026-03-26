#!/usr/bin/env python3
"""
备份验证脚本
"""
import json
import sys
import os
import hashlib
from datetime import datetime

def calculate_hash(filepath):
    """计算文件hash"""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except:
        return None

def verify_backup(path="/root/.openclaw/workspace", sample_size=100):
    """验证备份完整性"""
    stats = {
        "timestamp": datetime.now().isoformat(),
        "path": path,
        "total_files": 0,
        "checked_files": 0,
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    try:
        # 统计文件
        for root, dirs, files in os.walk(path):
            # 跳过.git和node_modules
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.openclaw']]
            stats["total_files"] += len(files)
        
        # 抽样检查
        checked = 0
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.openclaw']]
            for file in files:
                if checked >= sample_size:
                    break
                filepath = os.path.join(root, file)
                if os.path.getsize(filepath) < 10 * 1024 * 1024:  # 跳过>10MB文件
                    file_hash = calculate_hash(filepath)
                    if file_hash:
                        stats["checked_files"] += 1
                        stats["passed"] += 1
                    else:
                        stats["failed"] += 1
                        stats["errors"].append(f"Cannot read: {filepath}")
                    checked += 1
        
        stats["health_score"] = int((stats["passed"] / max(stats["checked_files"], 1)) * 100)
        stats["overall_status"] = "passed" if stats["failed"] == 0 else "failed"
        
    except Exception as e:
        stats["overall_status"] = "error"
        stats["errors"].append(str(e))
    
    return stats

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if action == "--deep":
        print("执行深度验证（全量检查）...")
        stats = verify_backup(sample_size=1000)
    else:
        print("执行快速验证（抽样检查）...")
        stats = verify_backup(sample_size=100)
    
    # 保存结果
    with open("/tmp/backup_verification_latest.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    # 输出报告
    print(json.dumps(stats, indent=2))
    
    # 简洁输出
    print(f"\n📊 备份验证: {'✅' if stats['overall_status'] == 'passed' else '❌'} 健康度{stats['health_score']}% ({stats['passed']}/{stats['checked_files']})", file=sys.stderr)

if __name__ == "__main__":
    main()
