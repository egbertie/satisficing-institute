# -*- coding: utf-8 -*-
"""层级管理模块"""

from typing import Dict


class TierManager:
    """Cron层级管理器"""
    
    def __init__(self, manager):
        self.manager = manager
    
    def set_tier(self, cron_id: str, tier: int) -> str:
        """设置Cron层级"""
        if cron_id not in self.manager.crons:
            return f"错误: Cron '{cron_id}' 不存在"
        
        cron = self.manager.crons[cron_id]
        old_tier = cron.tier.value
        
        from cron_manager import CronTier, RiskLevel
        
        # 更新层级
        cron.tier = CronTier(tier)
        
        # 根据层级自动调整其他属性
        if tier == 1:
            # Tier 1: 自动执行，低风险
            cron.auto_execute = True
            cron.confirmation_window = None
            if cron.risk_level == RiskLevel.HIGH:
                cron.risk_level = RiskLevel.MEDIUM
        
        elif tier == 2:
            # Tier 2: 确认窗口，中风险
            cron.auto_execute = False
            cron.confirmation_window = 15  # 默认15分钟
            if cron.risk_level == RiskLevel.HIGH:
                cron.risk_level = RiskLevel.MEDIUM
        
        elif tier == 3:
            # Tier 3: 强制阻断，高风险
            cron.auto_execute = False
            cron.confirmation_window = None
            cron.risk_level = RiskLevel.HIGH
        
        # 保存更改
        self.manager._save_crons()
        
        tier_names = {
            1: "自动执行（Tier 1）",
            2: "确认窗口（Tier 2）",
            3: "强制阻断（Tier 3）"
        }
        
        return (
            f"已更新 Cron '{cron.name}' 的层级:\n"
            f"  Tier {old_tier} -> Tier {tier} ({tier_names[tier]})\n"
            f"  自动执行: {cron.auto_execute}\n"
            f"  确认窗口: {cron.confirmation_window or '无'} 分钟\n"
            f"  风险等级: {cron.risk_level.value}"
        )
    
    def list_tiers(self) -> str:
        """列出层级分布"""
        crons = self.manager.crons
        
        tier1 = []
        tier2 = []
        tier3 = []
        
        for cid, cron in crons.items():
            info = f"  - {cron.name} ({cid})"
            if cron.tier.value == 1:
                tier1.append(info)
            elif cron.tier.value == 2:
                tier2.append(info)
            elif cron.tier.value == 3:
                tier3.append(info)
        
        lines = []
        lines.append("=" * 60)
        lines.append("Cron层级分布")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append("【Tier 1 - 自动执行】")
        lines.append(f"低风险Cron，共 {len(tier1)} 个")
        if tier1:
            lines.extend(tier1)
        lines.append("")
        
        lines.append("【Tier 2 - 确认窗口】")
        lines.append(f"中风险Cron，共 {len(tier2)} 个")
        if tier2:
            lines.extend(tier2)
        lines.append("")
        
        lines.append("【Tier 3 - 强制阻断】")
        lines.append(f"高风险Cron，共 {len(tier3)} 个")
        if tier3:
            lines.extend(tier3)
        lines.append("")
        
        lines.append("=" * 60)
        lines.append(f"总计: {len(crons)} 个 Cron")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def get_tier_description(self, tier: int) -> Dict:
        """获取层级描述"""
        descriptions = {
            1: {
                'name': '自动执行',
                'description': '低风险任务，系统自动执行',
                'features': [
                    '无需用户确认',
                    '失败后自动通知',
                    '适合维护类任务'
                ],
                'examples': ['备份检查', '日志归档', '磁盘监控']
            },
            2: {
                'name': '确认窗口',
                'description': '中风险任务，提供确认窗口',
                'features': [
                    '执行前提醒用户',
                    '可设置默认行为',
                    '无响应则按默认执行'
                ],
                'examples': ['报告生成', '数据同步', '价值复盘']
            },
            3: {
                'name': '强制阻断',
                'description': '高风险任务，必须手动确认',
                'features': [
                    '必须用户确认',
                    '绝不自动执行',
                    '适合敏感操作'
                ],
                'examples': ['外部发送', '费用操作', 'Skill安装']
            }
        }
        
        return descriptions.get(tier, {})
