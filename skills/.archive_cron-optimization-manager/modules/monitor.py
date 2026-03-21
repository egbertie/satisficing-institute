# -*- coding: utf-8 -*-
"""监控模块"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class CronMonitor:
    """Cron监控器"""
    
    def __init__(self, manager):
        self.manager = manager
        self.log_file = manager.data_dir / "execution_log.json"
        self.stats_file = manager.data_dir / "efficiency_stats.json"
    
    def get_status(self, crons: Dict, detailed: bool = False) -> str:
        """获取状态报告"""
        lines = []
        lines.append("=" * 80)
        lines.append("Cron系统状态报告")
        lines.append("=" * 80)
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 统计概览
        total = len(crons)
        enabled = sum(1 for c in crons.values() if c.enabled)
        disabled = total - enabled
        
        tier1 = sum(1 for c in crons.values() if c.tier.value == 1)
        tier2 = sum(1 for c in crons.values() if c.tier.value == 2)
        tier3 = sum(1 for c in crons.values() if c.tier.value == 3)
        
        lines.append("【概览】")
        lines.append(f"  总计: {total} 个 Cron")
        lines.append(f"  启用: {enabled} | 禁用: {disabled}")
        lines.append(f"  Tier 1 (自动): {tier1} | Tier 2 (确认): {tier2} | Tier 3 (阻断): {tier3}")
        lines.append("")
        
        # 执行统计
        total_executions = sum(c.execution_count for c in crons.values())
        total_tokens = sum(c.token_consumption for c in crons.values())
        avg_empty_rate = sum(c.empty_rate for c in crons.values()) / total if total > 0 else 0
        
        lines.append("【执行统计】")
        lines.append(f"  总执行次数: {total_executions}")
        lines.append(f"  总Token消耗: {total_tokens:,}")
        lines.append(f"  平均空转率: {avg_empty_rate*100:.1f}%")
        lines.append("")
        
        # 待优化项
        need_optimize = []
        for cid, cron in crons.items():
            if not cron.enabled:
                continue
            issues = []
            if cron.empty_rate > 0.8:
                issues.append("高空转率")
            if cron.token_consumption > 3000:
                issues.append("高Token消耗")
            if issues:
                need_optimize.append((cron.name, issues))
        
        if need_optimize:
            lines.append("【待优化项】")
            for name, issues in need_optimize[:10]:
                lines.append(f"  - {name}: {', '.join(issues)}")
            if len(need_optimize) > 10:
                lines.append(f"  ... 还有 {len(need_optimize)-10} 项")
            lines.append("")
        
        # 详细列表
        if detailed:
            lines.append("【Cron列表】")
            lines.append("-" * 80)
            for cid, cron in sorted(crons.items()):
                status = "启用" if cron.enabled else "禁用"
                lines.append(f"{cid:<20} | Tier{cron.tier.value} | {status:<4} | {cron.name}")
                lines.append(f"  调度: {cron.schedule}")
                lines.append(f"  任务: {', '.join(cron.tasks)}")
                lines.append(f"  执行: {cron.execution_count} 次 | Token: {cron.token_consumption:,} | 空转: {cron.empty_rate*100:.0f}%")
                lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def log_execution(self, cron_id: str, success: bool, tokens_used: int, output_size: int):
        """记录执行日志"""
        log_entry = {
            'cron_id': cron_id,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'tokens_used': tokens_used,
            'output_size': output_size
        }
        
        logs = []
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        
        logs.append(log_entry)
        
        # 只保留最近90天
        cutoff = (datetime.now() - timedelta(days=90)).isoformat()
        logs = [l for l in logs if l['timestamp'] > cutoff]
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def get_efficiency_stats(self, days: int = 7) -> Dict:
        """获取效率统计"""
        if not self.log_file.exists():
            return {
                'total_executions': 0,
                'total_tokens': 0,
                'success_rate': 0,
                'avg_tokens_per_execution': 0
            }
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            try:
                logs = json.load(f)
            except:
                return {}
        
        # 过滤时间范围
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        recent_logs = [l for l in logs if l['timestamp'] > cutoff]
        
        if not recent_logs:
            return {
                'total_executions': 0,
                'total_tokens': 0,
                'success_rate': 0,
                'avg_tokens_per_execution': 0
            }
        
        total = len(recent_logs)
        success = sum(1 for l in recent_logs if l['success'])
        tokens = sum(l['tokens_used'] for l in recent_logs)
        
        return {
            'total_executions': total,
            'total_tokens': tokens,
            'success_rate': success / total if total > 0 else 0,
            'avg_tokens_per_execution': tokens / total if total > 0 else 0,
            'period_days': days
        }
    
    def check_alerts(self) -> List[Dict]:
        """检查预警"""
        alerts = []
        
        # 获取最近7天统计
        stats = self.get_efficiency_stats(7)
        
        # 检查Token超支
        daily_budget = 20000  # 假设日预算20K
        daily_avg = stats['total_tokens'] / 7 if stats['period_days'] > 0 else 0
        
        if daily_avg > daily_budget * 1.5:
            alerts.append({
                'level': 'critical',
                'type': 'token_overuse',
                'message': f'日均Token消耗 {daily_avg:.0f}，超过预算 150%',
                'suggestion': '请检查高频Cron并优化'
            })
        elif daily_avg > daily_budget:
            alerts.append({
                'level': 'warning',
                'type': 'token_high',
                'message': f'日均Token消耗 {daily_avg:.0f}，接近预算上限',
                'suggestion': '建议优化高消耗Cron'
            })
        
        # 检查失败率
        if stats['success_rate'] < 0.5:
            alerts.append({
                'level': 'critical',
                'type': 'high_failure_rate',
                'message': f'成功率仅 {stats["success_rate"]*100:.1f}%',
                'suggestion': '请检查Cron配置和依赖服务'
            })
        
        return alerts
