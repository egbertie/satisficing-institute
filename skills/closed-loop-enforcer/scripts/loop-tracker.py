#!/usr/bin/env python3
"""
信息闭环三原则执行脚本
版本: V2.0
功能: 追踪信息发出→确认→落实→反馈的完整闭环
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

STATE_FILE = "/tmp/closed-loop-state.json"
LOG_FILE = "/tmp/closed-loop.log"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def load_state():
    """加载状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"loops": []}

def save_state(state):
    """保存状态"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def check_pending_confirmations():
    """检查待确认项"""
    state = load_state()
    pending = []
    
    for loop in state.get("loops", []):
        if loop["status"] == "sent":
            sent_time = datetime.fromisoformat(loop["sent_at"])
            if datetime.now() - sent_time > timedelta(hours=1):
                pending.append(loop)
    
    return pending

def check_pending_implementation():
    """检查待落实项"""
    state = load_state()
    pending = []
    
    for loop in state.get("loops", []):
        if loop["status"] == "confirmed":
            confirmed_time = datetime.fromisoformat(loop["confirmed_at"])
            if datetime.now() - confirmed_time > timedelta(hours=2):
                pending.append(loop)
    
    return pending

def check_pending_feedback():
    """检查待反馈项"""
    state = load_state()
    pending = []
    
    for loop in state.get("loops", []):
        if loop["status"] == "implemented":
            impl_time = datetime.fromisoformat(loop["implemented_at"])
            if datetime.now() - impl_time > timedelta(hours=4):
                pending.append(loop)
    
    return pending

def main():
    """主函数"""
    log("=" * 50)
    log("信息闭环三原则检查")
    log("=" * 50)
    
    # 检查各类待处理项
    pending_confirm = check_pending_confirmations()
    pending_impl = check_pending_implementation()
    pending_feedback = check_pending_feedback()
    
    total_pending = len(pending_confirm) + len(pending_impl) + len(pending_feedback)
    
    log(f"\n待确认: {len(pending_confirm)} 项")
    for item in pending_confirm:
        log(f"  - {item.get('content', 'Unknown')[:50]}...")
    
    log(f"\n待落实: {len(pending_impl)} 项")
    for item in pending_impl:
        log(f"  - {item.get('content', 'Unknown')[:50]}...")
    
    log(f"\n待反馈: {len(pending_feedback)} 项")
    for item in pending_feedback:
        log(f"  - {item.get('content', 'Unknown')[:50]}...")
    
    if total_pending > 0:
        log(f"\n⚠️ 发现 {total_pending} 个未闭环项，需要处理")
        return 1
    else:
        log("\n✅ 所有信息已闭环")
        return 0

if __name__ == "__main__":
    exit(main())
