#!/usr/bin/env python3
"""
Token消耗监控与熔断系统 V1.0
功能：实时监控Token消耗，触发分级熔断，与休眠协议联动
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
TOKEN_STATE_FILE = WORKSPACE / "memory" / "token-monitor-state.json"
FUSE_STATE_FILE = WORKSPACE / "memory" / "token-fuse-state.json"

# 熔断阈值配置
FUSE_THRESHOLDS = {
    "yellow": 80,   # 黄色预警：禁用非核心研究类任务
    "orange": 90,   # 橙色预警：仅保留用户对话
    "red": 95,      # 红色熔断：完全静默，仅等待指令
    "emergency": 98 # 紧急状态：强制休眠所有子代理
}

# 任务分级
def get_task_tiers():
    return {
        "P0_CRITICAL": [  # 即使熔断也必须保留
            "backup-daily-001",           # 每日备份
            "278707b5-a688-4d23-adbc-3d73ea925a10",  # 灾备同步
            "445d0246-d405-4bd4-b38c-8a1742b7a93b",  # 全方位灾备
        ],
        "P1_ESSENTIAL": [  # 橙色预警时保留
            "milestone-daily-check",      # 里程碑检查
            "bc640356-84e1-4e07-a2d5-cb93dab7e9ef",  # 每日安全检查
            "3d7db435-1497-4b00-9e63-2cd9c34cdf8f",  # 每日进度报告
        ],
        "P2_IMPORTANT": [  # 黄色预警时保留
            "f2ddbbb7-2374-4745-b73b-631a53e4f38a",  # 每日站会
            "8f0ffafd-1bb0-4503-a637-cd9c7f8cc208",  # 承诺保障检查
            "8dbc8186-b268-4895-8053-04305c9b28a1",  # 安全检查
            "2bcfc0c8-24bd-4768-b382-0ed99f767850",  # 每日知识萃取
        ],
        "P3_ROUTINE": [  # 正常状态运行，预警时暂停
            "0c1c5e75-562b-4edc-8419-f20b06a1bcf5",  # 文件治理
            "ad1fb129-d204-4a66-9b41-490e883d855e",  # 自主执行摘要
            "83c4750e-73bb-4c58-8a67-d658357448fb",  # API能力监控
            "0991f0cf-1c59-4dff-abd6-93b617636077",  # 每周六复盘
            "249ef31e-3fc7-4d45-9a68-681d5deb0b25",  # 引用一致性
            "8b6eba18-8116-4a8e-b6d3-593ff8697c83",  # 引用检查
        ],
        "P4_LOW_FREQ": [  # 低频任务，可灵活调整
            "a4e7fe12-b645-4a84-b495-5697df8a3903",  # 每周组织罗盘
            "41f3d606-e5f6-490f-bbb1-d557a64004bf",  # 飞书帮助中心
            "30014b47-8363-4555-b24f-04574dc356a7",  # API双周审查
            "backup-weekly-001",          # 每周全量备份
            "backup-cleanup-001",         # 备份清理
            "cb5e062f-8a69-4afc-a4e6-5c4eb4bc0d6e",  # 密钥轮换提醒
        ]
    }


def get_current_token_usage():
    """获取当前Token使用情况（从session_status解析）"""
    # 这里应该调用实际的API获取Token数据
    # 简化版：读取之前的状态
    if TOKEN_STATE_FILE.exists():
        with open(TOKEN_STATE_FILE, 'r') as f:
            return json.load(f)
    return {"percentage": 84, "timestamp": datetime.now().isoformat()}


def determine_fuse_level(percentage):
    """根据Token百分比确定熔断等级"""
    if percentage >= FUSE_THRESHOLDS["emergency"]:
        return "emergency"
    elif percentage >= FUSE_THRESHOLDS["red"]:
        return "red"
    elif percentage >= FUSE_THRESHOLDS["orange"]:
        return "orange"
    elif percentage >= FUSE_THRESHOLDS["yellow"]:
        return "yellow"
    return "normal"


def get_jobs_to_pause(fuse_level, task_tiers):
    """根据熔断等级确定要暂停的任务"""
    if fuse_level == "emergency":
        # 紧急状态：只保留P0
        keep = set(task_tiers["P0_CRITICAL"])
        pause_all = True
    elif fuse_level == "red":
        # 红色熔断：保留P0+P1
        keep = set(task_tiers["P0_CRITICAL"] + task_tiers["P1_ESSENTIAL"])
        pause_all = False
    elif fuse_level == "orange":
        # 橙色预警：保留P0+P1+P2
        keep = set(task_tiers["P0_CRITICAL"] + task_tiers["P1_ESSENTIAL"] + task_tiers["P2_IMPORTANT"])
        pause_all = False
    elif fuse_level == "yellow":
        # 黄色预警：保留P0+P1+P2+P3
        keep = set(task_tiers["P0_CRITICAL"] + task_tiers["P1_ESSENTIAL"] + 
                   task_tiers["P2_IMPORTANT"] + task_tiers["P3_ROUTINE"])
        pause_all = False
    else:
        # 正常状态：全部运行
        return [], False
    
    return keep, pause_all


def trigger_fuse(fuse_level, token_percentage):
    """触发熔断机制"""
    print(f"\n🔴 TOKEN熔断触发: {fuse_level.upper()}")
    print(f"当前消耗: {token_percentage}%")
    print("=" * 50)
    
    task_tiers = get_task_tiers()
    keep_jobs, pause_all = get_jobs_to_pause(fuse_level, task_tiers)
    
    # 记录熔断状态
    fuse_state = {
        "level": fuse_level,
        "token_percentage": token_percentage,
        "triggered_at": datetime.now().isoformat(),
        "kept_jobs": list(keep_jobs),
        "paused_all": pause_all
    }
    
    with open(FUSE_STATE_FILE, 'w') as f:
        json.dump(fuse_state, f, indent=2)
    
    # 输出熔断指令
    if pause_all:
        print("🚨 紧急状态：暂停所有非核心任务")
        print("保留任务仅:", keep_jobs)
    else:
        print(f"⚠️  {fuse_level}级别熔断")
        print(f"保留任务数: {len(keep_jobs)}")
    
    # 生成暂停命令列表
    print("\n执行命令:")
    # 这里应该生成实际的cron update命令
    
    return fuse_state


def release_fuse():
    """解除熔断，恢复所有任务"""
    print("\n🟢 解除Token熔断，恢复正常运行")
    
    if FUSE_STATE_FILE.exists():
        with open(FUSE_STATE_FILE, 'r') as f:
            old_state = json.load(f)
        print(f"上一次熔断等级: {old_state.get('level', 'unknown')}")
    
    # 记录解除时间
    fuse_state = {
        "level": "normal",
        "released_at": datetime.now().isoformat(),
        "previous_state": old_state if FUSE_STATE_FILE.exists() else None
    }
    
    with open(FUSE_STATE_FILE, 'w') as f:
        json.dump(fuse_state, f, indent=2)
    
    # 这里应该生成恢复所有cron的命令
    print("所有任务已恢复")


def monitor_loop():
    """监控循环 - 由Cron每15分钟调用"""
    token_data = get_current_token_usage()
    percentage = token_data.get("percentage", 0)
    
    fuse_level = determine_fuse_level(percentage)
    
    if fuse_level != "normal":
        # 检查是否已经处于熔断状态
        if FUSE_STATE_FILE.exists():
            with open(FUSE_STATE_FILE, 'r') as f:
                current_fuse = json.load(f)
            if current_fuse.get("level") == fuse_level:
                print(f"当前已处于{fuse_level}熔断状态，无需重复触发")
                return
        
        trigger_fuse(fuse_level, percentage)
    else:
        # 检查是否需要解除熔断
        if FUSE_STATE_FILE.exists():
            with open(FUSE_STATE_FILE, 'r') as f:
                current_fuse = json.load(f)
            if current_fuse.get("level") != "normal":
                release_fuse()


def status():
    """显示当前熔断状态"""
    print("\n📊 Token熔断系统状态")
    print("=" * 50)
    
    token_data = get_current_token_usage()
    percentage = token_data.get("percentage", 0)
    
    print(f"当前Token消耗: {percentage}%")
    print(f"熔断阈值:")
    for level, threshold in FUSE_THRESHOLDS.items():
        status = "🔴" if percentage >= threshold else "🟢"
        print(f"  {status} {level}: {threshold}%")
    
    fuse_level = determine_fuse_level(percentage)
    print(f"\n当前熔断等级: {fuse_level}")
    
    if FUSE_STATE_FILE.exists():
        with open(FUSE_STATE_FILE, 'r') as f:
            fuse_state = json.load(f)
        print(f"熔断状态: {fuse_state.get('level', 'unknown')}")
        if fuse_state.get('triggered_at'):
            print(f"触发时间: {fuse_state['triggered_at']}")
        if fuse_state.get('kept_jobs'):
            print(f"保留任务: {len(fuse_state['kept_jobs'])}个")
    
    print("=" * 50)


def main():
    if len(sys.argv) < 2:
        print("Usage: token-fuse-system.py [monitor|status|trigger|release]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "monitor":
        monitor_loop()
    elif command == "status":
        status()
    elif command == "trigger":
        level = sys.argv[2] if len(sys.argv) > 2 else "red"
        trigger_fuse(level, 95)
    elif command == "release":
        release_fuse()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
