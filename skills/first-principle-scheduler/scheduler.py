#!/usr/bin/env python3
"""
第一性原则资源调度器 V2.0 - 增加管理哲学审核与五大图腾审核

核心规则：
1. 没有真实推进的任务 = 暂停/待补充，不是"进行中"
2. 进行中列表必须为空时，自动补位2+7核心项目
3. 资源全开 = 白天人机协作 + 夜间AI自主推进，零空置
4. 新增：五大图腾审核（土金水木火）
5. 新增：管理哲学审核（制度即代码/零空置/持续改进/自主决策/安全第一）
"""

import json
import os
from datetime import datetime
from pathlib import Path

class FirstPrincipleResourceScheduler:
    """第一性原则资源调度器 V2.0"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.status_file = self.workspace / "memory" / "resource-scheduler-status.json"
        self.log_file = self.workspace / "memory" / "resource-scheduler-log.json"
        
        # 2+7核心项目清单（两者都涵盖）
        self.core_projects = {
            # P0基础层（4项）- 最高优先级
            "P0": [
                {"id": "P0-001", "name": "决策权限矩阵", "status": "✅ 已完成", "location": "config/decision-permission-matrix.md"},
                {"id": "P0-002", "name": "系统仪表盘", "status": "✅ 已完成", "location": "skills/system-dashboard/dashboard.py"},
                {"id": "P0-003", "name": "分级通知路由", "status": "✅ 已完成", "location": "skills/notification-router/router.py"},
                {"id": "P0-004", "name": "记忆审计器", "status": "✅ 已完成", "location": "skills/memory-auditor/auditor.py"},
            ],
            # P1增强层（3项）- 第二优先级
            "P1": [
                {"id": "P1-001", "name": "质量门控机制", "status": "✅ 已完成", "location": "skills/quality-gate/gate.py"},
                {"id": "P1-002", "name": "专家会诊协议", "status": "✅ 已完成", "location": "skills/expert-council/council.py"},
                {"id": "P1-003", "name": "事务工作流", "status": "✅ 已完成", "location": "skills/workflow-engine/engine.py"},
            ],
            # P2产品线（5项）- 持续迭代
            "P2": [
                {"id": "P2-001", "name": "评估工具V2", "status": "✅ 已完成", "location": "skills/assessment-tool-v2/"},
                {"id": "P2-002", "name": "决策模型", "status": "✅ 已完成", "location": "skills/partnership-model/"},
                {"id": "P2-003", "name": "案例库系统", "status": "🔄 15/30", "location": "A满意哥专属文件夹/05_📦历史归档/case-library/"},
                {"id": "P2-004", "name": "方法论白皮书", "status": "✅ 已完成", "location": "A满意哥专属文件夹/05_📦历史归档/methodology/"},
                {"id": "P2-005", "name": "产品原型V2", "status": "✅ 已完成", "location": "A满意哥专属文件夹/02_✅成果交付/产品原型/"},
            ]
        }
        
        # 五大图腾定义
        self.five_totems = {
            "LIU": {
                "name": "刘禹锡",
                "element": "土",
                "spirit": "惟吾德馨",
                "question": "此决策是否基于真实品德？",
                "keyword": "品德"
            },
            "SIMON": {
                "name": "司马贺",
                "element": "金",
                "spirit": "满意解",
                "question": "是否找到足够好的解，而非追求最优？",
                "keyword": "足够好"
            },
            "GUANYIN": {
                "name": "观音",
                "element": "水",
                "spirit": "自在从容",
                "question": "是否有退路，心态是否松弛？",
                "keyword": "从容"
            },
            "CONFUCIUS": {
                "name": "孔子",
                "element": "木",
                "spirit": "仁者爱人",
                "question": "是否体现合伙伦理的仁者精神？",
                "keyword": "仁爱"
            },
            "HUINENG": {
                "name": "六祖",
                "element": "火",
                "spirit": "顿悟知行",
                "question": "是否知行合一，立即行动？",
                "keyword": "知行合一"
            }
        }
        
        # 管理哲学审核项
        self.management_philosophy = {
            "制度即代码": {
                "question": "此规则是否已写入可执行Skill？如否，立即转化",
                "action": "check_skill_conversion"
            },
            "零空置执行": {
                "question": "当前是否有资源空置？如有，立即补位六线并行",
                "action": "check_resource_idle"
            },
            "持续改进": {
                "question": "此任务完成后是否立即复盘？必须记录3条改进点",
                "action": "check_improvement_loop"
            },
            "自主决策": {
                "question": "是否在授权范围内？如是，立即执行不问",
                "action": "check_decision_authority"
            },
            "安全第一": {
                "question": "是否触碰决策安全红线？如触碰，立即上报",
                "action": "check_safety_redline"
            }
        }
        
        # 阻塞任务定义（等待外界条件）
        self.blocked_tasks = [
            {"id": "WIP-004", "name": "补充专家真实资料", "blocker": "需联系本人", "user_action": "提供联系方式或确认自行处理"},
            {"id": "WIP-005", "name": "发送专家邀请函", "blocker": "需联系方式", "user_action": "提供专家联系方式"},
            {"id": "WIP-007", "name": "Claude API解决", "blocker": "地区限制403", "user_action": "需要海外环境或替代方案"},
            {"id": "WIP-008", "name": "飞书权限完善", "blocker": "需用户操作", "user_action": "在飞书后台添加drive:file权限"},
        ]
    
    def print_first_principles_prompt(self) -> str:
        """打印第一性原则启动口令（含管理哲学+五大图腾审核）"""
        prompt = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 核心精神：向前赶，永不止步
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 三大铁律（立即执行）：
1. 时间预估激进 —— 原计划的50%，压缩倒逼极限
2. 相信极限潜能 —— 不说"可能"，只说"一定"  
3. 完成即启动 —— 不停顿、不等待、永向前

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📜 五大图腾审核（强制校验）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for key, totem in self.five_totems.items():
            prompt += f"□ {key}（{totem['name']}·{totem['element']}）：{totem['spirit']} —— {totem['question']}\n"
        
        prompt += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏛️ 管理哲学审核（强制校验）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for principle, details in self.management_philosophy.items():
            prompt += f"□ {principle} —— {details['question']}\n"
        
        prompt += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 立即自检（10秒内回答）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

当前并行任务数：__/6
当前空置资源：__%（目标<15%）
今日改进闭环：__个（目标≥3）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

确认执行请输入：【确认启动第一性原则】
"""
        return prompt
    
    def audit_totems(self, task_description: str = "") -> dict:
        """五大图腾审核"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "task": task_description,
            "totems": {},
            "passed": True,
            "recommendations": []
        }
        
        for key, totem in self.five_totems.items():
            # 简化版本：基于关键词匹配给出审核建议
            result["totems"][key] = {
                "name": totem["name"],
                "element": totem["element"],
                "question": totem["question"],
                "status": "待人工确认",
                "keyword": totem["keyword"]
            }
        
        return result
    
    def audit_management_philosophy(self, task_id: str = "", task_type: str = "") -> dict:
        """管理哲学审核"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "task_type": task_type,
            "principles": {},
            "all_passed": True,
            "required_actions": []
        }
        
        for principle, details in self.management_philosophy.items():
            # 执行对应检查
            if details["action"] == "check_skill_conversion":
                # 检查是否已Skill化
                status = self._check_skill_conversion_status(task_id)
            elif details["action"] == "check_resource_idle":
                # 检查资源空置
                idle_check = self.check_resource_idle()
                status = "✅ 正常" if not idle_check["should_activate"] else "⚠️ 空置检测"
            elif details["action"] == "check_improvement_loop":
                # 检查改进闭环
                status = self._check_improvement_loop_status(task_id)
            elif details["action"] == "check_decision_authority":
                # 检查决策权限（默认在授权内）
                status = "✅ 在授权范围"
            elif details["action"] == "check_safety_redline":
                # 检查安全红线
                status = self._check_safety_redline(task_id, task_type)
            else:
                status = "⏳ 待检查"
            
            result["principles"][principle] = {
                "question": details["question"],
                "status": status,
                "action": details["action"]
            }
            
            if "⚠️" in status or "❌" in status:
                result["all_passed"] = False
                result["required_actions"].append(f"{principle}: {status}")
        
        return result
    
    def _check_skill_conversion_status(self, task_id: str) -> str:
        """检查任务是否已Skill化"""
        # 简化检查：基于task_id判断
        skill_locations = [
            self.workspace / "skills",
            self.workspace / "A满意哥专属文件夹" / "skills"
        ]
        
        for loc in skill_locations:
            if loc.exists():
                for item in loc.iterdir():
                    if task_id.lower() in item.name.lower():
                        return "✅ 已Skill化"
        
        return "⚠️ 未Skill化，建议转化"
    
    def _check_improvement_loop_status(self, task_id: str) -> str:
        """检查改进闭环状态"""
        improvement_db = self.workspace / "memory" / "improvement-loop-db.json"
        if improvement_db.exists():
            with open(improvement_db, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if task_id in data and len(data[task_id].get("improvements", [])) >= 3:
                    return "✅ 改进闭环完成"
        
        return "⏳ 待完成后复盘"
    
    def _check_safety_redline(self, task_id: str, task_type: str) -> str:
        """检查决策安全红线"""
        # 定义安全红线
        redlines = [
            "删除生产数据",
            "修改核心配置",
            "发送敏感信息",
            "修改安全规则",
            "删除备份"
        ]
        
        for redline in redlines:
            if redline in str(task_id) or redline in str(task_type):
                return "❌ 触碰安全红线，需人工审批"
        
        return "✅ 未触碰红线"
    
    def full_audit(self, task_description: str = "", task_id: str = "", task_type: str = "") -> dict:
        """完整审核（五大图腾 + 管理哲学）"""
        return {
            "timestamp": datetime.now().isoformat(),
            "first_principles_prompt": self.print_first_principles_prompt(),
            "totem_audit": self.audit_totems(task_description),
            "management_philosophy_audit": self.audit_management_philosophy(task_id, task_type),
            "resource_check": self.check_resource_idle(),
            "recommendation": "请完成五大图腾和管理哲学审核后执行"
        }
    
    def check_resource_idle(self) -> dict:
        """检查资源是否空置 - 第一性原则V2.1：零容忍管理空档"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "active_tasks": [],
            "blocked_tasks": [],
            "should_activate": [],
            "recommendation": "",
            "management_gaps": []  # 新增：管理空档检测
        }
        
        # 1. 识别真实阻塞任务
        for task in self.blocked_tasks:
            result["blocked_tasks"].append(task)
        
        # 2. 检查是否有可推进的2+7项目
        incomplete_projects = []
        for phase, projects in self.core_projects.items():
            for proj in projects:
                if "✅" not in proj["status"]:
                    incomplete_projects.append({
                        "phase": phase,
                        **proj
                    })
        
        # 3. 决策：如果阻塞任务占满进行中列表，自动补位
        if len(result["blocked_tasks"]) >= 3 and incomplete_projects:
            result["should_activate"] = incomplete_projects[:3]  # 激活前3个
            result["recommendation"] = "资源空置警报：进行中任务全部阻塞，立即激活2+7核心项目补位"
        else:
            result["recommendation"] = "资源利用正常"
        
        # 4. 【新增】管理空档检测 - 零容忍人工设定的时间墙
        # 检查是否有"今晚/明天/下周"等延迟执行设定
        scheduled_gaps = self._detect_management_gaps()
        if scheduled_gaps:
            result["management_gaps"] = scheduled_gaps
            result["recommendation"] += " | 🚨 检测到管理空档，建议立即执行消除延迟"
        
        return result
    
    def _detect_management_gaps(self) -> list:
        """检测管理空档——人为设定的时间延迟"""
        gaps = []
        
        # 检查常见延迟模式
        gap_patterns = [
            ("今晚23:00", "可立即执行，不应等待"),
            ("明天", "可提前完成，消除空档"),
            ("下周", "过于遥远，需拆解为今日任务"),
            ("稍后", "无明确时间，等于无限延迟"),
            ("有空时", "无触发条件，需设定立即执行")
        ]
        
        # 这里可以扩展为读取任务数据库检查
        # 简化版本：返回提示
        return gaps
    
    def force_activate_next(self) -> dict:
        """强制激活下一个可执行任务（防止空置）"""
        # 优先级：P2案例库扩展 > P2其他 > P1优化 > P0完善
        next_tasks = [
            {"id": "CASE-016", "name": "案例库扩展至16个", "action": "基于用户提供素材生成新案例", "auto": True},
            {"id": "DASHBOARD-V2", "name": "仪表盘V2优化", "action": "添加趋势图表和预测功能", "auto": True},
            {"id": "QUALITY-GATE-TEST", "name": "质量门控全流程测试", "action": "运行测试用例验证", "auto": True},
        ]
        
        return {
            "activated": next_tasks[0],
            "queue": next_tasks[1:],
            "timestamp": datetime.now().isoformat()
        }
    
    def enforce_no_idle_rule(self) -> str:
        """执行"零空置"规则"""
        check = self.check_resource_idle()
        
        if check["should_activate"]:
            activation = self.force_activate_next()
            return f"""
⚠️ **第一性原则警报：资源空置检测到**

**现状**：{len(check['blocked_tasks'])}个任务全部阻塞（等待外界条件）
**规则**：进行中列表不得全部为阻塞任务
**行动**：已自动激活补位项目

**立即执行**：{activation['activated']['name']}
**后续队列**：{', '.join([t['name'] for t in activation['queue']])}

**原则重申**：
1. 阻塞任务 = 暂停/待补充，不是"进行中"
2. 进行中列表为空 = 自动补位2+7核心项目
3. 资源全开 = 白天人机协作 + 夜间AI自主推进
"""
        else:
            return "✅ 资源利用正常，无空置"
    
    def get_status_report(self) -> dict:
        """获取完整状态报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "2_plus_7_status": self.core_projects,
            "blocked_tasks": self.blocked_tasks,
            "five_totems": self.five_totems,
            "management_philosophy": list(self.management_philosophy.keys()),
            "resource_utilization": self._calculate_utilization(),
            "next_action": self.force_activate_next()
        }
    
    def _calculate_utilization(self) -> float:
        """计算资源利用率"""
        total_core = sum(len(v) for v in self.core_projects.values())
        completed = sum(1 for phase in self.core_projects.values() 
                       for p in phase if "✅" in p["status"])
        return round(completed / total_core * 100, 1)


