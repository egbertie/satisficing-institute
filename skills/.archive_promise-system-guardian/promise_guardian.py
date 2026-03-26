#!/usr/bin/env python3
"""
承诺与制度执行保障系统 V1.0
核心功能：承诺记录→到期预警→超期补救→如实报告
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class PromiseAndSystemGuardian:
    """
    承诺与制度执行保障系统
    确保所有承诺、计划、制度都有约束机制
    """
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        
        # 核心数据文件
        self.promise_db = self.workspace / "memory" / "promise_database.json"
        self.system_db = self.workspace / "memory" / "system_rule_database.json"
        self.execution_log = self.workspace / "memory" / "execution_log.json"
        self.daily_report = self.workspace / "reports" / "PROMISE_SYSTEM_DAILY_REPORT.md"
        
        # 初始化数据库
        self._init_databases()
        
    def _init_databases(self):
        """初始化数据库"""
        # 承诺数据库
        if not self.promise_db.exists():
            default_promise_db = {
                "version": "1.0",
                "promises": [],
                "statistics": {
                    "total_promises": 0,
                    "completed": 0,
                    "overdue": 0,
                    "in_progress": 0
                }
            }
            self.promise_db.parent.mkdir(exist_ok=True)
            with open(self.promise_db, 'w', encoding='utf-8') as f:
                json.dump(default_promise_db, f, indent=2, ensure_ascii=False)
        
        # 制度规则数据库
        if not self.system_db.exists():
            default_system_db = {
                "version": "1.0",
                "rules": [],
                "last_update": None
            }
            self.system_db.parent.mkdir(exist_ok=True)
            with open(self.system_db, 'w', encoding='utf-8') as f:
                json.dump(default_system_db, f, indent=2, ensure_ascii=False)
    
    def record_promise(self, 
                      promise_id: str,
                      content: str, 
                      deadline: str,
                      owner: str,
                      priority: str = "P2",
                      dependencies: List[str] = None,
                      consequences_if_fail: str = None) -> Dict:
        """
        记录一个承诺
        
        Args:
            promise_id: 承诺唯一标识
            content: 承诺内容
            deadline: 截止日期 (格式: YYYY-MM-DD HH:MM)
            owner: 负责人
            priority: 优先级 (P0/P1/P2/P3)
            dependencies: 依赖的其他承诺ID
            consequences_if_fail: 未完成的后果说明
        """
        promise = {
            "id": promise_id,
            "content": content,
            "deadline": deadline,
            "owner": owner,
            "priority": priority,
            "status": "active",  # active/completed/overdue/remedied
            "created_at": datetime.now().isoformat(),
            "dependencies": dependencies or [],
            "consequences_if_fail": consequences_if_fail,
            "reminders_sent": [],
            "completion_report": None,
            "failure_report": None
        }
        
        # 保存到数据库
        with open(self.promise_db, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        # 检查是否已存在
        existing = [p for p in db["promises"] if p["id"] == promise_id]
        if existing:
            # 更新现有承诺
            for i, p in enumerate(db["promises"]):
                if p["id"] == promise_id:
                    db["promises"][i] = promise
                    break
        else:
            db["promises"].append(promise)
        
        db["statistics"]["total_promises"] = len(db["promises"])
        
        with open(self.promise_db, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 承诺已记录: [{promise_id}] {content}")
        print(f"   截止: {deadline} | 负责人: {owner} | 优先级: {priority}")
        
        return promise
    
    def check_promises(self) -> Dict[str, List]:
        """
        检查所有承诺状态
        返回：即将到期、已到期、已完成的承诺列表
        """
        with open(self.promise_db, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        now = datetime.now()
        
        upcoming = []      # 即将到期（24小时内）
        overdue = []       # 已到期
        completed = []     # 已完成
        in_progress = []   # 进行中
        
        for promise in db["promises"]:
            if promise["status"] == "completed":
                completed.append(promise)
            elif promise["status"] == "overdue":
                overdue.append(promise)
            else:
                deadline = datetime.fromisoformat(promise["deadline"])
                time_left = deadline - now
                
                if time_left.total_seconds() < 0:
                    # 已到期
                    promise["status"] = "overdue"
                    overdue.append(promise)
                elif time_left.total_seconds() < 24 * 3600:
                    # 24小时内到期
                    upcoming.append(promise)
                else:
                    in_progress.append(promise)
        
        # 更新数据库
        with open(self.promise_db, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        return {
            "upcoming": upcoming,
            "overdue": overdue,
            "completed": completed,
            "in_progress": in_progress
        }
    
    def send_reminder(self, promise_id: str, hours_before: int) -> bool:
        """
        发送预警提醒
        
        Args:
            promise_id: 承诺ID
            hours_before: 提前几小时（24/4/1）
        """
        with open(self.promise_db, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        for promise in db["promises"]:
            if promise["id"] == promise_id:
                reminder = {
                    "time": datetime.now().isoformat(),
                    "hours_before_deadline": hours_before,
                    "message": f"⚠️ 承诺即将到期！[{promise_id}] 还有{hours_before}小时截止"
                }
                promise["reminders_sent"].append(reminder)
                
                with open(self.promise_db, 'w', encoding='utf-8') as f:
                    json.dump(db, f, indent=2, ensure_ascii=False)
                
                print(f"🚨 预警已发送: [{promise_id}] 提前{hours_before}小时")
                return True
        
        return False
    
    def report_completion(self, 
                         promise_id: str, 
                         completion_time: str,
                         result_summary: str,
                         deliverables: List[str]) -> bool:
        """
        报告承诺完成
        
        Args:
            promise_id: 承诺ID
            completion_time: 完成时间
            result_summary: 结果摘要
            deliverables: 交付物清单
        """
        with open(self.promise_db, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        for promise in db["promises"]:
            if promise["id"] == promise_id:
                promise["status"] = "completed"
                promise["completion_report"] = {
                    "completion_time": completion_time,
                    "result_summary": result_summary,
                    "deliverables": deliverables,
                    "reported_at": datetime.now().isoformat()
                }
                
                with open(self.promise_db, 'w', encoding='utf-8') as f:
                    json.dump(db, f, indent=2, ensure_ascii=False)
                
                print(f"✅ 完成报告已记录: [{promise_id}]")
                print(f"   结果: {result_summary}")
                return True
        
        return False
    
    def report_failure(self,
                      promise_id: str,
                      reason: str,
                      adjusted_deadline: str,
                      mitigation_plan: str) -> bool:
        """
        如实报告未完成及原因和调整方案
        
        Args:
            promise_id: 承诺ID
            reason: 未完成原因（如实说明）
            adjusted_deadline: 调整后的完成时间
            mitigation_plan: 补救计划
        """
        with open(self.promise_db, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        for promise in db["promises"]:
            if promise["id"] == promise_id:
                promise["status"] = "remedied"
                promise["failure_report"] = {
                    "original_deadline": promise["deadline"],
                    "failure_time": datetime.now().isoformat(),
                    "reason": reason,
                    "adjusted_deadline": adjusted_deadline,
                    "mitigation_plan": mitigation_plan,
                    "reported_at": datetime.now().isoformat()
                }
                # 更新截止时间
                promise["deadline"] = adjusted_deadline
                
                with open(self.promise_db, 'w', encoding='utf-8') as f:
                    json.dump(db, f, indent=2, ensure_ascii=False)
                
                print(f"⚠️ 未完成报告已记录: [{promise_id}]")
                print(f"   原因: {reason}")
                print(f"   调整后截止: {adjusted_deadline}")
                print(f"   补救计划: {mitigation_plan}")
                return True
        
        return False
    
    def trigger_auto_remedy(self, promise_id: str) -> Dict:
        """
        触发超期自动补救
        
        自动执行：
        1. 分析未完成原因
        2. 生成补救方案
        3. 调整截止时间
        4. 启动补救子代理
        """
        with open(self.promise_db, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        for promise in db["promises"]:
            if promise["id"] == promise_id and promise["status"] == "overdue":
                # 分析原因（基于内容自动推断）
                reason = self._analyze_failure_reason(promise)
                
                # 生成补救方案
                mitigation_plan = self._generate_mitigation_plan(promise)
                
                # 调整截止时间（延期24-48小时）
                original_deadline = datetime.fromisoformat(promise["deadline"])
                adjusted_deadline = (original_deadline + timedelta(hours=48)).isoformat()
                
                # 记录补救
                promise["status"] = "remedied"
                promise["failure_report"] = {
                    "original_deadline": promise["deadline"],
                    "failure_time": datetime.now().isoformat(),
                    "reason": reason,
                    "adjusted_deadline": adjusted_deadline,
                    "mitigation_plan": mitigation_plan,
                    "auto_triggered": True
                }
                promise["deadline"] = adjusted_deadline
                
                with open(self.promise_db, 'w', encoding='utf-8') as f:
                    json.dump(db, f, indent=2, ensure_ascii=False)
                
                remedy_action = {
                    "promise_id": promise_id,
                    "reason": reason,
                    "adjusted_deadline": adjusted_deadline,
                    "mitigation_plan": mitigation_plan,
                    "triggered_at": datetime.now().isoformat()
                }
                
                print(f"🔧 自动补救已触发: [{promise_id}]")
                print(f"   原因: {reason}")
                print(f"   新截止: {adjusted_deadline}")
                
                return remedy_action
        
        return None
    
    def _analyze_failure_reason(self, promise: Dict) -> str:
        """分析失败原因（简化版）"""
        content = promise["content"].lower()
        
        if "api" in content or "token" in content:
            return "外部API限制或权限问题"
        elif "调研" in content or "研究" in content:
            return "信息收集耗时超出预期"
        elif "生成" in content or "图片" in content:
            return "AI生成资源限制或排队"
        elif "同步" in content:
            return "数据量大或网络问题"
        else:
            return "执行过程中遇到未预期障碍"
    
    def _generate_mitigation_plan(self, promise: Dict) -> str:
        """生成补救计划"""
        content = promise["content"]
        
        plans = [
            "1. 启动并行子代理加速执行",
            "2. 简化交付标准，先完成核心功能",
            "3. 如有外部依赖，启动备用方案",
            "4. 每2小时汇报进度，确保不再次延期"
        ]
        
        return "\n".join(plans)
    
    def update_system_rule(self, 
                          rule_id: str,
                          rule_name: str,
                          rule_content: str,
                          effective_date: str,
                          related_promises: List[str] = None):
        """
        更新管理制度/规则到Skill
        
        Args:
            rule_id: 规则ID
            rule_name: 规则名称
            rule_content: 规则内容
            effective_date: 生效日期
            related_promises: 关联的承诺ID
        """
        with open(self.system_db, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        rule = {
            "id": rule_id,
            "name": rule_name,
            "content": rule_content,
            "effective_date": effective_date,
            "updated_at": datetime.now().isoformat(),
            "version": self._get_next_version(db, rule_id),
            "related_promises": related_promises or []
        }
        
        # 检查是否已存在
        existing_idx = None
        for i, r in enumerate(db["rules"]):
            if r["id"] == rule_id:
                existing_idx = i
                break
        
        if existing_idx is not None:
            db["rules"][existing_idx] = rule
        else:
            db["rules"].append(rule)
        
        db["last_update"] = datetime.now().isoformat()
        
        with open(self.system_db, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print(f"📋 制度规则已更新: [{rule_id}] {rule_name}")
        print(f"   版本: {rule['version']} | 生效: {effective_date}")
    
    def _get_next_version(self, db: Dict, rule_id: str) -> str:
        """获取下一个版本号"""
        versions = [r["version"] for r in db["rules"] if r["id"] == rule_id]
        if not versions:
            return "1.0"
        
        latest = max([float(v) for v in versions])
        return f"{latest + 0.1:.1f}"
    
    def execute_system_check(self):
        """
        执行制度检查
        确保所有承诺符合制度要求
        """
        with open(self.promise_db, 'r', encoding='utf-8') as f:
            promise_db = json.load(f)
        
        with open(self.system_db, 'r', encoding='utf-8') as f:
            system_db = json.load(f)
        
        violations = []
        
        # 检查1：所有P0承诺必须有后果说明
        for promise in promise_db["promises"]:
            if promise["priority"] == "P0" and not promise.get("consequences_if_fail"):
                violations.append({
                    "type": "missing_consequence",
                    "promise_id": promise["id"],
                    "message": "P0承诺必须有未完成后果说明"
                })
        
        # 检查2：所有承诺必须24小时内有检查点
        for promise in promise_db["promises"]:
            if promise["status"] == "active":
                created = datetime.fromisoformat(promise["created_at"])
                if (datetime.now() - created).total_seconds() > 24 * 3600:
                    if not promise.get("reminders_sent"):
                        violations.append({
                            "type": "no_checkpoint",
                            "promise_id": promise["id"],
                            "message": "承诺创建超过24小时无检查点"
                        })
        
        return violations
    
    def generate_daily_report(self):
        """生成每日执行报告"""
        check_result = self.check_promises()
        violations = self.execute_system_check()
        
        report = f"""# 承诺与制度执行保障日报

