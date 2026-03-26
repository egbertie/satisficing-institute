#!/usr/bin/env python3
"""
Optimization Prioritizer - 优化建议分级处理器
对优化建议进行P0-P3分级
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class Priority(Enum):
    P0 = "P0"  # 紧急
    P1 = "P1"  # 重要
    P2 = "P2"  # 一般
    P3 = "P3"  # 建议

@dataclass
class Suggestion:
    """优化建议"""
    id: str
    title: str
    description: str
    impact_scope: str  # system_wide, multiple_modules, single_module, minor
    is_security_issue: bool
    is_data_risk: bool
    days_overdue: int
    estimated_hours: float
    can_rollback: bool
    has_test_coverage: bool
    created_at: str
    priority: Optional[Priority] = None

class PriorityCalculator:
    """优先级计算器"""
    
    IMPACT_SCORES = {
        'system_wide': 100,
        'multiple_modules': 75,
        'single_module': 50,
        'minor': 25
    }
    
    def calculate(self, suggestion: Suggestion) -> Priority:
        """计算优先级"""
        # 基础分数计算
        impact_score = self._calc_impact(suggestion)
        urgency_score = self._calc_urgency(suggestion)
        effort_score = self._calc_effort(suggestion)
        risk_score = self._calc_risk(suggestion)
        
        # 综合评分 (0-100)
        total_score = (
            impact_score * 0.35 +
            urgency_score * 0.30 +
            effort_score * 0.20 +
            risk_score * 0.15
        )
        
        return self._score_to_priority(total_score)
    
    def _calc_impact(self, suggestion: Suggestion) -> float:
        """影响范围评分"""
        return self.IMPACT_SCORES.get(suggestion.impact_scope, 50)
    
    def _calc_urgency(self, suggestion: Suggestion) -> float:
        """紧急程度评分"""
        if suggestion.is_security_issue:
            return 100
        if suggestion.is_data_risk:
            return 95
        if suggestion.days_overdue > 7:
            return 85
        if suggestion.days_overdue > 3:
            return 70
        return 50
    
    def _calc_effort(self, suggestion: Suggestion) -> float:
        """实施成本评分（越高表示成本越低）"""
        hours = suggestion.estimated_hours
        if hours <= 1:
            return 100
        if hours <= 4:
            return 75
        if hours <= 8:
            return 50
        if hours <= 16:
            return 25
        return 10
    
    def _calc_risk(self, suggestion: Suggestion) -> float:
        """风险评估评分（越高表示风险越低）"""
        if suggestion.can_rollback:
            return 90
        if suggestion.has_test_coverage:
            return 70
        return 40
    
    def _score_to_priority(self, score: float) -> Priority:
        """分数映射到优先级"""
        if score >= 85:
            return Priority.P0
        if score >= 70:
            return Priority.P1
        if score >= 50:
            return Priority.P2
        return Priority.P3

class QueueManager:
    """队列管理器"""
    
    QUEUE_LIMITS = {
        Priority.P0: 5,
        Priority.P1: 20,
        Priority.P2: 50,
        Priority.P3: float('inf')
    }
    
    def __init__(self, queue_file: str = 'data/suggestion-queue.json'):
        self.queue_file = Path(queue_file)
        self.queue = self._load_queue()
    
    def _load_queue(self) -> Dict[Priority, List[Suggestion]]:
        """加载队列"""
        if not self.queue_file.exists():
            return {p: [] for p in Priority}
        
        with open(self.queue_file) as f:
            data = json.load(f)
        
        queue = {p: [] for p in Priority}
        for p_str, suggestions in data.items():
            p = Priority(p_str)
            queue[p] = [Suggestion(**s) for s in suggestions]
        
        return queue
    
    def _save_queue(self):
        """保存队列"""
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {}
        for p, suggestions in self.queue.items():
            data[p.value] = [asdict(s) for s in suggestions]
        
        with open(self.queue_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_suggestion(self, suggestion: Suggestion) -> Priority:
        """添加建议到队列"""
        calculator = PriorityCalculator()
        priority = calculator.calculate(suggestion)
        suggestion.priority = priority
        
        # 检查队列限制
        if len(self.queue[priority]) >= self.QUEUE_LIMITS[priority]:
            # 升级或降级
            if priority == Priority.P3:
                return None  # 丢弃
            # 尝试降级
            next_priority = self._get_next_priority(priority)
            if next_priority:
                return self.add_suggestion(suggestion)
        
        self.queue[priority].append(suggestion)
        self._save_queue()
        
        return priority
    
    def _get_next_priority(self, priority: Priority) -> Optional[Priority]:
        """获取下一优先级（降级）"""
        order = [Priority.P0, Priority.P1, Priority.P2, Priority.P3]
        idx = order.index(priority)
        if idx + 1 < len(order):
            return order[idx + 1]
        return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            'total': sum(len(q) for q in self.queue.values()),
            'by_priority': {
                p.value: {
                    'count': len(q),
                    'limit': self.QUEUE_LIMITS[p],
                    'full': len(q) >= self.QUEUE_LIMITS[p]
                }
                for p, q in self.queue.items()
            }
        }
    
    def generate_weekly_summary(self) -> str:
        """生成周报"""
        lines = [
            "# 优化建议周报",
            f"生成时间: {datetime.now().isoformat()}",
            "",
            "## 队列状态",
        ]
        
        status = self.get_queue_status()
        for p, info in status['by_priority'].items():
            lines.append(f"- **{p}**: {info['count']}/{info['limit']} {'(已满)' if info['full'] else ''}")
        
        lines.extend([
            "",
            f"**总计**: {status['total']} 个待处理建议",
        ])
        
        return "\n".join(lines)


def main():
    """命令行入口"""
    import sys
    
    manager = QueueManager()
    
    task = sys.argv[1] if len(sys.argv) > 1 else 'process-queue'
    
    if task == 'process-queue':
        status = manager.get_queue_status()
        print(f"队列处理完成。当前队列: {status['total']} 个建议")
        
    elif task == 'weekly-summary':
        report = manager.generate_weekly_summary()
        print(report)
        
    elif task == 'add-suggestion':
        # 示例：添加建议
        suggestion = Suggestion(
            id=f"SUG-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title="示例建议",
            description="这是一个示例建议",
            impact_scope='single_module',
            is_security_issue=False,
            is_data_risk=False,
            days_overdue=0,
            estimated_hours=2,
            can_rollback=True,
            has_test_coverage=True,
            created_at=datetime.now().isoformat()
        )
        priority = manager.add_suggestion(suggestion)
        print(f"建议已添加，优先级: {priority.value if priority else '已丢弃'}")
    
    else:
        print(f"未知任务: {task}")
        sys.exit(1)


if __name__ == '__main__':
    main()
