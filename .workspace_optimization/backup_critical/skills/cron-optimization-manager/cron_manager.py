#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cron管理器主模块
提供Cron优化管理的统一入口
"""

import os
import sys
import json
import yaml
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.analyzer import CronAnalyzer
from modules.optimizer import CronOptimizer
from modules.monitor import CronMonitor
from modules.reporter import CronReporter
from modules.tier_manager import TierManager


class CronTier(Enum):
    """Cron层级"""
    TIER_1 = 1  # 自动执行
    TIER_2 = 2  # 确认窗口
    TIER_3 = 3  # 强制阻断


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class CronJob:
    """Cron任务定义"""
    id: str
    name: str
    tier: CronTier
    schedule: str
    tasks: List[str]
    risk_level: RiskLevel
    auto_execute: bool
    confirmation_window: Optional[int] = None  # 分钟
    enabled: bool = True
    description: str = ""
    created_at: str = ""
    last_executed: Optional[str] = None
    execution_count: int = 0
    token_consumption: int = 0
    empty_rate: float = 0.0


class CronManager:
    """Cron管理器主类"""
    
    def __init__(self, config_dir: str = None):
        """初始化管理器"""
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = Path(config_dir) if config_dir else self.base_dir / "config"
        self.data_dir = self.base_dir / "data"
        self.templates_dir = self.base_dir / "templates"
        
        # 确保目录存在
        self.data_dir.mkdir(exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        self.crons: Dict[str, CronJob] = {}
        
        # 初始化子模块
        self.analyzer = CronAnalyzer(self)
        self.optimizer = CronOptimizer(self)
        self.monitor = CronMonitor(self)
        self.reporter = CronReporter(self)
        self.tier_manager = TierManager(self)
        
        # 加载Cron定义
        self._load_crons()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_file = self.config_dir / "cron_rules.yaml"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _load_crons(self):
        """加载Cron定义"""
        crons_config = self.config.get('crons', [])
        for cron_config in crons_config:
            cron = CronJob(
                id=cron_config.get('id', ''),
                name=cron_config.get('name', ''),
                tier=CronTier(cron_config.get('tier', 1)),
                schedule=cron_config.get('schedule', ''),
                tasks=cron_config.get('tasks', []),
                risk_level=RiskLevel(cron_config.get('risk_level', 'low')),
                auto_execute=cron_config.get('auto_execute', False),
                confirmation_window=cron_config.get('confirmation_window'),
                enabled=cron_config.get('enabled', True),
                description=cron_config.get('description', ''),
                created_at=cron_config.get('created_at', datetime.now().isoformat()),
                last_executed=cron_config.get('last_executed'),
                execution_count=cron_config.get('execution_count', 0),
                token_consumption=cron_config.get('token_consumption', 0),
                empty_rate=cron_config.get('empty_rate', 0.0)
            )
            self.crons[cron.id] = cron
    
    def audit_all(self, output_format: str = "table") -> str:
        """
        全面审计所有Cron
        
        Args:
            output_format: 输出格式 (table|json|markdown)
        
        Returns:
            审计报告
        """
        return self.analyzer.audit_all(self.crons, output_format)
    
    def audit_one(self, cron_id: str) -> Optional[Dict]:
        """
        审计单个Cron
        
        Args:
            cron_id: Cron ID
        
        Returns:
            审计结果
        """
        if cron_id not in self.crons:
            return None
        return self.analyzer.audit_cron(self.crons[cron_id])
    
    def optimize(self, cron_id: str, auto: bool = False) -> str:
        """
        优化指定Cron
        
        Args:
            cron_id: Cron ID
            auto: 是否自动执行
        
        Returns:
            优化结果
        """
        if cron_id not in self.crons:
            return f"错误: Cron '{cron_id}' 不存在"
        
        cron = self.crons[cron_id]
        suggestions = self.optimizer.get_suggestions(cron)
        
        if not suggestions:
            return f"Cron '{cron.name}' 无需优化"
        
        if auto and cron.tier == CronTier.TIER_1:
            # Tier 1自动执行
            result = self.optimizer.apply_optimizations(cron, suggestions)
            return f"已自动优化 Cron '{cron.name}':\n" + "\n".join([f"  - {s['action']}" for s in suggestions])
        else:
            # 生成建议报告
            report = f"优化建议 for '{cron.name}':\n"
            for i, s in enumerate(suggestions, 1):
                report += f"\n{i}. {s['description']}"
                report += f"\n   措施: {s['action']}"
                report += f"\n   预期效果: {s['expected_impact']}"
            report += f"\n\n使用 --auto 自动应用优化（仅限Tier 1）"
            return report
    
    def merge(self, cron_ids: List[str], new_name: str = None) -> str:
        """
        合并多个Cron
        
        Args:
            cron_ids: Cron ID列表
            new_name: 新Cron名称
        
        Returns:
            合并结果
        """
        return self.optimizer.merge_crons(cron_ids, new_name)
    
    def set_tier(self, cron_id: str, tier: int) -> str:
        """
        设置Cron层级
        
        Args:
            cron_id: Cron ID
            tier: 层级 (1|2|3)
        
        Returns:
            设置结果
        """
        return self.tier_manager.set_tier(cron_id, tier)
    
    def list_tiers(self) -> str:
        """
        列出层级分布
        
        Returns:
            层级分布报告
        """
        return self.tier_manager.list_tiers()
    
    def generate_report(self, period: str) -> str:
        """
        生成报告
        
        Args:
            period: 报告周期 (daily|weekly|monthly)
        
        Returns:
            报告路径
        """
        return self.reporter.generate_report(period, self.crons)
    
    def get_status(self, detailed: bool = False) -> str:
        """
        获取状态
        
        Args:
            detailed: 是否详细
        
        Returns:
            状态报告
        """
        return self.monitor.get_status(self.crons, detailed)
    
    def enable(self, cron_id: str) -> str:
        """
        启用Cron
        
        Args:
            cron_id: Cron ID
        
        Returns:
            操作结果
        """
        if cron_id not in self.crons:
            return f"错误: Cron '{cron_id}' 不存在"
        
        self.crons[cron_id].enabled = True
        self._save_crons()
        return f"已启用 Cron '{self.crons[cron_id].name}'"
    
    def disable(self, cron_id: str, reason: str = None) -> str:
        """
        禁用Cron
        
        Args:
            cron_id: Cron ID
            reason: 禁用原因
        
        Returns:
            操作结果
        """
        if cron_id not in self.crons:
            return f"错误: Cron '{cron_id}' 不存在"
        
        self.crons[cron_id].enabled = False
        self._save_crons()
        
        msg = f"已禁用 Cron '{self.crons[cron_id].name}'"
        if reason:
            msg += f"\n原因: {reason}"
        return msg
    
    def list_rollback_points(self) -> str:
        """
        列出回滚点
        
        Returns:
            回滚点列表
        """
        backup_dir = Path("/root/.openclaw/workspace/backups/cron")
        if not backup_dir.exists():
            return "暂无回滚点"
        
        points = sorted(backup_dir.glob("init-*"), reverse=True)
        if not points:
            return "暂无回滚点"
        
        result = "可用回滚点:\n"
        for i, p in enumerate(points[:10], 1):
            result += f"{i}. {p.name}\n"
        return result
    
    def rollback(self, timestamp: str = None) -> str:
        """
        回滚到指定状态
        
        Args:
            timestamp: 时间点
        
        Returns:
            回滚结果
        """
        return self.optimizer.rollback(timestamp)
    
    def auto_optimize(self) -> str:
        """
        自动优化所有可优化的Cron
        
        Returns:
            优化结果
        """
        results = []
        for cron_id, cron in self.crons.items():
            if cron.tier == CronTier.TIER_1 and cron.enabled:
                suggestions = self.optimizer.get_suggestions(cron)
                if suggestions:
                    result = self.optimizer.apply_optimizations(cron, suggestions)
                    results.append(f"{cron.name}: 应用了 {len(suggestions)} 项优化")
        
        if not results:
            return "没有需要自动优化的Cron"
        
        return "自动优化完成:\n" + "\n".join(results)
    
    def _save_crons(self):
        """保存Cron配置"""
        config = {
            'crons': [
                {
                    'id': c.id,
                    'name': c.name,
                    'tier': c.tier.value,
                    'schedule': c.schedule,
                    'tasks': c.tasks,
                    'risk_level': c.risk_level.value,
                    'auto_execute': c.auto_execute,
                    'confirmation_window': c.confirmation_window,
                    'enabled': c.enabled,
                    'description': c.description,
                    'created_at': c.created_at,
                    'last_executed': c.last_executed,
                    'execution_count': c.execution_count,
                    'token_consumption': c.token_consumption,
                    'empty_rate': c.empty_rate
                }
                for c in self.crons.values()
            ]
        }
        
        config_file = self.config_dir / "cron_rules.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False)


def main():
    """CLI入口"""
    parser = argparse.ArgumentParser(description='Cron优化管理器')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # audit命令
    audit_parser = subparsers.add_parser('audit', help='审计Cron')
    audit_parser.add_argument('--all', action='store_true', help='审计所有Cron')
    audit_parser.add_argument('--id', help='指定Cron ID')
    audit_parser.add_argument('--output', default='table', choices=['table', 'json', 'markdown'])
    
    # optimize命令
    optimize_parser = subparsers.add_parser('optimize', help='优化Cron')
    optimize_parser.add_argument('--id', required=True, help='Cron ID')
    optimize_parser.add_argument('--auto', action='store_true', help='自动执行')
    
    # merge命令
    merge_parser = subparsers.add_parser('merge', help='合并Cron')
    merge_parser.add_argument('--ids', required=True, help='逗号分隔的Cron ID')
    merge_parser.add_argument('--name', help='新Cron名称')
    
    # tier命令
    tier_parser = subparsers.add_parser('tier', help='层级管理')
    tier_parser.add_argument('--list', action='store_true', help='列出层级')
    tier_parser.add_argument('--set', help='设置Cron ID')
    tier_parser.add_argument('--tier', type=int, choices=[1, 2, 3], help='层级')
    
    # report命令
    report_parser = subparsers.add_parser('report', help='生成报告')
    report_parser.add_argument('--daily', action='store_true', help='日报')
    report_parser.add_argument('--weekly', action='store_true', help='周报')
    report_parser.add_argument('--monthly', action='store_true', help='月报')
    
    # status命令
    status_parser = subparsers.add_parser('status', help='查看状态')
    status_parser.add_argument('--detailed', action='store_true', help='详细')
    
    # enable/disable命令
    enable_parser = subparsers.add_parser('enable', help='启用Cron')
    enable_parser.add_argument('id', help='Cron ID')
    
    disable_parser = subparsers.add_parser('disable', help='禁用Cron')
    disable_parser.add_argument('id', help='Cron ID')
    disable_parser.add_argument('--reason', help='禁用原因')
    
    # rollback命令
    rollback_parser = subparsers.add_parser('rollback', help='回滚')
    rollback_parser.add_argument('--list', action='store_true', help='列出回滚点')
    rollback_parser.add_argument('--to', help='回滚到指定时间')
    
    # auto-optimize命令
    subparsers.add_parser('auto-optimize', help='自动优化')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = CronManager()
    
    if args.command == 'audit':
        if args.id:
            result = manager.audit_one(args.id)
            print(json.dumps(result, indent=2, ensure_ascii=False) if result else "Cron不存在")
        else:
            print(manager.audit_all(args.output))
    
    elif args.command == 'optimize':
        print(manager.optimize(args.id, args.auto))
    
    elif args.command == 'merge':
        ids = args.ids.split(',')
        print(manager.merge(ids, args.name))
    
    elif args.command == 'tier':
        if args.list:
            print(manager.list_tiers())
        elif args.set and args.tier:
            print(manager.set_tier(args.set, args.tier))
        else:
            tier_parser.print_help()
    
    elif args.command == 'report':
        if args.daily:
            print(manager.generate_report('daily'))
        elif args.weekly:
            print(manager.generate_report('weekly'))
        elif args.monthly:
            print(manager.generate_report('monthly'))
        else:
            print(manager.generate_report('weekly'))
    
    elif args.command == 'status':
        print(manager.get_status(args.detailed))
    
    elif args.command == 'enable':
        print(manager.enable(args.id))
    
    elif args.command == 'disable':
        print(manager.disable(args.id, args.reason))
    
    elif args.command == 'rollback':
        if args.list:
            print(manager.list_rollback_points())
        elif args.to:
            print(manager.rollback(args.to))
        else:
            rollback_parser.print_help()
    
    elif args.command == 'auto-optimize':
        print(manager.auto_optimize())


if __name__ == '__main__':
    main()
