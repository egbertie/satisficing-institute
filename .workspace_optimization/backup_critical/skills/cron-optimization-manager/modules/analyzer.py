# -*- coding: utf-8 -*-
"""分析模块"""

from typing import Dict, List, Optional
from datetime import datetime


class CronAnalyzer:
    """Cron分析器"""
    
    def __init__(self, manager):
        self.manager = manager
    
    def audit_all(self, crons: Dict, output_format: str = "table") -> str:
        """全面审计所有Cron"""
        results = []
        
        for cron_id, cron in crons.items():
            audit = self.audit_cron(cron)
            results.append(audit)
        
        # 按得分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        if output_format == "json":
            import json
            return json.dumps(results, indent=2, ensure_ascii=False)
        
        elif output_format == "markdown":
            return self._format_markdown(results)
        
        else:  # table
            return self._format_table(results)
    
    def audit_cron(self, cron) -> Dict:
        """审计单个Cron"""
        # 必要性评分 (40%)
        necessity_score = self._score_necessity(cron)
        
        # 频率合理性评分 (30%)
        frequency_score = self._score_frequency(cron)
        
        # Token效率评分 (20%)
        token_score = self._score_token_efficiency(cron)
        
        # 可控性评分 (10%)
        control_score = self._score_controllability(cron)
        
        # 综合得分
        total_score = (
            necessity_score * 0.4 +
            frequency_score * 0.3 +
            token_score * 0.2 +
            control_score * 0.1
        )
        
        # 分类
        classification = self._classify(total_score)
        
        # 建议
        suggestions = self._generate_suggestions(cron, total_score)
        
        return {
            'id': cron.id,
            'name': cron.name,
            'tier': cron.tier.value,
            'enabled': cron.enabled,
            'score': round(total_score, 2),
            'scores': {
                'necessity': round(necessity_score, 2),
                'frequency': round(frequency_score, 2),
                'token_efficiency': round(token_score, 2),
                'controllability': round(control_score, 2)
            },
            'classification': classification,
            'suggestions': suggestions,
            'metrics': {
                'execution_count': cron.execution_count,
                'token_consumption': cron.token_consumption,
                'empty_rate': round(cron.empty_rate, 2),
                'last_executed': cron.last_executed
            }
        }
    
    def _score_necessity(self, cron) -> float:
        """评估必要性 (0-10)"""
        score = 7.0  # 基础分
        
        # 根据任务类型调整
        critical_tasks = ['backup', 'security', 'monitor']
        if any(t in cron.tasks for t in critical_tasks):
            score += 2.0
        
        # 根据执行频率调整
        if cron.execution_count > 100:
            score += 0.5
        
        # 根据产出调整
        if cron.empty_rate < 0.3:
            score += 0.5
        
        return min(10.0, score)
    
    def _score_frequency(self, cron) -> float:
        """评估频率合理性 (0-10)"""
        score = 7.0
        
        # 解析频率
        schedule = cron.schedule
        
        # 高频检查扣分
        if '*/' in schedule:
            # 计算间隔
            try:
                interval = int(schedule.split('*/')[1].split()[0])
                if interval < 60:  # 小于1小时
                    score -= 3.0
                elif interval < 120:  # 小于2小时
                    score -= 1.5
            except:
                pass
        
        # 整点执行扣分（资源竞争）
        if schedule.startswith('0 ') or ' 0 ' in schedule:
            score -= 0.5
        
        return max(0.0, min(10.0, score))
    
    def _score_token_efficiency(self, cron) -> float:
        """评估Token效率 (0-10)"""
        score = 7.0
        
        # 根据消耗调整
        if cron.token_consumption > 5000:
            score -= 2.0
        elif cron.token_consumption > 2000:
            score -= 1.0
        
        # 根据空转率调整
        if cron.empty_rate > 0.8:
            score -= 2.0
        elif cron.empty_rate > 0.5:
            score -= 1.0
        
        return max(0.0, min(10.0, score))
    
    def _score_controllability(self, cron) -> float:
        """评估可控性 (0-10)"""
        score = 8.0
        
        # Tier越高，可控性越好
        if cron.tier.value == 3:
            score += 1.0
        elif cron.tier.value == 2:
            score += 0.5
        
        # 自动执行扣分
        if cron.auto_execute:
            score -= 0.5
        
        return min(10.0, score)
    
    def _classify(self, score: float) -> str:
        """根据得分分类"""
        if score >= 8.0:
            return "P0-保留"
        elif score >= 6.0:
            return "P1-优化"
        elif score >= 4.0:
            return "P2-延迟"
        else:
            return "P3-删除"
    
    def _generate_suggestions(self, cron, score: float) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        if cron.empty_rate > 0.8:
            suggestions.append("空转率过高，建议降低频率或改为事件驱动")
        
        if cron.token_consumption > 3000:
            suggestions.append("Token消耗过高，建议优化执行逻辑")
        
        if '*/' in cron.schedule:
            try:
                interval = int(cron.schedule.split('*/')[1].split()[0])
                if interval < 60:
                    suggestions.append(f"频率过高({interval}分钟)，建议延长至2小时以上")
            except:
                pass
        
        if not cron.confirmation_window and not cron.auto_execute:
            suggestions.append("建议设置确认窗口以提升可控性")
        
        return suggestions
    
    def _format_table(self, results: List[Dict]) -> str:
        """格式化为表格"""
        lines = []
        lines.append("=" * 100)
        lines.append(f"{'ID':<20} {'名称':<25} {'层级':<6} {'得分':<6} {'分类':<10} {'状态':<6}")
        lines.append("-" * 100)
        
        for r in results:
            status = "启用" if r['enabled'] else "禁用"
            lines.append(
                f"{r['id']:<20} {r['name']:<25} "
                f"Tier{r['tier']:<5} {r['score']:<6} "
                f"{r['classification']:<10} {status:<6}"
            )
        
        lines.append("=" * 100)
        lines.append(f"\n总计: {len(results)} 个 Cron")
        lines.append(f"P0-保留: {sum(1 for r in results if r['classification'] == 'P0-保留')} 个")
        lines.append(f"P1-优化: {sum(1 for r in results if r['classification'] == 'P1-优化')} 个")
        lines.append(f"P2-延迟: {sum(1 for r in results if r['classification'] == 'P2-延迟')} 个")
        lines.append(f"P3-删除: {sum(1 for r in results if r['classification'] == 'P3-删除')} 个")
        
        return "\n".join(lines)
    
    def _format_markdown(self, results: List[Dict]) -> str:
        """格式化为Markdown"""
        lines = []
        lines.append("# Cron审计报告")
        lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\n总计: {len(results)} 个 Cron\n")
        
        for r in results:
            lines.append(f"\n## {r['name']} ({r['id']})")
            lines.append(f"- **层级**: Tier {r['tier']}")
            lines.append(f"- **得分**: {r['score']}/10")
            lines.append(f"- **分类**: {r['classification']}")
            lines.append(f"- **状态**: {'启用' if r['enabled'] else '禁用'}")
            lines.append(f"\n**详细评分**:")
            lines.append(f"- 必要性: {r['scores']['necessity']}/10")
            lines.append(f"- 频率合理性: {r['scores']['frequency']}/10")
            lines.append(f"- Token效率: {r['scores']['token_efficiency']}/10")
            lines.append(f"- 可控性: {r['scores']['controllability']}/10")
            
            if r['suggestions']:
                lines.append(f"\n**优化建议**:")
                for s in r['suggestions']:
                    lines.append(f"- {s}")
        
        return "\n".join(lines)
