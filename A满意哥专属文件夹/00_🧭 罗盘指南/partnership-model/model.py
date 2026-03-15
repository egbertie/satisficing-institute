#!/usr/bin/env python3
"""
满意解研究所 - 合伙人决策建模体系 V1.0
基于10个案例数据构建的评估模型
"""

import json
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    CRITICAL = "critical"    # 必须否决
    HIGH = "high"           # 需要专家会诊
    MEDIUM = "medium"       # 需要关注
    LOW = "low"             # 正常范围
    EXCELLENT = "excellent" # 优势特征

@dataclass
class DimensionScore:
    """维度评分"""
    dimension: str
    score: float  # 0-10
    weight: float
    evidence: List[str]
    risk_signals: List[str]

@dataclass
class PartnershipModel:
    """合伙人匹配模型"""
    founder: Dict
    partner: Dict
    dimension_scores: List[DimensionScore]
    overall_score: float
    risk_level: RiskLevel
    confidence: float
    recommendations: List[str]


class SatisficingDecisionModel:
    """
    满意解决策模型
    基于10个案例验证的7维度评估体系
    """
    
    # 7维度权重（基于10个案例验证）
    DIMENSION_WEIGHTS = {
        "values_alignment": 0.25,      # 价值观契合度
        "capability_complementarity": 0.20,  # 能力互补性
        "communication_efficiency": 0.15,    # 沟通效率
        "commitment_credibility": 0.15,      # 承诺可信度
        "interest_alignment": 0.10,          # 利益一致性
        "exit_acceptability": 0.10,          # 退出可接受性
        "growth_matching": 0.05              # 成长匹配度
    }
    
    # 维度名称映射
    DIMENSION_NAMES = {
        "values_alignment": "价值观契合度",
        "capability_complementarity": "能力互补性",
        "communication_efficiency": "沟通效率",
        "commitment_credibility": "承诺可信度",
        "interest_alignment": "利益一致性",
        "exit_acceptability": "退出可接受性",
        "growth_matching": "成长匹配度"
    }
    
    # 风险阈值（基于案例统计）
    RISK_THRESHOLDS = {
        "values_alignment": 5.0,       # <5 高风险（价值观冲突是主要失败原因）
        "commitment_credibility": 6.0, # <6 高风险（承诺不足导致失败）
        "communication_efficiency": 5.0, # <5 中风险
        "overall": 6.5                 # 综合分<6.5 需谨慎
    }
    
    def __init__(self):
        self.case_data = self._load_case_data()
    
    def _load_case_data(self) -> List[Dict]:
        """加载10个案例的满意解评分数据"""
        return [
            # CASE-001: 成功
            {"id": "CASE-001", "outcome": "success", 
             "scores": {"values_alignment": 9, "capability_complementarity": 9, 
                       "commitment_credibility": 8, "communication_efficiency": 8,
                       "interest_alignment": 7, "exit_acceptability": 7, "growth_matching": 8}},
            # CASE-002: 失败
            {"id": "CASE-002", "outcome": "failure",
             "scores": {"values_alignment": 2, "capability_complementarity": 7,
                       "commitment_credibility": 4, "communication_efficiency": 3,
                       "interest_alignment": 2, "exit_acceptability": 5, "growth_matching": 3}},
            # CASE-003: 进行中
            {"id": "CASE-003", "outcome": "ongoing",
             "scores": {"values_alignment": 6, "capability_complementarity": 9,
                       "commitment_credibility": 5, "communication_efficiency": 5,
                       "interest_alignment": 6, "exit_acceptability": 6, "growth_matching": 7}},
            # CASE-004: 成功
            {"id": "CASE-004", "outcome": "success",
             "scores": {"values_alignment": 8, "capability_complementarity": 9,
                       "commitment_credibility": 9, "communication_efficiency": 8,
                       "interest_alignment": 8, "exit_acceptability": 7, "growth_matching": 8}},
            # CASE-005: 失败
            {"id": "CASE-005", "outcome": "failure",
             "scores": {"values_alignment": 4, "capability_complementarity": 8,
                       "commitment_credibility": 5, "communication_efficiency": 3,
                       "interest_alignment": 4, "exit_acceptability": 4, "growth_matching": 4}},
            # CASE-006: 成功
            {"id": "CASE-006", "outcome": "success",
             "scores": {"values_alignment": 9, "capability_complementarity": 9,
                       "commitment_credibility": 9, "communication_efficiency": 8,
                       "interest_alignment": 8, "exit_acceptability": 8, "growth_matching": 8}},
            # CASE-007: 进行中
            {"id": "CASE-007", "outcome": "ongoing",
             "scores": {"values_alignment": 5, "capability_complementarity": 9,
                       "commitment_credibility": 6, "communication_efficiency": 4,
                       "interest_alignment": 5, "exit_acceptability": 6, "growth_matching": 5}},
            # CASE-008: 成功
            {"id": "CASE-008", "outcome": "success",
             "scores": {"values_alignment": 9, "capability_complementarity": 9,
                       "commitment_credibility": 8, "communication_efficiency": 8,
                       "interest_alignment": 8, "exit_acceptability": 7, "growth_matching": 8}},
            # CASE-009: 失败
            {"id": "CASE-009", "outcome": "failure",
             "scores": {"values_alignment": 5, "capability_complementarity": 8,
                       "commitment_credibility": 3, "communication_efficiency": 5,
                       "interest_alignment": 4, "exit_acceptability": 8, "growth_matching": 3}},
            # CASE-010: 成功
            {"id": "CASE-010", "outcome": "success",
             "scores": {"values_alignment": 8, "capability_complementarity": 9,
                       "commitment_credibility": 9, "communication_efficiency": 9,
                       "interest_alignment": 8, "exit_acceptability": 8, "growth_matching": 8}}
        ]
    
    def evaluate(self, scores: Dict[str, float]) -> PartnershipModel:
        """
        评估合伙人匹配度
        
        Args:
            scores: 7维度评分，每个维度0-10
        
        Returns:
            评估结果模型
        """
        dimension_scores = []
        weighted_sum = 0
        total_weight = 0
        
        # 计算各维度加权分
        for dim_key, weight in self.DIMENSION_WEIGHTS.items():
            score = scores.get(dim_key, 5.0)  # 默认5分
            weighted_score = score * weight
            weighted_sum += weighted_score
            total_weight += weight
            
            # 生成证据和风险信号
            evidence = self._generate_evidence(dim_key, score)
            risk_signals = self._generate_risk_signals(dim_key, score)
            
            dimension_scores.append(DimensionScore(
                dimension=self.DIMENSION_NAMES[dim_key],
                score=score,
                weight=weight,
                evidence=evidence,
                risk_signals=risk_signals
            ))
        
        # 综合得分
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        # 确定风险等级
        risk_level = self._determine_risk_level(scores, overall_score)
        
        # 生成建议
        recommendations = self._generate_recommendations(scores, risk_level)
        
        # 计算置信度（数据完整度）
        confidence = len([s for s in scores.values() if s > 0]) / len(self.DIMENSION_WEIGHTS)
        
        return PartnershipModel(
            founder={},
            partner={},
            dimension_scores=dimension_scores,
            overall_score=overall_score,
            risk_level=risk_level,
            confidence=confidence,
            recommendations=recommendations
        )
    
    def _generate_evidence(self, dimension: str, score: float) -> List[str]:
        """生成维度证据"""
        evidence_map = {
            "values_alignment": {
                "high": ["核心价值观高度一致", "对商业伦理有共同理解", "长期目标对齐"],
                "medium": ["价值观基本一致，部分差异", "需要磨合"],
                "low": ["价值观存在显著差异", "可能对重大决策产生分歧"]
            },
            "capability_complementarity": {
                "high": ["能力高度互补", "覆盖关键业务领域", "形成完整能力圈"],
                "medium": ["有一定互补性", "部分能力重叠或缺失"],
                "low": ["能力重叠度高", "关键能力缺失"]
            },
            "commitment_credibility": {
                "high": ["全职承诺", "有兑现记录", "投入度高"],
                "medium": ["承诺基本可信", "需要持续观察"],
                "low": ["兼职或不确定", "承诺兑现存疑"]
            },
            "communication_efficiency": {
                "high": ["沟通顺畅", "信息透明", "决策高效"],
                "medium": ["沟通基本顺畅", "偶有误解"],
                "low": ["沟通成本高", "信息不透明", "决策缓慢"]
            },
            "interest_alignment": {
                "high": ["利益高度一致", "股权结构合理", "激励机制对齐"],
                "medium": ["利益基本一致", " minor差异可调和"],
                "low": ["利益冲突明显", "股权结构不合理"]
            },
            "exit_acceptability": {
                "high": ["退出机制明确", "双方可接受", "风险可控"],
                "medium": ["退出机制基本合理", "部分条款需商议"],
                "low": ["退出机制缺失", "一方难以接受"]
            },
            "growth_matching": {
                "high": ["成长速度匹配", "互相促进", "共同进步"],
                "medium": ["成长速度略有差异", "基本可接受"],
                "low": ["成长速度差异大", "可能产生隔阂"]
            }
        }
        
        level = "high" if score >= 7 else "medium" if score >= 5 else "low"
        return evidence_map.get(dimension, {}).get(level, [])
    
    def _generate_risk_signals(self, dimension: str, score: float) -> List[str]:
        """生成风险信号"""
        risk_signals = []
        
        threshold = self.RISK_THRESHOLDS.get(dimension, 5.0)
        if score < threshold:
            risk_signals.append(f"{self.DIMENSION_NAMES[dimension]}低于安全阈值({threshold})")
        
        # 特定维度的额外风险信号
        if dimension == "values_alignment" and score < 5:
            risk_signals.append("价值观冲突是合伙失败的首要原因（基于案例统计）")
        
        if dimension == "commitment_credibility" and score < 6:
            risk_signals.append("承诺不足是硬科技创业失败的关键因素")
        
        if dimension == "communication_efficiency" and score < 5:
            risk_signals.append("沟通障碍会在磨合期显著放大")
        
        return risk_signals
    
    def _determine_risk_level(self, scores: Dict[str, float], overall_score: float) -> RiskLevel:
        """确定风险等级"""
        # 检查是否有致命缺陷
        if scores.get("values_alignment", 10) < 4:
            return RiskLevel.CRITICAL
        
        if scores.get("commitment_credibility", 10) < 4:
            return RiskLevel.CRITICAL
        
        # 检查高风险情况
        critical_count = sum(1 for s in scores.values() if s < 5)
        if critical_count >= 2 or overall_score < 5.5:
            return RiskLevel.HIGH
        
        if critical_count == 1 or overall_score < 6.5:
            return RiskLevel.MEDIUM
        
        if overall_score >= 8:
            return RiskLevel.EXCELLENT
        
        return RiskLevel.LOW
    
    def _generate_recommendations(self, scores: Dict[str, float], risk_level: RiskLevel) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append("⚠️ 存在致命风险，建议重新评估合伙可行性")
        
        if risk_level == RiskLevel.HIGH:
            recommendations.append("⚠️ 风险较高，建议在专业顾问指导下深入尽调")
        
        # 针对低分维度给出建议
        if scores.get("values_alignment", 10) < 6:
            recommendations.append("建议通过深度对话和场景测试验证价值观契合度")
        
        if scores.get("commitment_credibility", 10) < 7:
            recommendations.append("明确全职承诺时间表，设定阶段性投入里程碑")
        
        if scores.get("communication_efficiency", 10) < 6:
            recommendations.append("建立定期沟通机制，明确决策流程和信息共享规范")
        
        if scores.get("capability_complementarity", 10) < 7:
            recommendations.append("绘制能力地图，识别关键能力缺口和冗余")
        
        if scores.get("exit_acceptability", 10) < 6:
            recommendations.append("尽早设计退出机制，明确退出条件和补偿方案")
        
        if not recommendations:
            recommendations.append("✅ 各项指标良好，建议进入尽职调查阶段")
        
        return recommendations
    
    def compare_with_cases(self, scores: Dict[str, float]) -> Dict:
        """与案例库中的案例对比"""
        similarities = []
        
        for case in self.case_data:
            # 计算欧氏距离
            distance = math.sqrt(sum(
                (scores.get(k, 5) - case["scores"].get(k, 5)) ** 2
                for k in self.DIMENSION_WEIGHTS.keys()
            ))
            
            similarities.append({
                "case_id": case["id"],
                "outcome": case["outcome"],
                "similarity": max(0, 10 - distance) / 10  # 转换为相似度
            })
        
        # 按相似度排序
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # 统计最相似的案例结果
        top_similar = similarities[:3]
        success_rate = sum(1 for s in top_similar if s["outcome"] == "success") / len(top_similar)
        
        return {
            "most_similar_cases": top_similar,
            "predicted_success_rate": success_rate,
            "similarity_analysis": f"与{top_similar[0]['case_id']}最相似（相似度{top_similar[0]['similarity']:.1%}）"
        }
    
    def generate_report(self, model: PartnershipModel) -> str:
        """生成评估报告"""
        report = f"""# 合伙人匹配评估报告

## 综合评分

**总体得分**: {model.overall_score:.1f}/10  
**风险等级**: {model.risk_level.value.upper()}  
**置信度**: {model.confidence:.0%}

---

## 维度分析

"""
        
        for ds in model.dimension_scores:
            report += f"""### {ds.dimension} (权重{ds.weight:.0%})
- **得分**: {ds.score:.1f}/10
- **证据**: {', '.join(ds.evidence) if ds.evidence else '无明显特征'}
- **风险信号**: {', '.join(ds.risk_signals) if ds.risk_signals else '无'}

"""
        
        report += f"""---

## 建议行动

"""
        for i, rec in enumerate(model.recommendations, 1):
            report += f"{i}. {rec}\n"
        
        # 对比案例
        case_comparison = self.compare_with_cases({
            self._get_dim_key(ds.dimension): ds.score
            for ds in model.dimension_scores
        })
        
        report += f"""
---

## 案例对比

**相似案例**: {case_comparison['similarity_analysis']}  
**预测成功率**: {case_comparison['predicted_success_rate']:.0%}

基于案例库分析，该合伙人组合的历史表现参考：
"""
        for sim in case_comparison['most_similar_cases'][:3]:
            icon = "✅" if sim["outcome"] == "success" else "❌" if sim["outcome"] == "failure" else "🔄"
            report += f"- {icon} {sim['case_id']}: {sim['similarity']:.0%} 相似\n"
        
        report += f"""
---

*报告生成时间: 2026-03-15*  
*基于满意解研究所10个案例数据*
"""
        
        return report
    
    def _get_dim_key(self, name: str) -> str:
        """根据名称获取维度key"""
        for k, v in self.DIMENSION_NAMES.items():
            if v == name:
                return k
        return ""