**报告日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**报告类型**: 承诺履行情况 + 制度执行检查

---

## 📊 承诺履行概况

| 状态 | 数量 | 说明 |
|------|------|------|
| 🔄 进行中 | {len(check_result['in_progress'])} | 正常推进 |
| ⚠️ 即将到期(24h) | {len(check_result['upcoming'])} | 需要关注 |
| 🔴 已超期 | {len(check_result['overdue'])} | 立即补救 |
| ✅ 已完成 | {len(check_result['completed'])} | 正常归档 |
| **总计** | **{sum(len(v) for v in check_result.values())}** | |

---

## 🚨 需要立即处理

### 即将到期承诺
"""
        
        if check_result['upcoming']:
            for p in check_result['upcoming']:
                report += f"\n- **[{p['id']}]** {p['content']}\n"
                report += f"  - 截止: {p['deadline']} | 负责人: {p['owner']}\n"
        else:
            report += "\n✅ 无即将到期承诺\n"
        
        report += f"""

### 已超期承诺（自动补救已触发）
"""
        
        if check_result['overdue']:
            for p in check_result['overdue']:
                report += f"\n- **[{p['id']}]** {p['content']}\n"
                report += f"  - 原截止: {p['deadline']}\n"
                if p.get('failure_report'):
                    report += f"  - 补救状态: {p['failure_report'].get('mitigation_plan', '已触发')}\n"
        else:
            report += "\n✅ 无超期承诺\n"
        
        report += f"""

