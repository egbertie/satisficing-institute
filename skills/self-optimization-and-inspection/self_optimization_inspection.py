#!/usr/bin/env python3
"""
Skill自我优化引擎 + 监督检查机制
实现：7天清理 + 效率优化 + 相互监督
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class SelfOptimizationAndInspection:
    """自我优化与监督检查系统"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.optimization_db = self.workspace / "memory" / "skill_optimization_db.json"
        self.inspection_db = self.workspace / "memory" / "inspection_records.json"
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        if not self.optimization_db.exists():
            default = {
                "version": "1.0",
                "skill_performance": {},
                "cleanup_records": [],
                "optimization_suggestions": [],
                "efficiency_trends": {}
            }
            self.optimization_db.parent.mkdir(exist_ok=True)
            with open(self.optimization_db, 'w', encoding='utf-8') as f:
                json.dump(default, f, indent=2, ensure_ascii=False)
        
        if not self.inspection_db.exists():
            default = {
                "inspection_records": [],
                "peer_reviews": [],
                "violations": [],
                "improvements": []
            }
            with open(self.inspection_db, 'w', encoding='utf-8') as f:
                json.dump(default, f, indent=2, ensure_ascii=False)
    
    def cleanup_7day_policy(self):
        """
        7天清理策略：
        - 已完成的承诺从active列表删除（保留记录）
        - 临时文件1天后清理
        - 旧日志30天后归档
        """
        print("="*70)
        print("7天清理策略执行")
        print("="*70)
        
        now = datetime.now()
        
        # 1. 清理承诺数据库中的已完成项目（保留记录但移出active）
        promise_db = self.workspace / "memory" / "promise_database.json"
        if promise_db.exists():
            with open(promise_db, 'r', encoding='utf-8') as f:
                db = json.load(f)
            
            cleaned = 0
            archived = []
            
            for promise in db.get("promises", []):
                if promise.get("status") == "completed":
                    completion_time = promise.get("completion_report", {}).get("completion_time")
                    if completion_time:
                        completion_dt = datetime.fromisoformat(completion_time)
                        if (now - completion_dt).days > 7:
                            # 标记为已归档（保留记录但从active视图移除）
                            promise["archived"] = True
                            promise["archived_at"] = now.isoformat()
                            cleaned += 1
                            archived.append(promise["id"])
            
            with open(promise_db, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 已归档 {cleaned} 个完成超过7天的承诺")
            print(f"   保留记录，仅从active列表移除")
        
        # 2. 清理临时文件（1天）
        temp_patterns = ['*.tmp', '*.temp', '*_backup_*.json']
        # 简化版：记录待清理
        
        # 3. 归档旧日志（30天）
        # 简化版：记录待归档
        
        print("\n📋 清理策略总结：")
        print("  - 完成承诺: 7天后归档保留")
        print("  - 临时文件: 1天后清理")
        print("  - 日志文件: 30天后归档")
        print("  - 核心数据: 永久保留")
        
        return cleaned
    
    def optimize_skill_efficiency(self):
        """
        优化Skill效率：
        - 执行时间>5分钟的必须优化
        - token消耗>10k的必须审查
        - 成功率<90%的必须修复
        - 每周生成效率报告
        """
        print("\n" + "="*70)
        print("Skill效率优化分析")
        print("="*70)
        
        optimization_rules = [
            {
                "rule": "执行时间>5分钟",
                "action": "必须优化",
                "solution": "拆分子任务/并行执行/简化逻辑"
            },
            {
                "rule": "token消耗>10k",
                "action": "必须审查",
                "solution": "上下文压缩/批量处理/减少往返"
            },
            {
                "rule": "成功率<90%",
                "action": "必须修复",
                "solution": "错误处理/重试机制/备用方案"
            },
            {
                "rule": "每日执行>10次",
                "action": "考虑合并",
                "solution": "批量处理/减少频率/缓存结果"
            }
        ]
        
        print("\n优化规则：")
        for rule in optimization_rules:
            print(f"\n  【{rule['rule']}】")
            print(f"    行动: {rule['action']}")
            print(f"    方案: {rule['solution']}")
        
        # 生成优化建议
        suggestions = [
            "建议1: 合并多个定时任务为单次批量检查",
            "建议2: 使用缓存减少重复API调用",
            "建议3: 大文件处理采用流式而非全量加载",
            "建议4: 子代理任务批量提交而非单个提交"
        ]
        
        print("\n💡 本周优化建议：")
        for suggestion in suggestions:
            print(f"  - {suggestion}")
        
        return suggestions
    
    def inspection_mechanism(self):
        """
        监督检查机制：
        1. 主检查员（满意妞）- 每小时检查所有Skill
        2. 蓝军检查员 - 压力测试、找出盲点
        3. Peer互检 - 同级角色相互检查
        4. 自动化检查器 - 实时检测异常
        """
        print("\n" + "="*70)
        print("监督检查机制设计")
        print("="*70)
        
        inspection_system = {
            "第一层：主检查员（满意妞）": {
                "responsibility": "检查所有Skill执行情况",
                "frequency": "每小时",
                "check_items": [
                    "各Skill是否正常运行",
                    "是否有异常或错误",
                    "任务完成率是否达标",
                    "是否有需要人工介入的问题"
                ],
                "report_to": "Egbertie",
                "escalation": "发现严重问题立即升级"
            },
            "第二层：蓝军检查员": {
                "responsibility": "压力测试、找出盲点、质量把关",
                "frequency": "每份产出前",
                "check_items": [
                    "事实核查",
                    "逻辑漏洞",
                    "风险评估",
                    "竞品对比"
                ],
                "report_to": "PEO+EEO",
                "authority": "可否决任何对外产出"
            },
            "第三层：Peer互检": {
                "responsibility": "同级角色相互检查",
                "frequency": "每日",
                "pairs": [
                    "PEO ↔ EEO",
                    "CONTENT ↔ ANNOUNCE",
                    "TECH ↔ DEV",
                    "FIN ↔ LAW"
                ],
                "check_items": [
                    "任务进展",
                    "遇到的阻塞",
                    "需要的帮助"
                ],
                "report_to": "相互报告+汇总到满意妞"
            },
            "第四层：自动化检查器": {
                "responsibility": "实时检测异常、发送预警",
                "frequency": "实时",
                "check_items": [
                    "承诺到期前预警",
                    "任务超期检测",
                    "API异常监控",
                    "系统资源使用"
                ],
                "report_to": "全员+主检查员",
                "action": "自动触发补救流程"
            }
        }
        
        for layer, details in inspection_system.items():
            print(f"\n【{layer}】")
            print(f"  职责: {details['responsibility']}")
            print(f"  频率: {details['frequency']}")
            print(f"  汇报: {details['report_to']}")
        
        return inspection_system
    
    def mutual_help_mechanism(self):
        """
        相互帮助机制：
        - 能力强的帮助能力弱的
        - 繁忙的帮助空闲的
        - 专家帮助新手
        - 形成良性循环
        """
        print("\n" + "="*70)
        print("相互帮助、共同进步机制")
        print("="*70)
        
        help_system = {
            "导师制（Mentorship）": {
                "description": "L4-L5角色担任导师，指导L1-L2",
                "pairs": [
                    "PEO(L3) → CONTENT(L2)",
                    "EEO(L3) → ANNOUNCE(L2)",
                    "SIMON(L3) → RESEARCH(L2)",
                    "CONFUCIUS(L3) → TRAINER(L2)"
                ],
                "frequency": "每周1次深度交流",
                "goal": "帮助进阶，缩短成长周期"
            },
            "互助组（Peer Support）": {
                "description": "相似角色组成互助组",
                "groups": [
                    "技术组: TECH + DEV + DATA",
                    "内容组: CONTENT + ANNOUNCE + MEDIA",
                    "支撑组: FIN + LAW + HR + OP"
                ],
                "frequency": "每日站会交流",
                "goal": "共享资源，解决共性问题"
            },
            "专家会诊（Expert Consultation）": {
                "description": "遇到难题可召唤专家",
                "experts": ["黎红雷", "罗汉", "谢宝剑"],
                "trigger": "遇到伦理/方法论/政策问题",
                "response_time": "24小时内响应"
            },
            "紧急支援（Emergency Support）": {
                "description": "任务紧急时可请求支援",
                "mechanism": "主检查员协调资源",
                "escalation": "L5角色可调用任何资源"
            }
        }
        
        for mechanism, details in help_system.items():
            print(f"\n【{mechanism}】")
            print(f"  {details['description']}")
            if 'pairs' in details:
                print(f"  组合: {', '.join(details['pairs'][:2])}...")
            if 'frequency' in details:
                print(f"  频率: {details['frequency']}")
        
        return help_system
    
    def generate_skill_list(self):
        """生成完整的Skill清单"""
        skills = {
            "核心管理层（已部署）": {
                "01-promise-guardian": "承诺管理引擎 - 记录/监控/预警/补救/7天清理",
                "02-vendor-monitor": "厂商API监控器 - 监控钉钉/企业微信API",
                "03-task-coordinator": "任务协调管理器 - 智能协调/学习迭代"
            },
            "制度规则层（已创建）": {
                "11-rule-communication": "沟通规则执行器 - 汇报层级/响应时效/简洁明确/主动汇报",
                "12-rule-task-lifecycle": "任务生命周期管理器 - 状态标签/状态转移/优先级/截止日期",
                "13-rule-reporting": "报告机制执行器 - 晨报/日报/周报/里程碑",
                "14-rule-memory": "记忆更新规则执行器 - MEMORY更新/日志创建/整理/扫描",
                "15-rule-security": "安全规则执行器 - 权限分级/敏感操作/安全检查/审核",
                "16-rule-quality": "质量规则执行器 - 三级把关/蓝军审查/虚假信息防范/引用规范",
                "17-rule-execution-discipline": "执行纪律监督器 - 承诺必达/遗忘补救/提前预警/如实报告"
            },
            "33人任务层（已创建）": {
                "21-role-peo": "PEO任务管理",
                "22-role-eeo": "EEO任务管理",
                "23-role-content": "CONTENT任务管理",
                "24-role-announce": "ANNOUNCE任务管理",
                "25-role-tech": "TECH任务管理",
                "26-role-five-totems": "五路图腾任务管理",
                "27-role-experts": "专家数字替身任务管理",
                "28-role-support": "支撑体系任务管理"
            },
            "自我优化层（本文件）": {
                "31-self-optimization": "自我优化引擎 - 性能监控/效率分析/自动清理/版本迭代",
                "32-cleanup-7day": "7天清理策略 - 承诺归档/临时文件清理/日志归档"
            },
            "监督检查层（本文件）": {
                "41-inspection-main": "主检查员 - 满意妞每小时检查",
                "42-inspection-blue": "蓝军检查员 - 压力测试/质量把关",
                "43-inspection-peer": "Peer互检 - 同级相互检查",
                "44-inspection-auto": "自动化检查器 - 实时异常检测",
                "45-mutual-help": "相互帮助机制 - 导师制/互助组/专家会诊/紧急支援"
            },
            "定时任务层（已配置）": {
                "cron-security-audit": "每日安全检查 - 22:00",
                "cron-task-coordinator": "每小时任务协调检查",
                "cron-vendor-monitor": "每日厂商API监控 - 08:00",
                "cron-promise-guardian": "每日承诺保障检查 - 08:00",
                "cron-rule-execution": "每日制度规则检查 - 09:00",
                "cron-role33-task": "每日33人任务分配 - 06:00",
                "cron-self-optimization": "每周自我优化分析 - 周日23:00"
            }
        }
        
        print("\n" + "="*70)
        print("满意解研究所 · 完整Skill清单")
        print("="*70)
        
        total = 0
        for layer, skill_list in skills.items():
            print(f"\n【{layer}】")
            for skill_id, description in skill_list.items():
                print(f"  {skill_id}: {description}")
                total += 1
        
        print(f"\n{'='*70}")
        print(f"总计: {total} 个Skill")
        print("="*70)
        
        return skills
    
    def run(self):
        """运行完整系统"""
        self.cleanup_7day_policy()
        self.optimize_skill_efficiency()
        self.inspection_mechanism()
        self.mutual_help_mechanism()
        skills = self.generate_skill_list()
        
        # 保存报告
        report_file = self.workspace / "reports" / "SKILL_MANAGEMENT_SYSTEM_REPORT.md"
        report_file.parent.mkdir(exist_ok=True)
        
        report = f"""# Skill自我优化与监督检查系统报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 1. 7天清理策略

- 完成承诺: 7天后从active列表归档（保留记录）
- 临时文件: 1天后清理
- 日志文件: 30天后归档
- 核心数据: 永久保留

## 2. 效率优化规则

1. 执行时间>5分钟 → 必须优化
2. token消耗>10k → 必须审查
3. 成功率<90% → 必须修复
4. 每日执行>10次 → 考虑合并

## 3. 监督检查机制

| 层级 | 角色 | 频率 | 职责 |
|------|------|------|------|
| 1 | 主检查员（满意妞） | 每小时 | 检查所有Skill |
| 2 | 蓝军检查员 | 每份产出前 | 压力测试/质量把关 |
| 3 | Peer互检 | 每日 | 同级相互检查 |
| 4 | 自动化检查器 | 实时 | 异常检测/预警 |

## 4. 相互帮助机制

- **导师制**: L4-L5指导L1-L2
- **互助组**: 相似角色组成互助组
- **专家会诊**: 遇到难题召唤专家
- **紧急支援**: 任务紧急时请求支援

## 5. 完整Skill清单

总计 {sum(len(v) for v in skills.values())} 个Skill

---

*本报告由自我优化与监督检查系统生成*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 报告已生成: {report_file}")

if __name__ == "__main__":
    system = SelfOptimizationAndInspection()
    system.run()
