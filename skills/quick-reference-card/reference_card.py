#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速参考卡 - 查询工具
Quick Reference Card Query Tool

功能：
- 7维度评估体系查询
- 风险等级判定
- 决策流程速查
"""

import sys
import json

# 参考卡数据
REFERENCE_DATA = {
    "institute": {
        "name": "满意解研究所",
        "positioning": "专注硬科技转化的合伙人匹配决策教练",
        "methodology": "西蒙满意解理论 + 五路图腾决策法 + 儒商合伙伦理"
    },
    
    "dimensions": {
        "价值观契合度": {
            "weight": "25%",
            "threshold": "<5 致命风险",
            "description": "创业理念、工作态度、道德底线的一致性",
            "questions": [
                "对创业目的的理解是否一致？",
                "长期愿景是否兼容？",
                "面对困难的态度是否一致？"
            ]
        },
        "能力互补性": {
            "weight": "20%",
            "threshold": "<7 需补强",
            "description": "技术能力、商业能力、资源网络的互补程度",
            "questions": [
                "是否具备技术+商业双轮驱动？",
                "核心能力是否互补？",
                "资源网络是否有重叠？"
            ]
        },
        "沟通效率": {
            "weight": "15%",
            "threshold": "<5 中风险",
            "description": "信息透明度、响应速度、决策效率",
            "questions": [
                "信息沟通是否顺畅？",
                "决策效率如何？",
                "是否有沟通障碍？"
            ]
        },
        "承诺可信度": {
            "weight": "15%",
            "threshold": "<6 高风险",
            "description": "历史信用、投入意愿、兑现能力",
            "questions": [
                "过往承诺的兑现情况？",
                "资源投入意愿如何？",
                "是否有可靠的信用记录？"
            ]
        },
        "利益一致性": {
            "weight": "10%",
            "threshold": "需机制保障",
            "description": "股权分配、利益分配、长期利益的一致性",
            "questions": [
                "股权分配方案是否合理？",
                "利益分配机制是否清晰？",
                "长期利益是否一致？"
            ]
        },
        "退出可接受性": {
            "weight": "10%",
            "threshold": "需预设",
            "description": "退出机制、股权回购、竞业禁止的可接受度",
            "questions": [
                "退出机制是否预设？",
                "股权回购条款是否可接受？",
                "竞业禁止范围是否合理？"
            ]
        },
        "成长匹配度": {
            "weight": "5%",
            "threshold": "长期观察",
            "description": "学习能力、适应性、发展潜力的匹配",
            "questions": [
                "学习能力是否匹配？",
                "适应性如何？",
                "发展潜力是否一致？"
            ]
        }
    },
    
    "risk_levels": {
        "EXCELLENT": {"min": 8.0, "max": 10.0, "emoji": "🟢", "advice": "强烈推荐"},
        "LOW": {"min": 7.0, "max": 7.9, "emoji": "🟡", "advice": "可以推进"},
        "MEDIUM": {"min": 6.0, "max": 6.9, "emoji": "🟠", "advice": "需谨慎"},
        "HIGH": {"min": 5.5, "max": 5.9, "emoji": "🔴", "advice": "需深度尽调"},
        "CRITICAL": {"min": 0.0, "max": 5.4, "emoji": "⛔", "advice": "建议否决"}
    },
    
    "key_data": {
        "案例库": "15个（8成功+5失败+2进行中）",
        "成功率": "50%",
        "预测准确率": "85%+",
        "评估时长": "8-10分钟",
        "临界值": "6.5分区分成功/失败"
    },
    
    "failure_reasons": [
        "价值观冲突（67%）⚠️ 最致命",
        "承诺不足（资源投入不对等）",
        "沟通障碍（磨合期放大）"
    ],
    
    "success_patterns": [
        "技术+商业互补最稳定",
        "价值观契合度≥7",
        "全职承诺是硬科技前提"
    ]
}

class ReferenceCard:
    """快速参考卡"""
    
    def __init__(self):
        self.data = REFERENCE_DATA
    
    def get_full_card(self):
        """获取完整参考卡"""
        return self.data
    
    def get_dimension(self, name):
        """获取特定维度信息"""
        return self.data["dimensions"].get(name, None)
    
    def get_risk_level(self, score):
        """根据分数获取风险等级"""
        for level, info in self.data["risk_levels"].items():
            if info["min"] <= score <= info["max"]:
                return {
                    "level": level,
                    "emoji": info["emoji"],
                    "advice": info["advice"]
                }
        return None
    
    def list_dimensions(self):
        """列出所有维度"""
        return list(self.data["dimensions"].keys())
    
    def get_key_data(self):
        """获取关键数据"""
        return self.data["key_data"]

def main():
    """主入口"""
    card = ReferenceCard()
    
    if len(sys.argv) < 2:
        print("Usage: python3 reference_card.py [full|dimension|risk|list|data]")
        print("Examples:")
        print("  python3 reference_card.py full")
        print("  python3 reference_card.py dimension 价值观契合度")
        print("  python3 reference_card.py risk 7.2")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "full":
        print(json.dumps(card.get_full_card(), indent=2, ensure_ascii=False))
    elif command == "dimension":
        if len(sys.argv) < 3:
            print("Error: 请指定维度名称")
            sys.exit(1)
        dim_name = sys.argv[2]
        result = card.get_dimension(dim_name)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"未找到维度: {dim_name}")
            print(f"可用维度: {', '.join(card.list_dimensions())}")
    elif command == "risk":
        if len(sys.argv) < 3:
            print("Error: 请指定分数")
            sys.exit(1)
        score = float(sys.argv[2])
        result = card.get_risk_level(score)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("无效的分数范围")
    elif command == "list":
        print("可用维度:")
        for dim in card.list_dimensions():
            print(f"  - {dim}")
    elif command == "data":
        print(json.dumps(card.get_key_data(), indent=2, ensure_ascii=False))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
