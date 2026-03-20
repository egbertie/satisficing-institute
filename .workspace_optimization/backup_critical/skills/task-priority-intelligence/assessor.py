#!/usr/bin/env python3
"""
任务优先级智能判定器 - Task Priority Intelligence

功能：自动判定任务优先级（P0/P1/P2/P3）
算法：多因子评分（紧急度×0.4 + 重要度×0.3 + 依赖度×0.2 + 资源匹配度×0.1）
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class TaskInput:
    """任务输入"""
    description: str
    deadline: Optional[str] = None  # ISO格式日期
    dependencies: List[str] = None
    resource_requirements: List[str] = None
    estimated_hours: Optional[float] = None

@dataclass
class PriorityResult:
    """优先级判定结果"""
    priority: str  # P0/P1/P2/P3
    score: float
    urgency_score: float
    importance_score: float
    dependency_score: float
    resource_score: float
    reasoning: str
    suggested_order: int


class TaskPriorityIntelligence:
    """任务优先级智能判定器"""
    
    # 优先级阈值
    PRIORITY_THRESHOLDS = {
        "P0": 85,  # 极高优先级
        "P1": 70,  # 高优先级
        "P2": 50,  # 中优先级
        "P3": 0    # 低优先级
    }
    
    # 权重配置（更新：增加外部依赖风险权重）
    WEIGHTS = {
        "urgency": 0.35,
        "importance": 0.25,
        "dependency": 0.2,
        "resource": 0.1,
        "external_dependency_risk": 0.1  # 新增：外部依赖风险
    }
    
    # 关键词库
    KEYWORDS = {
        "high_urgency": ["立即", "马上", "紧急", "严重", "阻塞", "故障", "崩溃", "泄露", "安全"],
        "high_importance": ["官宣", "发布", "里程碑", "客户", "签约", "收入", "战略", "核心"],
        "medium": ["优化", "改进", "完善", "补充", "更新", "维护"],
        "low": ["研究", "调研", "探索", "尝试", "可选", "未来"],
        # 新增：外部依赖相关关键词
        "external_dependency": ["等待", "依赖", "附件", "外部", "对方", "第三方", "待确认"]
    }
    
    def assess_priority(self, task: TaskInput) -> PriorityResult:
        """
        评估任务优先级
        
        Args:
            task: 任务输入
            
        Returns:
            优先级判定结果
        """
        # 计算各维度分数
        urgency_score = self._calculate_urgency(task)
        importance_score = self._calculate_importance(task)
        dependency_score = self._calculate_dependency(task)
        resource_score = self._calculate_resource_match(task)
        external_risk_score, suggested_action = self._calculate_external_dependency_risk(task)
        
        # 加权总分
        total_score = (
            urgency_score * self.WEIGHTS["urgency"] +
            importance_score * self.WEIGHTS["importance"] +
            dependency_score * self.WEIGHTS["dependency"] +
            resource_score * self.WEIGHTS["resource"] +
            external_risk_score * self.WEIGHTS["external_dependency_risk"]
        )
        
        # 外部依赖风险加分（提升优先级以触发处理）
        if external_risk_score > 30:
            total_score += 15  # 强制提升优先级
        if external_risk_score > 50:
            total_score += 10  # 严重风险，再提升
        
        total_score = min(100, total_score)
        
        # 确定优先级
        priority = self._score_to_priority(total_score)
        
        # 生成判定理由
        reasoning = self._generate_reasoning(
            task, urgency_score, importance_score, 
            dependency_score, resource_score, priority,
            external_risk_score, suggested_action
        )
        
        return PriorityResult(
            priority=priority,
            score=round(total_score, 1),
            urgency_score=round(urgency_score, 1),
            importance_score=round(importance_score, 1),
            dependency_score=round(dependency_score, 1),
            resource_score=round(resource_score, 1),
            reasoning=reasoning,
            suggested_order=self._suggest_order(priority, total_score)
        )
    
    def _calculate_urgency(self, task: TaskInput) -> float:
        """计算紧急度分数 (0-100)"""
        score = 50  # 基础分
        
        # 基于截止时间
        if task.deadline:
            try:
                deadline = datetime.fromisoformat(task.deadline.replace('Z', '+00:00'))
                now = datetime.now()
                hours_until = (deadline - now).total_seconds() / 3600
                
                if hours_until < 0:
                    score += 50  # 已逾期
                elif hours_until < 24:
                    score += 40  # 24小时内
                elif hours_until < 72:
                    score += 25  # 3天内
                elif hours_until < 168:
                    score += 10  # 1周内
            except:
                pass
        
        # 基于关键词
        desc_lower = task.description.lower()
        for keyword in self.KEYWORDS["high_urgency"]:
            if keyword in desc_lower:
                score += 15
                break
        
        return min(100, score)
    
    def _calculate_importance(self, task: TaskInput) -> float:
        """计算重要度分数 (0-100)"""
        score = 50  # 基础分
        
        desc_lower = task.description.lower()
        
        # 高重要性关键词
        for keyword in self.KEYWORDS["high_importance"]:
            if keyword in desc_lower:
                score += 30
                break
        
        # 中重要性关键词
        for keyword in self.KEYWORDS["medium"]:
            if keyword in desc_lower:
                score += 10
                break
        
        # 低重要性关键词
        for keyword in self.KEYWORDS["low"]:
            if keyword in desc_lower:
                score -= 15
                break
        
        return max(0, min(100, score))
    
    def _calculate_dependency(self, task: TaskInput) -> float:
        """计算依赖度分数 (0-100)"""
        score = 50  # 基础分
        
        if task.dependencies:
            dep_count = len(task.dependencies)
            if dep_count >= 5:
                score += 40
            elif dep_count >= 3:
                score += 25
            elif dep_count >= 1:
                score += 10
        
        return min(100, score)
    
    def _calculate_resource_match(self, task: TaskInput) -> float:
        """计算资源匹配度分数 (0-100)"""
        score = 70  # 基础分（默认匹配）
        
        # 如果任务需要大量资源，分数降低（表示需要更多协调）
        if task.estimated_hours:
            if task.estimated_hours > 40:
                score -= 20
            elif task.estimated_hours > 20:
                score -= 10
            elif task.estimated_hours < 4:
                score += 10  # 小任务容易执行
        
        return max(0, min(100, score))
    
    def _calculate_external_dependency_risk(self, task: TaskInput) -> tuple[float, str]:
        """
        计算外部依赖风险分数 (0-100) 和建议动作
        
        返回: (分数, 建议动作)
        分数越高表示风险越大，需要提升优先级处理
        """
        score = 0  # 基础分（无风险）
        action = "正常推进"
        
        desc_lower = task.description.lower()
        
        # 检测外部依赖关键词
        has_external_dep = any(
            keyword in desc_lower 
            for keyword in self.KEYWORDS["external_dependency"]
        )
        
        if has_external_dep:
            # 第一性原则：内部优先，外部补充
            
            # 规则1：检测"等待附件"类描述
            if "等待" in desc_lower and ("附件" in desc_lower or "下载" in desc_lower):
                score += 40  # 高风险：被动等待
                action = "立即评估内部替代方案（70%规则）"
            
            # 规则2：检测"外部输入"类描述  
            if "外部" in desc_lower or "第三方" in desc_lower:
                score += 30
                action = "启动内部版本，标记'待优化'"
            
            # 规则3：检测"待确认"类描述
            if "待确认" in desc_lower or "待核实" in desc_lower:
                score += 25
                action = "72小时内无反馈则切换内部方案"
        
        # 返回风险分数和建议动作
        return min(100, score), action
    
    def _score_to_priority(self, score: float) -> str:
        """分数转换为优先级"""
        if score >= self.PRIORITY_THRESHOLDS["P0"]:
            return "P0"
        elif score >= self.PRIORITY_THRESHOLDS["P1"]:
            return "P1"
        elif score >= self.PRIORITY_THRESHOLDS["P2"]:
            return "P2"
        else:
            return "P3"
    
    def _generate_reasoning(self, task: TaskInput, urgency: float, 
                           importance: float, dependency: float, 
                           resource: float, priority: str,
                           external_risk: float = 0, action: str = "") -> str:
        """生成判定理由"""
        reasons = []
        
        if urgency >= 70:
            reasons.append(f"紧急度高({urgency:.0f})")
        if importance >= 70:
            reasons.append(f"重要度高({importance:.0f})")
        if dependency >= 70:
            reasons.append(f"依赖度高({dependency:.0f})")
        if resource < 60:
            reasons.append(f"资源需求大({resource:.0f})")
        
        # 新增：外部依赖风险说明
        if external_risk > 30:
            reasons.append(f"⚠️ 外部依赖风险({external_risk:.0f})-{action}")
        
        if not reasons:
            reasons.append("常规任务")
        
        return f"判定为{priority}级：{', '.join(reasons)}"
    
    def _suggest_order(self, priority: str, score: float) -> int:
        """建议执行顺序（数字越小越优先）"""
        priority_order = {"P0": 0, "P1": 100, "P2": 200, "P3": 300}
        base = priority_order.get(priority, 300)
        # 同优先级内按分数排序
        offset = int(100 - score)
        return base + offset
    
    def batch_assess(self, tasks: List[TaskInput]) -> List[PriorityResult]:
        """批量评估多个任务"""
        results = []
        for task in tasks:
            result = self.assess_priority(task)
            results.append(result)
        
        # 按建议顺序排序
        results.sort(key=lambda x: x.suggested_order)
        return results
    
    def generate_report(self, task: TaskInput, result: PriorityResult) -> str:
        """生成优先级判定报告"""
        lines = [
            "# 任务优先级判定报告",
            "",
            f"**任务描述**: {task.description}",
            f"**截止时间**: {task.deadline or '未设定'}",
            f"**预估工时**: {task.estimated_hours or '未设定'}小时",
            "",
            "## 判定结果",
            "",
            f"**优先级**: {result.priority}",
            f"**综合分数**: {result.score}/100",
            f"**建议执行顺序**: 第{result.suggested_order}位",
            "",
            "## 维度分析",
            "",
            "| 维度 | 权重 | 分数 | 说明 |",
            "|------|------|------|------|",
            f"| 紧急度 | 35% | {result.urgency_score} | 基于截止时间和关键词 |",
            f"| 重要度 | 25% | {result.importance_score} | 基于任务性质 |",
            f"| 依赖度 | 20% | {result.dependency_score} | 基于依赖任务数量 |",
            f"| 资源匹配 | 10% | {result.resource_score} | 基于资源需求 |",
            f"| 外部依赖风险 | 10% | {result.external_risk_score if hasattr(result, 'external_risk_score') else 'N/A'} | 基于第一性原则评估 |",
            "",
            "## 判定理由",
            "",
            f"> {result.reasoning}",
            "",
            "---",
            "",
            "*算法：紧急度×0.35 + 重要度×0.25 + 依赖度×0.2 + 资源匹配度×0.1 + 外部依赖风险×0.1*",
            "",
            "**第一性原则**：外部依赖任务优先评估内部可完成度，70%可完成则立即启动，72小时无输入强制切换。"
        ]
        ]
        
        return "\n".join(lines)


def main():
    """主函数 - 演示"""
    print("=" * 60)
    print("任务优先级智能判定器 v1.0")
    print("=" * 60)
    
    # 创建判定器
    assessor = TaskPriorityIntelligence()
    
    # 示例任务
    tasks = [
        TaskInput(
            description="修复生产环境安全漏洞",
            deadline=(datetime.now() + timedelta(hours=4)).isoformat(),
            estimated_hours=2
        ),
        TaskInput(
            description="准备3月25日官宣文案",
            deadline="2026-03-25T09:00:00",
            estimated_hours=8,
            dependencies=["品牌设计", "产品定位"]
        ),
        TaskInput(
            description="研究行业竞品最新动态",
            estimated_hours=4
        ),
        TaskInput(
            description="优化内部文档格式",
            estimated_hours=1
        )
    ]
    
    # 批量评估
    print("\n开始评估...\n")
    results = assessor.batch_assess(tasks)
    
    # 显示结果
    for i, (task, result) in enumerate(zip(tasks, results), 1):
        print(f"\n【任务{i}】{task.description[:30]}...")
        print(f"  优先级: {result.priority} | 分数: {result.score} | 排序: {result.suggested_order}")
        print(f"  理由: {result.reasoning}")
    
    # 生成详细报告（第一个任务）
    print("\n" + "=" * 60)
    print("详细报告示例：")
    print("=" * 60)
    report = assessor.generate_report(tasks[0], results[0])
    print(report)


if __name__ == "__main__":
    main()
