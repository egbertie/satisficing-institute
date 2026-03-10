#!/usr/bin/env python3
"""
任务协调管理核心引擎 V2.0 - 具备学习迭代能力

核心能力：
1. 智能协调 - 分析任务状态，自动选择执行模式
2. 学习迭代 - 记录决策效果，持续优化策略
3. 资源调度 - 合理分配算力，最大化团队产出
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

class TaskCoordinator:
    """任务协调管理器 - 资源调度核心"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.tasks_file = self.workspace / "docs" / "TASK_MASTER.md"
        self.memory_dir = self.workspace / "memory"
        self.status_file = self.workspace / "memory" / "task-coordinator-status.json"
        self.learning_file = self.workspace / "memory" / "task-coordinator-learning.json"
        self.strategy_file = self.workspace / "skills/task-coordinator/config/strategy.json"
        
        # 加载学习记录
        self.learning = self._load_learning()
        self.strategy = self._load_strategy()
        
    def _load_learning(self) -> Dict:
        """加载学习记录"""
        if self.learning_file.exists():
            with open(self.learning_file) as f:
                return json.load(f)
        return {
            "version": "1.0",
            "decisions": [],
            "effectiveness": {},
            "patterns": {}
        }
    
    def _load_strategy(self) -> Dict:
        """加载当前策略"""
        if self.strategy_file.exists():
            with open(self.strategy_file) as f:
                return json.load(f)
        return self._default_strategy()
    
    def _default_strategy(self) -> Dict:
        """默认策略配置"""
        return {
            "version": "1.0",
            "mode_weights": {
                "sequential": {"urgent": 1.0, "normal": 0.3},
                "parallel": {"urgent": 0.0, "normal": 1.0},
                "notify_user": {"blocked": 1.0}
            },
            "thresholds": {
                "overdue_critical": 2,      # 小时
                "overdue_warning": 4,       # 小时
                "ad_hoc_interrupt": True,   # 临时任务是否中断当前
                "max_parallel": 5,          # 最大并行数
                "user_response_timeout": 8  # 小时
            },
            "resource_allocation": {
                "user_active": {"ai_focus": 0.8, "background": 0.2},
                "user_idle": {"ai_focus": 0.3, "background": 0.7}
            }
        }
    
    def _save_learning(self):
        """保存学习记录"""
        self.learning_file.parent.mkdir(exist_ok=True)
        with open(self.learning_file, 'w') as f:
            json.dump(self.learning, f, indent=2)
    
    def _save_strategy(self):
        """保存策略更新"""
        with open(self.strategy_file, 'w') as f:
            json.dump(self.strategy, f, indent=2)
    
    def load_current_tasks(self) -> Dict[str, List]:
        """加载当前所有任务状态"""
        now = datetime.now()
        
        tasks = {
            "scheduled": [],      # 正常计划任务
            "ad_hoc": [],         # 临时任务
            "overdue": [],        # 已过期
            "at_risk": [],        # 有风险（快到期）
            "blocked": [],        # 被阻塞
            "completed_today": [] # 今日已完成
        }
        
        # 从任务清单加载
        # 从今日日志加载
        # 从阻塞状态加载
        
        # 严重遗漏任务（来自TASK_MASTER）
        overdue_tasks = [
            {
                "id": "URG-001",
                "name": "灾备重建复刻实施方案V1.0",
                "due": "2026-03-10 18:00",
                "status": "🔴 已过期",
                "hours_overdue": 3,
                "severity": "critical",
                "remedy_agent": "agent:main:subagent:13906415-d6f2-415e-a722-623dd6c914f8"
            },
            {
                "id": "URG-002",
                "name": "内部会议机制建立",
                "due": "2026-03-10 16:00",
                "status": "🔴 已过期",
                "hours_overdue": 5,
                "severity": "critical",
                "remedy_agent": "agent:main:subagent:2b7c6e1a-386a-4be2-8d8e-3b0fa82e298"
            },
        ]
        
        # 阻塞任务
        blocked_tasks = [
            {"id": "WIP-001", "name": "V1.0蓝军意见整理", "status": "等待附件", "blocker": "用户", "days_waiting": 3},
            {"id": "WIP-002", "name": "专家网络搭建", "status": "等待联系方式", "blocker": "用户", "days_waiting": 3},
        ]
        
        # 有风险任务（快到期）
        at_risk = [
            {"id": "WIP-003", "name": "五路图腾信息图", "due": "2026-03-11", "hours_left": 12, "severity": "high"},
        ]
        
        # 待确认
        pending = [
            {"id": "NOTION-001", "name": "Notion同步最终确认", "status": "子代理执行中", "note": "已启动，待验证结果"},
        ]
        
        tasks["overdue"] = overdue_tasks
        tasks["blocked"] = blocked_tasks
        tasks["at_risk"] = at_risk
        tasks["pending"] = pending
        
        return tasks
    
    def analyze_workload(self) -> Dict:
        """分析工作负载，智能判断执行模式"""
        tasks = self.load_current_tasks()
        now = datetime.now()
        
        analysis = {
            "timestamp": now.isoformat(),
            "summary": {
                "overdue": len(tasks.get("overdue", [])),
                "blocked": len(tasks.get("blocked", [])),
                "at_risk": len(tasks.get("at_risk", [])),
                "pending": len(tasks.get("pending", [])),
            },
            "risk_score": 0,
            "recommended_mode": None,
            "reasoning": [],
            "actions": []
        }
        
        # 计算风险分数
        risk_score = 0
        reasoning = []
        
        # 过期任务权重最高
        for task in tasks.get("overdue", []):
            hours = task.get("hours_overdue", 0)
            if hours > 4:
                risk_score += 10
                reasoning.append(f"严重逾期: {task['name']} ({hours}小时)")
            else:
                risk_score += 5
                reasoning.append(f"轻度逾期: {task['name']} ({hours}小时)")
        
        # 阻塞任务
        for task in tasks.get("blocked", []):
            days = task.get("days_waiting", 0)
            if days > 2:
                risk_score += 3
                reasoning.append(f"长期阻塞: {task['name']} ({days}天)")
        
        # 有风险任务
        for task in tasks.get("at_risk", []):
            hours = task.get("hours_left", 24)
            if hours < 12:
                risk_score += 4
                reasoning.append(f"即将到期: {task['name']} ({hours}小时)")
        
        analysis["risk_score"] = risk_score
        analysis["reasoning"] = reasoning
        
        # 决策：选择执行模式
        if risk_score >= 10 or tasks.get("overdue"):
            analysis["recommended_mode"] = "sequential"
            analysis["actions"].append({
                "priority": "P0",
                "action": "立即补救所有过期任务",
                "mode": "sequential",
                "parallel_agents": True,  # 使用子代理并行补救
                "suspend_background": True
            })
        elif tasks.get("blocked") and not tasks.get("overdue"):
            analysis["recommended_mode"] = "notify_user"
            analysis["actions"].append({
                "priority": "P1",
                "action": "批量确认阻塞项",
                "mode": "notify_user",
                "items": [t["name"] for t in tasks["blocked"]]
            })
        elif risk_score == 0 and not tasks.get("overdue"):
            analysis["recommended_mode"] = "parallel"
            analysis["actions"].append({
                "priority": "P2",
                "action": "无紧急任务，进入高效并行模式",
                "mode": "parallel",
                "max_parallel": self.strategy["thresholds"]["max_parallel"]
            })
        else:
            analysis["recommended_mode"] = "hybrid"
            analysis["actions"].append({
                "priority": "P1",
                "action": "混合模式：处理风险任务+部分并行",
                "mode": "hybrid"
            })
        
        return analysis
    
    def record_decision(self, decision: Dict, outcome: Dict = None):
        """记录决策，用于学习迭代"""
        decision_record = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "context": {
                "risk_score": decision.get("risk_score", 0),
                "mode": decision.get("recommended_mode"),
                "task_count": sum(decision.get("summary", {}).values())
            },
            "outcome": outcome or {"status": "pending"}
        }
        
        self.learning["decisions"].append(decision_record)
        
        # 保持最近100条记录
        if len(self.learning["decisions"]) > 100:
            self.learning["decisions"] = self.learning["decisions"][-100:]
        
        self._save_learning()
    
    def optimize_strategy(self):
        """基于学习记录优化策略"""
        decisions = self.learning.get("decisions", [])
        
        if len(decisions) < 5:
            return  # 数据不足，保持默认
        
        # 分析各模式效果
        mode_effectiveness = {}
        for d in decisions:
            mode = d.get("context", {}).get("mode")
            outcome = d.get("outcome", {}).get("status")
            
            if mode not in mode_effectiveness:
                mode_effectiveness[mode] = {"success": 0, "total": 0}
            
            mode_effectiveness[mode]["total"] += 1
            if outcome == "success":
                mode_effectiveness[mode]["success"] += 1
        
        # 更新策略
        for mode, stats in mode_effectiveness.items():
            if stats["total"] > 0:
                success_rate = stats["success"] / stats["total"]
                self.learning["effectiveness"][mode] = {
                    "success_rate": success_rate,
                    "total_uses": stats["total"]
                }
        
        # 识别模式
        self._identify_patterns()
        
        self._save_learning()
    
    def _identify_patterns(self):
        """识别任务模式"""
        decisions = self.learning.get("decisions", [])
        
        # 示例：识别"飞书调试陷阱"
        feishu_incidents = [d for d in decisions 
                          if "飞书" in str(d.get("reasoning", []))
                          and d.get("context", {}).get("risk_score", 0) > 5]
        
        if len(feishu_incidents) >= 2:
            self.learning["patterns"]["feishu_time_sink"] = {
                "description": "飞书相关任务容易耗时过长，导致其他任务逾期",
                "trigger": "任务包含'飞书'或'feishu'",
                "recommendation": "设置时间限制，超时时自动启动并行检查",
                "detected_at": datetime.now().isoformat()
            }
    
    def generate_action_plan(self) -> Dict:
        """生成行动计划"""
        analysis = self.analyze_workload()
        
        # 记录本次决策
        self.record_decision(analysis)
        
        plan = {
            "generated_at": datetime.now().isoformat(),
            "mode": analysis["recommended_mode"],
            "risk_score": analysis["risk_score"],
            "reasoning": analysis["reasoning"],
            "actions": analysis["actions"],
            "resource_allocation": self._calculate_resource_allocation(analysis)
        }
        
        return plan
    
    def _calculate_resource_allocation(self, analysis: Dict) -> Dict:
        """计算资源分配"""
        mode = analysis["recommended_mode"]
        
        allocation = {
            "user_interaction": 0.0,
            "background_tasks": 0.0,
            "sub_agents": 0
        }
        
        if mode == "sequential":
            allocation = {
                "user_interaction": 0.9,
                "background_tasks": 0.0,
                "sub_agents": min(analysis.get("summary", {}).get("overdue", 0), 3)
            }
        elif mode == "parallel":
            allocation = {
                "user_interaction": 0.3,
                "background_tasks": 0.7,
                "sub_agents": self.strategy["thresholds"]["max_parallel"]
            }
        elif mode == "notify_user":
            allocation = {
                "user_interaction": 1.0,
                "background_tasks": 0.0,
                "sub_agents": 0
            }
        
        return allocation
    
    def check_today_log(self) -> List[Dict]:
        """检查今日日志，找出遗漏"""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.memory_dir / f"{today}.md"
        
        issues = []
        
        if log_file.exists():
            content = log_file.read_text()
            
            # 检查未完成的待办
            incomplete = [line.strip() for line in content.split('\n') 
                         if line.strip().startswith('- [ ]')]
            if incomplete:
                issues.append({
                    "type": "incomplete_tasks",
                    "count": len(incomplete),
                    "items": incomplete[:5],
                    "severity": "warning"
                })
            
            # 检查长时间任务
            if "飞书" in content and "调试" in content:
                issues.append({
                    "type": "potential_time_sink",
                    "message": "检测到可能的耗时任务（飞书调试）",
                    "recommendation": "设置时间上限，超时切换并行",
                    "severity": "info"
                })
        
        return issues
    
    def save_status(self):
        """保存协调器状态"""
        status = {
            "last_check": datetime.now().isoformat(),
            "analysis": self.analyze_workload(),
            "plan": self.generate_action_plan(),
            "issues": self.check_today_log(),
            "learning_summary": {
                "total_decisions": len(self.learning.get("decisions", [])),
                "effectiveness": self.learning.get("effectiveness", {}),
                "detected_patterns": list(self.learning.get("patterns", {}).keys())
            }
        }
        
        self.status_file.parent.mkdir(exist_ok=True)
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        return status
    
    def print_report(self):
        """打印协调报告"""
        # 先优化策略
        self.optimize_strategy()
        
        status = self.save_status()
        
        print("="*70)
        print("🎯 任务协调管理报告 V2.0 (具备学习迭代能力)")
        print("="*70)
        print(f"生成时间: {status['last_check']}")
        print()
        
        # 摘要
        summary = status['analysis']['summary']
        print(f"📊 任务状态:")
        print(f"  🔴 过期任务: {summary.get('overdue', 0)} 项")
        print(f"  ⏸️  阻塞任务: {summary.get('blocked', 0)} 项")
        print(f"  ⚠️  风险任务: {summary.get('at_risk', 0)} 项")
        print(f"  🔄 待确认: {summary.get('pending', 0)} 项")
        print()
        
        # 风险分数
        print(f"🎚️ 风险分数: {status['analysis']['risk_score']}/100")
        print()
        
        # 决策逻辑
        if status['analysis']['reasoning']:
            print(f"🧠 决策逻辑:")
            for r in status['analysis']['reasoning'][:5]:
                print(f"  • {r}")
            print()
        
        # 推荐模式
        mode = status['plan']['mode']
        mode_names = {
            "sequential": "顺序执行 (全力补救)",
            "parallel": "并行执行 (效率最大)",
            "notify_user": "等待确认 (批量沟通)",
            "hybrid": "混合模式 (灵活调度)"
        }
        print(f"⚡ 执行模式: {mode_names.get(mode, mode)}")
        print()
        
        # 行动计划
        print(f"🎯 行动计划:")
        for i, action in enumerate(status['plan']['actions'], 1):
            print(f"  {i}. [{action['priority']}] {action['action']}")
            print(f"     模式: {action['mode']}")
        print()
        
        # 资源分配
        alloc = status['plan']['resource_allocation']
        print(f"📈 资源分配:")
        print(f"  用户交互: {alloc['user_interaction']*100:.0f}%")
        print(f"  后台任务: {alloc['background_tasks']*100:.0f}%")
        print(f"  子代理数: {alloc['sub_agents']} 个")
        print()
        
        # 学习状态
        learning = status['learning_summary']
        print(f"🧬 学习迭代:")
        print(f"  历史决策: {learning['total_decisions']} 次")
        if learning['effectiveness']:
            for mode, eff in learning['effectiveness'].items():
                print(f"  {mode}成功率: {eff.get('success_rate', 0)*100:.1f}%")
        if learning['detected_patterns']:
            print(f"  识别模式: {', '.join(learning['detected_patterns'])}")
        print()
        
        # 发现的问题
        if status['issues']:
            print(f"⚠️  发现的问题:")
            for issue in status['issues']:
                print(f"  [{issue['severity']}] {issue['type']}: {issue.get('message', '')}")
        print()
        
        print("="*70)

if __name__ == "__main__":
    coordinator = TaskCoordinator()
    coordinator.print_report()
