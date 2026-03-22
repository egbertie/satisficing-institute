# Task Queue Skill - 并行任务管理

## 功能概述

这是一个支持并发执行的智能任务队列管理系统，能够：
- 管理多个并发任务（最多5个同时运行）
- 自动跟踪任务状态
- 检测并提醒超时/遗忘的任务
- 支持任务优先级（高/中/低）
- 可视化展示任务状态

## 核心特性

### 1. 并发控制
- 最大并发数：5个任务
- 新任务自动排队，不会打断现有任务
- 资源保护机制，防止过载

### 2. 优先级系统
- **高优先级**：超时 600秒，优先执行
- **中优先级**：超时 300秒（默认）
- **低优先级**：超时 180秒，空闲时执行

### 3. 状态跟踪
```
PENDING     → 等待执行
RUNNING     → 正在执行
COMPLETED   → 已完成
FAILED      → 执行失败
TIMEOUT     → 执行超时
ORPHANED    → 遗忘任务（需人工介入）
```

### 4. 遗忘任务检测
- 每30秒自动扫描一次
- 任务超时未报告自动标记为 ORPHANED
- 发送提醒通知

## 使用方法

### 启动任务管理器
```bash
python /root/.openclaw/skills/task-queue/scripts/task-manager.py
```

### Python API

```python
from task_manager import TaskManager, Task

# 创建任务管理器
manager = TaskManager()

# 添加任务
task = manager.add_task(
    name="数据处理",
    func=my_function,
    args=(arg1, arg2),
    priority="medium",  # high/medium/low
    timeout=300         # 可选，覆盖默认超时
)

# 获取所有任务状态
status = manager.get_status()

# 等待任务完成
result = manager.wait_for_task(task.id)

# 取消任务
manager.cancel_task(task.id)
```

### 命令行交互

```bash
# 添加任务
python task-manager.py add --name "任务名称" --priority high --command "python script.py"

# 查看状态
python task-manager.py status

# 取消任务
python task-manager.py cancel --id <task_id>

# 停止管理器
python task-manager.py stop
```

## 输出格式

### 状态展示（终端）
```
┌─────────────────────────────────────────────────────┐
│                  任务队列状态                        │
├──────────┬─────────┬──────────┬─────────┬───────────┤
│ ID       │ 名称    │ 优先级   │ 状态    │ 耗时      │
├──────────┼─────────┼──────────┼─────────┼───────────┤
│ t-001    │ 任务A   │ HIGH     │ RUNNING │ 00:02:15  │
│ t-002    │ 任务B   │ MEDIUM   │ PENDING │ 00:00:30  │
│ t-003    │ 任务C   │ LOW      │ PENDING │ 00:01:00  │
└──────────┴─────────┴──────────┴─────────┴───────────┘
当前运行: 1/5 | 等待: 2 | 已完成: 0 | 失败: 0 | 遗忘: 0
```

### JSON 输出
```json
{
  "tasks": [
    {
      "id": "t-001",
      "name": "任务A",
      "priority": "high",
      "status": "RUNNING",
      "created_at": "2026-03-10T10:55:00",
      "started_at": "2026-03-10T10:55:05",
      "duration_seconds": 135
    }
  ],
  "summary": {
    "running": 1,
    "pending": 2,
    "completed": 0,
    "failed": 0,
    "orphaned": 0,
    "max_concurrent": 5
  }
}
```

## 文件结构

```
/root/.openclaw/skills/task-queue/
├── SKILL.md                    # 本说明文档
├── config/
│   └── limits.json            # 配置参数
└── scripts/
    └── task-manager.py        # 主程序
```

## 配置说明

编辑 `config/limits.json` 可调整：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| max_concurrent_tasks | 5 | 最大并发任务数 |
| default_timeout_seconds | 300 | 默认超时时间 |
| priority_timeout_seconds | {} | 各优先级超时时间 |
| orphan_detection_interval | 30 | 遗忘检测间隔（秒）|
| task_poll_interval | 1 | 任务轮询间隔（秒）|
| auto_cleanup_completed | true | 自动清理已完成任务 |
| cleanup_after_seconds | 3600 | 清理延迟时间 |

## 最佳实践

1. **合理设置优先级**：紧急任务用 `high`，后台任务用 `low`
2. **预估超时时间**：避免任务无限期挂起
3. **处理异常**：在任务函数中捕获异常，避免状态混乱
4. **定期检查**：养成查看任务状态的习惯

## 注意事项

- 任务ID格式：`t-{timestamp}-{sequence}`
- 任务函数必须是可序列化的（用于多进程）
- 建议使用 `manager.wait_for_task()` 获取结果，而非直接访问
- 遗忘任务需要手动处理或重启管理器清理
