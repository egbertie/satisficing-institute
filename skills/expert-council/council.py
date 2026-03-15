#!/usr/bin/env python3
"""
专家会诊协议 - 多专家替身协同决策
冲突检测 → 优先级裁决 → 真人确认
"""

import json
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ExpertOpinion:
    """专家意见"""
    expert_id: str
    expert_name: str
    totem: str  # 五路图腾
    element: str  # 五行
    opinion: str
    confidence: float  # 0-1
    reasoning: str
    timestamp: str

@dataclass
class Conflict:
    """意见冲突"""
    experts_involved: List[str]
    conflict_type: str  # "ethical", "methodological", "strategic"
    description: str
    severity: str  # "minor", "moderate", "severe"


class ExpertCouncil:
    """专家会诊中心"""
    
    # 五路图腾优先级（伦理 > 逻辑 > 效率）
    TOTEM_PRIORITY = {
        "CONFUCIUS": 5,   # 木 - 伦理
        "SIMON": 4,       # 金 - 逻辑
        "GUANYIN": 3,     # 水 - 自在
        "LIU": 2,         # 土 - 德馨
        "HUINENG": 1      # 火 - 顿悟
    }
    
    # 冲突类型裁决规则
    CONFLICT_RULES = {
        "ethical": {  # 伦理冲突
            "priority": ["CONFUCIUS", "SIMON", "GUANYIN"],
            "description": "伦理问题优先"
        },
        "methodological": {  # 方法论冲突
            "priority": ["SIMON", "CONFUCIUS", "HUINENG"],
            "description": "逻辑严谨优先"
        },
        "strategic": {  # 战略冲突
            "priority": ["GUANYIN", "SIMON", "CONFUCIUS"],
            "description": "长期视角优先"
        }
    }
    
    def __init__(self):
        self.experts = {
            "lihonglei": {
                "name": "黎红雷",
                "totem": "CONFUCIUS",
                "element": "木",
                "style": "伦理校准",
                "triggers": ["伦理", "价值观", "道德", "仁义"]
            },
            "luohan": {
                "name": "罗汉",
                "totem": "SIMON",
                "element": "金",
                "style": "方法论把关",
                "triggers": ["逻辑", "数学", "模型", "量化"]
            },
            "xiebaojian": {
                "name": "谢宝剑",
                "totem": "GUANYIN",
                "element": "水",
                "style": "战略分析",
                "triggers": ["政策", "地理", "深港", "战略"]
            },
            "ai_redteam": {
                "name": "AI蓝军首席",
                "totem": "HUINENG",
                "element": "火",
                "style": "压力测试",
                "triggers": ["风险", "漏洞", "压力", "测试"]
            }
        }
        self.consultation_history = []
    
    def consult(self, question: str, context: Dict = None) -> Dict:
        """
        专家会诊流程
        
        Args:
            question: 咨询问题
            context: 上下文信息
        
        Returns:
            会诊结果
        """
        context = context or {}
        
        print(f"🔍 启动专家会诊: {question[:50]}...")
        
        # Step 1: 路由到相关专家
        print("  → 识别相关专家...")
        relevant_experts = self._route_to_experts(question, context)
        print(f"  → 召集专家: {', '.join([self.experts[e]['name'] for e in relevant_experts])}")
        
        # Step 2: 并行征询意见
        print("  → 并行征询意见...")
        opinions = self._gather_opinions(question, relevant_experts, context)
        
        # Step 3: 冲突检测
        print("  → 检测意见冲突...")
        conflicts = self._detect_conflicts(opinions)
        
        if conflicts:
            print(f"  ⚠️ 发现 {len(conflicts)} 处冲突")
            # Step 4: 冲突裁决
            resolution = self._resolve_conflicts(opinions, conflicts)
        else:
            print("  ✅ 无冲突，意见一致")
            resolution = {
                "method": "consensus",
                "final_opinion": self._synthesize_opinions(opinions),
                "confidence": max(o.confidence for o in opinions)
            }
        
        # Step 5: 判断是否需要真人确认
        risk_level = self._assess_risk(question, context, conflicts)
        requires_human = risk_level in ["high", "critical"]
        
        # 生成会诊报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "experts_consulted": [self.experts[e]["name"] for e in relevant_experts],
            "opinions": [
                {
                    "expert": o.expert_name,
                    "totem": o.totem,
                    "opinion": o.opinion,
                    "confidence": o.confidence,
                    "reasoning": o.reasoning
                }
                for o in opinions
            ],
            "conflicts": [
                {
                    "type": c.conflict_type,
                    "severity": c.severity,
                    "experts": c.experts_involved,
                    "description": c.description
                }
                for c in conflicts
            ],
            "resolution": resolution,
            "risk_level": risk_level,
            "requires_human_confirmation": requires_human,
            "status": "pending_human" if requires_human else "resolved"
        }
        
        self.consultation_history.append(report)
        
        return report
    
    def _route_to_experts(self, question: str, context: Dict) -> List[str]:
        """路由到相关专家"""
        question_lower = question.lower()
        
        # 基于关键词匹配
        matched_experts = []
        scores = {}
        
        for expert_id, expert in self.experts.items():
            score = 0
            for trigger in expert["triggers"]:
                if trigger in question_lower:
                    score += 1
            if score > 0:
                scores[expert_id] = score
        
        # 如果没有匹配，默认召集SIMON（方法论）和CONFUCIUS（伦理）
        if not scores:
            return ["luohan", "lihonglei"]
        
        # 选择得分最高的2-3个专家
        sorted_experts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        selected = [e[0] for e in sorted_experts[:3]]
        
        return selected
    
    def _gather_opinions(self, question: str, expert_ids: List[str], context: Dict) -> List[ExpertOpinion]:
        """收集专家意见（模拟）"""
        opinions = []
        
        for expert_id in expert_ids:
            expert = self.experts[expert_id]
            
            # 模拟专家基于其风格生成意见
            opinion = self._generate_expert_opinion(expert, question, context)
            opinions.append(opinion)
        
        return opinions
    
    def _generate_expert_opinion(self, expert: Dict, question: str, context: Dict) -> ExpertOpinion:
        """生成专家意见（实际应调用数字替身API）"""
        
        # 基于专家风格生成模板意见
        style_templates = {
            "CONFUCIUS": {
                "prefix": "从儒商伦理来看，",
                "focus": "仁义",
                "confidence_range": (0.7, 0.9)
            },
            "SIMON": {
                "prefix": "从决策科学角度，",
                "focus": "逻辑",
                "confidence_range": (0.75, 0.95)
            },
            "GUANYIN": {
                "prefix": "从战略地缘视角，",
                "focus": "自在",
                "confidence_range": (0.65, 0.85)
            },
            "HUINENG": {
                "prefix": "通过压力测试发现，",
                "focus": "风险",
                "confidence_range": (0.6, 0.8)
            }
        }
        
        template = style_templates.get(expert["totem"], style_templates["SIMON"])
        
        # 生成意见（简化版）
        opinion_text = f"{template['prefix']}这个问题需要重点关注{template['focus']}。"
        
        import random
        confidence = random.uniform(*template["confidence_range"])
        
        return ExpertOpinion(
            expert_id=expert["name"],
            expert_name=expert["name"],
            totem=expert["totem"],
            element=expert["element"],
            opinion=opinion_text,
            confidence=confidence,
            reasoning=f"基于{expert['style']}的分析框架",
            timestamp=datetime.now().isoformat()
        )
    
    def _detect_conflicts(self, opinions: List[ExpertOpinion]) -> List[Conflict]:
        """检测意见冲突"""
        conflicts = []
        
        # 检查置信度差异（如果差异过大，可能存在冲突）
        confidences = [o.confidence for o in opinions]
        if max(confidences) - min(confidences) > 0.3:
            max_conf = max(opinions, key=lambda x: x.confidence)
            min_conf = min(opinions, key=lambda x: x.confidence)
            
            conflicts.append(Conflict(
                experts_involved=[max_conf.expert_name, min_conf.expert_name],
                conflict_type="methodological",
                description=f"置信度差异显著 ({max_conf.confidence:.2f} vs {min_conf.confidence:.2f})",
                severity="moderate"
            ))
        
        # 检查图腾对立（简化版：金木对立）
        elements = [o.element for o in opinions]
        if "金" in elements and "木" in elements:
            metal_expert = next(o for o in opinions if o.element == "金")
            wood_expert = next(o for o in opinions if o.element == "木")
            
            conflicts.append(Conflict(
                experts_involved=[metal_expert.expert_name, wood_expert.expert_name],
                conflict_type="ethical",
                description="逻辑与伦理的潜在冲突",
                severity="moderate"
            ))
        
        return conflicts
    
    def _resolve_conflicts(self, opinions: List[ExpertOpinion], conflicts: List[Conflict]) -> Dict:
        """裁决冲突"""
        
        # 按优先级排序意见
        def priority_key(opinion):
            return self.TOTEM_PRIORITY.get(opinion.totem, 0)
        
        sorted_opinions = sorted(opinions, key=priority_key, reverse=True)
        highest_priority = sorted_opinions[0]
        
        # 生成裁决结果
        resolution = {
            "method": "priority_based",
            "priority_rule": "伦理 > 逻辑 > 效率",
            "final_opinion": {
                "expert": highest_priority.expert_name,
                "totem": highest_priority.totem,
                "opinion": highest_priority.opinion,
                "reasoning": f"基于{highest_priority.totem}优先级最高"
            },
            "dissenting_opinions": [
                {
                    "expert": o.expert_name,
                    "opinion": o.opinion,
                    "note": "意见被采纳但优先级较低"
                }
                for o in sorted_opinions[1:]
            ],
            "confidence": highest_priority.confidence
        }
        
        return resolution
    
    def _synthesize_opinions(self, opinions: List[ExpertOpinion]) -> Dict:
        """综合一致意见"""
        # 简单综合：取平均置信度，合并意见
        avg_confidence = sum(o.confidence for o in opinions) / len(opinions)
        
        return {
            "synthesis": "各专家意见一致",
            "supporting_experts": [o.expert_name for o in opinions],
            "combined_confidence": avg_confidence
        }
    
    def _assess_risk(self, question: str, context: Dict, conflicts: List[Conflict]) -> str:
        """评估风险等级"""
        risk_score = 0
        
        # 冲突增加风险
        risk_score += len(conflicts) * 20
        
        # 外部影响增加风险
        if context.get("external"):
            risk_score += 30
        
        # 财务影响增加风险
        if context.get("financial"):
            risk_score += 40
        
        # 不可逆操作增加风险
        if context.get("irreversible"):
            risk_score += 50
        
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 60:
            return "high"
        elif risk_score >= 40:
            return "medium"
        else:
            return "low"
    
    def get_consultation_history(self, limit: int = 10) -> List[Dict]:
        """获取会诊历史"""
        return self.consultation_history[-limit:]


# 便捷函数
def expert_consult(question: str, context: Dict = None) -> Dict:
    """快速专家会诊"""
    council = ExpertCouncil()
    return council.consult(question, context)


if __name__ == "__main__":
    # 测试
    print("=== 专家会诊测试 ===\n")
    
    test_question = "合伙人价值观不一致，是否应该继续合作？"
    
    result = expert_consult(test_question, {"external": False})
    
    print(f"\n会诊结果:")
    print(f"  参与专家: {result['experts_consulted']}")
    print(f"  冲突数量: {len(result['conflicts'])}")
    print(f"  风险等级: {result['risk_level']}")
    print(f"  需要真人确认: {result['requires_human_confirmation']}")
    print(f"  裁决方式: {result['resolution']['method']}")
    if 'final_opinion' in result['resolution']:
        print(f"  最终意见: {result['resolution']['final_opinion'].get('expert', 'N/A')}")
