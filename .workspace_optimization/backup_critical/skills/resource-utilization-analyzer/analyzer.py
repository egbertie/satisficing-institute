#!/usr/bin/env python3
"""
资源利用日志分析器 - Resource Utilization Analyzer

核心原则：数据驱动复盘，第一性原则优化
用户目标：每天3-5%资源用于持续复盘和优化

分析维度：
1. 时间利用率：预估 vs 实际 vs 优化空间
2. 并行效率：单线 vs 多线 vs 理论最优
3. Skill命中率：手动执行 vs Skill调用
4. 决策质量：自主决策 vs 用户确认 vs 等待成本
5. 迭代速率：完成任务数 / 时间单位
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import statistics

class ResourceUtilizationAnalyzer:
    """资源利用日志分析器 - 发现优化空间"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.memory_dir = self.workspace / "memory"
        self.log_dir = self.workspace / "logs"
        self.analysis_file = self.workspace / "memory" / "resource-utilization-analysis.json"
        
        # 确保日志目录存在
        self.log_dir.mkdir(exist_ok=True)
        
        # 加载历史分析
        self.analysis = self._load_analysis()
    
    def _load_analysis(self) -> dict:
        """加载历史分析数据"""
        if self.analysis_file.exists():
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "daily_stats": [],
            "optimization_insights": [],
            "baseline_efficiency": 1.0,
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_analysis(self):
        """保存分析数据"""
        self.analysis["last_updated"] = datetime.now().isoformat()
        with open(self.analysis_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, ensure_ascii=False, indent=2)
    
    def parse_daily_logs(self, date_str: str = None) -> dict:
        """
        解析当日日志，提取资源利用数据
        
        Returns:
            当日资源利用统计
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # 读取当日记忆文件
        memory_file = self.memory_dir / f"{date_str}.md"
        if not memory_file.exists():
            return self._empty_stats(date_str)
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        stats = {
            "date": date_str,
            "tasks_completed": self._count_pattern(content, r"✅.*完成"),
            "tasks_blocked": self._count_pattern(content, r"⏸️|阻塞|等待"),
            "skills_used": self._extract_skills_used(content),
            "time_estimates": self._extract_time_estimates(content),
            "parallel_executions": self._count_pattern(content, r"并行|六线|多线"),
            "autonomous_decisions": self._count_pattern(content, r"自主|自动"),
            "user_confirmations": self._count_pattern(content, r"需用户确认|等待用户"),
            "violations": self._extract_violations(content),
            "improvements": self._extract_improvements(content),
        }
        
        # 计算效率指标
        stats["efficiency_score"] = self._calculate_efficiency(stats)
        stats["optimization_potential"] = self._calculate_optimization_potential(stats)
        
        return stats
    
    def _count_pattern(self, content: str, pattern: str) -> int:
        """统计模式出现次数"""
        return len(re.findall(pattern, content, re.IGNORECASE))
    
    def _extract_skills_used(self, content: str) -> list:
        """提取使用的Skill"""
        skill_patterns = [
            r"zero-idle-enforcer",
            r"self-assessment-calibrator",
            r"daily-reminder-auditor",
            r"first-principle-scheduler",
            r"task-coordinator",
        ]
        skills = []
        for pattern in skill_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                skills.append(pattern)
        return skills
    
    def _extract_time_estimates(self, content: str) -> dict:
        """提取时间预估数据"""
        # 匹配 "预估X天/小时" 和 "实际X天/小时"
        estimates = re.findall(r"预估[：:]?\s*(\d+)\s*(天|小时|h)", content, re.IGNORECASE)
        actuals = re.findall(r"实际[：:]?\s*(\d+)\s*(天|小时|h)", content, re.IGNORECASE)
        
        return {
            "estimates_count": len(estimates),
            "actuals_count": len(actuals),
            "accuracy": len(actuals) / len(estimates) if estimates else 0
        }
    
    def _extract_violations(self, content: str) -> list:
        """提取违规记录"""
        violations = []
        
        # 零空置违规
        if re.search(r"零空置.*违规|NO_ACTIVE|ALL_BLOCKED", content, re.IGNORECASE):
            violations.append({"type": "zero_idle", "severity": "high"})
        
        # 自我评估违规
        if re.search(r"预估.*实际.*超预期|低估", content, re.IGNORECASE):
            violations.append({"type": "self_assessment", "severity": "medium"})
        
        return violations
    
    def _extract_improvements(self, content: str) -> list:
        """提取改进记录"""
        improvements = []
        
        # 匹配改进相关段落
        patterns = [
            (r"【.*改进.*】", "system_improvement"),
            (r"制度.*升级|V\d+\.\d+", "version_upgrade"),
            (r"Skill.*新建|Skill.*部署", "skill_deployment"),
        ]
        
        for pattern, imp_type in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                improvements.append({"type": imp_type, "description": match})
        
        return improvements
    
    def _calculate_efficiency(self, stats: dict) -> float:
        """计算效率分数（0-100）"""
        score = 50  # 基础分
        
        # 完成任务加分
        score += min(stats["tasks_completed"] * 5, 20)
        
        # 并行执行加分
        score += min(stats["parallel_executions"] * 3, 10)
        
        # 自主决策加分
        score += min(stats["autonomous_decisions"] * 2, 10)
        
        # 违规减分
        score -= len(stats["violations"]) * 10
        
        # Skill使用加分
        score += min(len(stats["skills_used"]) * 2, 10)
        
        return max(0, min(100, score))
    
    def _calculate_optimization_potential(self, stats: dict) -> dict:
        """计算优化潜力"""
        potential = {
            "time_estimation": 0,
            "parallelization": 0,
            "skill_usage": 0,
            "autonomy": 0
        }
        
        # 时间预估优化潜力
        if stats["time_estimates"]["accuracy"] < 0.5:
            potential["time_estimation"] = 30  # 30%提升空间
        elif stats["time_estimates"]["accuracy"] < 0.8:
            potential["time_estimation"] = 15
        
        # 并行化优化潜力
        if stats["parallel_executions"] < 3:
            potential["parallelization"] = 25
        elif stats["parallel_executions"] < 6:
            potential["parallelization"] = 10
        
        # Skill使用优化潜力
        if len(stats["skills_used"]) < 3:
            potential["skill_usage"] = 20
        
        # 自主决策优化潜力
        if stats["user_confirmations"] > stats["autonomous_decisions"]:
            potential["autonomy"] = 15
        
        return potential
    
    def _empty_stats(self, date_str: str) -> dict:
        """返回空统计"""
        return {
            "date": date_str,
            "tasks_completed": 0,
            "tasks_blocked": 0,
            "skills_used": [],
            "time_estimates": {"estimates_count": 0, "actuals_count": 0, "accuracy": 0},
            "parallel_executions": 0,
            "autonomous_decisions": 0,
            "user_confirmations": 0,
            "violations": [],
            "improvements": [],
            "efficiency_score": 0,
            "optimization_potential": {}
        }
    
    def generate_insights(self, stats: dict) -> list:
        """
        基于统计数据生成洞察
        
        Returns:
            优化建议列表
        """
        insights = []
        
        # 洞察1：时间预估准确性
        if stats["time_estimates"]["accuracy"] < 0.5:
            insights.append({
                "category": "时间预估",
                "finding": f"预估准确率仅{stats['time_estimates']['accuracy']*100:.0f}%，存在严重低估",
                "root_cause": "用旧标准评估，缺乏激进系数",
                "action": "强制应用自我评估校准器（×0.3激进系数）",
                "expected_improvement": "30%"
            })
        
        # 洞察2：并行化程度
        if stats["parallel_executions"] < 3:
            insights.append({
                "category": "并行效率",
                "finding": f"并行执行次数仅{stats['parallel_executions']}次，未充分利用六线",
                "root_cause": "默认串行思维，未检查依赖关系",
                "action": "强制并行检查：无硬依赖则六线全开",
                "expected_improvement": "25%"
            })
        
        # 洞察3：Skill使用
        if len(stats["skills_used"]) < 3:
            insights.append({
                "category": "Skill利用",
                "finding": f"仅使用{len(stats['skills_used'])}个Skill，存在手动重复劳动",
                "root_cause": "任务前未检查Skill库",
                "action": "强制Skill检查：任务前先查可用Skill",
                "expected_improvement": "20%"
            })
        
        # 洞察4：自主决策
        if stats["user_confirmations"] > stats["autonomous_decisions"]:
            insights.append({
                "category": "决策效率",
                "finding": f"用户确认({stats['user_confirmations']})多于自主决策({stats['autonomous_decisions']})",
                "root_cause": "过度谨慎，边界不清",
                "action": "明确自主决策边界：内部低敏感度自主推进",
                "expected_improvement": "15%"
            })
        
        # 洞察5：违规频率
        if len(stats["violations"]) > 2:
            insights.append({
                "category": "制度执行",
                "finding": f"当日违规{len(stats['violations'])}次，强制执行不到位",
                "root_cause": "检查频率不足，响应延迟",
                "action": "提高检查频率至每5分钟，0延迟响应",
                "expected_improvement": "10%"
            })
        
        return insights
    
    def generate_daily_report(self, date_str: str = None) -> str:
        """生成每日资源利用分析报告"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # 解析当日数据
        stats = self.parse_daily_logs(date_str)
        
        # 生成洞察
        insights = self.generate_insights(stats)
        
        # 保存到历史
        self.analysis["daily_stats"].append(stats)
        self.analysis["optimization_insights"].extend(insights)
        self._save_analysis()
        
        # 生成报告
        report_lines = [
            f"# 资源利用分析报告 - {date_str}",
            "",
            f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**效率评分**: {stats['efficiency_score']}/100",
            "",
            "## 当日统计",
            "",
            "| 指标 | 数值 | 状态 |",
            "|------|------|------|",
            f"| 完成任务 | {stats['tasks_completed']} | {'✅' if stats['tasks_completed'] >= 5 else '⚠️'} |",
            f"| 阻塞任务 | {stats['tasks_blocked']} | {'✅' if stats['tasks_blocked'] == 0 else '🔴'} |",
            f"| Skill使用 | {len(stats['skills_used'])} | {'✅' if len(stats['skills_used']) >= 3 else '⚠️'} |",
            f"| 并行执行 | {stats['parallel_executions']} | {'✅' if stats['parallel_executions'] >= 4 else '⚠️'} |",
            f"| 自主决策 | {stats['autonomous_decisions']} | {'✅' if stats['autonomous_decisions'] >= stats['user_confirmations'] else '⚠️'} |",
            f"| 违规次数 | {len(stats['violations'])} | {'✅' if len(stats['violations']) == 0 else '🔴'} |",
            "",
            "## 优化潜力分析",
            ""
        ]
        
        if stats["optimization_potential"]:
            for key, value in stats["optimization_potential"].items():
                report_lines.append(f"- **{key}**: {value}% 提升空间")
        else:
            report_lines.append("- 暂无优化空间（已达高效状态）")
        
        report_lines.extend([
            "",
            "## 优化洞察与行动",
            ""
        ])
        
        if insights:
            for i, insight in enumerate(insights, 1):
                report_lines.extend([
                    f"### 洞察{i}: {insight['category']}",
                    "",
                    f"**发现**: {insight['finding']}",
                    f"**根因**: {insight['root_cause']}",
                    f"**行动**: {insight['action']}",
                    f"**预期提升**: {insight['expected_improvement']}",
                    ""
                ])
        else:
            report_lines.append("当日运行良好，未发现明显优化空间。")
        
        # 累计统计
        if len(self.analysis["daily_stats"]) > 1:
            avg_efficiency = statistics.mean([s["efficiency_score"] for s in self.analysis["daily_stats"][-7:]])
            report_lines.extend([
                "",
                "## 趋势分析（近7天）",
                "",
                f"- 平均效率: {avg_efficiency:.1f}/100",
                f"- 效率趋势: {'↗️ 上升' if avg_efficiency > 60 else '→️ 平稳' if avg_efficiency > 40 else '↘️ 下降'}",
                f"- 累计洞察: {len(self.analysis['optimization_insights'])} 条",
            ])
        
        report_lines.extend([
            "",
            "---",
            "",
            "*每日3-5%资源用于复盘优化，持续成为最好的自己*"
        ])
        
        return "\n".join(report_lines)


def main():
    """主函数"""
    analyzer = ResourceUtilizationAnalyzer()
    
    # 生成并输出报告
    report = analyzer.generate_daily_report()
    print(report)
    
    # 保存报告
    today = datetime.now().strftime("%Y-%m-%d")
    report_file = analyzer.workspace / "memory" / f"resource-analysis-{today}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存: {report_file}")


if __name__ == "__main__":
    main()
