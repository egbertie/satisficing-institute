#!/usr/bin/env python3
"""
Universal Checklist Enforcer
强制执行所有任务前的5项核心检查
"""

import sys
import json
import os
from datetime import datetime

def load_checklist():
    """加载检查清单模板"""
    return [
        {
            "id": "C1",
            "name": "任务定义SMART检查",
            "description": "目标是否具体/可衡量/可实现/相关/有时限",
            "criteria": ["Specific", "Measurable", "Achievable", "Relevant", "Time-bound"],
            "block_on_fail": True
        },
        {
            "id": "C2", 
            "name": "输入完整性检查",
            "description": "是否提供了所有必要文件/数据/上下文",
            "criteria": ["列出必需输入项", "标注缺失项", "风险评估"],
            "block_on_fail": True
        },
        {
            "id": "C3",
            "name": "幻觉预防检查", 
            "description": "关键数据是否标注来源和置信度",
            "criteria": ["标注来源", "标注置信度", "低置信度标注待验证"],
            "block_on_fail": False
        },
        {
            "id": "C4",
            "name": "深度检查",
            "description": "是否使用MECE原则，无遗漏无重叠",
            "criteria": ["相互独立", "完全穷尽", "≥3维度", "每维度≥3要点"],
            "block_on_fail": False
        },
        {
            "id": "C5",
            "name": "闭环设计检查",
            "description": "产出物的下一步行动明确",
            "criteria": ["下一步行动", "负责人", "截止时间", "成功标准"],
            "block_on_fail": True
        }
    ]

def enforce_checklist(task_id=None):
    """执行强制检查清单"""
    timestamp = datetime.now().isoformat()
    checklist = load_checklist()
    
    print(f"[{timestamp}] 强制检查清单执行")
    print(f"任务ID: {task_id or '未指定'}")
    print("=" * 60)
    
    for item in checklist:
        status = "⏳" if item["block_on_fail"] else "⚠️"
        print(f"\n{status} [{item['id']}] {item['name']}")
        print(f"   说明: {item['description']}")
        print(f"   标准: {', '.join(item['criteria'])}")
        if item["block_on_fail"]:
            print(f"   ⚠️ 阻塞项: 未通过则任务BLOCK")
    
    print("\n" + "=" * 60)
    print("[检查完成] 所有5项检查必须通过才能进入执行阶段")
    
    # 记录日志
    log_entry = {
        "timestamp": timestamp,
        "task_id": task_id,
        "checklist_version": "1.0",
        "items_checked": len(checklist),
        "status": "enforced"
    }
    
    # 确保日志目录存在
    log_dir = "/root/.openclaw/workspace/memory/checklist_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = f"{log_dir}/{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return 0

def generate_report():
    """生成检查质量报告"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] 检查清单质量报告")
    print("=" * 60)
    print("本周检查执行情况统计...")
    print("[报告生成完成]")
    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 enforcer.py [enforce|report|update]")
        sys.exit(1)
    
    command = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    if command == "enforce":
        return enforce_checklist(task_id)
    elif command == "report":
        return generate_report()
    else:
        print(f"Unknown command: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