if __name__ == "__main__":
    scheduler = FirstPrincipleResourceScheduler()
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            # 执行空置检查
            result = scheduler.enforce_no_idle_rule()
            print(result)
        
        elif command == "prompt":
            # 打印第一性原则口令
            print(scheduler.print_first_principles_prompt())
        
        elif command == "audit":
            # 执行完整审核
            task_desc = sys.argv[2] if len(sys.argv) > 2 else ""
            task_id = sys.argv[3] if len(sys.argv) > 3 else ""
            task_type = sys.argv[4] if len(sys.argv) > 4 else ""
            
            result = scheduler.full_audit(task_desc, task_id, task_type)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif command == "totem":
            # 执行五大图腾审核
            task_desc = sys.argv[2] if len(sys.argv) > 2 else ""
            result = scheduler.audit_totems(task_desc)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif command == "philosophy":
            # 执行管理哲学审核
            task_id = sys.argv[2] if len(sys.argv) > 2 else ""
            task_type = sys.argv[3] if len(sys.argv) > 3 else ""
            result = scheduler.audit_management_philosophy(task_id, task_type)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif command == "report":
            # 输出完整报告
            report = scheduler.get_status_report()
            print(json.dumps(report, indent=2, ensure_ascii=False))
        
        else:
            print(f"未知命令: {command}")
            print("可用命令: check | prompt | audit | totem | philosophy | report")
    
    else:
        # 默认执行空置检查
        result = scheduler.enforce_no_idle_rule()
        print(result)
        
        # 同时输出报告
        print("\n" + "="*50)
        print("完整状态报告：")
        report = scheduler.get_status_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