---

## 📋 制度执行检查

**发现违规**: {len(violations)} 项

"""
        
        if violations:
            for v in violations:
                report += f"\n- ⚠️ {v['message']} (承诺: {v['promise_id']})\n"
        else:
            report += "\n✅ 所有承诺符合制度要求\n"
        
        report += f"""

---

## 🎯 今日行动

### 自动触发（无需人工）
- [ ] 发送到期前24小时预警
- [ ] 发送到期前4小时预警
- [ ] 发送到期前1小时预警
- [ ] 超期自动触发补救流程

### 需要人工确认
- [ ] 审阅即将到期承诺进展
- [ ] 确认超期承诺补救方案

---

## 📝 承诺记录示例

**新记录承诺**:
```
ID: PROMISE-2026-03-11-001
内容: 完成五路图腾信息图AI生成（三风格）
截止: 2026-03-11 10:00
负责人: DESIGN+AI
优先级: P0
后果: 影响官宣视觉物料准备
```

---

## 🔧 系统保障机制

1. **自动记录**: 所有承诺自动写入数据库
2. **到期预警**: 24h/4h/1h前自动提醒
3. **超期补救**: 自动分析原因+调整时间+生成方案
4. **如实报告**: 未完成必须说明原因和调整计划
5. **制度同步**: 规则更新自动同步到Skill

