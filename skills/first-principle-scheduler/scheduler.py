#!/usr/bin/env python3
"""
第一性原则资源调度器 - 防止资源空置的核心机制

核心规则：
1. 没有真实推进的任务 = 暂停/待补充，不是"进行中"
2. 进行中列表必须为空时，自动补位2+7核心项目
3. 资源全开 = 白天人机协作 + 夜间AI自主推进，零空置
"""

import json
import os
from datetime import datetime
from pathlib import Path

class FirstPrincipleResourceScheduler:
    """第一性原则资源调度器"""
    
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
        
        # 阻塞任务定义（等待外界条件）
        self.blocked_tasks = [
            {"id": "WIP-004", "name": "补充专家真实资料", "blocker": "需联系本人", "user_action": "提供联系方式或确认自行处理"},
            {"id": "WIP-005", "name": "发送专家邀请函", "blocker": "需联系方式", "user_action": "提供专家联系方式"},
            {"id": "WIP-007", "name": "Claude API解决", "blocker": "地区限制403", "user_action": "需要海外环境或替代方案"},
            {"id": "WIP-008", "name": "飞书权限完善", "blocker": "需用户操作", "user_action": "在飞书后台添加drive:file权限"},
        ]
    
    def check_resource_idle(self) -> dict:
        """检查资源是否空置"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "active_tasks": [],
            "blocked_tasks": [],
            "should_activate": [],
            "recommendation": ""
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
        
        return result
    
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
    
    # 执行空置检查
    result = scheduler.enforce_no_idle_rule()
    print(result)
    
    # 输出完整报告
    import json
    report = scheduler.get_status_report()
    print("\n" + "="*50)
    print("完整状态报告：")
    print(json.dumps(report, indent=2, ensure_ascii=False))
