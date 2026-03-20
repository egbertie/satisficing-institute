# 零空置强制执行标准Skill V4.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V4.0 | 更新: 2026-03-20 | 修复: 脚本误删问题 | 模式: 精简2线

---

## 一、全局考虑（六层全覆盖+资源状态）

### L0: 核心身份层
- AI身份下保持持续可用性
- 空闲时主动创造价值

### L1: 项目状态层（核心）
- 检测NO_ACTIVE状态
- 识别空闲窗口（用户无响应>2h）
- Token余量充足（>30%）

### L2: 系统配置层
- 自动补位队列配置
- 6线并行任务池
- 资源分配策略

### L3: 外部集成层
- 学习资源自动获取
- 研究成果外部归档
- 知识图谱自动更新

### L4: 交付物层
- 学习笔记产出
- 研究报告生成
- 技能实践成果

### L5: 历史归档层
- 学习轨迹记录
- 能力提升追踪
- 知识沉淀归档

### 资源状态监控

| 资源类型 | 监控指标 | 触发条件 | 暂停规则 |
|----------|----------|----------|----------|
| Token | 余量百分比 | >30%允许补位 | <30%暂停线1，<15%全停 |
| 注意力 | 用户响应时间 | >2h无响应 | 用户活跃时不触发 |
| 算力 | API响应状态 | 正常 | 异常时降级 |

---

## 二、系统考虑（检测→补位→执行→复盘闭环）

### 2.1 精简2线模式（V3.0→V4.0优化）

**V4.0改进**: 从6线精简为2线，降低Token消耗，提高执行效率

```
┌─────────┐    ┌─────────────┐    ┌─────────────┐
│ 空闲检测 │ →  │  线1:学习研究 │ →  │  成果产出   │
│(>2h+Token>30%)│    │(论文研读+模型研究)│    │(笔记+报告)  │
└─────────┘    └─────────────┘    └─────────────┘
       ↓
┌─────────────┐    ┌─────────────┐
│  线2:优化复盘 │ →  │  系统改进   │
│(复盘+轻维护)  │    │(配置优化)   │
└─────────────┘    └─────────────┘
```

### 2.2 补位任务队列

#### 线1: 学习研究合并（Token上限: 10K/次）

| 任务ID | 任务内容 | 频率 | 产出 |
|--------|----------|------|------|
| LEARN-001 | 专家论文深度研读 | 空闲>2h触发 | 学习笔记 |
| LEARN-002 | AI模型/技术研究 | 每日1次 | 技术报告 |
| LEARN-003 | 行业趋势分析 | 每周2次 | 洞察报告 |
| LEARN-004 | 案例库扩展研究 | 每周3次 | 案例分析 |

#### 线2: 优化复盘合并（Token上限: 5K/次）

| 任务ID | 任务内容 | 频率 | 产出 |
|--------|----------|------|------|
| OPT-001 | 当日工作复盘 | 每日1次 | 复盘日志 |
| OPT-002 | 系统配置轻维护 | 按需 | 优化建议 |
| OPT-003 | 知识图谱更新 | 每日1次 | 图谱增量 |
| OPT-004 | Skill质量自检 | 每周1次 | 自检报告 |

---

## 三、迭代机制（PDCA+极限测试）

### 3.1 每周复盘优化

| 维度 | 检查内容 | 优化动作 |
|------|----------|----------|
| 补位效率 | 补位任务完成率 | 调整任务难度/时长 |
| Token效率 | 单位Token产出价值 | 优化提示词/任务选择 |
| 用户价值 | 补位成果被使用比例 | 调整任务优先级 |
| 系统健康 | 误触发/漏触发次数 | 优化检测阈值 |

### 3.2 极限测试模式（周期末）

**触发条件**: 每月最后1天

**测试内容**:
- 恢复6线全开模式
- 验证最大承载量
- 收集消耗数据
- 评估扩展空间

### 3.3 演化日志

```markdown
## V1.0 (2026-03-10)
- 初始版本，6线并行

## V2.0 (2026-03-12)
- 增加资源监控
- 优化触发逻辑

## V3.0 (2026-03-15)
- 精简为2线模式
- Token管理优化

## V4.0 (2026-03-20)
- 修复脚本误删问题
- 5标准Skill化
- 增加极限测试模式
```

---

## 四、Skill化（可执行）

### 4.1 触发条件

```yaml
zero_idle_trigger:
  condition_1: "user_inactive > 2h"
  condition_2: "token_remaining > 30%"
  condition_3: "no_user_explicit_task"
  condition_4: "time_since_last_fill > 2h"
  
  priority_check:
    - "Token < 30% → 暂停线1，仅保留线2"
    - "Token < 15% → 完全暂停，等待用户指令"
    - "用户明确任务期间 → 不触发补位"
```

### 4.2 执行流程