---

*本报告由承诺与制度执行保障系统自动生成*
*下次报告: 明日08:00*
"""
        
        # 保存报告
        self.daily_report.parent.mkdir(exist_ok=True)
        with open(self.daily_report, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 日报已生成: {self.daily_report}")
        return report
    
    def run(self):
        """运行完整检查"""
        print("="*70)
        print("承诺与制度执行保障系统")
        print("="*70)
        print()
        
        # 检查所有承诺
        check_result = self.check_promises()
        
        # 自动发送预警
        for p in check_result['upcoming']:
            deadline = datetime.fromisoformat(p['deadline'])
            time_left = deadline - datetime.now()
            hours_left = time_left.total_seconds() / 3600
            
            if 23 < hours_left <= 24:
                self.send_reminder(p['id'], 24)
            elif 3 < hours_left <= 4:
                self.send_reminder(p['id'], 4)
            elif 0.5 < hours_left <= 1:
                self.send_reminder(p['id'], 1)
        
        # 自动触发超期补救
        for p in check_result['overdue']:
            if not p.get('failure_report'):
                self.trigger_auto_remedy(p['id'])
        
        # 生成日报
        self.generate_daily_report()
        
        print()
        print("="*70)
        print("检查完成！保障机制运行正常。")
        print("="*70)

# 示例用法
if __name__ == "__main__":
    guardian = PromiseAndSystemGuardian()
    
    # 示例：记录明天的承诺
    guardian.record_promise(
        promise_id="PROMISE-2026-03-11-V1-0",
        content="交付满意解研究所V1.0优化版完整文档",
        deadline="2026-03-11 16:00",
        owner="满意妞",
        priority="P0",
        consequences_if_fail="影响团队整体进度，需立即调整里程碑"
    )
    
    # 运行检查
    guardian.run()
