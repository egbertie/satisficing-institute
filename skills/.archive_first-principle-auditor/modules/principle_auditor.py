#!/usr/bin/env python3
"""
First Principle Auditor - 第一性原则审计器
审计工作是否符合六大第一性原理
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class FirstPrincipleAuditor:
    """第一性原则审计器"""
    
    PRINCIPLES = {
        'system_first': {
            'name': '系统层优先',
            'description': '新增能力必须嵌入系统',
            'checks': [
                '是否注册到skill-registry.json',
                '是否有系统级文档',
                '是否游离于现有系统'
            ]
        },
        'evaluation_first': {
            'name': '评测先行',
            'description': '新增工作项必须有评测指标',
            'checks': [
                '是否有评测指标',
                '是否有质量评分',
                '数据是否被记录'
            ]
        },
        'feedback_loop': {
            'name': '反馈飞轮',
            'description': '任务必须走完完整闭环',
            'checks': [
                '是否记录到经验池',
                '失败是否记录到失败库',
                '闭环是否完整'
            ]
        },
        'explicit_process': {
            'name': '流程显式',
            'description': '流程必须有SOP文档',
            'checks': [
                '是否有SOP文档',
                '是否有检查清单',
                '流程是否可复现'
            ]
        },
        'negative_samples': {
            'name': '负样宝贵',
            'description': '失败必须记录入库',
            'checks': [
                '本周是否有失败记录',
                '失败是否有根因分析',
                '失败记录是否完整'
            ]
        },
        'embedded_governance': {
            'name': '治理嵌入',
            'description': '关键变更必须有日志审计',
            'checks': [
                '关键变更是否有日志',
                '是否有审计记录',
                '是否可追溯'
            ]
        }
    }
    
    def __init__(self, workspace_path: str = '/root/.openclaw/workspace'):
        self.workspace = Path(workspace_path)
        self.results = {}
    
    def audit(self, period: str = 'weekly') -> Dict[str, Any]:
        """执行原则审计"""
        for principle_id, principle in self.PRINCIPLES.items():
            self.results[principle_id] = self._audit_principle(principle_id, principle)
        
        overall_compliance = self._calculate_overall_compliance()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'period': period,
            'results': self.results,
            'overall_compliance': overall_compliance,
            'violations': self._collect_violations(),
            'trends': self._analyze_trends(),
            'recommendations': self._generate_recommendations()
        }
    
    def _audit_principle(self, principle_id: str, principle: Dict) -> Dict[str, Any]:
        """审计单个原则"""
        # 简化实现，实际应检查具体工作项
        checks_passed = 0
        total_checks = len(principle['checks'])
        violations = []
        
        # 这里应根据实际情况检查
        # 示例：系统层优先检查
        if principle_id == 'system_first':
            skill_registry = self.workspace / 'skill.json'
            if skill_registry.exists():
                checks_passed = 2  # 假设通过2项
            else:
                violations.append('skill-registry.json不存在')
        
        compliance_rate = (checks_passed / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'name': principle['name'],
            'description': principle['description'],
            'compliance_rate': round(compliance_rate, 1),
            'checks_passed': checks_passed,
            'total_checks': total_checks,
            'violations': violations,
            'status': self._get_status(compliance_rate)
        }
    
    def _calculate_overall_compliance(self) -> float:
        """计算总体合规率"""
        if not self.results:
            return 0.0
        
        total = sum(r['compliance_rate'] for r in self.results.values())
        return round(total / len(self.results), 1)
    
    def _collect_violations(self) -> List[Dict[str, Any]]:
        """收集所有违规项"""
        violations = []
        for principle_id, result in self.results.items():
            for violation in result.get('violations', []):
                violations.append({
                    'principle': result['name'],
                    'violation': violation
                })
        return violations
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """分析趋势（与上周对比）"""
        # 实际应读取历史数据
        return {
            'compared_to_last_week': '持平',
            'improved_principles': [],
            'declined_principles': []
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        for principle_id, result in self.results.items():
            if result['compliance_rate'] < 80:
                recommendations.append(
                    f"改进{result['name']}: 当前合规率{result['compliance_rate']}%"
                )
        
        return recommendations
    
    def _get_status(self, rate: float) -> str:
        """根据合规率获取状态"""
        if rate >= 90:
            return 'excellent'
        elif rate >= 80:
            return 'good'
        elif rate >= 70:
            return 'fair'
        elif rate >= 60:
            return 'poor'
        else:
            return 'critical'
    
    def generate_report(self, result: Dict[str, Any]) -> str:
        """生成审计报告"""
        lines = [
            "# 第一性原则审计报告",
            f"审计周期: {result['period']}",
            f"生成时间: {result['timestamp']}",
            "",
            f"## 总体合规率: {result['overall_compliance']}%",
            "",
            "## 各原则合规率",
            "| 原则 | 合规率 | 状态 |",
            "|------|--------|------|",
        ]
        
        for principle_id, r in result['results'].items():
            status_emoji = {
                'excellent': '🟢', 'good': '🟢', 'fair': '🟡',
                'poor': '🟠', 'critical': '🔴'
            }.get(r['status'], '⚪')
            lines.append(f"| {r['name']} | {r['compliance_rate']}% | {status_emoji} |")
        
        lines.extend([
            "",
            "## 违规项",
        ])
        
        for v in result['violations']:
            lines.append(f"- [{v['principle']}] {v['violation']}")
        
        return "\n".join(lines)


def main():
    """命令行入口"""
    import sys
    
    auditor = FirstPrincipleAuditor()
    
    task = 'weekly-audit'
    if len(sys.argv) > 1:
        task = sys.argv[1]
    
    if task == 'weekly-audit':
        result = auditor.audit('weekly')
    else:
        print(f"未知任务: {task}")
        sys.exit(1)
    
    report = auditor.generate_report(result)
    print(report)
    
    # 保存结果
    output_dir = Path('/root/.openclaw/workspace/reports/audit')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = output_dir / f'principle-audit-{timestamp}.md'
    output_file.write_text(report)
    
    print(f"\n报告已保存: {output_file}")


if __name__ == '__main__':
    main()
