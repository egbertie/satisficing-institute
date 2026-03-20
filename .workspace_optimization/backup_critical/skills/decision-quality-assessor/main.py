#!/usr/bin/env python3
"""
决策质量评估器 (Decision Quality Assessor)
功能：评估已做决策的质量和后续结果
追踪：决策→结果→复盘→改进的完整闭环
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class DecisionType(Enum):
    STRATEGIC = "战略决策"
    TACTICAL = "战术决策"
    OPERATIONAL = "运营决策"
    PERSONNEL = "人事决策"
    FINANCIAL = "财务决策"


class OutcomeStatus(Enum):
    EXCEEDED = "超预期"
    ACHIEVED = "达成目标"
    PARTIAL = "部分达成"
    MISSED = "未达成"
    UNKNOWN = "待观察"


@dataclass
class DecisionInput:
    """决策输入数据"""
    description: str
    decision_type: DecisionType
    decision_date: str
    expected_result: str
    expected_metrics: Dict[str, float]  # 预期指标：{"revenue": 1000000, "users": 10000}
    context: Dict = None  # 决策背景信息
    alternatives: List[str] = None  # 备选方案
    stakeholders: List[str] = None  # 决策参与者
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.alternatives is None:
            self.alternatives = []
        if self.stakeholders is None:
            self.stakeholders = []


@dataclass
class ActualOutcome:
    """实际结果数据"""
    actual_result: str
    actual_metrics: Dict[str, float]
    outcome_date: str
    qualitative_feedback: str = ""
    lessons_learned: List[str] = None
    
    def __post_init__(self):
        if self.lessons_learned is None:
            self.lessons_learned = []


@dataclass
class AssessmentResult:
    """评估结果"""
    decision_id: str
    overall_score: float  # 0-100
    outcome_status: OutcomeStatus
    deviation_analysis: Dict
    quality_breakdown: Dict[str, float]
    improvement_suggestions: List[str]
    learning_points: List[str]
    next_actions: List[str]
    assessment_date: str


class DecisionQualityAssessor:
    """决策质量评估器"""
    
    # 评估权重
    WEIGHTS = {
        "outcome_achievement": 0.35,
        "process_quality": 0.25,
        "learning_value": 0.20,
        "timeliness": 0.10,
        "stakeholder_satisfaction": 0.10
    }
    
    def __init__(self):
        self.decision_history = []
    
    def _calculate_outcome_achievement(self, expected: Dict, actual: Dict) -> float:
        """计算目标达成度"""
        if not expected:
            return 50.0
        
        scores = []
        for key, expected_val in expected.items():
            actual_val = actual.get(key, 0)
            if expected_val == 0:
                continue
            ratio = actual_val / expected_val
            if ratio >= 1.2:
                scores.append(100)  # 超预期
            elif ratio >= 1.0:
                scores.append(90)   # 达成
            elif ratio >= 0.8:
                scores.append(70)   # 基本达成
            elif ratio >= 0.5:
                scores.append(50)   # 部分达成
            else:
                scores.append(30)   # 未达成
        
        return sum(scores) / len(scores) if scores else 50.0
    
    def _determine_outcome_status(self, achievement_score: float) -> OutcomeStatus:
        """确定结果状态"""
        if achievement_score >= 95:
            return OutcomeStatus.EXCEEDED
        elif achievement_score >= 80:
            return OutcomeStatus.ACHIEVED
        elif achievement_score >= 60:
            return OutcomeStatus.PARTIAL
        else:
            return OutcomeStatus.MISSED
    
    def _analyze_deviation(self, expected: Dict, actual: Dict) -> Dict:
        """分析偏差"""
        deviations = {}
        
        all_keys = set(expected.keys()) | set(actual.keys())
        for key in all_keys:
            expected_val = expected.get(key, 0)
            actual_val = actual.get(key, 0)
            
            if expected_val == 0:
                deviation_pct = 0 if actual_val == 0 else 100
            else:
                deviation_pct = ((actual_val - expected_val) / expected_val) * 100
            
            deviations[key] = {
                "expected": expected_val,
                "actual": actual_val,
                "deviation": actual_val - expected_val,
                "deviation_pct": round(deviation_pct, 2),
                "status": "超出" if deviation_pct > 10 else "达成" if deviation_pct >= -10 else "低于"
            }
        
        return deviations
    
    def _calculate_process_quality(self, decision: DecisionInput) -> float:
        """评估决策过程质量"""
        score = 50.0  # 基础分
        
        # 有明确预期指标
        if decision.expected_metrics:
            score += 15
        
        # 有备选方案
        if len(decision.alternatives) >= 2:
            score += 15
        elif len(decision.alternatives) == 1:
            score += 8
        
        # 有利益相关者参与
        if len(decision.stakeholders) >= 2:
            score += 10
        
        # 有决策背景记录
        if decision.context:
            score += 10
        
        return min(100, score)
    
    def _calculate_learning_value(self, outcome: ActualOutcome, achievement: float) -> float:
        """计算学习价值"""
        score = 50.0
        
        # 有经验总结
        if len(outcome.lessons_learned) >= 3:
            score += 20
        elif len(outcome.lessons_learned) >= 1:
            score += 10
        
        # 有定性反馈
        if outcome.qualitative_feedback and len(outcome.qualitative_feedback) > 20:
            score += 15
        
        # 即使未达成也有学习价值
        if achievement < 60 and len(outcome.lessons_learned) > 0:
            score += 15
        
        return min(100, score)
    
    def _calculate_timeliness(self, decision_date: str, outcome_date: str) -> float:
        """评估时效性"""
        try:
            d_date = datetime.strptime(decision_date, "%Y-%m-%d")
            o_date = datetime.strptime(outcome_date, "%Y-%m-%d")
            days_diff = (o_date - d_date).days
            
            # 决策到结果的时间合理性
            if days_diff <= 7:
                return 95
            elif days_diff <= 30:
                return 85
            elif days_diff <= 90:
                return 75
            elif days_diff <= 180:
                return 65
            else:
                return 50
        except:
            return 70
    
    def _generate_suggestions(self, result: AssessmentResult, decision: DecisionInput, outcome: ActualOutcome) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于目标达成度
        if result.quality_breakdown["outcome_achievement"] < 60:
            suggestions.append("【目标设定】预期目标可能过于激进或缺乏充分论证，建议下次使用SMART原则重新评估")
            suggestions.append("【执行追踪】建立更频繁的里程碑检查机制，及时发现问题")
        
        # 基于过程质量
        if result.quality_breakdown["process_quality"] < 70:
            if len(decision.alternatives) < 2:
                suggestions.append("【决策流程】建议引入更多备选方案，使用决策矩阵进行评估")
            if len(decision.stakeholders) < 2:
                suggestions.append("【参与机制】增加关键利益相关者的参与度，获取多元视角")
        
        # 基于偏差分析
        for metric, deviation in result.deviation_analysis.items():
            if deviation["deviation_pct"] < -30:
                suggestions.append(f"【{metric}】实际值远低于预期，建议复盘执行过程中的关键瓶颈")
            elif deviation["deviation_pct"] > 50:
                suggestions.append(f"【{metric}】实际值超预期，建议分析成功因素并沉淀为方法论")
        
        # 通用建议
        if not suggestions:
            suggestions.append("【持续优化】继续保持当前决策质量，建议定期复盘成功经验")
            suggestions.append("【知识沉淀】将此决策过程和方法论文档化，供团队学习参考")
        
        return suggestions
    
    def _generate_learning_points(self, decision: DecisionInput, outcome: ActualOutcome, deviation: Dict) -> List[str]:
        """生成学习要点"""
        points = outcome.lessons_learned.copy() if outcome.lessons_learned else []
        
        # 基于决策质量自动提炼
        if decision.expected_metrics and any(d.get("deviation_pct", 0) < -20 for d in deviation.values()):
            points.append("目标设定需要考虑更多外部不确定因素")
        
        if len(decision.alternatives) < 2:
            points.append("单一方案决策风险较高，应建立方案对比机制")
        
        if not points:
            points.append("决策执行过程基本顺利，经验值得在类似场景中复用")
        
        return points
    
    def _generate_next_actions(self, result: AssessmentResult) -> List[str]:
        """生成后续行动建议"""
        actions = []
        
        if result.outcome_status in [OutcomeStatus.MISSED, OutcomeStatus.PARTIAL]:
            actions.append("30天内召开复盘会议，深入分析未达成原因")
            actions.append("制定纠偏行动计划，明确责任人和时间节点")
        
        if result.quality_breakdown["learning_value"] < 70:
            actions.append("整理本次决策的经验教训，更新团队知识库")
        
        actions.append(f"将评估报告归档，建立决策ID: {result.decision_id}的追踪档案")
        actions.append("在下次类似决策时参考本次评估结论")
        
        return actions
    
    def assess(self, decision: DecisionInput, outcome: ActualOutcome) -> AssessmentResult:
        """评估决策质量"""
        
        decision_id = f"DEC-{datetime.now().strftime('%Y%m%d')}-{len(self.decision_history)+1:04d}"
        
        # 计算各部分得分
        outcome_achievement = self._calculate_outcome_achievement(
            decision.expected_metrics, outcome.actual_metrics
        )
        
        deviation_analysis = self._analyze_deviation(
            decision.expected_metrics, outcome.actual_metrics
        )
        
        process_quality = self._calculate_process_quality(decision)
        learning_value = self._calculate_learning_value(outcome, outcome_achievement)
        timeliness = self._calculate_timeliness(decision.decision_date, outcome.outcome_date)
        
        # 利益相关者满意度（简化处理）
        stakeholder_satisfaction = 75.0 if len(decision.stakeholders) > 0 else 60.0
        
        # 计算总分
        quality_breakdown = {
            "outcome_achievement": round(outcome_achievement, 2),
            "process_quality": round(process_quality, 2),
            "learning_value": round(learning_value, 2),
            "timeliness": round(timeliness, 2),
            "stakeholder_satisfaction": round(stakeholder_satisfaction, 2)
        }
        
        overall_score = (
            quality_breakdown["outcome_achievement"] * self.WEIGHTS["outcome_achievement"] +
            quality_breakdown["process_quality"] * self.WEIGHTS["process_quality"] +
            quality_breakdown["learning_value"] * self.WEIGHTS["learning_value"] +
            quality_breakdown["timeliness"] * self.WEIGHTS["timeliness"] +
            quality_breakdown["stakeholder_satisfaction"] * self.WEIGHTS["stakeholder_satisfaction"]
        )
        
        outcome_status = self._determine_outcome_status(outcome_achievement)
        
        result = AssessmentResult(
            decision_id=decision_id,
            overall_score=round(overall_score, 2),
            outcome_status=outcome_status,
            deviation_analysis=deviation_analysis,
            quality_breakdown=quality_breakdown,
            improvement_suggestions=[],
            learning_points=[],
            next_actions=[],
            assessment_date=datetime.now().isoformat()
        )
        
        # 生成建议
        result.improvement_suggestions = self._generate_suggestions(result, decision, outcome)
        result.learning_points = self._generate_learning_points(decision, outcome, deviation_analysis)
        result.next_actions = self._generate_next_actions(result)
        
        # 保存历史
        self.decision_history.append({
            "decision_id": decision_id,
            "decision": asdict(decision),
            "outcome": asdict(outcome),
            "assessment": asdict(result)
        })
        
        return result
    
    def generate_report(self, result: AssessmentResult, decision: DecisionInput, outcome: ActualOutcome) -> str:
        """生成评估报告"""
        lines = [
            "=" * 70,
            "                决策质量评估报告",
            "=" * 70,
            f"决策ID: {result.decision_id}",
            f"评估日期: {result.assessment_date}",
            "",
            "【决策信息】",
            f"  决策描述: {decision.description}",
            f"  决策类型: {decision.decision_type.value}",
            f"  决策日期: {decision.decision_date}",
            f"  参与人员: {', '.join(decision.stakeholders) if decision.stakeholders else '未记录'}",
            "",
            "【预期 vs 实际】",
            f"  预期结果: {decision.expected_result}",
            f"  实际结果: {outcome.actual_result}",
            f"  结果状态: {result.outcome_status.value}",
            "",
            "【偏差分析】",
        ]
        
        for metric, dev in result.deviation_analysis.items():
            lines.append(f"  {metric}:")
            lines.append(f"    预期: {dev['expected']}, 实际: {dev['actual']}")
            lines.append(f"    偏差: {dev['deviation']} ({dev['deviation_pct']}%) - {dev['status']}")
        
        lines.extend([
            "",
            "【质量评分】",
            f"  综合得分: {result.overall_score}/100",
            f"  ├─ 目标达成度: {result.quality_breakdown['outcome_achievement']} (权重35%)",
            f"  ├─ 决策过程质量: {result.quality_breakdown['process_quality']} (权重25%)",
            f"  ├─ 学习价值: {result.quality_breakdown['learning_value']} (权重20%)",
            f"  ├─ 时效性: {result.quality_breakdown['timeliness']} (权重10%)",
            f"  └─ 利益相关者满意度: {result.quality_breakdown['stakeholder_satisfaction']} (权重10%)",
            "",
            "【改进建议】",
        ])
        
        for i, suggestion in enumerate(result.improvement_suggestions, 1):
            lines.append(f"  {i}. {suggestion}")
        
        lines.extend([
            "",
            "【学习要点】",
        ])
        
        for i, point in enumerate(result.learning_points, 1):
            lines.append(f"  {i}. {point}")
        
        lines.extend([
            "",
            "【后续行动】",
        ])
        
        for i, action in enumerate(result.next_actions, 1):
            lines.append(f"  {i}. {action}")
        
        lines.extend([
            "",
            "=" * 70,
            "评估完成 - 建议将本报告归档并定期回顾",
            "=" * 70
        ])
        
        return "\n".join(lines)


def main():
    """主函数演示"""
    print("🎯 决策质量评估器 - 演示\n")
    
    # 初始化评估器
    assessor = DecisionQualityAssessor()
    
    # 示例决策1：成功的战略决策
    decision1 = DecisionInput(
        description="Q1战略：进军华东市场，开设3个新办事处",
        decision_type=DecisionType.STRATEGIC,
        decision_date="2024-01-15",
        expected_result="在华东地区建立品牌影响力，获取首批100家企业客户",
        expected_metrics={"新客户": 100, "营收增长": 5000000, "市场占有率": 5.0},
        context={"市场趋势": "华东地区数字化转型加速", "竞争态势": "竞争对手较少"},
        alternatives=["专注深耕现有市场", "通过代理模式进入", "直接开设办事处"],
        stakeholders=["CEO", "销售总监", "财务总监"]
    )
    
    outcome1 = ActualOutcome(
        actual_result="成功开设3个办事处，品牌影响力提升",
        actual_metrics={"新客户": 85, "营收增长": 4200000, "市场占有率": 4.2},
        outcome_date="2024-03-31",
        qualitative_feedback="整体执行顺利，客户获取速度略低于预期但客户质量较高",
        lessons_learned=[
            "本地化团队建设需要更长时间",
            "早期应投入更多市场教育预算",
            "与当地政府建立关系对业务拓展很有帮助"
        ]
    )
    
    # 示例决策2：未达预期的产品决策
    decision2 = DecisionInput(
        description="上线新功能：AI智能客服系统",
        decision_type=DecisionType.TACTICAL,
        decision_date="2024-02-01",
        expected_result="减少人工客服工作量50%，提升客户满意度至90%",
        expected_metrics={"工单处理效率提升": 50, "客户满意度": 90, "成本节约": 200000},
        context={"技术成熟度": "AI技术已相对成熟", "需求紧迫性": "客服团队压力大"},
        alternatives=["增加人工客服", "外包客服", "上线AI客服"],
        stakeholders=["产品总监", "CTO", "客服经理"]
    )
    
    outcome2 = ActualOutcome(
        actual_result="AI客服系统上线但效果不理想，用户投诉增加",
        actual_metrics={"工单处理效率提升": 15, "客户满意度": 72, "成本节约": 50000},
        outcome_date="2024-03-15",
        qualitative_feedback="AI理解能力有限，复杂问题处理不佳，用户反馈体验下降",
        lessons_learned=[
            "AI客服需要更长的训练周期",
            "应设置更完善的人工接管机制",
            "用户需求调研不够充分"
        ]
    )
    
    # 评估两个决策
    print("=" * 70)
    print("案例1: 华东市场拓展战略")
    print("=" * 70)
    result1 = assessor.assess(decision1, outcome1)
    print(assessor.generate_report(result1, decision1, outcome1))
    
    print("\n\n")
    print("=" * 70)
    print("案例2: AI客服系统上线")
    print("=" * 70)
    result2 = assessor.assess(decision2, outcome2)
    print(assessor.generate_report(result2, decision2, outcome2))
    
    # 输出JSON格式
    print("\n\n📊 JSON格式输出:")
    json_output = {
        "assessments": [
            {
                "decision_id": result1.decision_id,
                "overall_score": result1.overall_score,
                "outcome_status": result1.outcome_status.value,
                "quality_breakdown": result1.quality_breakdown
            },
            {
                "decision_id": result2.decision_id,
                "overall_score": result2.overall_score,
                "outcome_status": result2.outcome_status.value,
                "quality_breakdown": result2.quality_breakdown
            }
        ]
    }
    print(json.dumps(json_output, ensure_ascii=False, indent=2))
    
    return [result1, result2]


if __name__ == "__main__":
    main()
