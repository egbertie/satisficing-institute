#!/usr/bin/env python3
"""
管理哲学思维框架 - Management Philosophy Framework

核心功能：将辩证思维、系统思维等管理哲学与第一性原则联动
用户指令：提到"第一性原则"时自动增加这些管理哲学思维

哲学体系：
1. 辩证思维：对立统一、量变质变、否定之否定
2. 系统思维：整体大于部分、动态平衡、涌现性
3. 批判性思维：质疑假设、证据检验、逻辑一致性
4. 复杂性思维：非线性、不确定性、适应性

与第一性原则的融合：
- 第一性原则找到本质
- 管理哲学提供思考角度
- 联动使用 = 更全面的决策
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class ManagementPhilosophyFramework:
    """管理哲学思维框架 - 与第一性原则联动"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.framework_file = self.workspace / "skills" / "management-philosophy-framework" / "framework.json"
        self.application_log = self.workspace / "memory" / "philosophy-application-log.jsonl"
        
        # 加载框架
        self.framework = self._load_framework()
    
    def _load_framework(self) -> dict:
        """加载管理哲学框架"""
        if self.framework_file.exists():
            with open(self.framework_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._init_framework()
    
    def _init_framework(self) -> dict:
        """初始化管理哲学框架"""
        return {
            "version": "1.0.0",
            "philosophies": {
                "dialectical_thinking": {
                    "name": "辩证思维",
                    "name_en": "Dialectical Thinking",
                    "core_principles": [
                        {
                            "principle": "对立统一",
                            "description": "矛盾双方既对立又统一，推动事物发展",
                            "application": "看到问题的两面性，寻找平衡点",
                            "example": "防守vs进攻、质量vs效率、自主vs协作"
                        },
                        {
                            "principle": "量变质变",
                            "description": "量变积累到一定程度引起质变",
                            "application": "关注积累效应，识别临界点",
                            "example": "每日3-5%改进积累成巨大提升"
                        },
                        {
                            "principle": "否定之否定",
                            "description": "发展是螺旋式上升，经历肯定-否定-否定之否定",
                            "application": "接受反复和修正，视之为进步过程",
                            "example": "重复提醒→制度改进→更高水平"
                        }
                    ],
                    "questions": [
                        "这个决策的对立面是什么？",
                        "如何在矛盾中找到统一？",
                        "当前是量变阶段还是质变阶段？",
                        "是否需要否定现有方案重新开始？"
                    ]
                },
                "systems_thinking": {
                    "name": "系统思维",
                    "name_en": "Systems Thinking",
                    "core_principles": [
                        {
                            "principle": "整体大于部分之和",
                            "description": "系统的整体功能不是各部分简单相加",
                            "application": "关注组件间的相互作用和涌现效应",
                            "example": "六线并行产生单一任务无法达到的效率"
                        },
                        {
                            "principle": "动态平衡",
                            "description": "系统在变化中维持相对稳定",
                            "application": "寻找最优资源配置，而非最大化某一部分",
                            "example": "3-5%资源用于复盘，而非全部执行或全部优化"
                        },
                        {
                            "principle": "反馈回路",
                            "description": "系统的输出影响输入，形成循环",
                            "application": "建立正反馈促进增长，负反馈防止失控",
                            "example": "每日审计→发现问题→制度改进→效果更好"
                        }
                    ],
                    "questions": [
                        "这个决策对系统整体有什么影响？",
                        "各个组件如何相互作用？",
                        " feedback回路在哪里？",
                        "如何维持动态平衡？"
                    ]
                },
                "critical_thinking": {
                    "name": "批判性思维",
                    "name_en": "Critical Thinking",
                    "core_principles": [
                        {
                            "principle": "质疑假设",
                            "description": "不轻易接受前提，审视假设的合理性",
                            "application": "问自己'如果前提不成立呢？'",
                            "example": "'需要2天'→质疑→实际2小时"
                        },
                        {
                            "principle": "证据检验",
                            "description": "基于证据而非直觉做判断",
                            "application": "要求数据支撑，量化评估",
                            "example": "用过滤率、效率分数衡量信息质量"
                        },
                        {
                            "principle": "逻辑一致性",
                            "description": "确保推理过程没有矛盾",
                            "application": "检查因果关系，避免滑坡谬误",
                            "example": "阻塞任务≠进行中，重新定义避免矛盾"
                        }
                    ],
                    "questions": [
                        "这个结论的假设是什么？",
                        "有什么证据支撑？",
                        "推理过程是否逻辑一致？",
                        "有没有考虑反例？"
                    ]
                },
                "complexity_thinking": {
                    "name": "复杂性思维",
                    "name_en": "Complexity Thinking",
                    "core_principles": [
                        {
                            "principle": "非线性",
                            "description": "输入输出不成正比，小投入可能大产出",
                            "application": "寻找杠杆点，用最小投入获得最大改进",
                            "example": "制度即代码，一次写入，持续生效"
                        },
                        {
                            "principle": "不确定性",
                            "description": "无法完全预测，需要适应性",
                            "application": "保持灵活性，快速响应变化",
                            "example": "自动补位队列应对不确定的任务需求"
                        },
                        {
                            "principle": "涌现性",
                            "description": "简单规则产生复杂行为",
                            "application": "设定简单明确的规则，让系统自组织",
                            "example": "零空置规则→自动补位→资源全开"
                        }
                    ],
                    "questions": [
                        "系统的杠杆点在哪里？",
                        "如何应对不确定性？",
                        "简单规则能否产生期望的复杂行为？",
                        "是否需要保持适应性？"
                    ]
                }
            },
            "integration_with_first_principles": {
                "description": "管理哲学与第一性原则的融合方式",
                "process": [
                    "Step 1: 用第一性原则找到本质（What is the fundamental truth?）",
                    "Step 2: 用辩证思维看到两面性（What are the contradictions?）",
                    "Step 3: 用系统思维看整体影响（How does it affect the system?）",
                    "Step 4: 用批判性思维检验假设（What are the assumptions?）",
                    "Step 5: 用复杂性思维找杠杆点（Where is the leverage point?）"
                ],
                "output": "融合后的全面决策框架"
            }
        }
    
    def apply_framework(self, context: str, decision: str) -> Dict:
        """
        应用管理哲学思维框架
        
        Args:
            context: 决策背景
            decision: 待做的决策
        
        Returns:
            融合所有哲学维度的分析结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "decision": decision,
            "first_principle": self._apply_first_principle(context, decision),
            "dialectical_analysis": self._apply_dialectical_thinking(context, decision),
            "systems_analysis": self._apply_systems_thinking(context, decision),
            "critical_analysis": self._apply_critical_thinking(context, decision),
            "complexity_analysis": self._apply_complexity_thinking(context, decision),
            "integrated_recommendation": ""
        }
        
        # 生成综合建议
        result["integrated_recommendation"] = self._generate_integrated_recommendation(result)
        
        # 记录应用
        self._log_application(result)
        
        return result
    
    def _apply_first_principle(self, context: str, decision: str) -> Dict:
        """应用第一性原则"""
        return {
            "principle": "回归本质，剥离假设",
            "fundamental_question": "这个问题的本质是什么？",
            "assumptions_to_strip": [
                "现有做法只是其中一种可能",
                "'不可能'往往基于当前假设",
                "时间和资源限制可能是人为设定"
            ],
            "essential_truth": "找到不可再简化的核心事实",
            "breakthrough_potential": "从本质重新构建解决方案"
        }
    
    def _apply_dialectical_thinking(self, context: str, decision: str) -> Dict:
        """应用辩证思维"""
        # 识别决策中的对立面
        opposites = self._identify_opposites(context, decision)
        
        return {
            "principle": "对立统一",
            "opposites_identified": opposites,
            "unity_in_contradiction": "如何在矛盾中找到平衡点",
            "transformation_potential": "当前阶段是量变还是质变？",
            "synthesis": "超越二元对立，找到第三条路"
        }
    
    def _identify_opposites(self, context: str, decision: str) -> List[Dict]:
        """识别决策中的对立面"""
        common_opposites = [
            {"pair": ["防守", "进攻"], "context": "信息防火墙"},
            {"pair": ["质量", "效率"], "context": "搜索策略"},
            {"pair": ["自主", "协作"], "context": "任务执行"},
            {"pair": ["保守", "激进"], "context": "时间预估"},
            {"pair": ["集中", "分散"], "context": "资源配置"},
            {"pair": ["短期", "长期"], "context": "规划视角"}
        ]
        
        relevant = []
        for opp in common_opposites:
            if any(word in context or word in decision for word in opp["pair"]):
                relevant.append(opp)
        
        return relevant
    
    def _apply_systems_thinking(self, context: str, decision: str) -> Dict:
        """应用系统思维"""
        return {
            "principle": "整体大于部分",
            "system_components": [
                "输入（信息/任务/资源）",
                "处理（搜索/执行/优化）",
                "输出（结果/交付物）",
                "反馈（监控/审计/复盘）"
            ],
            "interconnections": "组件间的相互作用",
            "emergent_properties": "整体涌现的新特性",
            "dynamic_balance": "如何在变化中保持稳定",
            "feedback_loops": "正反馈和负反馈回路"
        }
    
    def _apply_critical_thinking(self, context: str, decision: str) -> Dict:
        """应用批判性思维"""
        return {
            "principle": "质疑假设",
            "assumptions": [
                "当前做法是基于什么假设？",
                "如果假设不成立会怎样？",
                "有没有未考虑的替代方案？"
            ],
            "evidence_required": "需要什么证据来支撑决策？",
            "logical_consistency": "推理过程是否有矛盾？",
            "cognitive_biases": "可能存在什么认知偏差？"
        }
    
    def _apply_complexity_thinking(self, context: str, decision: str) -> Dict:
        """应用复杂性思维"""
        return {
            "principle": "非线性与涌现",
            "leverage_points": [
                "制度即代码（一次写入，持续生效）",
                "自动补位（简单规则，复杂行为）",
                "3-5%复盘投入（小投入，大回报）"
            ],
            "uncertainty_management": "如何应对不可预测的变化",
            "adaptability": "保持灵活性和响应能力",
            "simple_rules": "设定简单明确的规则"
        }
    
    def _generate_integrated_recommendation(self, analysis: Dict) -> str:
        """生成综合建议"""
        recommendations = []
        
        # 基于第一性原则
        recommendations.append("从本质出发，剥离所有假设")
        
        # 基于辩证思维
        opposites = analysis["dialectical_analysis"].get("opposites_identified", [])
        if opposites:
            recommendations.append(f"平衡对立面：{opposites[0]['pair'][0]} vs {opposites[0]['pair'][1]}")
        
        # 基于系统思维
        recommendations.append("考虑对整体系统的影响")
        
        # 基于批判性思维
        recommendations.append("质疑关键假设，要求证据支撑")
        
        # 基于复杂性思维
        recommendations.append("寻找杠杆点，用简单规则实现复杂目标")
        
        return "；".join(recommendations)
    
    def _log_application(self, result: Dict):
        """记录框架应用"""
        with open(self.application_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "timestamp": result["timestamp"],
                "context": result["context"],
                "decision": result["decision"],
                "recommendation": result["integrated_recommendation"]
            }, ensure_ascii=False) + "\n")
    
    def generate_thinking_report(self, analysis: Dict) -> str:
        """生成思维分析报告"""
        lines = [
            "# 管理哲学思维分析报告",
            "",
            f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**决策背景**: {analysis['context']}",
            f"**待做决策**: {analysis['decision']}",
            "",
            "## 第一性原则",
            ""
        ]
        
        fp = analysis["first_principle"]
        lines.extend([
            f"**核心**: {fp['principle']}",
            f"**关键问题**: {fp['fundamental_question']}",
            "",
            "## 辩证思维",
            ""
        ])
        
        dt = analysis["dialectical_analysis"]
        if dt.get("opposites_identified"):
            lines.append("**识别的对立面**:")
            for opp in dt["opposites_identified"]:
                lines.append(f"- {opp['pair'][0]} vs {opp['pair'][1]} ({opp['context']})")
        lines.append(f"**综合**: {dt.get('synthesis', '')}")
        lines.append("")
        
        lines.extend([
            "## 系统思维",
            "",
            "**系统组件**:",
        ])
        for comp in analysis["systems_analysis"]["system_components"]:
            lines.append(f"- {comp}")
        lines.append("")
        
        lines.extend([
            "## 批判性思维",
            "",
            "**需要质疑的假设**:",
        ])
        for assumption in analysis["critical_analysis"]["assumptions"]:
            lines.append(f"- {assumption}")
        lines.append("")
        
        lines.extend([
            "## 复杂性思维",
            "",
            "**杠杆点**:",
        ])
        for point in analysis["complexity_analysis"]["leverage_points"]:
            lines.append(f"- {point}")
        lines.append("")
        
        lines.extend([
            "## 综合建议",
            "",
            f"> {analysis['integrated_recommendation']}",
            "",
            "---",
            "",
            "*第一性原则 + 管理哲学 = 全面决策*"
        ])
        
        return "\n".join(lines)


def main():
    """主函数"""
    framework = ManagementPhilosophyFramework()
    
    # 示例：应用框架
    analysis = framework.apply_framework(
        context="信息搜索与甄别",
        decision="如何平衡搜索效率和信息质量"
    )
    
    # 生成报告
    report = framework.generate_thinking_report(analysis)
    print(report)


if __name__ == "__main__":
    main()
