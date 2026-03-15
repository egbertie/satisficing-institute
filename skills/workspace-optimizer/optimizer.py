#!/usr/bin/env python3
"""
Workspace Optimizer - 工作空间优化器

基于审计报告执行优化操作。
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class OptimizationAction:
    """优化动作"""
    id: str
    type: str  # delete, merge, simplify, solidify
    target: str
    description: str
    risk_level: RiskLevel
    estimated_impact: str
    confirmation_required: bool = True


class WorkspaceOptimizer:
    """工作空间优化器"""
    
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.skills_path = self.workspace / "skills"
        self.docs_path = self.workspace / "docs"
        self.memory_path = self.workspace / "memory"
        self.backup_path = self.workspace / "backups"
        
        self.audit_report: Optional[Dict] = None
        self.actions: List[OptimizationAction] = []
        self.executed_actions: List[str] = []
        self.failed_actions: List[Tuple[str, str]] = []
    
    def load_audit_report(self, report_path: str) -> bool:
        """
        加载审计报告
        
        Args:
            report_path: 审计报告路径
        
        Returns:
            是否成功加载
        """
        try:
            path = Path(report_path)
            if not path.exists():
                print(f"❌ 审计报告不存在: {report_path}")
                return False
            
            if path.suffix == '.json':
                self.audit_report = json.loads(path.read_text())
            else:
                # 尝试从Markdown解析（简化版）
                print("⚠️ Markdown格式解析受限，建议提供JSON格式")
                self.audit_report = {"source": str(path)}
            
            self._generate_actions()
            print(f"✓ 已加载审计报告，生成 {len(self.actions)} 个优化动作")
            return True
            
        except Exception as e:
            print(f"❌ 加载审计报告失败: {e}")
            return False
    
    def _generate_actions(self):
        """根据审计报告生成优化动作"""
        self.actions = []
        
        if not self.audit_report:
            return
        
        # 从Skill问题生成动作
        if "skills" in self.audit_report and "issues" in self.audit_report["skills"]:
            for i, issue in enumerate(self.audit_report["skills"]["issues"]):
                if issue.get("type") == "duplication":
                    action = OptimizationAction(
                        id=f"SKILL-MERGE-{i:03d}",
                        type="merge",
                        target="skill",
                        description=issue.get("message", ""),
                        risk_level=RiskLevel.HIGH,
                        estimated_impact=issue.get("estimated_saving", ""),
                        confirmation_required=True
                    )
                    self.actions.append(action)
        
        # 从文档问题生成动作
        if "docs" in self.audit_report and "issues" in self.audit_report["docs"]:
            for i, issue in enumerate(self.audit_report["docs"]["issues"]):
                if issue.get("type") == "duplication":
                    action = OptimizationAction(
                        id=f"DOC-MERGE-{i:03d}",
                        type="merge",
                        target="doc",
                        description=issue.get("message", ""),
                        risk_level=RiskLevel.MEDIUM,
                        estimated_impact=issue.get("estimated_saving", ""),
                        confirmation_required=True
                    )
                    self.actions.append(action)
    
    def create_backup(self, label: str = "pre-optimize") -> Optional[Path]:
        """
        创建备份
        
        Args:
            label: 备份标签
        
        Returns:
            备份目录路径
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = self.backup_path / f"{label}-{timestamp}"
        
        try:
            self.backup_path.mkdir(exist_ok=True)
            
            # 备份关键目录
            for subdir in ["skills", "docs", "memory"]:
                src = self.workspace / subdir
                if src.exists():
                    dst = backup_dir / subdir
                    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            
            print(f"✓ 备份已创建: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            print(f"❌ 备份创建失败: {e}")
            return None
    
    def optimize(self, scope: str = "all", dry_run: bool = True, 
                 confirm: bool = False, auto_execute: bool = False) -> Dict:
        """
        执行优化
        
        Args:
            scope: 优化范围 (all/skill/doc/cron)
            dry_run: 是否模拟运行
            confirm: 是否每项操作前确认
            auto_execute: 是否自动执行低风险操作
        
        Returns:
            执行结果
        """
        print(f"🔧 开始优化 (范围: {scope}, 模拟: {dry_run})")
        
        if not self.actions:
            print("⚠️ 没有可执行的优化动作")
            return {"status": "no_actions"}
        
        # 筛选动作
        filtered_actions = [a for a in self.actions if scope == "all" or a.target == scope]
        
        if dry_run:
            print("\n" + "=" * 50)
            print("[DRY RUN] 模拟执行以下优化:")
            print("=" * 50)
            
            for action in filtered_actions:
                print(f"\n[{action.id}]")
                print(f"  类型: {action.type}")
                print(f"  目标: {action.target}")
                print(f"  描述: {action.description}")
                print(f"  风险: {action.risk_level.value}")
                print(f"  影响: {action.estimated_impact}")
            
            print("\n" + "=" * 50)
            print(f"共 {len(filtered_actions)} 个优化动作")
            print("使用 --execute 确认实际执行")
            return {"status": "dry_run", "actions_count": len(filtered_actions)}
        
        # 实际执行
        for action in filtered_actions:
            self._execute_action(action, confirm, auto_execute)
        
        return {
            "status": "executed",
            "executed": len(self.executed_actions),
            "failed": len(self.failed_actions)
        }
    
    def _execute_action(self, action: OptimizationAction, confirm: bool, auto_execute: bool):
        """执行单个优化动作"""
        print(f"\n[{action.id}] {action.description}")
        
        # 判断是否需要确认
        need_confirm = confirm or action.confirmation_required
        
        if need_confirm and not auto_execute:
            user_input = input(f"  确认执行? [y/N] ")
            if user_input.lower() != 'y':
                print("  ⏭️ 跳过")
                return
        
        try:
            if action.type == "delete":
                self._execute_delete(action)
            elif action.type == "merge":
                self._execute_merge(action)
            elif action.type == "simplify":
                self._execute_simplify(action)
            elif action.type == "solidify":
                self._execute_solidify(action)
            
            self.executed_actions.append(action.id)
            print(f"  ✓ 执行成功")
            
        except Exception as e:
            self.failed_actions.append((action.id, str(e)))
            print(f"  ❌ 执行失败: {e}")
    
    def _execute_delete(self, action: OptimizationAction):
        """执行删除操作"""
        # 实现删除逻辑
        pass
    
    def _execute_merge(self, action: OptimizationAction):
        """执行合并操作"""
        # 实现合并逻辑
        pass
    
    def _execute_simplify(self, action: OptimizationAction):
        """执行简化操作"""
        # 实现简化逻辑
        pass
    
    def _execute_solidify(self, action: OptimizationAction):
        """执行固化操作"""
        # 实现固化逻辑
        pass
    
    def generate_report(self) -> str:
        """生成优化执行报告"""
        lines = [
            "# 工作空间优化执行报告",
            "",
            f"**执行时间**: {datetime.now().isoformat()}",
            f"**执行动作**: {len(self.executed_actions)}",
            f"**失败动作**: {len(self.failed_actions)}",
            "",
            "## 执行成功的动作",
            ""
        ]
        
        for action_id in self.executed_actions:
            lines.append(f"- ✅ {action_id}")
        
        if self.failed_actions:
            lines.extend([
                "",
                "## 执行失败的动作",
                ""
            ])
            for action_id, error in self.failed_actions:
                lines.append(f"- ❌ {action_id}: {error}")
        
        return "\n".join(lines)
    
    def rollback(self, backup_id: str) -> bool:
        """
        回滚到指定备份
        
        Args:
            backup_id: 备份ID
        
        Returns:
            是否成功回滚
        """
        backup_dir = self.backup_path / backup_id
        
        if not backup_dir.exists():
            print(f"❌ 备份不存在: {backup_id}")
            return False
        
        try:
            # 恢复备份
            for subdir in ["skills", "docs", "memory"]:
                src = backup_dir / subdir
                dst = self.workspace / subdir
                
                if dst.exists():
                    shutil.rmtree(dst)
                
                if src.exists():
                    shutil.copytree(src, dst)
            
            print(f"✓ 已回滚到: {backup_id}")
            return True
            
        except Exception as e:
            print(f"❌ 回滚失败: {e}")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="工作空间优化器")
    parser.add_argument("--audit-report", required=True,
                       help="审计报告路径")
    parser.add_argument("--scope", default="all",
                       choices=["all", "skill", "doc", "cron"],
                       help="优化范围")
    parser.add_argument("--dry-run", action="store_true",
                       help="模拟运行")
    parser.add_argument("--backup", action="store_true",
                       help="执行前备份")
    parser.add_argument("--confirm", action="store_true",
                       help="每项操作前确认")
    parser.add_argument("--rollback",
                       help="回滚到指定备份")
    
    args = parser.parse_args()
    
    optimizer = WorkspaceOptimizer()
    
    # 回滚模式
    if args.rollback:
        optimizer.rollback(args.rollback)
        return
    
    # 加载审计报告
    if not optimizer.load_audit_report(args.audit_report):
        return
    
    # 创建备份
    if args.backup and not args.dry_run:
        backup = optimizer.create_backup()
        if not backup:
            print("❌ 备份失败，终止执行")
            return
    
    # 执行优化
    result = optimizer.optimize(
        scope=args.scope,
        dry_run=args.dry_run,
        confirm=args.confirm
    )
    
    # 生成报告
    if not args.dry_run:
        report = optimizer.generate_report()
        print("\n" + report)


if __name__ == "__main__":
    main()
