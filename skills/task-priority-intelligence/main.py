#!/usr/bin/env python3
"""
任务优先级智能判定器 (Task Priority Intelligence)
功能：自动判定任务优先级（P0/P1/P2/P3）
算法：多因子评分（紧急度×0.4 + 重要度×0.3 + 依赖度×0.2 + 资源匹配度×0.1）
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class PriorityLevel(Enum):
    P0 = "P0"  # 最高优先级 - 必须立即处理
    P1 = "P1"  # 高优先级 - 24小时内处理
    P2 = "P2"  # 中优先级 - 本周内处理
    P3 = "P3"  # 低优先级 - 可延后处理


@dataclass
class TaskInput:
    """任务输入数据结构"""
    description: str
    deadline: Optional[str] = None  # 格式：YYYY-MM-DD HH:MM
    dependencies: List[str] = None  # 依赖的其他任务ID或描述
    resource_requirements: Dict = None  # 资源需求：{"人力": 2, "预算": 1000}
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.resource_requirements is None:
            self.resource_requirements = {}


@dataclass
class PriorityResult:
    """优先级判定结果"""
    task_id: str
    priority: PriorityLevel
    score: float
    reasoning: str
    suggested_order: int
    factors: Dict[str, float]
    estimated_duration: str
    risk_level: str


class TaskPriorityIntelligence:
    """任务优先级智能判定器"""
    
    # 权重配置
    WEIGHTS = {
        "urgency": 0.4,
        "importance": 0.3,
        "dependency": 0.2,
        "resource_match": 0.1
    }
    
    # 优先级阈值
    PRIORITY_THRESHOLDS = {
        PriorityLevel.P0: 85,
        PriorityLevel.P1: 70,
        PriorityLevel.P2: 50,
        PriorityLevel.P3: 0
    }
    
    def __init__(self, available_resources: Dict = None):
        self.available_resources = available_resources or {"人力": 10, "预算": 10000}
        self.task_counter = 0
    
    def _calculate_urgency_score(self, deadline: Optional[str]) -> float:
        """计算紧急度分数 (0-100)"""
        if not deadline:
            return 30.0  # 无截止时间默认中等紧急
        
        try:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
            now = datetime.now()
            hours_until = (deadline_dt - now).total_seconds() / 3600
            
            if hours_until <= 0:
                return 100.0  # 已逾期
            elif hours_until <= 4:
                return 95.0
            elif hours_until <= 8:
                return 85.0
            elif hours_until <= 24:
                return 75.0
            elif hours_until <= 72:
                return 60.0
            elif hours_until <= 168:  # 1周
                return 45.0
            else:
                return 30.0
        except:
            return 30.0
    
    def _calculate_importance_score(self, description: str) -> float:
        """计算重要度分数 (0-100)"""
        score = 50.0  # 基础分数
        
        # 关键词分析
        high_importance_keywords = [
            "关键", "核心", "战略", "紧急", "重要", "客户", "交付", "上线",
            "bug", "故障", "事故", "修复", "阻塞", "blocker", "critical"
        ]
        medium_importance_keywords = [
            "优化", "改进", "提升", "需求", "功能", "开发", "测试"
        ]
        low_importance_keywords = [
            "文档", "整理", "记录", "备份", "清理", "重构"
        ]
        
        desc_lower = description.lower()
        
        for kw in high_importance_keywords:
            if kw in desc_lower:
                score += 15
        for kw in medium_importance_keywords:
            if kw in desc_lower:
                score += 8
        for kw in low_importance_keywords:
            if kw in desc_lower:
                score -= 5
        
        return min(100, max(0, score))
    
    def _calculate_dependency_score(self, dependencies: List[str]) -> float:
        """计算依赖度分数 (0-100)"""
        if not dependencies:
            return 50.0  # 无依赖
        
        dep_count = len(dependencies)
        if dep_count >= 5:
            return 95.0
        elif dep_count >= 3:
            return 80.0
        elif dep_count >= 1:
            return 65.0
        return 50.0
    
    def _calculate_resource_match_score(self, requirements: Dict) -> float:
        """计算资源匹配度分数 (0-100)"""
        if not requirements:
            return 70.0  # 无特殊资源需求默认良好匹配
        
        scores = []
        for resource, needed in requirements.items():
            available = self.available_resources.get(resource, 0)
            if available == 0:
                scores.append(0)
            else:
                ratio = min(needed / available, 1.0) if needed <= available else 0.3
                scores.append(ratio * 100)
        
        return sum(scores) / len(scores) if scores else 70.0
    
    def _determine_priority(self, total_score: float) -> PriorityLevel:
        """根据总分确定优先级等级"""
        if total_score >= self.PRIORITY_THRESHOLDS[PriorityLevel.P0]:
            return PriorityLevel.P0
        elif total_score >= self.PRIORITY_THRESHOLDS[PriorityLevel.P1]:
            return PriorityLevel.P1
        elif total_score >= self.PRIORITY_THRESHOLDS[PriorityLevel.P2]:
            return PriorityLevel.P2
        return PriorityLevel.P3
    
    def _generate_reasoning(self, priority: PriorityLevel, factors: Dict, task: TaskInput) -> str:
        """生成判定理由"""
        reasons = []
        
        # 紧急度理由
        urgency = factors["urgency"]
        if urgency >= 90:
            reasons.append("已逾期或即将到期")
        elif urgency >= 75:
            reasons.append("24小时内到期")
        elif urgency >= 60:
            reasons.append("3天内到期")
        
        # 重要度理由
        importance = factors["importance"]
        if importance >= 80:
            reasons.append("涉及核心业务/关键客户")
        elif importance >= 60:
            reasons.append("对业务有显著影响")
        
        # 依赖理由
        if task.dependencies:
            reasons.append(f"阻塞{len(task.dependencies)}个下游任务")
        
        # 资源理由
        resource = factors["resource_match"]
        if resource < 50:
            reasons.append("资源缺口较大")
        
        if not reasons:
            if priority == PriorityLevel.P3:
                reasons.append("常规维护类任务，可延后")
            else:
                reasons.append("综合评估得分决定")
        
        return "；".join(reasons)
    
    def _estimate_duration(self, priority: PriorityLevel, task: TaskInput) -> str:
        """预估任务处理时长"""
        base_hours = {
            PriorityLevel.P0: "立即-4小时",
            PriorityLevel.P1: "4-24小时",
            PriorityLevel.P2: "1-3天",
            PriorityLevel.P3: "可延后至本周末"
        }
        return base_hours[priority]
    
    def _assess_risk(self, priority: PriorityLevel, factors: Dict) -> str:
        """评估风险等级"""
        if priority == PriorityLevel.P0 or factors["urgency"] >= 90:
            return "高风险"
        elif priority == PriorityLevel.P1 or factors["urgency"] >= 70:
            return "中高风险"
        elif priority == PriorityLevel.P2:
            return "中风险"
        return "低风险"
    
    def evaluate(self, task: TaskInput) -> PriorityResult:
        """评估单个任务的优先级"""
        self.task_counter += 1
        task_id = f"TASK-{datetime.now().strftime('%Y%m%d')}-{self.task_counter:04d}"
        
        # 计算各因子分数
        factors = {
            "urgency": self._calculate_urgency_score(task.deadline),
            "importance": self._calculate_importance_score(task.description),
            "dependency": self._calculate_dependency_score(task.dependencies),
            "resource_match": self._calculate_resource_match_score(task.resource_requirements)
        }
        
        # 计算加权总分
        total_score = (
            factors["urgency"] * self.WEIGHTS["urgency"] +
            factors["importance"] * self.WEIGHTS["importance"] +
            factors["dependency"] * self.WEIGHTS["dependency"] +
            factors["resource_match"] * self.WEIGHTS["resource_match"]
        )
        
        priority = self._determine_priority(total_score)
        reasoning = self._generate_reasoning(priority, factors, task)
        estimated_duration = self._estimate_duration(priority, task)
        risk_level = self._assess_risk(priority, factors)
        
        return PriorityResult(
            task_id=task_id,
            priority=priority,
            score=round(total_score, 2),
            reasoning=reasoning,
            suggested_order=int(total_score),
            factors=factors,
            estimated_duration=estimated_duration,
            risk_level=risk_level
        )
    
    def batch_evaluate(self, tasks: List[TaskInput]) -> List[PriorityResult]:
        """批量评估多个任务"""
        results = [self.evaluate(task) for task in tasks]
        # 按分数降序排序（分数越高优先级越高）
        results.sort(key=lambda x: x.score, reverse=True)
        # 更新建议执行顺序
        for i, result in enumerate(results):
            result.suggested_order = i + 1
        return results
    
    def generate_report(self, results: List[PriorityResult]) -> str:
        """生成评估报告"""
        lines = [
            "=" * 60,
            "           任务优先级智能判定报告",
            "=" * 60,
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"评估任务数: {len(results)}",
            "-" * 60
        ]
        
        # 按优先级分组统计
        priority_count = {p: 0 for p in PriorityLevel}
        for r in results:
            priority_count[r.priority] += 1
        
        lines.append("优先级分布:")
        for p in [PriorityLevel.P0, PriorityLevel.P1, PriorityLevel.P2, PriorityLevel.P3]:
            lines.append(f"  {p.value}: {priority_count[p]}个任务")
        lines.append("-" * 60)
        
        # 详细任务列表
        lines.append("\n详细任务列表（按优先级排序）:")
        for i, result in enumerate(results, 1):
            lines.append(f"\n【{i}】任务ID: {result.task_id}")
            lines.append(f"    优先级: {result.priority.value} | 综合评分: {result.score}")
            lines.append(f"    判定理由: {result.reasoning}")
            lines.append(f"    预计处理: {result.estimated_duration}")
            lines.append(f"    风险等级: {result.risk_level}")
            lines.append(f"    因子明细: 紧急度{result.factors['urgency']:.1f} | 重要度{result.factors['importance']:.1f} | 依赖度{result.factors['dependency']:.1f} | 资源匹配{result.factors['resource_match']:.1f}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


def main():
    """主函数演示"""
    print("🎯 任务优先级智能判定器 - 演示\n")
    
    # 初始化判定器
    priority_ai = TaskPriorityIntelligence(
        available_resources={"人力": 5, "预算": 50000}
    )
    
    # 创建测试任务
    test_tasks = [
        TaskInput(
            description="修复生产环境核心服务崩溃问题，影响所有用户登录",
            deadline=(datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
            dependencies=["TASK-001", "TASK-002"],
            resource_requirements={"人力": 3, "预算": 0}
        ),
        TaskInput(
            description="完成客户A的项目交付文档编写",
            deadline=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            dependencies=[],
            resource_requirements={"人力": 1, "预算": 0}
        ),
        TaskInput(
            description="优化数据库查询性能",
            deadline=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M"),
            dependencies=[],
            resource_requirements={"人力": 2, "预算": 0}
        ),
        TaskInput(
            description="整理上季度会议纪要",
            deadline=None,
            dependencies=[],
            resource_requirements={"人力": 1}
        ),
        TaskInput(
            description="战略级产品新功能开发 - 支撑下季度核心KPI",
            deadline=(datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
            dependencies=["需求评审", "技术方案", "UI设计"],
            resource_requirements={"人力": 4, "预算": 20000}
        )
    ]
    
    # 批量评估
    print("📊 开始批量评估任务...\n")
    results = priority_ai.batch_evaluate(test_tasks)
    
    # 生成并打印报告
    report = priority_ai.generate_report(results)
    print(report)
    
    # 输出JSON格式结果
    print("\n\n📋 JSON格式输出:")
    json_output = [
        {
            "task_id": r.task_id,
            "priority": r.priority.value,
            "score": r.score,
            "reasoning": r.reasoning,
            "suggested_order": r.suggested_order,
            "factors": r.factors,
            "estimated_duration": r.estimated_duration,
            "risk_level": r.risk_level
        }
        for r in results
    ]
    print(json.dumps(json_output, ensure_ascii=False, indent=2))
    
    return results


if __name__ == "__main__":
    main()
