#!/usr/bin/env python3
"""
制度规则执行引擎
将管理制度拆解为可执行的小规则
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class RuleExecutionEngine:
    """制度规则执行引擎"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.rules_db = self.workspace / "memory" / "rule_execution_db.json"
        self.violations_log = self.workspace / "memory" / "rule_violations.json"
        self._init_db()
        
        # 7大制度规则定义
        self.rules = {
            "RULE-001-沟通规则": {
                "name": "沟通规则执行器",
                "rules": [
                    {
                        "id": "R1-1",
                        "content": "汇报层级规则：L1指挥官/L2满意妞/L3角色间",
                        "check_method": "检查汇报对象是否正确",
                        "violation_example": "绕过满意妞直接向指挥官汇报P2任务",
                        "auto_check": False,  # 需要语义理解
                        "priority": "P1"
                    },
                    {
                        "id": "R1-2",
                        "content": "响应时效规则：紧急即时/重要2h/常规4h/非紧急24h",
                        "check_method": "检查响应时间",
                        "auto_check": True,
                        "thresholds": {"紧急": 0, "重要": 7200, "常规": 14400, "非紧急": 86400},
                        "priority": "P0"
                    },
                    {
                        "id": "R1-3",
                        "content": "简洁明确规则：汇报包含现状-问题-建议三部分",
                        "check_method": "检查汇报结构",
                        "auto_check": False,
                        "priority": "P2"
                    },
                    {
                        "id": "R1-4",
                        "content": "主动汇报规则：任务状态变更立即通知",
                        "check_method": "检查状态变更后是否在1小时内汇报",
                        "auto_check": True,
                        "threshold": 3600,
                        "priority": "P1"
                    }
                ]
            },
            
            "RULE-002-任务生命周期": {
                "name": "任务生命周期管理器",
                "rules": [
                    {
                        "id": "R2-1",
                        "content": "任务必须有状态标签：待启动/进行中/待验收/已完成/已暂停/已取消",
                        "check_method": "检查TASK_MASTER.md中任务是否有状态",
                        "auto_check": True,
                        "priority": "P0"
                    },
                    {
                        "id": "R2-2",
                        "content": "状态转移必须经过确认：创建→确认→执行→验收→归档",
                        "check_method": "检查状态转移是否合规",
                        "auto_check": True,
                        "priority": "P1"
                    },
                    {
                        "id": "R2-3",
                        "content": "所有任务必须有优先级：P0紧急/P1高优/P2正常/P3低优/P4备忘",
                        "check_method": "检查优先级字段",
                        "auto_check": True,
                        "priority": "P0"
                    },
                    {
                        "id": "R2-4",
                        "content": "所有承诺必须有截止日期和后果说明",
                        "check_method": "检查promise_database.json",
                        "auto_check": True,
                        "priority": "P0"
                    }
                ]
            },
            
            "RULE-003-报告机制": {
                "name": "报告机制执行器",
                "rules": [
                    {
                        "id": "R3-1",
                        "content": "晨报每日09:00生成，包含今日重点/昨日完成/风险",
                        "check_method": "检查reports/下是否有当日晨报",
                        "auto_check": True,
                        "schedule": "09:00",
                        "priority": "P0"
                    },
                    {
                        "id": "R3-2",
                        "content": "日报每日23:59生成，33角色全景状态",
                        "check_method": "检查日报是否存在",
                        "auto_check": True,
                        "schedule": "23:59",
                        "priority": "P1"
                    },
                    {
                        "id": "R3-3",
                        "content": "周报每周日20:00，周进展+下周计划",
                        "check_method": "检查周日是否有周报",
                        "auto_check": True,
                        "schedule": "周日20:00",
                        "priority": "P1"
                    },
                    {
                        "id": "R3-4",
                        "content": "里程碑报告达成时立即生成",
                        "check_method": "检查里程碑任务完成后是否有报告",
                        "auto_check": True,
                        "trigger": "milestone_complete",
                        "priority": "P0"
                    }
                ]
            },
            
            "RULE-004-记忆更新": {
                "name": "记忆更新规则执行器",
                "rules": [
                    {
                        "id": "R4-1",
                        "content": "每次对话结束必须更新MEMORY.md",
                        "check_method": "检查最后对话时间与MEMORY.md修改时间",
                        "auto_check": True,
                        "tolerance": 300,  # 5分钟容差
                        "priority": "P1"
                    },
                    {
                        "id": "R4-2",
                        "content": "每日必须创建memory/YYYY-MM-DD.md",
                        "check_method": "检查当日日志文件是否存在",
                        "auto_check": True,
                        "schedule": "每日23:59",
                        "priority": "P0"
                    },
                    {
                        "id": "R4-3",
                        "content": "MEMORY.md整理频率：每3天一次",
                        "check_method": "检查最后整理时间",
                        "auto_check": True,
                        "interval": 259200,  # 3天
                        "priority": "P2"
                    },
                    {
                        "id": "R4-4",
                        "content": "被遗忘任务扫描：每日一次",
                        "check_method": "检查遗忘任务扫描记录",
                        "auto_check": True,
                        "schedule": "每日10:00",
                        "priority": "P1"
                    }
                ]
            },
            
            "RULE-005-安全规则": {
                "name": "安全规则执行器",
                "rules": [
                    {
                        "id": "R5-1",
                        "content": "权限分级：公开/内部/机密/绝密",
                        "check_method": "检查文档是否有分级标签",
                        "auto_check": True,
                        "priority": "P0"
                    },
                    {
                        "id": "R5-2",
                        "content": "敏感操作必须二次确认",
                        "check_method": "记录敏感操作确认状态",
                        "auto_check": False,  # 需要交互
                        "priority": "P0"
                    },
                    {
                        "id": "R5-3",
                        "content": "每日安全检查：22:00自动执行",
                        "check_method": "检查安全检查记录",
                        "auto_check": True,
                        "schedule": "22:00",
                        "priority": "P0"
                    },
                    {
                        "id": "R5-4",
                        "content": "对外发送必须经审核",
                        "check_method": "检查对外内容的审核标记",
                        "auto_check": False,  # 需要人工审核
                        "priority": "P0"
                    }
                ]
            },
            
            "RULE-006-质量规则": {
                "name": "质量规则执行器",
                "rules": [
                    {
                        "id": "R6-1",
                        "content": "三级把关：自检→Peer Review→专家",
                        "check_method": "检查产出是否有三级把关记录",
                        "auto_check": True,
                        "priority": "P0"
                    },
                    {
                        "id": "R6-2",
                        "content": "对外内容必须经蓝军审查",
                        "check_method": "检查对外内容是否有蓝军标记",
                        "auto_check": True,
                        "priority": "P0"
                    },
                    {
                        "id": "R6-3",
                        "content": "虚假信息防范：所有数据有来源",
                        "check_method": "检查引用标注",
                        "auto_check": False,  # 需要语义分析
                        "priority": "P0"
                    },
                    {
                        "id": "R6-4",
                        "content": "引用规范：一级官方/二级行业/三级网络",
                        "check_method": "检查引用级别标注",
                        "auto_check": True,
                        "priority": "P1"
                    }
                ]
            },
            
            "RULE-007-执行纪律": {
                "name": "执行纪律监督器",
                "rules": [
                    {
                        "id": "R7-1",
                        "content": "承诺必达：所有承诺必须有截止+后果",
                        "check_method": "检查promise_database.json",
                        "auto_check": True,
                        "priority": "P0"
                    },
                    {
                        "id": "R7-2",
                        "content": "遗忘补救：发现遗忘立即补救+记录",
                        "check_method": "检查是否有遗忘任务补救记录",
                        "auto_check": True,
                        "priority": "P0"
                    },
                    {
                        "id": "R7-3",
                        "content": "提前预警：无法完成必须提前24h预警",
                        "check_method": "检查是否有提前预警记录",
                        "auto_check": True,
                        "threshold": 86400,
                        "priority": "P0"
                    },
                    {
                        "id": "R7-4",
                        "content": "如实报告：未完成必须说明原因+调整",
                        "check_method": "检查failure_report是否完整",
                        "auto_check": True,
                        "priority": "P0"
                    }
                ]
            }
        }
    
    def _init_db(self):
        """初始化数据库"""
        if not self.rules_db.exists():
            default = {
                "version": "1.0",
                "rules_status": {},
                "execution_history": [],
                "last_check": None
            }
            self.rules_db.parent.mkdir(exist_ok=True)
            with open(self.rules_db, 'w', encoding='utf-8') as f:
                json.dump(default, f, indent=2, ensure_ascii=False)
        
        if not self.violations_log.exists():
            default = {
                "violations": [],
                "statistics": {"total": 0, "by_rule": {}}
            }
            with open(self.violations_log, 'w', encoding='utf-8') as f:
                json.dump(default, f, indent=2, ensure_ascii=False)
    
    def execute_all_rules(self):
        """执行所有规则检查"""
        print("="*70)
        print("制度规则执行引擎 - 全面检查")
        print("="*70)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print()
        
        total_rules = 0
        auto_check_rules = 0
        violations_found = []
        
        for rule_category, rule_info in self.rules.items():
            print(f"\n【{rule_info['name']}】")
            print("-"*70)
            
            for rule in rule_info['rules']:
                total_rules += 1
                status = "✅ 通过" if rule.get('auto_check') else "⏸️ 需人工"
                
                if rule.get('auto_check'):
                    auto_check_rules += 1
                    # 这里应该实现具体的自动检查逻辑
                    # 简化版：只显示待实现
                    status = "🔄 自动检查待实现"
                
                print(f"  {rule['id']}: {rule['content'][:40]}...")
                print(f"     状态: {status} | 优先级: {rule['priority']}")
        
        print("\n" + "="*70)
        print(f"统计: 总规则 {total_rules} | 可自动检查 {auto_check_rules} | 需人工 {total_rules-auto_check_rules}")
        print("="*70)
        
        return {
            "total_rules": total_rules,
            "auto_check_rules": auto_check_rules,
            "violations": violations_found
        }
    
    def add_rule(self, category, rule_def):
        """添加新规则（增）"""
        if category not in self.rules:
            self.rules[category] = {"name": category, "rules": []}
        
        self.rules[category]["rules"].append(rule_def)
        print(f"✅ 规则已添加: {rule_def['id']}")
    
    def update_rule(self, rule_id, updates):
        """更新规则（改）"""
        for category, rule_info in self.rules.items():
            for i, rule in enumerate(rule_info['rules']):
                if rule['id'] == rule_id:
                    rule.update(updates)
                    print(f"✅ 规则已更新: {rule_id}")
                    return True
        return False
    
    def delete_rule(self, rule_id):
        """删除规则（删）"""
        for category, rule_info in self.rules.items():
            for i, rule in enumerate(rule_info['rules']):
                if rule['id'] == rule_id:
                    del rule_info['rules'][i]
                    print(f"✅ 规则已删除: {rule_id}")
                    return True
        return False
    
    def export_rules_to_skill(self):
        """导出规则到Skill文件"""
        output_file = self.workspace / "skills" / "rule-execution-engine" / "active_rules.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.rules, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 规则已导出: {output_file}")

if __name__ == "__main__":
    engine = RuleExecutionEngine()
    engine.execute_all_rules()
    engine.export_rules_to_skill()
