#!/usr/bin/env python3
"""
休眠协议控制器 - Hibernation Protocol Controller
版本: V1.0
功能: 管理休眠模式的进入、维持和唤醒
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# 配置路径
WORKSPACE = Path("/root/.openclaw/workspace")
HIBERNATION_LOG = WORKSPACE / "memory" / "hibernation-log.json"
HIBERNATION_STATE = WORKSPACE / "memory" / "hibernation-state.json"

# 保留任务列表（即使在完全静默模式下也保留）
ESSENTIAL_JOBS = [
    "backup-daily-001",  # 每日自动备份
    "278707b5-a688-4d23-adbc-3d73ea925a10",  # 灾备复刻每日同步
    "445d0246-d405-4bd4-b38c-8a1742b7a93b",  # 全方位灾备同步
]

# 高风险任务列表（休眠时必须暂停）
HIGH_FREQUENCY_JOBS = [
    "bc1eb9e6-da6e-4757-8544-332a4b28b1e2",  # 零空置强制执行器（每15分钟）
    "51d81326-d84b-45cc-b46b-8fad2061fceb",  # 任务协调检查（每2小时）
]


def log_message(level, message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def get_hibernation_state():
    """获取当前休眠状态"""
    if HIBERNATION_STATE.exists():
        with open(HIBERNATION_STATE, 'r') as f:
            return json.load(f)
    return {
        "status": "awake",
        "hibernation_id": None,
        "start_time": None,
        "mode": None
    }


def set_hibernation_state(state):
    """设置休眠状态"""
    HIBERNATION_STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(HIBERNATION_STATE, 'w') as f:
        json.dump(state, f, indent=2)


def append_hibernation_log(entry):
    """追加休眠日志"""
    HIBERNATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    log_data = []
    if HIBERNATION_LOG.exists():
        with open(HIBERNATION_LOG, 'r') as f:
            try:
                log_data = json.load(f)
            except:
                log_data = []
    
    entry["timestamp"] = datetime.now().isoformat()
    log_data.append(entry)
    
    # 只保留最近100条
    log_data = log_data[-100:]
    
    with open(HIBERNATION_LOG, 'w') as f:
        json.dump(log_data, f, indent=2)


def sleep(mode="full"):
    """进入休眠模式"""
    log_message("INFO", f"正在进入休眠模式: {mode}")
    
    # 1. 记录休眠前状态
    hibernation_id = f"HIB-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # 2. 获取当前Cron任务状态
    import subprocess
    result = subprocess.run(
        ["openclaw", "cron", "list"],
        capture_output=True,
        text=True
    )
    
    # 3. 确定要暂停的任务
    jobs_to_pause = []
    jobs_to_keep = ESSENTIAL_JOBS if mode != "emergency" else []
    
    # 4. 暂停非保留任务
    paused_count = 0
    # 这里应该调用cron update来暂停任务
    # 简化版：记录状态，实际暂停由调用方执行
    
    # 5. 更新状态
    state = {
        "status": "hibernating",
        "hibernation_id": hibernation_id,
        "start_time": datetime.now().isoformat(),
        "mode": mode,
        "paused_jobs": jobs_to_pause,
        "kept_jobs": jobs_to_keep
    }
    set_hibernation_state(state)
    
    # 6. 记录日志
    append_hibernation_log({
        "event": "hibernation_start",
        "hibernation_id": hibernation_id,
        "mode": mode,
        "paused_count": paused_count
    })
    
    log_message("INFO", f"已进入休眠模式: {hibernation_id}")
    print(f"\n🌙 休眠模式已启动")
    print(f"模式: {mode}")
    print(f"休眠ID: {hibernation_id}")
    print(f"保留任务: {len(jobs_to_keep)}个")
    print(f"发送任意消息唤醒我\n")
    
    return hibernation_id


def wake():
    """从休眠中唤醒"""
    state = get_hibernation_state()
    
    if state["status"] != "hibernating":
        log_message("WARN", "当前不在休眠状态")
        print("⚠️ 当前未在休眠状态")
        return False
    
    log_message("INFO", "正在唤醒...")
    
    # 1. 计算休眠时长
    start_time = datetime.fromisoformat(state["start_time"])
    duration = datetime.now() - start_time
    duration_minutes = duration.total_seconds() / 60
    
    # 2. 恢复Cron任务
    # 这里应该调用cron update来恢复任务
    
    # 3. 更新状态
    state["status"] = "awake"
    state["end_time"] = datetime.now().isoformat()
    state["duration_minutes"] = duration_minutes
    set_hibernation_state(state)
    
    # 4. 记录日志
    append_hibernation_log({
        "event": "hibernation_end",
        "hibernation_id": state["hibernation_id"],
        "duration_minutes": duration_minutes
    })
    
    log_message("INFO", f"已唤醒，休眠时长: {duration_minutes:.1f}分钟")
    print(f"\n🌅 已唤醒")
    print(f"休眠时长: {duration_minutes:.1f}分钟")
    print(f"欢迎回来！\n")
    
    return True


def status():
    """查看休眠状态"""
    state = get_hibernation_state()
    
    print("\n📊 休眠协议状态")
    print("=" * 40)
    print(f"状态: {'🌙 休眠中' if state['status'] == 'hibernating' else '🌅 正常运行'}")
    
    if state["status"] == "hibernating":
        start_time = datetime.fromisoformat(state["start_time"])
        duration = datetime.now() - start_time
        print(f"休眠ID: {state['hibernation_id']}")
        print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"已休眠: {duration.total_seconds()/60:.1f}分钟")
        print(f"模式: {state['mode']}")
        print(f"保留任务: {len(state.get('kept_jobs', []))}个")
    
    print("=" * 40)
    print()


def auto_check():
    """自动休眠检测（由Cron调用）"""
    # 读取最后交互时间
    last_interaction_file = WORKSPACE / "memory" / "last-interaction.json"
    
    if not last_interaction_file.exists():
        return
    
    with open(last_interaction_file, 'r') as f:
        data = json.load(f)
    
    last_time = datetime.fromisoformat(data.get("timestamp", "2026-01-01T00:00:00"))
    elapsed = datetime.now() - last_time
    
    # 检查是否超过10分钟
    if elapsed.total_seconds() > 600:  # 10分钟
        state = get_hibernation_state()
        if state["status"] != "hibernating":
            # 检查是否有夜间任务
            night_task_file = WORKSPACE / "memory" / "night-task-scheduled.json"
            if not night_task_file.exists():
                log_message("INFO", "10分钟无交互，自动进入休眠")
                sleep("full")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: hibernation-control.py [sleep|wake|status|auto-check]")
        print("       sleep [--mode full|partial|emergency]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "sleep":
        mode = "full"
        if "--mode" in sys.argv:
            mode_idx = sys.argv.index("--mode") + 1
            if mode_idx < len(sys.argv):
                mode = sys.argv[mode_idx]
        sleep(mode)
    
    elif command == "wake":
        wake()
    
    elif command == "status":
        status()
    
    elif command == "auto-check":
        auto_check()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
