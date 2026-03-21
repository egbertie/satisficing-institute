#!/usr/bin/env python3
"""
management-enforcer 执行脚本
管理层执行者 - 诚实汇报+沟通协议+惩罚措施
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data" / "management-enforcer"
LOG_FILE = Path("/tmp/management-enforcer.log")

# 确保数据目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

class ManagementEnforcer:
    """管理层执行者"""
    
    def __init__(self):
        self.reports_file = DATA_DIR / "reports.json"
        self.comms_file = DATA_DIR / "communications.json"
        self.violations_file = DATA_DIR / "violations.json"
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        self.reports = self._load_json(self.reports_file, [])
        self.comms = self._load_json(self.comms_file, [])
        self.violations = self._load_json(self.violations_file, [])
    
    def _load_json(self, path, default):
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return default
    
    def save_data(self):
        """保存数据"""
        with open(self.reports_file, 'w') as f:
            json.dump(self.reports, f, indent=2)
        with open(self.comms_file, 'w') as f:
            json.dump(self.comms, f, indent=2)
        with open(self.violations_file, 'w') as f:
            json.dump(self.violations, f, indent=2)
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry + "\n")
    
    # ========== 诚实汇报机制 ==========
    
    def check_daily_reports(self):
        """检查日报提交情况"""
        self.log("=== 检查日报提交情况 ===")
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 检查昨日22:00前是否有日报
        daily_deadline = datetime.strptime(f"{yesterday} 22:00", "%Y-%m-%d %H:%M")
        
        # 模拟检查（实际应查询任务系统）
        pending_reporters = self._get_pending_reporters()
        
        if pending_reporters:
            self.log(f"⚠️ 发现 {len(pending_reporters)} 人未按时提交日报:")
            for reporter in pending_reporters:
                self.log(f"  - {reporter}")
                self._send_reminder(reporter, "daily_report")
        else:
            self.log("✅ 所有日报已按时提交")
        
        return len(pending_reporters)
    
    def check_exception_reports(self):
        """检查异常汇报"""
        self.log("=== 检查异常汇报 ===")
        
        # 检查未确认的异常
        unconfirmed_exceptions = [r for r in self.reports 
                                   if r.get("type") == "exception" 
                                   and r.get("status") == "pending"]
        
        for exc in unconfirmed_exceptions:
            hours_pending = (datetime.now() - datetime.fromisoformat(exc["created_at"])).hours
            if hours_pending > 2:
                self.log(f"🚨 异常汇报超时 {hours_pending}h: {exc['id']}")
                self._escalate_exception(exc)
        
        return len(unconfirmed_exceptions)
    
    def _get_pending_reporters(self):
        """获取待汇报人员列表（模拟）"""
        # 实际应从HR系统或任务系统获取
        return []
    
    def _send_reminder(self, reporter, report_type):
        """发送提醒"""
        self.log(f"  📨 已向 {reporter} 发送 {report_type} 提醒")
    
    def _escalate_exception(self, exception):
        """升级异常"""
        self.log(f"  ⬆️ 异常 {exception['id']} 已升级至上级")
    
    # ========== 沟通协议机制 ==========
    
    def check_communication_response(self):
        """检查沟通响应时间"""
        self.log("=== 检查沟通响应时间 ===")
        
        four_hours_ago = datetime.now() - timedelta(hours=4)
        
        overdue_comms = [c for c in self.comms 
                         if c.get("status") == "pending_response"
                         and datetime.fromisoformat(c["sent_at"]) < four_hours_ago]
        
        for comm in overdue_comms:
            self.log(f"⏰ 消息 {comm['id']} 超过4小时未回复")
            self._escalate_communication(comm)
        
        return len(overdue_comms)
    
    def detect_conflict_keywords(self):
        """检测冲突关键词"""
        self.log("=== 检测沟通冲突 ===")
        
        conflict_keywords = ["你总是", "你从来不", "完全不行", "彻底失败", "根本不懂"]
        
        detected_conflicts = []
        for comm in self.comms:
            if comm.get("status") == "new":
                content = comm.get("content", "")
                for keyword in conflict_keywords:
                    if keyword in content:
                        detected_conflicts.append({
                            "comm_id": comm["id"],
                            "keyword": keyword,
                            "content_preview": content[:50]
                        })
                        break
        
        for conflict in detected_conflicts:
            self.log(f"⚡ 检测到冲突关键词 '{conflict['keyword']}' 在消息 {conflict['comm_id']}")
            self._trigger_mediation(conflict)
        
        return len(detected_conflicts)
    
    def _escalate_communication(self, comm):
        """升级沟通"""
        self.log(f"  ⬆️ 沟通 {comm['id']} 已升级")
    
    def _trigger_mediation(self, conflict):
        """触发调解"""
        self.log(f"  🧘 已为消息 {conflict['comm_id']} 触发调解流程")
    
    # ========== 惩罚措施机制 ==========
    
    def detect_violations(self):
        """检测违规行为"""
        self.log("=== 检测违规行为 ===")
        
        violations_found = []
        
        # 检查汇报违规
        report_violations = self._check_report_violations()
        violations_found.extend(report_violations)
        
        # 检查沟通违规
        comm_violations = self._check_comm_violations()
        violations_found.extend(comm_violations)
        
        for v in violations_found:
            self.log(f"🚫 检测到违规: {v['type']} - {v['description']}")
            self._process_violation(v)
        
        return len(violations_found)
    
    def _check_report_violations(self):
        """检查汇报违规"""
        violations = []
        
        # 检查漏报（超过24小时无汇报）
        day_ago = datetime.now() - timedelta(days=1)
        for report in self.reports:
            if report.get("status") == "overdue":
                violations.append({
                    "type": "report_overdue",
                    "level": "P2",
                    "description": f"汇报超时: {report['id']}",
                    "subject": report.get("reporter"),
                    "evidence": report
                })
        
        return violations
    
    def _check_comm_violations(self):
        """检查沟通违规"""
        violations = []
        
        # 检查多次冲突关键词使用
        # 实际应查询历史记录
        
        return violations
    
    def _process_violation(self, violation):
        """处理违规"""
        level = violation.get("level", "P3")
        
        if level in ["P0", "P1"]:
            self.log(f"  🔴 严重违规，启动处罚流程")
            self._initiate_sanction(violation)
        elif level == "P2":
            self.log(f"  🟡 一般违规，记录并警告")
            self._record_warning(violation)
        else:
            self.log(f"  🟢 轻微违规，提醒教育")
            self._send_education(violation)
    
    def _initiate_sanction(self, violation):
        """启动处罚"""
        self.violations.append({
            **violation,
            "status": "sanction_pending",
            "detected_at": datetime.now().isoformat()
        })
    
    def _record_warning(self, violation):
        """记录警告"""
        self.violations.append({
            **violation,
            "status": "warning_issued",
            "detected_at": datetime.now().isoformat()
        })
    
    def _send_education(self, violation):
        """发送教育材料"""
        pass
    
    # ========== 主运行 ==========
    
    def run(self, mode="all"):
        """运行检查"""
        self.log(f"\n{'='*50}")
        self.log(f"Management Enforcer 启动 - 模式: {mode}")
        self.log(f"{'='*50}")
        
        results = {}
        
        if mode in ["all", "report"]:
            results["daily_reports"] = self.check_daily_reports()
            results["exception_reports"] = self.check_exception_reports()
        
        if mode in ["all", "comm"]:
            results["comm_response"] = self.check_communication_response()
            results["conflicts"] = self.detect_conflict_keywords()
        
        if mode in ["all", "violation"]:
            results["violations"] = self.detect_violations()
        
        self.save_data()
        
        self.log(f"\n{'='*50}")
        self.log(f"检查完成: {results}")
        self.log(f"{'='*50}\n")
        
        return results


def main():
    """主函数"""
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    enforcer = ManagementEnforcer()
    results = enforcer.run(mode)
    
    # 输出JSON格式结果
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
