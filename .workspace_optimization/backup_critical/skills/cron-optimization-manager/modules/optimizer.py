# -*- coding: utf-8 -*-
"""优化模块"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CronOptimizer:
    """Cron优化器"""
    
    def __init__(self, manager):
        self.manager = manager
    
    def get_suggestions(self, cron) -> List[Dict]:
        """获取优化建议"""
        suggestions = []
        
        # 空转率优化
        if cron.empty_rate > 0.8:
            suggestions.append({
                'type': 'frequency',
                'description': f"空转率 {cron.empty_rate*100:.0f}% 过高",
                'action': '降低频率或改为事件驱动',
                'expected_impact': '减少 60-80% 无效执行'
            })
        
        # Token消耗优化
        if cron.token_consumption > 3000:
            suggestions.append({
                'type': 'token',
                'description': f"Token消耗 {cron.token_consumption} 过高",
                'action': '优化执行逻辑，减少不必要操作',
                'expected_impact': '减少 30-50% Token消耗'
            })
        
        # 频率优化
        if '*/' in cron.schedule:
            try:
                import re
                match = re.search(r'\*/(\d+)', cron.schedule)
                if match:
                    interval = int(match.group(1))
                    if interval < 60:
                        suggestions.append({
                            'type': 'frequency',
                            'description': f"执行间隔仅 {interval} 分钟",
                            'action': '延长至2-4小时',
                            'expected_impact': '减少 50-75% 执行次数'
                        })
            except:
                pass
        
        # 整点优化
        if cron.schedule.startswith('0 ') or ' 0 ' in cron.schedule:
            suggestions.append({
                'type': 'timing',
                'description': '整点执行可能导致资源竞争',
                'action': '错峰执行，如改为17分、37分',
                'expected_impact': '减少资源竞争，提升稳定性'
            })
        
        # 层级优化
        if cron.tier.value == 1 and not cron.auto_execute:
            suggestions.append({
                'type': 'tier',
                'description': 'Tier 1 Cron未设置自动执行',
                'action': '根据实际风险调整层级或启用自动执行',
                'expected_impact': '提升执行效率'
            })
        
        return suggestions
    
    def apply_optimizations(self, cron, suggestions: List[Dict]) -> bool:
        """应用优化措施"""
        backup_created = self._create_backup()
        
        for suggestion in suggestions:
            if suggestion['type'] == 'frequency':
                self._optimize_frequency(cron)
            elif suggestion['type'] == 'timing':
                self._optimize_timing(cron)
            elif suggestion['type'] == 'tier':
                self._optimize_tier(cron)
        
        # 保存更改
        self.manager._save_crons()
        return True
    
    def merge_crons(self, cron_ids: List[str], new_name: str = None) -> str:
        """合并多个Cron"""
        if len(cron_ids) < 2:
            return "错误: 至少需要2个Cron才能合并"
        
        # 验证所有Cron存在
        for cid in cron_ids:
            if cid not in self.manager.crons:
                return f"错误: Cron '{cid}' 不存在"
        
        crons = [self.manager.crons[cid] for cid in cron_ids]
        
        # 生成新的Cron配置
        merged_id = f"merged_{'_'.join(cron_ids)[:30]}"
        merged_name = new_name or f"合并任务 ({', '.join([c.name for c in crons])})"
        
        # 合并任务列表
        all_tasks = []
        for c in crons:
            all_tasks.extend(c.tasks)
        
        # 去重
        merged_tasks = list(set(all_tasks))
        
        # 选择最高层级
        max_tier = max(c.tier.value for c in crons)
        
        # 创建新Cron
        from cron_manager import CronJob, CronTier, RiskLevel
        
        merged_cron = CronJob(
            id=merged_id,
            name=merged_name,
            tier=CronTier(max_tier),
            schedule=crons[0].schedule,  # 使用第一个的调度
            tasks=merged_tasks,
            risk_level=RiskLevel(max([c.risk_level.value for c in crons])),
            auto_execute=all(c.auto_execute for c in crons),
            description=f"合并自: {', '.join(cron_ids)}"
        )
        
        # 备份并禁用旧Cron
        self._create_backup()
        for cid in cron_ids:
            self.manager.crons[cid].enabled = False
        
        # 添加新Cron
        self.manager.crons[merged_id] = merged_cron
        self.manager._save_crons()
        
        return (
            f"已合并 {len(cron_ids)} 个 Cron 为 '{merged_name}'\n"
            f"新ID: {merged_id}\n"
            f"合并任务数: {len(merged_tasks)}\n"
            f"原Cron已禁用"
        )
    
    def rollback(self, timestamp: str = None) -> str:
        """回滚到指定状态"""
        backup_dir = Path("/root/.openclaw/workspace/backups/cron")
        
        if not backup_dir.exists():
            return "错误: 备份目录不存在"
        
        if timestamp:
            target = backup_dir / f"init-{timestamp}"
        else:
            # 获取最新的备份
            backups = sorted(backup_dir.glob("init-*"), reverse=True)
            if not backups:
                return "错误: 没有可用的备份"
            target = backups[0]
        
        if not target.exists():
            return f"错误: 备份 '{target}' 不存在"
        
        # 恢复配置
        config_file = target / "cron_rules.yaml"
        if config_file.exists():
            current_config = self.manager.config_dir / "cron_rules.yaml"
            shutil.copy2(config_file, current_config)
            
            # 重新加载
            self.manager.config = self.manager._load_config()
            self.manager.crons.clear()
            self.manager._load_crons()
            
            return f"已回滚到: {target.name}"
        
        return "错误: 备份文件不完整"
    
    def _create_backup(self) -> bool:
        """创建备份"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = Path(f"/root/.openclaw/workspace/backups/cron/init-{timestamp}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份配置文件
        config_file = self.manager.config_dir / "cron_rules.yaml"
        if config_file.exists():
            shutil.copy2(config_file, backup_dir / "cron_rules.yaml")
        
        # 备份执行历史
        data_dir = self.manager.data_dir
        if data_dir.exists():
            for f in data_dir.glob("*.json"):
                shutil.copy2(f, backup_dir / f.name)
        
        return True
    
    def _optimize_frequency(self, cron):
        """优化频率"""
        # 将高频改为每2-4小时
        if '*/' in cron.schedule:
            cron.schedule = cron.schedule.replace('*/15', '17 */2').replace('*/30', '17 */2')
            cron.schedule = cron.schedule.replace('0 *', '17 */2')
    
    def _optimize_timing(self, cron):
        """优化执行时间（错峰）"""
        # 将整点改为17分或37分
        if cron.schedule.startswith('0 '):
            cron.schedule = '17' + cron.schedule[1:]
        elif ' 0 ' in cron.schedule:
            cron.schedule = cron.schedule.replace(' 0 ', ' 17 ', 1)
    
    def _optimize_tier(self, cron):
        """优化层级"""
        # 根据风险自动调整
        critical_tasks = ['backup', 'security', 'monitor']
        if any(t in cron.tasks for t in critical_tasks):
            cron.tier = self.manager.__class__.__dict__['CronTier'].TIER_1
            cron.auto_execute = True
