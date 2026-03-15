#!/usr/bin/env python3
"""
每日提醒审计器 - Daily Reminder Auditor

核心原则：重复提醒 = 制度失效，需立即根治
用户指令："每天定期做这个检查，这样我们的迭代升级就有保障了"

审计规则：
1. 每日22:00自动执行
2. 提取当日所有"提醒/又说/再次/重复/还是"关键词
3. 匹配历史提醒记录
4. 发现重复主题 → 触发制度升级流程
5. 写入强制执行代码
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class DailyReminderAuditor:
    """每日提醒审计器 - 防止重复提醒，持续迭代升级"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.memory_dir = self.workspace / "memory"
        self.audit_log = self.workspace / "memory" / "reminder-audit-log.jsonl"
        self.repeated_issues = self.workspace / "memory" / "repeated-issues-tracker.json"
        
        # 提醒关键词
        self.reminder_keywords = [
            "提醒", "又说", "再次", "重复", "还是", "还是这样",
            "反复", "多次", "还是不行", "还是没", "又说一遍"
        ]
        
        # 加载历史问题
        self.issues = self._load_issues()
    
    def _load_issues(self) -> dict:
        """加载历史重复问题"""
        if self.repeated_issues.exists():
            with open(self.repeated_issues, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "issues": [],
            "total_count": 0,
            "resolved_count": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_issues(self):
        """保存问题记录"""
        self.issues["last_updated"] = datetime.now().isoformat()
        with open(self.repeated_issues, 'w', encoding='utf-8') as f:
            json.dump(self.issues, f, ensure_ascii=False, indent=2)
    
    def scan_daily_conversations(self, date_str: str = None) -> list:
        """
        扫描当日对话，提取提醒关键词
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD)，默认今天
        
        Returns:
            发现的提醒列表
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # 读取当日记忆文件
        memory_file = self.memory_dir / f"{date_str}.md"
        if not memory_file.exists():
            return []
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取用户反馈段落
        reminders = []
        
        # 查找包含提醒关键词的段落
        for keyword in self.reminder_keywords:
            # 匹配用户反馈段落
            pattern = rf"用户反馈.*?(?:{keyword}).*?\n\n"
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                # 提取主题
                theme = self._extract_theme(match)
                reminders.append({
                    "keyword": keyword,
                    "theme": theme,
                    "context": match.strip(),
                    "date": date_str
                })
        
        return reminders
    
    def _extract_theme(self, context: str) -> str:
        """从上下文中提取主题"""
        # 常见主题映射
        theme_patterns = {
            r"资源空置|自动补位|阻塞任务": "资源空置与自动补位",
            r"时间预估|评估|预计": "时间预估准确性",
            r"专家联系方式|WIP-002": "专家联系方式处理",
            r"替身|专家|术语": "替身术语标准化",
            r"重复|又说|再次": "重复提醒机制",
            r"制度|规则|执行": "制度执行力度",
        }
        
        for pattern, theme in theme_patterns.items():
            if re.search(pattern, context, re.IGNORECASE):
                return theme
        
        return "其他"
    
    def check_repeated_issues(self, new_reminders: list) -> list:
        """
        检查是否有重复问题
        
        Args:
            new_reminders: 新发现的提醒列表
        
        Returns:
            重复问题列表
        """
        repeated = []
        
        for reminder in new_reminders:
            theme = reminder["theme"]
            
            # 检查是否已有相同主题
            existing = [i for i in self.issues["issues"] if i["theme"] == theme]
            
            if existing:
                # 更新计数
                existing[0]["count"] += 1
                existing[0]["last_occurrence"] = reminder["date"]
                existing[0]["history"].append({
                    "date": reminder["date"],
                    "context": reminder["context"][:200]  # 截取前200字符
                })
                
                if existing[0]["count"] >= 2:
                    repeated.append(existing[0])
            else:
                # 新增问题
                self.issues["issues"].append({
                    "theme": theme,
                    "count": 1,
                    "first_occurrence": reminder["date"],
                    "last_occurrence": reminder["date"],
                    "status": "new",
                    "history": [{
                        "date": reminder["date"],
                        "context": reminder["context"][:200]
                    }]
                })
                self.issues["total_count"] += 1
        
        self._save_issues()
        return repeated
    
    def generate_upgrade_plan(self, repeated_issues: list) -> dict:
        """
        为重复问题生成升级计划
        
        Args:
            repeated_issues: 重复问题列表
        
        Returns:
            升级计划
        """
        upgrade_plans = {
            "资源空置与自动补位": {
                "root_cause": "制度文档化，依赖人记住执行",
                "solution": "零空置强制执行V2.0 - 写入代码",
                "skill": "zero-idle-enforcer",
                "status": "deployed"
            },
            "时间预估准确性": {
                "root_cause": "用旧标准评估升级后的实力",
                "solution": "自我评估校准器 - 激进系数×0.3",
                "skill": "self-assessment-calibrator",
                "status": "deploying"
            },
            "专家联系方式处理": {
                "root_cause": "等待用户决策，未明确责任边界",
                "solution": "用户自行处理，AI不再等待",
                "skill": "N/A",
                "status": "resolved"
            },
            "替身术语标准化": {
                "root_cause": "缺乏统一术语规范",
                "solution": "术语标准化Skill + 自动检查",
                "skill": "terminology-standardizer",
                "status": "pending"
            },
            "重复提醒机制": {
                "root_cause": "缺乏系统性审计",
                "solution": "每日提醒审计器 - 自动检查",
                "skill": "daily-reminder-auditor",
                "status": "deploying"
            },
            "制度执行力度": {
                "root_cause": "规则在文档，不在执行",
                "solution": "制度即代码 - 强制执行",
                "skill": "code-based-enforcement",
                "status": "deploying"
            }
        }
        
        plans = []
        for issue in repeated_issues:
            theme = issue["theme"]
            if theme in upgrade_plans:
                plan = upgrade_plans[theme].copy()
                plan["theme"] = theme
                plan["occurrence_count"] = issue["count"]
                plans.append(plan)
        
        return plans
    
    def generate_audit_report(self, date_str: str = None) -> str:
        """生成审计报告"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # 扫描当日提醒
        reminders = self.scan_daily_conversations(date_str)
        
        # 检查重复问题
        repeated = self.check_repeated_issues(reminders)
        
        # 生成升级计划
        upgrade_plans = self.generate_upgrade_plan(repeated)
        
        # 记录审计日志
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "date": date_str,
            "reminders_found": len(reminders),
            "repeated_issues": len(repeated),
            "upgrade_plans_generated": len(upgrade_plans)
        }
        
        with open(self.audit_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        # 生成报告
        report_lines = [
            f"# 每日提醒审计报告 - {date_str}",
            "",
            f"**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**提醒关键词发现**: {len(reminders)} 个",
            f"**重复问题识别**: {len(repeated)} 项",
            "",
            "## 当日提醒摘要",
        ]
        
        if reminders:
            for r in reminders:
                report_lines.append(f"- [{r['theme']}] 关键词: {r['keyword']}")
        else:
            report_lines.append("- 未发现提醒关键词")
        
        if repeated:
            report_lines.extend([
                "",
                "## ⚠️ 重复问题（需立即根治）",
                "",
                "| 主题 | 出现次数 | 根因 | 解决方案 | 状态 |",
                "|------|----------|------|----------|------|"
            ])
            
            for plan in upgrade_plans:
                report_lines.append(
                    f"| {plan['theme']} | {plan['occurrence_count']} | {plan['root_cause']} | {plan['solution']} | {plan['status']} |"
                )
            
            report_lines.extend([
                "",
                "## 强制执行计划",
                "",
                "针对重复问题，已触发以下强制执行：",
                ""
            ])
            
            for plan in upgrade_plans:
                if plan['status'] == 'pending':
                    report_lines.append(f"- [ ] 创建Skill: {plan['skill']}")
                elif plan['status'] == 'deploying':
                    report_lines.append(f"- [🔄] 部署中: {plan['skill']}")
                elif plan['status'] == 'deployed':
                    report_lines.append(f"- [✅] 已部署: {plan['skill']}")
        else:
            report_lines.extend([
                "",
                "## ✅ 当日状态",
                "",
                "未发现重复提醒问题，制度运行良好。"
            ])
        
        report_lines.extend([
            "",
            "## 历史累计",
            "",
            f"- 总问题数: {self.issues['total_count']}",
            f"- 已解决: {self.issues['resolved_count']}",
            f"- 待处理: {self.issues['total_count'] - self.issues['resolved_count']}",
            "",
            "---",
            "",
            "*重复提醒 = 制度失效，必须立即根治*"
        ])
        
        return "\n".join(report_lines)
    
    def mark_resolved(self, theme: str):
        """标记问题已解决"""
        for issue in self.issues["issues"]:
            if issue["theme"] == theme:
                issue["status"] = "resolved"
                issue["resolved_at"] = datetime.now().isoformat()
                self.issues["resolved_count"] += 1
                break
        
        self._save_issues()


def main():
    """主函数 - 执行每日审计"""
    auditor = DailyReminderAuditor()
    
    # 生成并输出报告
    report = auditor.generate_audit_report()
    print(report)
    
    # 保存报告
    today = datetime.now().strftime("%Y-%m-%d")
    report_file = auditor.workspace / "memory" / f"reminder-audit-report-{today}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存: {report_file}")


if __name__ == "__main__":
    main()
