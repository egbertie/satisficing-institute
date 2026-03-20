#!/usr/bin/env python3
"""
元认知监控器 - Meta-Cognitive Monitor

核心功能：监控自身的认知过程，确保3-5%资源持续用于优化

监控维度：
1. 时间分配：是否每天投入43-72分钟用于复盘？
2. 算力分配：是否每小时分配5%算力用于快速复盘？
3. 上下文分配：是否任务后分配3%用于即时复盘？
4. 改进闭环：洞察→方案→实施→验证 是否完整？

触发机制：
- 每日23:00：深度复盘（30分钟，2%时间资源）
- 每小时整点：快速复盘（5分钟，2%算力资源）
- 任务完成：即时复盘（2分钟，1%上下文资源）
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

class MetaCognitiveMonitor:
    """元认知监控器 - 确保改进资源到位"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.monitor_file = self.workspace / "memory" / "metacognitive-monitor.json"
        self.alert_log = self.workspace / "memory" / "improvement-alerts.jsonl"
        
        # 资源配置标准
        self.RESOURCE_TARGETS = {
            "daily_time": {"min": 43, "max": 72, "unit": "minutes"},  # 3-5% of 24h
            "hourly_compute": {"target": 5, "unit": "percentage"},
            "task_context": {"target": 3, "unit": "percentage"}
        }
        
        # 加载监控状态
        self.status = self._load_status()
    
    def _load_status(self) -> dict:
        """加载监控状态"""
        if self.monitor_file.exists():
            with open(self.monitor_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "total_reviews": 0,
            "deep_reviews": 0,
            "quick_reviews": 0,
            "instant_reviews": 0,
            "resource_utilization": {
                "time_allocated": 0,
                "compute_allocated": 0,
                "context_allocated": 0
            },
            "last_review": None,
            "improvement_velocity": 0
        }
    
    def _save_status(self):
        """保存监控状态"""
        with open(self.monitor_file, 'w', encoding='utf-8') as f:
            json.dump(self.status, f, ensure_ascii=False, indent=2)
    
    def _log_alert(self, alert_type: str, message: str, severity: str):
        """记录告警"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "severity": severity
        }
        with open(self.alert_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(alert, ensure_ascii=False) + "\n")
    
    def check_daily_allocation(self) -> dict:
        """检查每日资源分配"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 检查今日是否已执行深度复盘
        last_deep = self.status.get("last_deep_review")
        
        if last_deep != today:
            # 如果当前时间已过23:00，则触发告警
            if datetime.now().hour >= 23:
                self._log_alert(
                    "DAILY_REVIEW_MISSED",
                    f"今日深度复盘未执行，资源投入不足",
                    "HIGH"
                )
                return {
                    "status": "ALERT",
                    "issue": "今日深度复盘未执行",
                    "action": "立即执行 skills/continuous-improvement-engine/engine.py"
                }
        
        return {"status": "OK", "message": "每日复盘资源已分配"}
    
    def check_hourly_allocation(self) -> dict:
        """检查每小时资源分配"""
        last_quick = self.status.get("last_quick_review")
        
        if last_quick:
            last_time = datetime.fromisoformat(last_quick)
            if datetime.now() - last_time > timedelta(hours=1.5):
                self._log_alert(
                    "HOURLY_REVIEW_MISSED",
                    f"过去1.5小时未执行快速复盘",
                    "MEDIUM"
                )
                return {
                    "status": "WARNING",
                    "issue": "快速复盘频率不足",
                    "action": "下次心跳时触发快速复盘"
                }
        
        return {"status": "OK", "message": "每小时复盘资源已分配"}
    
    def check_improvement_loop(self) -> dict:
        """检查改进闭环完整性"""
        # 检查是否有未验证的改进
        improvements_file = self.workspace / "memory" / "continuous-improvement-log.jsonl"
        
        if not improvements_file.exists():
            return {"status": "OK", "message": "暂无改进记录"}
        
        # 读取最近的改进记录
        recent_improvements = []
        with open(improvements_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    entry_time = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
                    if datetime.now() - entry_time < timedelta(days=2):
                        recent_improvements.append(entry)
                except:
                    continue
        
        # 检查是否有未实施的洞察
        unimplemented = 0
        for imp in recent_improvements:
            if imp.get("steps", {}).get("implement", {}).get("implementations"):
                for impl in imp["steps"]["implement"]["implementations"]:
                    if impl.get("status") == "planned":
                        unimplemented += 1
        
        if unimplemented > 2:
            self._log_alert(
                "IMPROVEMENT_LOOP_BROKEN",
                f"有{unimplemented}项改进方案未实施",
                "HIGH"
            )
            return {
                "status": "ALERT",
                "issue": f"{unimplemented}项改进未实施",
                "action": "立即实施未完成的改进方案"
            }
        
        return {"status": "OK", "message": "改进闭环完整"}
    
    def generate_monitor_report(self) -> str:
        """生成监控报告"""
        daily_check = self.check_daily_allocation()
        hourly_check = self.check_hourly_allocation()
        loop_check = self.check_improvement_loop()
        
        report_lines = [
            f"# 元认知监控报告",
            "",
            f"**监控时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**累计复盘**: {self.status['total_reviews']}次",
            f"**改进速度**: {self.status['improvement_velocity']}项/周",
            "",
            "## 资源配置检查",
            ""
        ]
        
        # 每日分配
        report_lines.append(f"### 每日深度复盘 (目标: 43-72分钟)")
        if daily_check["status"] == "OK":
            report_lines.append("✅ **状态正常** - 今日资源已分配")
        else:
            report_lines.append(f"🔴 **{daily_check['issue']}**")
            report_lines.append(f"   → 行动: {daily_check['action']}")
        
        report_lines.append("")
        
        # 每小时分配
        report_lines.append(f"### 每小时快速复盘 (目标: 5%算力)")
        if hourly_check["status"] == "OK":
            report_lines.append("✅ **状态正常** - 复盘频率达标")
        else:
            report_lines.append(f"⚠️ **{hourly_check['issue']}**")
            report_lines.append(f"   → 行动: {hourly_check['action']}")
        
        report_lines.append("")
        
        # 改进闭环
        report_lines.append(f"### 改进闭环完整性")
        if loop_check["status"] == "OK":
            report_lines.append("✅ **状态正常** - 洞察已转化为实施")
        else:
            report_lines.append(f"🔴 **{loop_check['issue']}**")
            report_lines.append(f"   → 行动: {loop_check['action']}")
        
        report_lines.extend([
            "",
            "## 资源配置标准",
            "",
            "| 资源类型 | 目标占比 | 实际投入 | 状态 |",
            "|----------|----------|----------|------|",
            f"| 时间资源 | 3-5% (43-72分钟) | {self.status['resource_utilization']['time_allocated']}分钟 | {'✅' if self.status['resource_utilization']['time_allocated'] >= 43 else '🔴'} |",
            f"| 算力资源 | 5%每小时 | {self.status['resource_utilization']['compute_allocated']}% | {'✅' if self.status['resource_utilization']['compute_allocated'] >= 5 else '🔴'} |",
            f"| 上下文资源 | 3%每任务 | {self.status['resource_utilization']['context_allocated']}% | {'✅' if self.status['resource_utilization']['context_allocated'] >= 3 else '🔴'} |",
            "",
            "---",
            "",
            "*元认知监控：确保3-5%资源持续用于自我改进*"
        ])
        
        return "\n".join(report_lines)
    
    def update_review_count(self, review_type: str):
        """更新复盘计数"""
        self.status["total_reviews"] += 1
        
        if review_type == "deep":
            self.status["deep_reviews"] += 1
            self.status["last_deep_review"] = datetime.now().strftime("%Y-%m-%d")
        elif review_type == "quick":
            self.status["quick_reviews"] += 1
            self.status["last_quick_review"] = datetime.now().isoformat()
        elif review_type == "instant":
            self.status["instant_reviews"] += 1
        
        self._save_status()


def main():
    """主函数"""
    monitor = MetaCognitiveMonitor()
    
    # 生成监控报告
    report = monitor.generate_monitor_report()
    print(report)


if __name__ == "__main__":
    main()