```python
def zero_idle_enforcer():
    """
    零空置强制执行
    """
    # 1. 状态检测
    if not check_trigger_conditions():
        return "条件不满足，跳过"
    
    # 2. 资源评估
    token_level = get_token_level()
    if token_level == "LOW":
        return "Token不足，暂停补位"
    
    # 3. 选择补位线
    if token_level == "MEDIUM":
        # Token 15-30%，仅执行线2
        execute_line_2_only()
    else:
        # Token > 30%，执行双线
        execute_line_1_learning()
        execute_line_2_optimization()
    
    # 4. 记录执行
    log_fill_activity()
    
    # 5. 产出归档
    archive_outputs()
    
    return "补位执行完成"

def execute_line_1_learning():
    """线1: 学习研究合并"""
    tasks = [
        "expert_paper_reading",
        "ai_model_research", 
        "industry_trend_analysis",
        "case_study_expansion"
    ]
    
    for task in tasks:
        if get_token_consumed() < 10000:  # 10K上限
            result = execute_task(task)
            save_output(result)

def execute_line_2_optimization():
    """线2: 优化复盘合并"""
    tasks = [
        "daily_retrospective",
        "config_maintenance",
        "knowledge_graph_update",
        "skill_self_check"
    ]
    
    for task in tasks:
        if get_token_consumed() < 5000:  # 5K上限
            result = execute_task(task)
            save_output(result)
```

### 4.3 产出标准

| 产出物 | 格式 | 位置 | 标准 |
|--------|------|------|------|
| 学习笔记 | Markdown | `05_📦历史归档/学习笔记/` | 引用来源+个人思考 |
| 技术报告 | Markdown | `05_📦历史归档/研究报告/` | 结构完整+数据支撑 |
| 复盘日志 | Markdown | `memory/` | 客观记录+改进建议 |
| 优化建议 | Markdown | `docs/improvements/` | 具体可行+优先级 |

---

## 五、流程自动化（Cron+脚本）

### 5.1 空闲检测Cron

```json
{
  "job": {
    "name": "zero-idle-check",
    "schedule": "*/30 * * * *",
    "enabled": true,
    "condition": "user_inactive > 2h AND token > 30%"
  }
}
```

### 5.2 自动化脚本

```bash
#!/bin/bash
# scripts/zero-idle-enforcer.sh

echo "=== 零空置强制执行检查 ==="

# 1. 检查用户活跃度
LAST_USER_ACTIVITY=$(get_last_user_activity_timestamp)
CURRENT_TIME=$(date +%s)
INACTIVE_TIME=$((CURRENT_TIME - LAST_USER_ACTIVITY))

if [ $INACTIVE_TIME -lt 7200 ]; then  # 2小时
    echo "用户活跃中，跳过补位"
    exit 0
fi

# 2. 检查Token余量
TOKEN_LEVEL=$(get_token_level)
if [ "$TOKEN_LEVEL" == "CRITICAL" ]; then
    echo "Token不足15%，完全暂停"
    exit 0
fi

# 3. 执行补位
if [ "$TOKEN_LEVEL" == "LOW" ]; then
    echo "Token 15-30%，仅执行线2"
    execute_line_2
else
    echo "Token充足，执行双线"
    execute_line_1 &
    execute_line_2 &
    wait
fi

echo "=== 补位执行完成 ==="
```

### 5.3 极限测试脚本

```bash
#!/bin/bash
# scripts/zero-idle-stress-test.sh
# 每月最后1天执行

echo "=== 零空置极限测试 ==="
echo "测试时间: $(date)"

# 恢复6线全开
export ZERO_IDLE_MODE="STRESS_TEST"

# 执行全量任务
for line in 1 2 3 4 5 6; do
    echo "启动线$line..."
    execute_line_$line &
done
wait

# 收集数据
echo "Token消耗: $(get_token_consumed)"
echo "任务完成数: $(get_completed_tasks)"
echo "系统稳定性: $(get_system_stability)"

# 生成报告
generate_stress_test_report

echo "=== 极限测试完成 ==="
```

---

## 六、质量门控

### 6.1 5标准自检清单

- [x] **全局考虑**: 6层覆盖+资源状态监控
- [x] **系统考虑**: 检测→补位→执行→复盘闭环
- [x] **迭代机制**: 每周复盘+极限测试
- [x] **Skill化**: 条件触发、双线执行、产出归档
- [x] **流程自动化**: Cron检测、脚本执行、报告生成

### 6.2 状态验证

```bash
# 检查当前模式
./scripts/zero-idle-status.sh

# 手动触发测试
./scripts/zero-idle-enforcer.sh --dry-run

# 查看历史记录
tail -50 logs/zero-idle-activity.log
```

---

## 七、使用方式

### 7.1 查看状态

```bash
# 查看当前补位状态
./scripts/zero-idle-status.sh

# 输出示例:
# 当前模式: 精简2线
# Token余量: 65% (充足)
# 用户状态: 空闲(3.5h)
# 上次补位: 2.1h前
# 待执行线1任务: 3
# 待执行线2任务: 2
```

### 7.2 手动控制

```bash
# 强制触发补位
./scripts/zero-idle-enforcer.sh --force

# 切换到极限测试模式
export ZERO_IDLE_MODE="STRESS_TEST"

# 暂停补位
./scripts/zero-idle-pause.sh
```

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*

*版本历史: V1.0(6线)→V2.0(资源监控)→V3.0(精简2线)→V4.0(5标准Skill)*