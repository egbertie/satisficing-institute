# task-manager Skill

## 功能说明

任务管理技能，用于满意解研究所的任务追踪、遗忘任务扫描和优先级管理。

## 核心功能

1. **任务创建与追踪** - 创建新任务并追踪状态
2. **遗忘任务扫描** - 定期扫描被遗忘的任务
3. **优先级管理** - 自动调整任务优先级
4. **依赖追踪** - 管理任务间依赖关系
5. **提醒机制** - 到期任务自动提醒

## 使用方法

```python
from skills.task_manager.scripts.task_manager import TaskManager

tm = TaskManager()

# 创建任务
tm.create_task(
    title="任务标题",
    priority="高",
    deadline="2026-03-15",
    assignee="满意妞"
)

# 扫描遗忘任务
forgotten = tm.scan_forgotten_tasks()

# 获取待办清单
todos = tm.get_todos()
```

## 配置说明

配置文件路径：`config/settings.json`

- `scan_interval`: 遗忘扫描间隔（小时）
- `reminder_days`: 提前提醒天数
- `priority_weights`: 优先级权重配置

## 集成说明

- 读取 `WORKSPACE_STATUS.md` 获取系统状态
- 与 `TASK_MASTER.md` 同步任务数据
- 向 MEMORY.md 写入任务提醒

## 维护

- 最后更新：2026-03-10
- 版本：1.0
- 维护者：满意妞
