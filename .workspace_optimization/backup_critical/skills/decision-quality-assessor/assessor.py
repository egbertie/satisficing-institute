#!/usr/bin/env python3
"""
决策质量评估器 - Decision Quality Assessor

功能：评估已做决策的质量和后续结果
追踪：决策→结果→复盘→改进的完整闭环
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Decision:
    """决策记录"""
    id: str
    description: str
    decision_date: str
    expected_result: str
    actual_result: Optional[str] = None
    result_date: Optional[str] = None
    stakeholders: List[str] = None

@dataclass
class AssessmentResult:
    """评估结果"""
    decision_id: str
    quality_score: float  # 0-100
    deviation_score: float  # 偏差分数
    timeliness_score: float  # 及时性
    stakeholder_satisfaction: float  # 相关方满意度
    root_cause_analysis: str
    improvement_suggestions: List[str]
    lessons_learned: str


class DecisionQualityAssessor:
    """决策质量评估器"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.decisions_file = self.workspace / "memory" / "decisions-database.json"
        self.assessments_file = self.workspace / "memory" / "decision-assessments.jsonl"
        self.decisions = self._load_decisions()
    
    def _load_decisions(self) -> Dict:
        """加载决策数据库"""
        if self.decisions_file.exists():
            with open(self.decisions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"decisions": [], "version": "1.0.0"}
    
    def record_decision(self, decision: Decision):
        """记录新决策"""
        decision_data = {
            "id": decision.id,
            "description": decision.description,
            "decision_date": decision.decision_date,
            "expected_result": decision.expected_result,
            "actual_result": decision.actual_result,
            "result_date": decision.result_date,
            "stakeholders": decision.stakeholders or [],
            "status": "pending"  # pending/completed
        }
        
        self.decisions["decisions"].append(decision_data)
        self._save_decisions()
    
    def _save_decisions(self):
        """保存决策数据库"""
        with open(self.decisions_file, 'w', encoding='utf-8') as f:
            json.dump(self.decisions, f, ensure_ascii=False, indent=2)
    
    def assess_decision(self, decision_id: str, actual_result: str, 
                       stakeholder_feedback: Dict[str, float] = None) -> AssessmentResult:
        """
        评估决策质量
        
        Args:
            decision_id: 决策ID
            actual_result: 实际结果
            stakeholder_feedback: 相关方反馈分数
            
        Returns:
            评估结果
        """
        # 查找决策
        decision = None
        for d in self.decisions["decisions"]:
            if d["id"] == decision_id:
                decision = d
                break
        
        if not decision:
            raise ValueError(f"决策 {decision_id} 不存在")
        
        # 更新实际结果
        decision["actual_result"] = actual_result
        decision["result_date"] = datetime.now().isoformat()
        decision["status"] = "completed"
        self._save_decisions()
        
        # 计算各项分数
        deviation_score = self._calculate_deviation(
            decision["expected_result"], actual_result
        )
        timeliness_score = self._calculate_timeliness(
            decision["decision_date"], decision["result_date"]
        )
        stakeholder_satisfaction = self._calculate_satisfaction(
            stakeholder_feedback or {}
        )
        
        # 综合质量分数
        quality_score = (
            (100 - deviation_score) * 0.5 +  # 偏差越小越好
            timeliness_score * 0.3 +
            stakeholder_satisfaction * 0.2
        )
        
        # 根因分析
        root_cause = self._analyze_root_cause(
            decision["expected_result"], actual_result, deviation_score
        )
        
        # 改进建议
        suggestions = self._generate_improvements(
            deviation_score, timeliness_score, stakeholder_satisfaction
        )
        
        # 经验教训
        lessons = self._extract_lessons(
            decision, actual_result, deviation_score
        )
        
        result = AssessmentResult(
            decision_id=decision_id,
            quality_score=round(quality_score, 1),
            deviation_score=round(deviation_score, 1),
            timeliness_score=round(timeliness_score, 1),
            stakeholder_satisfaction=round(stakeholder_satisfaction, 1),
            root_cause_analysis=root_cause,
            improvement_suggestions=suggestions,
            lessons_learned=lessons
        )
        
        # 记录评估
        self._log_assessment(result)
        
        return result
    
    def _calculate_deviation(self, expected: str, actual: str) -> float:
        """计算预期与实际的偏差（简化版，实际应更复杂）"""
        # 这里使用简单的文本相似度
        # 实际应用中可能需要更复杂的评估
        if expected.lower() == actual.lower():
            return 0.0
        
        # 关键词匹配
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())
        
        if not expected_words:
            return 50.0
        
        common = expected_words.intersection(actual_words)
        similarity = len(common) / len(expected_words)
        
        return (1 - similarity) * 100
    
    def _calculate_timeliness(self, decision_date: str, result_date: str) -> float:
        """计算及时性分数"""
        try:
            decision_dt = datetime.fromisoformat(decision_date.replace('Z', '+00:00'))
            result_dt = datetime.fromisoformat(result_date.replace('Z', '+00:00'))
            
            duration_days = (result_dt - decision_dt).days
            
            if duration_days <= 1:
                return 100.0
            elif duration_days <= 7:
                return 80.0
            elif duration_days <= 30:
                return 60.0
            else:
                return 40.0
        except:
            return 50.0
    
    def _calculate_satisfaction(self, feedback: Dict[str, float]) -> float:
        """计算相关方满意度"""
        if not feedback:
            return 70.0  # 默认值
        
        return sum(feedback.values()) / len(feedback)
    
    def _analyze_root_cause(self, expected: str, actual: str, deviation: float) -> str:
        """分析根因"""
        if deviation < 20:
            return "决策执行良好，偏差在可控范围内"
        elif deviation < 50:
            return "预期与实际存在中等偏差，可能原因：1)信息不完整 2)环境变化 3)执行偏差"
        else:
            return "预期与实际存在显著偏差，建议：1)重新评估假设 2)收集更多信息 3)调整策略"
    
    def _generate_improvements(self, deviation: float, timeliness: float, 
                              satisfaction: float) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if deviation > 30:
            suggestions.append("建立更完善的信息收集机制，提高预期准确性")
        
        if timeliness < 70:
            suggestions.append("优化决策执行流程，缩短决策到结果的周期")
        
        if satisfaction < 70:
            suggestions.append("加强相关方沟通，提高决策参与度和认同感")
        
        if not suggestions:
            suggestions.append("继续保持当前决策质量，定期复盘优化")
        
        return suggestions
    
    def _extract_lessons(self, decision: Dict, actual: str, deviation: float) -> str:
        """提取经验教训"""
        if deviation < 20:
            return f"本次决策'{decision['description'][:30]}...'执行成功，可将其作为最佳实践沉淀。"
        else:
            return f"本次决策'{decision['description'][:30]}...'存在偏差，关键教训：预期与实际不完全一致，下次应加强前期调研。"
    
    def _log_assessment(self, result: AssessmentResult):
        """记录评估"""
        with open(self.assessments_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "decision_id": result.decision_id,
                "quality_score": result.quality_score,
                "deviation_score": result.deviation_score
            }, ensure_ascii=False) + "\n")
    
    def generate_assessment_report(self, result: AssessmentResult) -> str:
        """生成评估报告"""
        lines = [
            f"# 决策质量评估报告",
            "",
            f"**决策ID**: {result.decision_id}",
            f"**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 评估结果",
            "",
            f"**综合质量分数**: {result.quality_score}/100",
            f"**偏差分数**: {result.deviation_score}/100（越低越好）",
            f"**及时性分数**: {result.timeliness_score}/100",
            f"**相关方满意度**: {result.stakeholder_satisfaction}/100",
            "",
            "## 根因分析",
            "",
            f"> {result.root_cause_analysis}",
            "",
            "## 改进建议",
            ""
        ]
        
        for i, suggestion in enumerate(result.improvement_suggestions, 1):
            lines.append(f"{i}. {suggestion}")
        
        lines.extend([
            "",
            "## 经验教训",
            "",
            f"> {result.lessons_learned}",
            "",
            "---",
            "",
            "*决策→结果→复盘→改进，形成闭环*"
        ])
        
        return "\n".join(lines)