# 便捷函数
def evaluate_partnership(scores: Dict[str, float]) -> PartnershipModel:
    """快速评估合伙人匹配度"""
    model = SatisficingDecisionModel()
    return model.evaluate(scores)


def generate_evaluation_report(scores: Dict[str, float]) -> str:
    """生成评估报告"""
    model = SatisficingDecisionModel()
    result = model.evaluate(scores)
    return model.generate_report(result)


if __name__ == "__main__":
    # 测试评估
    print("=== 满意解决策模型测试 ===\n")
    
    # 测试案例：模拟一个中等风险的组合
    test_scores = {
        "values_alignment": 6.5,
        "capability_complementarity": 8.0,
        "commitment_credibility": 6.0,
        "communication_efficiency": 5.5,
        "interest_alignment": 6.0,
        "exit_acceptability": 6.5,
        "growth_matching": 6.0
    }
    
    model = SatisficingDecisionModel()
    result = model.evaluate(test_scores)
    
    print(f"综合得分: {result.overall_score:.1f}")
    print(f"风险等级: {result.risk_level.value}")
    print(f"置信度: {result.confidence:.0%}")
    print(f"\n维度评分:")
    for ds in result.dimension_scores:
        print(f"  {ds.dimension}: {ds.score:.1f} (权重{ds.weight:.0%})")
    
    print(f"\n建议:")
    for rec in result.recommendations:
        print(f"  - {rec}")
    
    # 生成完整报告
    report = model.generate_report(result)
    print(f"\n{'='*50}")
    print("完整报告预览:")
    print(report[:500] + "...")
