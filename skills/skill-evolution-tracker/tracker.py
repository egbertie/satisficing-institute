#!/usr/bin/env python3
"""
技能进化追踪器 - Skill Evolution Tracker

功能：追踪每个Skill的使用频率和效果
指标：调用次数、成功率、用户满意度、迭代次数
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SkillMetrics:
    """Skill指标"""
    skill_name: str
    call_count: int
    success_count: int
    fail_count: int
    last_used: str
    avg_duration_ms: float
    user_satisfaction: float
    iteration_count: int


class SkillEvolutionTracker:
    """技能进化追踪器"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.skills_dir = self.workspace / "skills"
        self.metrics_file = self.workspace / "memory" / "skill-metrics.json"
        self.usage_log = self.workspace / "memory" / "skill-usage-log.jsonl"
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict:
        """加载指标数据"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"skills": {}, "last_scan": None}
    
    def _save_metrics(self):
        """保存指标数据"""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, ensure_ascii=False, indent=2)
    
    def record_usage(self, skill_name: str, success: bool, 
                    duration_ms: float = 0, user_rating: float = None):
        """记录Skill使用"""
        # 记录使用日志
        usage_record = {
            "timestamp": datetime.now().isoformat(),
            "skill": skill_name,
            "success": success,
            "duration_ms": duration_ms,
            "user_rating": user_rating
        }
        
        with open(self.usage_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(usage_record, ensure_ascii=False) + "\n")
        
        # 更新指标
        if skill_name not in self.metrics["skills"]:
            self.metrics["skills"][skill_name] = {
                "call_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "last_used": None,
                "total_duration_ms": 0,
                "satisfaction_sum": 0,
                "satisfaction_count": 0,
                "iteration_count": 0
            }
        
        skill_metric = self.metrics["skills"][skill_name]
        skill_metric["call_count"] += 1
        skill_metric["last_used"] = datetime.now().isoformat()
        
        if success:
            skill_metric["success_count"] += 1
        else:
            skill_metric["fail_count"] += 1
        
        skill_metric["total_duration_ms"] += duration_ms
        
        if user_rating:
            skill_metric["satisfaction_sum"] += user_rating
            skill_metric["satisfaction_count"] += 1
        
        self._save_metrics()
    
    def scan_all_skills(self) -> List[SkillMetrics]:
        """扫描所有Skill"""
        results = []
        
        # 遍历skills目录
        if self.skills_dir.exists():
            for skill_dir in self.skills_dir.iterdir():
                if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                    skill_name = skill_dir.name
                    metrics = self._get_skill_metrics(skill_name)
                    results.append(metrics)
        
        # 更新扫描时间
        self.metrics["last_scan"] = datetime.now().isoformat()
        self._save_metrics()
        
        # 按调用次数排序
        results.sort(key=lambda x: x.call_count, reverse=True)
        
        return results
    
    def _get_skill_metrics(self, skill_name: str) -> SkillMetrics:
        """获取Skill指标"""
        data = self.metrics["skills"].get(skill_name, {})
        
        call_count = data.get("call_count", 0)
        success_count = data.get("success_count", 0)
        fail_count = data.get("fail_count", 0)
        total_duration = data.get("total_duration_ms", 0)
        
        avg_duration = total_duration / call_count if call_count > 0 else 0
        
        satisfaction_sum = data.get("satisfaction_sum", 0)
        satisfaction_count = data.get("satisfaction_count", 0)
        satisfaction = satisfaction_sum / satisfaction_count if satisfaction_count > 0 else 70.0
        
        return SkillMetrics(
            skill_name=skill_name,
            call_count=call_count,
            success_count=success_count,
            fail_count=fail_count,
            last_used=data.get("last_used"),
            avg_duration_ms=round(avg_duration, 1),
            user_satisfaction=round(satisfaction, 1),
            iteration_count=data.get("iteration_count", 0)
        )
    
    def generate_improvement_suggestions(self, metrics: SkillMetrics) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 使用频率低
        if metrics.call_count < 5:
            suggestions.append(f"使用频率较低({metrics.call_count}次)，建议检查Skill可见性或推广使用")
        
        # 成功率低
        success_rate = metrics.success_count / metrics.call_count if metrics.call_count > 0 else 0
        if success_rate < 0.8 and metrics.call_count >= 5:
            suggestions.append(f"成功率较低({success_rate*100:.0f}%)，建议检查错误日志并修复")
        
        # 用户满意度低
        if metrics.user_satisfaction < 70 and metrics.call_count >= 5:
            suggestions.append(f"用户满意度较低({metrics.user_satisfaction:.0f}分)，建议收集反馈并优化")
        
        # 执行时间长
        if metrics.avg_duration_ms > 5000:
            suggestions.append(f"平均执行时间较长({metrics.avg_duration_ms:.0f}ms)，建议性能优化")
        
        # 很久未更新
        if metrics.iteration_count == 0 and metrics.call_count > 10:
            suggestions.append("已使用多次但未迭代，建议根据使用反馈进行优化")
        
        if not suggestions:
            suggestions.append("Skill运行良好，继续保持")
        
        return suggestions
    
    def generate_evolution_report(self) -> str:
        """生成进化报告"""
        metrics_list = self.scan_all_skills()
        
        lines = [
            "# Skill进化追踪报告",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Skill总数**: {len(metrics_list)}",
            "",
            "## 使用统计TOP10",
            "",
            "| Skill名称 | 调用次数 | 成功率 | 满意度 | 建议 |",
            "|-----------|----------|--------|--------|------|"
        ]
        
        for m in metrics_list[:10]:
            success_rate = m.success_count / m.call_count * 100 if m.call_count > 0 else 0
            suggestions = self.generate_improvement_suggestions(m)
            main_suggestion = suggestions[0][:30] + "..." if len(suggestions[0]) > 30 else suggestions[0]
            
            lines.append(f"| {m.skill_name[:20]} | {m.call_count} | {success_rate:.0f}% | {m.user_satisfaction:.0f} | {main_suggestion} |")
        
        lines.extend([
            "",
            "## 需要关注的Skill",
            ""
        ])
        
        # 找出需要关注的Skill
        for m in metrics_list:
            if m.call_count >= 5:
                success_rate = m.success_count / m.call_count
                if success_rate < 0.8 or m.user_satisfaction < 70:
                    lines.append(f"- **{m.skill_name}**: 成功率{success_rate*100:.0f}%, 满意度{m.user_satisfaction:.0f}")
        
        lines.extend([
            "",
            "---",
            "",
            "*持续追踪，持续进化*"
        ])
        
        return "\n".join(lines)


def main():
    """主函数 - 演示"""
    print("=" * 60)
    print("技能进化追踪器 v1.0")
    print("=" * 60)
    
    tracker = SkillEvolutionTracker()
    
    # 模拟一些使用记录
    print("\n模拟记录使用数据...")
    tracker.record_usage("zero-idle-enforcer", success=True, duration_ms=1200, user_rating=90)
    tracker.record_usage("information-intelligence", success=True, duration_ms=2500, user_rating=85)
    tracker.record_usage("task-priority-intelligence", success=False, duration_ms=800)
    tracker.record_usage("zero-idle-enforcer", success=True, duration_ms=1100, user_rating=95)
    
    # 生成报告
    print("\n生成进化报告...")
    report = tracker.generate_evolution_report()
    print(report)


if __name__ == "__main__":
    main()
