# Cron配置更新记录
## Cron Configuration Update Log

**更新日期**: 2026-03-15  
**更新版本**: 零空置机制 V3.0（精简2线模式）  
**更新原因**: Token优化管理，保留空间进行周期末极限测试  
**审批状态**: 已生效  

---

## 一、更新概要

### 1.1 变更对比

| 维度 | 变更前（V2.1） | 变更后（V3.0） |
|------|----------------|----------------|
| **模式** | 六线并行 | 精简2线 |
| **线路** | 学习/研究/迭代/替身/游戏化/优化 | 学习研究合并线 + 优化复盘合并线 |
| **触发频率** | 每30分钟/空置即触发 | 空闲>2h触发线1，每日1次线2 |
| **Token控制** | ~30K/次 | 线1: 10K/次，线2: 5K/次 |
| **状态** | 已暂停（保留Token） | 精简模式运行中 |

### 1.2 更新原因

1. **Token管理优化**: 原六线模式消耗过大，需为周期末极限测试保留空间
2. **效率提升**: 合并相关任务，减少上下文切换开销
3. **灵活调控**: 精简模式便于根据Token余量动态调整

---

## 二、V3.0 配置详情

### 2.1 精简2线配置

```yaml
# 零空置机制 V3.0 配置
version: "3.0"
mode: "精简2线"
status: "运行中"
updated_at: "2026-03-15T21:15:00+08:00"

lines:
  line_1:
    name: "学习研究合并线"
    tasks:
      - 专家论文研读
      - 决策模型研究
      - 知识沉淀与模式提炼
      - 学习笔记归档
    trigger:
      condition: "主线任务间隙 > 2小时"
      token_threshold: "> 30%"
      user_idle: true
    token_limit:
      per_trigger: "10K"
      daily_max: "30K"
    priority: "P2"
    
  line_2:
    name: "优化复盘合并线"
    tasks:
      - 已完成事项复盘改进
      - 系统优化建议整理
      - 轻量级维护任务
      - 文档整理与归档
    trigger:
      schedule: "22:00 daily"
      alternative: "主线任务完成后空闲时段"
    token_limit:
      per_trigger: "5K"
      daily_max: "5K"
    priority: "P3"

pause_rules:
  token_30:
    condition: "token < 30%"
    action: "暂停线1，仅保留线2"
  token_15:
    condition: "token < 15%"
    action: "完全暂停，等待用户指令"
  user_active:
    condition: "用户明确任务期间"
    action: "不触发补位"

stress_test_mode:
  trigger: "周期末最后一日"
  action: "恢复6线全开"
  purpose: "验证最大承载量，收集消耗数据"
  token_reserve: "15-20%"
```

### 2.2 触发条件详解

**线1触发条件**（需同时满足）:
1. 检测到NO_ACTIVE状态（无用户明确任务）
2. Token余量 > 30%
3. 距离上次补位 > 2小时
4. 距离用户最后交互 > 2小时

**线2触发条件**（满足任一）:
1. 每日22:00定时触发
2. 主线任务完成后的空闲时段（自动检测）

### 2.3 暂停规则详解

| Token余量 | 自动行为 | 用户干预 |
|-----------|----------|----------|
| > 50% | 精简2线正常补位 | 可随时暂停/恢复 |
| 30-50% | 仅保留线2（每日复盘） | 可指令恢复线1 |
| 15-30% | 暂停自动补位，仅响应用户 | 需用户明确指令才激活 |
| < 15% | 完全暂停，静默等待 | 等待Token重置或用户明确指令 |

---

## 三、配置文件更新

### 3.1 zero_idle_config.json

```json
{
  "version": "3.0",
  "mode": "精简2线",
  "status": "运行中",
  "updated_at": "2026-03-15T21:15:00+08:00",
  
  "lines": [
    {
      "id": "line_1",
      "name": "学习研究合并线",
      "tasks": [
        "专家论文研读",
        "决策模型研究",
        "知识沉淀与模式提炼",
        "学习笔记归档"
      ],
      "trigger": {
        "type": "idle_time",
        "min_idle_minutes": 120,
        "token_threshold_percent": 30,
        "user_task_active": false
      },
      "token_limit": {
        "per_trigger": 10000,
        "daily_max": 30000
      },
      "priority": "P2"
    },
    {
      "id": "line_2",
      "name": "优化复盘合并线",
      "tasks": [
        "已完成事项复盘改进",
        "系统优化建议整理",
        "轻量级维护任务",
        "文档整理与归档"
      ],
      "trigger": {
        "type": "scheduled",
        "cron": "0 22 * * *",
        "alternative_trigger": "post_task_idle"
      },
      "token_limit": {
        "per_trigger": 5000,
        "daily_max": 5000
      },
      "priority": "P3"
    }
  ],
  
  "pause_rules": [
    {
      "name": "token_30",
      "condition": "token_percent < 30",
      "action": "pause_line_1",
      "retain_line": ["line_2"]
    },
    {
      "name": "token_15",
      "condition": "token_percent < 15",
      "action": "pause_all",
      "wait_for": "user_command"
    },
    {
      "name": "user_active",
      "condition": "user_explicit_task",
      "action": "suppress_fill",
      "duration": "while_user_active"
    }
  ],
  
  "stress_test": {
    "enabled": true,
    "trigger": "cycle_last_day",
    "restore_mode": "6_line_full",
    "token_reserve_percent": 20,
    "purpose": "验证最大承载量，收集消耗数据"
  },
  
  "logging": {
    "level": "info",
    "output": "memory/zero-idle-log.jsonl",
    "metrics": ["trigger_count", "token_consumed", "task_completed"]
  }
}
```

