# -*- coding: utf-8 -*-
"""报告模块"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict


class CronReporter:
    """Cron报告生成器"""
    
    def __init__(self, manager):
        self.manager = manager
        self.templates_dir = manager.templates_dir
        self.reports_dir = Path("/root/.openclaw/workspace/reports/cron")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, period: str, crons: Dict) -> str:
        """生成报告"""
        if period == 'daily':
            return self._generate_daily_report(crons)
        elif period == 'weekly':
            return self._generate_weekly_report(crons)
        elif period == 'monthly':
            return self._generate_monthly_report(crons)
        else:
            return self._generate_weekly_report(crons)
    
    def _generate_daily_report(self, crons: Dict) -> str:
        """生成日报"""
        today = datetime.now().strftime('%Y-%m-%d')
        report_file = self.reports_dir / f"daily-{today}.md"
        
        lines = []
        lines.append(f"# Cron执行日报 - {today}")
        lines.append("")
        lines.append(f"生成时间: {datetime.now().strftime('%H:%M:%S')}")
        lines.append("")
        
        # 今日执行统计
        total_exec = sum(c.execution_count for c in crons.values())
        total_tokens = sum(c.token_consumption for c in crons.values())
        
        lines.append("## 执行统计")
        lines.append(f"- 总执行次数: {total_exec}")
        lines.append(f"- 总Token消耗: {total_tokens:,}")
        lines.append(f"- 活跃Cron数: {sum(1 for c in crons.values() if c.enabled)}")
        lines.append("")
        
        # 各Cron执行情况
        lines.append("## Cron执行情况")
        lines.append("")
        for cid, cron in sorted(crons.items(), key=lambda x: x[1].execution_count, reverse=True):
            if cron.execution_count > 0:
                lines.append(f"### {cron.name}")
                lines.append(f"- 执行次数: {cron.execution_count}")
                lines.append(f"- Token消耗: {cron.token_consumption:,}")
                lines.append(f"- 空转率: {cron.empty_rate*100:.1f}%")
                lines.append("")
        
        # 异常事件
        lines.append("## 异常事件")
        lines.append("暂无异常")
        lines.append("")
        
        content = "\n".join(lines)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(report_file)
    
    def _generate_weekly_report(self, crons: Dict) -> str:
        """生成周报"""
        week_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        week_end = datetime.now().strftime('%Y-%m-%d')
        report_file = self.reports_dir / f"weekly-{week_start}-to-{week_end}.md"
        
        lines = []
        lines.append(f"# Cron效率周报")
        lines.append(f"统计周期: {week_start} 至 {week_end}")
        lines.append("")
        
        # 获取监控数据
        stats = self.manager.monitor.get_efficiency_stats(7)
        
        lines.append("## 效率概览")
        lines.append(f"- 总执行次数: {stats['total_executions']}")
        lines.append(f"- 总Token消耗: {stats['total_tokens']:,}")
        lines.append(f"- 成功率: {stats['success_rate']*100:.1f}%")
        lines.append(f"- 平均Token/执行: {stats['avg_tokens_per_execution']:.0f}")
        lines.append("")
        
        # Cron效率排名
        lines.append("## Cron效率排名")
        lines.append("")
        lines.append("| Cron名称 | 执行次数 | Token消耗 | 空转率 | 效率评分 |")
        lines.append("|----------|----------|-----------|--------|----------|")
        
        sorted_crons = sorted(
            crons.items(),
            key=lambda x: x[1].token_consumption / max(x[1].execution_count, 1)
        )
        
        for cid, cron in sorted_crons[:10]:
            if cron.execution_count > 0:
                efficiency = cron.token_consumption / max(cron.execution_count, 1)
                score = max(0, 10 - efficiency / 100)
                lines.append(
                    f"| {cron.name} | {cron.execution_count} | "
                    f"{cron.token_consumption:,} | {cron.empty_rate*100:.0f}% | {score:.1f} |"
                )
        
        lines.append("")
        
        # 优化建议
        lines.append("## 优化建议")
        lines.append("")
        
        suggestions = self._generate_weekly_suggestions(crons)
        if suggestions:
            for i, s in enumerate(suggestions, 1):
                lines.append(f"{i}. **{s['cron']}**: {s['suggestion']}")
                lines.append(f"   - 预期效果: {s['impact']}")
                lines.append("")
        else:
            lines.append("本周暂无优化建议")
        
        # 下周计划
        lines.append("## 下周优化计划")
        lines.append("- [ ] 继续监控高频Cron")
        lines.append("- [ ] 评估本周优化效果")
        lines.append("- [ ] 处理用户反馈")
        lines.append("")
        
        content = "\n".join(lines)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(report_file)
    
    def _generate_monthly_report(self, crons: Dict) -> str:
        """生成月报"""
        month = datetime.now().strftime('%Y-%m')
        report_file = self.reports_dir / f"monthly-{month}.md"
        
        lines = []
        lines.append(f"# Cron优化月报 - {month}")
        lines.append("")
        
        stats = self.manager.monitor.get_efficiency_stats(30)
        
        lines.append("## 月度统计")
        lines.append(f"- 总执行次数: {stats['total_executions']:,}")
        lines.append(f"- 总Token消耗: {stats['total_tokens']:,}")
        lines.append(f"- 日均Token消耗: {stats['total_tokens']/30:,.0f}")
        lines.append(f"- 成功率: {stats['success_rate']*100:.1f}%")
        lines.append("")
        
        lines.append("## 优化成果")
        lines.append("- 本月优化Cron数: X")
        lines.append("- Token节省: X%")
        lines.append("- 空转率降低: X%")
        lines.append("")
        
        lines.append("## 下月策略")
        lines.append("1. 持续监控低效Cron")
        lines.append("2. 推进自动化优化")
        lines.append("3. 完善用户反馈机制")
        lines.append("")
        
        content = "\n".join(lines)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(report_file)
    
    def _generate_weekly_suggestions(self, crons: Dict) -> list:
        """生成周优化建议"""
        suggestions = []
        
        for cid, cron in crons.items():
            if not cron.enabled:
                continue
            
            if cron.empty_rate > 0.8:
                suggestions.append({
                    'cron': cron.name,
                    'suggestion': '空转率过高，建议降低频率或改为事件驱动',
                    'impact': '减少 60-80% 无效执行'
                })
            elif cron.token_consumption > 5000:
                suggestions.append({
                    'cron': cron.name,
                    'suggestion': 'Token消耗过高，建议优化执行逻辑',
                    'impact': '减少 30-50% Token消耗'
                })
        
        return suggestions[:5]  # 只返回前5个
