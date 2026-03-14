#!/usr/bin/env python3
"""
资源全开强制执行引擎 V2.0 - Zero Idle Protocol

核心原则：
1. 零空置原则：任何时候都必须有真实推进的任务在执行
2. 自动补位队列：主任务完成/阻塞时，0延迟自动切换
3. 多通路并行：学习+研究+迭代+优化 四线并行
4. 制度即代码：规则写入代码，不是文档，强制执行

零容忍规则：
- 进行中任务全部阻塞 = 立即触发补位，延迟<1秒
- 资源空置>5分钟 = 自动告警并强制激活备用队列
- 没有备用队列可激活 = AI自主创建新任务填补空缺
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

class ZeroIdleEnforcer:
    """零空置强制执行器 - 资源全开的终极保障"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.status_file = self.workspace / "memory" / "zero-idle-status.json"
        self.log_file = self.workspace / "memory" / "zero-idle-log.jsonl"
        
        # 零容忍阈值
        self.IDLE_THRESHOLD_SECONDS = 300  # 5分钟空置即告警
        
        # 主任务队列（高优先级，必须完成）
        self.primary_queue = []
        
        # 自动补位队列（常态化工作，随时可启动）
        self.auto_fill_queue = self._init_auto_fill_queue()
        
        # 多通路并行队列（四线并行）
        self.parallel_queues = self._init_parallel_queues()
        
    def _init_auto_fill_queue(self) -> List[Dict]:
        """初始化自动补位队列 - 常态化工作，随时可执行"""
        return [
            # 学习线
            {"id": "LEARN-001", "name": "专家论文深度研读", "category": "学习", "duration": "2h", "auto": True},
            {"id": "LEARN-002", "name": "行业报告信息采集", "category": "学习", "duration": "1h", "auto": True},
            {"id": "LEARN-003", "name": "方法论金句萃取", "category": "学习", "duration": "30m", "auto": True},
            {"id": "LEARN-004", "name": "竞品案例研究", "category": "学习", "duration": "1h", "auto": True},
            
            # 研究线
            {"id": "RESEARCH-001", "name": "决策模型参数调优", "category": "研究", "duration": "2h", "auto": True},
            {"id": "RESEARCH-002", "name": "评估工具迭代测试", "category": "研究", "duration": "1h", "auto": True},
            {"id": "RESEARCH-003", "name": "五路图腾体系深化", "category": "研究", "duration": "1h", "auto": True},
            {"id": "RESEARCH-004", "name": "合伙人制度沙盘推演", "category": "研究", "duration": "2h", "auto": True},
            
            # 迭代线
            {"id": "ITERATE-001", "name": "案例库扩展（16-20个）", "category": "迭代", "duration": "2h", "auto": True},
            {"id": "ITERATE-002", "name": "已交付文档V2优化", "category": "迭代", "duration": "1h", "auto": True},
            {"id": "ITERATE-003", "name": "仪表盘功能增强", "category": "迭代", "duration": "2h", "auto": True},
            {"id": "ITERATE-004", "name": "内部管理流程优化", "category": "迭代", "duration": "1h", "auto": True},
            
            # 替身线
            {"id": "AVATAR-001", "name": "黎红雷替身对话训练", "category": "替身", "duration": "1h", "auto": True},
            {"id": "AVATAR-002", "name": "罗汉替身材料更新", "category": "替身", "duration": "30m", "auto": True},
            {"id": "AVATAR-003", "name": "谢宝剑替身政策库更新", "category": "替身", "duration": "30m", "auto": True},
            {"id": "AVATAR-004", "name": "六祖顿悟机制优化", "category": "替身", "duration": "1h", "auto": True},
            
            # 游戏化线
            {"id": "GAME-001", "name": "GAME⭐机制产品化设计", "category": "游戏化", "duration": "2h", "auto": True},
            {"id": "GAME-002", "name": "版本管理自动化", "category": "游戏化", "duration": "1h", "auto": True},
            {"id": "GAME-003", "name": "迭代记录可视化", "category": "游戏化", "duration": "1h", "auto": True},
            
            # 优化线
            {"id": "OPT-001", "name": "已完成事项复盘改进", "category": "优化", "duration": "1h", "auto": True},
            {"id": "OPT-002", "name": "内部管理第一性原则审查", "category": "优化", "duration": "2h", "auto": True},
            {"id": "OPT-003", "name": "多通路并行效率分析", "category": "优化", "duration": "1h", "auto": True},
            {"id": "OPT-004", "name": "成本效益再评估", "category": "优化", "duration": "30m", "auto": True},
        ]
    
    def _init_parallel_queues(self) -> Dict[str, List[Dict]]:
        """初始化多通路并行队列"""
        return {
            "学习线": [t for t in self.auto_fill_queue if t["category"] == "学习"],
            "研究线": [t for t in self.auto_fill_queue if t["category"] == "研究"],
            "迭代线": [t for t in self.auto_fill_queue if t["category"] == "迭代"],
            "替身线": [t for t in self.auto_fill_queue if t["category"] == "替身"],
            "游戏化线": [t for t in self.auto_fill_queue if t["category"] == "游戏化"],
            "优化线": [t for t in self.auto_fill_queue if t["category"] == "优化"],
        }
    
    def check_idle_violation(self) -> Dict[str, Any]:
        """
        检查是否违反零空置原则
        
        返回:
            violation: 是否违规
            severity: 严重程度（1-5）
            action: 必须执行的动作
        """
        now = datetime.now()
        
        # 1. 检查进行中任务是否全部阻塞
        active_tasks = self._get_active_tasks()
        blocked_tasks = [t for t in active_tasks if self._is_blocked(t)]
        
        if len(active_tasks) > 0 and len(blocked_tasks) == len(active_tasks):
            # 进行中任务全部阻塞 = 严重违规
            return {
                "violation": True,
                "severity": 5,
                "type": "ALL_BLOCKED",
                "message": "进行中任务全部阻塞，资源严重空置",
                "blocked_count": len(blocked_tasks),
                "action": "IMMEDIATE_FILL"
            }
        
        # 2. 检查是否有进行中任务
        real_active = [t for t in active_tasks if not self._is_blocked(t)]
        if len(real_active) == 0:
            return {
                "violation": True,
                "severity": 4,
                "type": "NO_ACTIVE",
                "message": "无真实推进任务，资源空置",
                "action": "IMMEDIATE_FILL"
            }
        
        # 3. 检查单任务运行时间（是否僵死）
        for task in real_active:
            runtime = self._get_task_runtime(task)
            if runtime > 3600:  # 运行超过1小时无进展
                return {
                    "violation": True,
                    "severity": 3,
                    "type": "ZOMBIE_TASK",
                    "message": f"任务 {task['id']} 僵死运行{runtime//60}分钟",
                    "task": task,
                    "action": "PARALLEL_FILL"
                }
        
        return {"violation": False, "severity": 0, "action": "NONE"}
    
    def enforce_zero_idle(self) -> str:
        """
        强制执行零空置原则
        
        这是核心方法，必须在以下场景调用：
        1. 每次任务状态变更后
        2. 每次心跳检查时
        3. 用户交互间隙超过5分钟
        4. 每小时定时检查
        """
        check = self.check_idle_violation()
        
        if not check["violation"]:
            return "✅ 零空置原则遵守正常"
        
        # 严重违规 - 立即执行补位
        if check["action"] == "IMMEDIATE_FILL":
            activated = self._immediate_fill()
            self._log_enforcement(check, activated)
            return f"""
🚨 **零空置原则强制执行触发**

**违规类型**: {check['type']}
**严重程度**: {check['severity']}/5
**问题**: {check['message']}

**立即执行补位**:
{self._format_activated(activated)}

**强制执行规则**:
1. 阻塞任务 ≠ 进行中（已重新分类）
2. 进行中为空 = 0延迟自动补位
3. 多通路并行 = 同时激活4+条线
4. 资源全开 = 永不留空
"""
        
        elif check["action"] == "PARALLEL_FILL":
            activated = self._parallel_fill()
            self._log_enforcement(check, activated)
            return f"""
⚠️ **并行补位激活**

检测到任务僵死，已并行启动新任务：
{self._format_activated(activated)}
"""
        
        return "状态异常"
    
    def _immediate_fill(self) -> List[Dict]:
        """立即补位 - 从自动补位队列激活任务"""
        activated = []
        
        # 策略1：四线并行，每条线激活1个任务
        for line_name, line_tasks in self.parallel_queues.items():
            if line_tasks:
                task = line_tasks.pop(0)  # 取出第一个
                task["activated_at"] = datetime.now().isoformat()
                task["status"] = "🔄 进行中"
                activated.append(task)
        
        # 策略2：如果还有空位，随机再激活2个
        remaining = [t for t in self.auto_fill_queue if "status" not in t]
        if len(activated) < 4 and remaining:
            extra = random.sample(remaining, min(2, len(remaining)))
            for task in extra:
                task["activated_at"] = datetime.now().isoformat()
                task["status"] = "🔄 进行中"
                activated.append(task)
        
        return activated
    
    def _parallel_fill(self) -> List[Dict]:
        """并行补位 - 在现有任务基础上增加并行任务"""
        activated = []
        
        # 从不同的线各取一个
        categories = ["学习", "研究", "迭代", "替身"]
        for cat in categories:
            available = [t for t in self.auto_fill_queue 
                        if t["category"] == cat and "status" not in t]
            if available:
                task = available[0]
                task["activated_at"] = datetime.now().isoformat()
                task["status"] = "🔄 并行中"
                activated.append(task)
        
        return activated
    
    def _get_active_tasks(self) -> List[Dict]:
        """获取当前进行中任务"""
        # 从TASK_MASTER.md解析
        # 简化实现，实际应读取文件
        return []
    
    def _is_blocked(self, task: Dict) -> bool:
        """判断任务是否阻塞"""
        blockers = ["需联系本人", "需联系方式", "403错误", "需用户操作", "等待外界条件"]
        return any(b in task.get("name", "") or b in task.get("status", "") 
                  for b in blockers)
    
    def _get_task_runtime(self, task: Dict) -> int:
        """获取任务运行时间（秒）"""
        # 简化实现
        return 0
    
    def _format_activated(self, activated: List[Dict]) -> str:
        """格式化激活的任务列表"""
        lines = []
        for task in activated:
            lines.append(f"  • [{task['category']}] {task['name']} ({task['duration']})")
        return "\n".join(lines)
    
    def _log_enforcement(self, check: Dict, activated: List[Dict]):
        """记录强制执行日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "violation_type": check["type"],
            "severity": check["severity"],
            "activated_tasks": [t["id"] for t in activated],
            "total_activated": len(activated)
        }
        
        # 追加写入日志文件
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_system_status(self) -> Dict:
        """获取系统整体状态"""
        return {
            "timestamp": datetime.now().isoformat(),
            "auto_fill_queue_size": len(self.auto_fill_queue),
            "available_parallel_lines": len(self.parallel_queues),
            "total_standby_tasks": sum(len(t) for t in self.parallel_queues.values()),
            "zero_idle_status": "ENFORCED",
            "last_violation": self._get_last_violation()
        }
    
    def _get_last_violation(self) -> Optional[Dict]:
        """获取最后一次违规记录"""
        if not self.log_file.exists():
            return None
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    return json.loads(lines[-1])
        except:
            pass
        return None


if __name__ == "__main__":
    enforcer = ZeroIdleEnforcer()
    
    # 强制执行检查
    result = enforcer.enforce_zero_idle()
    print(result)
    
    # 输出系统状态
    print("\n" + "="*50)
    print("系统状态:")
    print(json.dumps(enforcer.get_system_status(), indent=2, ensure_ascii=False))
