#!/usr/bin/env python3
"""
感知力训练脚本
版本: V2.0
"""

import random
from datetime import datetime

TRAINING_PROMPTS = {
    "earth": [
        "回顾一个历史决策案例，分析其成功/失败原因",
        "从过去的经验中提取可复用的模式"
    ],
    "water": [
        "观察当前行业趋势的3个信号",
        "识别环境中正在发生的微妙变化"
    ],
    "wood": [
        "评估一个人/项目的成长潜力",
        "思考如何促进持续成长"
    ],
    "metal": [
        "用结构化方法分析一个复杂问题",
        "识别问题中的核心变量"
    ],
    "fire": [
        "模拟一个高压力场景，思考应对策略",
        "评估当前决策的风险边界"
    ]
}

def generate_training(dimension, level="basic"):
    """生成训练内容"""
    prompts = TRAINING_PROMPTS.get(dimension, [])
    if prompts:
        return random.choice(prompts)
    return "请进行10分钟正念练习"

def main():
    print("=== 感知力训练 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    for dimension in ["earth", "water", "wood", "metal", "fire"]:
        prompt = generate_training(dimension)
        print(f"【{dimension}】{prompt}")
    
    return 0

if __name__ == "__main__":
    main()