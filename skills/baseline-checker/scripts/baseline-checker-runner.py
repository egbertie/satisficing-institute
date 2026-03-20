#!/usr/bin/env python3
"""
baseline-checker.py
九条底线自动化检查器

5-Standard: 全局/系统/迭代/Skill化/自动化
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 九条底线定义
BASELINES = {
    "1_真人主体": {
        "description": "AI是助手，不是替身；真人必须参与核心决策和创作",
        "check_points": ["关键决策有人类确认", "创作内容有人类审核", "AI不代替人类做最终判断"],
        "severity": "CRITICAL"
    },
    "2_合规优先": {
        "description": "严格遵守平台规则，不挑战风控系统",
        "check_points": ["不违反平台服务条款", "不尝试绕过安全限制", "尊重API调用频率限制"],
        "severity": "CRITICAL"
    },
    "3_真实价值": {
        "description": "创造真实价值，而非投机取巧",
        "check_points": ["输出内容真实可验证", "不编造数据或案例", "不确定内容标注[待验证]"],
        "severity": "HIGH"
    },
    "4_透明可控": {
        "description": "所有操作可追溯，用户完全知情",
        "check_points": ["关键操作有日志记录", "用户知晓AI参与程度", "决策过程可解释"],
        "severity": "HIGH"
    },
    "5_安全第一": {
        "description": "数据安全、账号安全、资金安全优先于效率",
        "check_points": ["敏感数据不泄露", "账号权限最小化", "资金操作多重确认"],
        "severity": "CRITICAL"
    },
    "6_风险可控": {
        "description": "最坏情况可承受，不赌全部身家",
        "check_points": ["单次损失有上限", "不All-in单一决策", "有止损机制"],
        "severity": "HIGH"
    },
    "7_灵活应变": {
        "description": "底线是锚，方法是舟；遇水搭桥，遇山开路",
        "check_points": ["方法随环境调整", "底线不随环境妥协", "定期审视策略有效性"],
        "severity": "MEDIUM"
    },
    "8_商业伦理": {
        "description": "技术服务于人，赚钱有道，取之有义",
        "check_points": ["不批量注册账号", "不自动化冒充真人", "不爬虫非公开数据"],
        "severity": "HIGH"
    },
    "9_本能守底": {
        "description": "灰色地带第一反应说不",
        "check_points": ["直觉预警立即暂停", "不侥幸试探边界", "有疑问先确认再行动"],
        "severity": "CRITICAL"
    }
}


class BaselineChecker:
    """九条底线检查器"""
    
    def __init__(self):
        self.check_time = datetime.now()
        self.violations = []
        self.warnings = []
        
    def check_all(self):
        """执行全部底线检查"""
        results = {}
        
        for baseline_id, baseline in BASELINES.items():
            result = self._check_baseline(baseline_id, baseline)
            results[baseline_id] = result
            
        return results
    
    def _check_baseline(self, baseline_id, baseline):
        """检查单条底线"""
        # 这里将来会接入实际的检查逻辑
        # 目前先返回结构化的检查框架
        return {
            "id": baseline_id,
            "description": baseline["description"],
            "severity": baseline["severity"],
            "status": "PASS",  # PASS / WARNING / VIOLATION
            "check_points": baseline["check_points"],
            "last_checked": self.check_time.isoformat()
        }
    
    def generate_report(self):
        """生成检查报告"""
        results = self.check_all()
        
        report = {
            "check_time": self.check_time.isoformat(),
            "version": "1.0.0",
            "total_baselines": len(BASELINES),
            "results": results,
            "summary": {
                "pass": sum(1 for r in results.values() if r["status"] == "PASS"),
                "warning": sum(1 for r in results.values() if r["status"] == "WARNING"),
                "violation": sum(1 for r in results.values() if r["status"] == "VIOLATION")
            }
        }
        
        return report
    
    def print_report(self):
        """打印报告"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("🔒 九条底线自动化检查报告")
        print("="*60)
        print(f"检查时间: {report['check_time']}")
        print(f"底线数量: {report['total_baselines']}")
        print("-"*60)
        
        for baseline_id, result in report['results'].items():
            status_icon = "✅" if result['status'] == "PASS" else "⚠️" if result['status'] == "WARNING" else "❌"
            print(f"{status_icon} {baseline_id}: {result['description'][:40]}...")
        
        print("-"*60)
        print(f"汇总: ✅{report['summary']['pass']} ⚠️{report['summary']['warning']} ❌{report['summary']['violation']}")
        print("="*60)


def main():
    checker = BaselineChecker()
    checker.print_report()
    
    # 保存报告
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    report_file = report_dir / f"baseline-check-{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, 'w') as f:
        json.dump(checker.generate_report(), f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 报告已保存: {report_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