### 3.2 配置文件位置

- 配置文件: `/root/.openclaw/workspace/config/zero_idle_config.json`
- 日志文件: `/root/.openclaw/workspace/memory/zero-idle-log.jsonl`

---

## 四、HEARTBEAT.md 更新内容

### 4.1 新增/更新章节

在HEARTBEAT.md中新增以下章节（替换原有零空置相关内容）:

```markdown
### 零空置机制 V3.0（精简2线模式）

**状态**: 🟢 运行中（2026-03-15更新）

**触发条件**:
- 检测到NO_ACTIVE状态
- Token余量 > 30%
- 距离上次补位 > 2小时

**精简2线**:

| 线路 | 任务内容 | Token上限 | 触发频率 |
|------|----------|-----------|----------|
| **线1** | 学习研究合并（论文研读+模型研究）| 10K/次 | 空闲>2h |
| **线2** | 优化复盘合并（复盘+轻维护）| 5K/次 | 每日1次 |

**暂停规则**:
- Token < 30%：暂停线1，仅保留线2
- Token < 15%：完全暂停，等待用户指令
- 用户明确任务期间：不触发补位

**极限测试模式**:
- 周期末最后一日：恢复6线全开
- 验证最大承载量
- 收集消耗数据
```

### 4.2 历史记录更新

在HEARTBEAT.md的更新记录表中新增:

```markdown
| 2026-03-15 | V3.0 | 精简2线模式，优化Token管理 | 满意妞 |
```

---

## 五、监控与日志

### 5.1 监控指标

| 指标 | 目标 | 监控频率 | 告警条件 |
|------|------|----------|----------|
| 线1触发次数/日 | ≤ 3次 | 每日 | > 5次 |
| 线2触发次数/日 | = 1次 | 每日 | ≠ 1次 |
| Token消耗/日 | ≤ 35K | 每日 | > 40K |
| 违规空置次数 | = 0 | 实时 | > 0 |

### 5.2 日志格式

```json
{
  "timestamp": "2026-03-15T21:30:00+08:00",
  "event": "line_triggered",
  "line_id": "line_1",
  "trigger_reason": "idle_time",
  "token_before": 85000,
  "token_after": 76000,
  "tasks_activated": ["专家论文研读"],
  "duration_minutes": 15
}
```

---

## 六、回滚与恢复

### 6.1 回滚条件

以下情况可触发回滚至六线模式:
1. 用户明确指令恢复
2. Token重置后
3. 周期末极限测试期间

### 6.2 回滚操作

```bash
# 手动恢复六线模式
python3 skills/zero-idle-enforcer/enforcer.py restore --mode=6line

# 更新配置
sed -i 's/精简2线/六线并行/' config/zero_idle_config.json
```

---

## 七、更新验证

### 7.1 验证清单

- [x] 配置文件已更新
- [x] HEARTBEAT.md已更新
- [x] 日志路径已确认
- [x] 触发条件已测试
- [x] 暂停规则已验证
- [x] 文档已归档

### 7.2 生效确认

**确认人**: 满意妞  
**确认时间**: 2026-03-15 21:30  
**状态**: ✅ 已生效  

---

## 八、版本历史

| 日期 | 版本 | 模式 | 说明 |
|------|------|------|------|
| 2026-03-13 | V1.0 | 基础补位 | 初始零空置机制 |
| 2026-03-15 | V2.0 | 六线并行 | 强制执行六线补位 |
| 2026-03-15 | V2.1 | 六线暂停 | 为极限测试保留Token |
| 2026-03-15 | **V3.0** | **精简2线** | **当前版本，优化Token管理** |

---

*文档结束 | 满意解研究所 | 系统运维中心*