def main():
    """主函数 - 演示"""
    print("=" * 60)
    print("决策质量评估器 v1.0")
    print("=" * 60)
    
    assessor = DecisionQualityAssessor()
    
    # 记录一个示例决策
    decision = Decision(
        id="DEC-2026-001",
        description="选择3月25日作为官宣日期",
        decision_date=(datetime.now() - timedelta(days=10)).isoformat(),
        expected_result="官宣当天获得100+关注，媒体报道3+家",
        stakeholders=["Egbertie", "满意妞", "CONTENT"]
    )
    
    print(f"\n记录决策: {decision.description}")
    assessor.record_decision(decision)
    
    # 模拟评估
    print("\n评估决策结果...")
    result = assessor.assess_decision(
        decision_id="DEC-2026-001",
        actual_result="官宣当天获得150+关注，媒体报道5家",
        stakeholder_feedback={
            "Egbertie": 90.0,
            "满意妞": 85.0,
            "CONTENT": 88.0
        }
    )
    
    print(f"  质量分数: {result.quality_score}")
    print(f"  偏差分数: {result.deviation_score}")
    print(f"  改进建议: {len(result.improvement_suggestions)}条")
    
    # 生成报告
    print("\n" + "=" * 60)
    print("详细报告：")
    print("=" * 60)
    report = assessor.generate_assessment_report(result)
    print(report)


if __name__ == "__main__":
    main()
