# Daily Cron 合并优化方案 V1.2

> **基于第一性原理的Cron优化设计**
> 
> 创建时间: 2026-03-15  
> 版本: 1.2  
> 状态: 🟡 待实施

---

## 📋 执行摘要

### 问题背景
用户发现多个Daily Cron时间错开（09:00, 09:17, 09:30, 22:00, 22:17），询问是否可以合并以减少Token使用。

### 解决方案
采用**双Cron架构**（方案A），将9个Daily Cron合并为3个：
- **晨间统一Cron**（09:00）：合并6个任务
- **晚间统一Cron**（22:00）：合并3个任务
- **保留独立**：每日站会（09:30）需人工参与

### 预期收益
| 指标 | 合并前 | 合并后 | 节省 |
|------|--------|--------|------|
| Daily Cron数量 | 9个 | 3个 | **-67%** |
| 每日调度开销 | 9次 | 3次 | **-67%** |
| 预估Token/日 | ~35K | ~25K | **-28%** |
| 用户打扰次数 | 9次通知 | 3次通知 | **-67%** |

---

## 🔬 第一性原理分析

### 原理1：执行开销第一性

每个Cron执行都有固定开销：
- 调度器唤醒开销
- 上下文加载开销
- 基础Token消耗（即使任务简单）

**合并收益**：
- 5个Daily Cron → 1个Daily Cron = 减少4次调度开销
- 预估Token节省：15-20%

### 原理2：任务亲和性第一性

Daily Cron天然可以分组：
- **晨间组**（09:xx）：晨报、安全检查、资讯采集、维护
- **晚间组**（22:xx）：日报、复盘、审计、摘要

**合并原则**：
1. 同时间段（1小时内）的Daily任务合并
2. 同类性质（检查类/报告类）的任务合并
3. 依赖关系弱的任务才能合并

### 原理3：时间体验第一性

合并不能以牺牲用户体验为代价：
- 晨报需要在用户工作前完成（09:00前）
- 日报需要在当日结束后生成（22:00后）
- 安全检查需要固定时间形成习惯

---

## 📊 当前Daily Cron审计

### 晨间Cron组（09:00-09:30）

| 时间 | Cron名称 | 类型 | 可合并性 | 说明 |
|------|----------|------|----------|------|
| 09:00 | 每日晨报生成 | 报告 | ✅ 核心 | 用户工作前必须完成 |
| 09:00 | 每日安全检查 | 检查 | ✅ 可合并 | 轻量检查，可并行 |
| 09:00 | milestone-daily-check | 检查 | ✅ 可合并 | 检查里程碑进度 |
| 09:00 | learning-morning | 学习 | ⚠️ 可选 | 学习提醒，可选合并 |
| 09:00 | Kimi Search每日资讯采集 | 采集 | ✅ 可合并 | 信息采集任务 |
| 09:17 | auto_maintenance (Tier1) | 维护 | ✅ 可合并 | 系统维护，可后台运行 |
| 09:17 | economic_daily (Tier1) | 监测 | ✅ 可合并 | 经济数据监测 |
| 09:30 | 每日站会召开 | 会议 | ❌ 独立 | 需人工参与，保持独立 |

### 晚间Cron组（22:00-22:17）

| 时间 | Cron名称 | 类型 | 可合并性 | 说明 |
|------|----------|------|----------|------|
| 22:00 | daily-progress-report | 报告 | ✅ 核心 | 每日进度报告 |
| 22:00 | 每日提醒审计检查 | 审计 | ✅ 可合并 | 检查当日提醒执行情况 |
| 22:00 | daily-autonomous-summary | 摘要 | ✅ 可合并 | 六通道汇总 |
| 22:17 | daily_report (Tier2) | 报告 | ✅ 可合并 | 详细日报，时间接近22:00 |

---

## 🏗️ 合并方案设计

### 方案A：双Cron架构（⭐ 推荐）

#### 晨间统一Cron：09:00

```yaml
name: "晨间综合检查与晨报"
time: "0 9 * * *"  # 09:00
tasks:
  - 每日晨报生成（保留）
  - 每日安全检查（保留）
  - milestone检查（保留）
  - Kimi Search资讯采集（保留）
  - auto_maintenance（Tier1，如无冲突则执行）
  - economic_daily（Tier1，如无冲突则执行）
sequence: parallel  # 并行执行
estimated_duration: 3-5分钟
estimated_token: ~8K（原5个Cron共~15K）
```

**执行顺序**：
```
1. 安全检查（最快，30秒内）
2. Kimi Search资讯采集（并行，60秒）
3. milestone检查（并行，30秒）
4. auto_maintenance（后台，不阻塞）
5. economic_daily（后台，不阻塞）
6. 晨报生成（最后，汇总以上结果，120秒）
```

#### 晚间统一Cron：22:00

```yaml
name: "晚间综合报告与复盘"
time: "0 22 * * *"  # 22:00
tasks:
  - daily-progress-report（保留）
  - 每日提醒审计检查（保留）
  - daily-autonomous-summary（保留）
  - daily_report（Tier2，30分钟确认窗口，从22:17提前）
sequence: sequential  # 顺序执行（报告类）
estimated_duration: 5-8分钟
estimated_token: ~12K（原4个Cron共~20K）
```

**执行顺序**：
```
1. 提醒审计检查（检查当日提醒关键词，60秒）
2. daily-autonomous-summary（汇总六通道，90秒）
3. daily-progress-report（生成进度报告，120秒）
4. daily_report（Tier2，30分钟确认窗口，合并入此组）
```

#### 保留独立Cron

| Cron名称 | 时间 | 保留原因 |
|----------|------|----------|
| 每日站会召开 | 09:30 | 需人工参与，保持独立触发 |
| learning-morning | 09:00 | 可选合并，如Token紧张则并入晨间组 |

---

### 方案B：单Cron架构（极端优化）

**全量统一Cron：每日06:00**

```yaml
name: "每日全量检查与报告"
time: "0 6 * * *"  # 06:00（提前，避开工作高峰）
tasks:
  # 晨间任务
  - 晨报生成
  - 安全检查
  - milestone检查
  - 资讯采集
  # 预生成晚间报告（提前）
  - 日报预生成（草稿，22:00后刷新）
sequence: parallel + cache
```

**⚠️ 问题**：晚间报告需当日数据，06:00生成不准确。**不推荐**。

---

### 方案C：动态批次架构（高级）

```python
# 一个Cron，动态分发
name: "Daily Batch Orchestrator"
time: "0 9,22 * * *"  # 09:00和22:00各触发一次

if trigger_time == "09:00":
    run_morning_batch()  # 执行晨间任务组
elif trigger_time == "22:00":
    run_evening_batch()  # 执行晚间任务组
```

---

## 🎯 推荐方案：方案A（双Cron架构）

### 为什么选择方案A？

1. **平衡性**：在Token节省和任务准确性之间取得最佳平衡
2. **可维护性**：两个Cron职责清晰，晨间检查/晚间报告
3. **扩展性**：未来新增任务容易归类到对应时段
4. **安全性**：关键任务（站会）保持独立，避免合并风险

---

## 📋 实施计划

### 前置检查清单

- [ ] 备份当前所有Cron配置
- [ ] 确认各任务无强时间依赖
- [ ] 验证任务间无冲突资源
- [ ] 准备回滚脚本

### 步骤1：创建合并后的Cron

#### 晨间统一Cron

```python
cron.add({
    "name": "morning-batch-check",
    "schedule": "0 9 * * *",
    "tasks": [
        "security_check",
        "info_collection", 
        "milestone_check",
        "auto_maintenance",
        "economic_daily",
        "daily_morning_report"
    ],
    "parallel": True,
    "timeout": 600
})
```

#### 晚间统一Cron

```python
cron.add({
    "name": "evening-batch-report",
    "schedule": "0 22 * * *",
    "tasks": [
        "reminder_audit",
        "autonomous_summary",
        "daily_progress",
        "daily_report"  # 从22:17提前，统一22:00
    ],
    "parallel": False,  # 报告类顺序执行
    "timeout": 900
})
```

### 步骤2：禁用旧Cron

| 原Cron时间 | 原Cron名称 | 操作 |
|------------|------------|------|
| 09:00 | 每日安全检查 | 禁用 |
| 09:00 | milestone-daily-check | 禁用 |
| 09:00 | Kimi Search每日资讯采集 | 禁用 |
| 09:17 | auto_maintenance | 禁用 |
| 09:17 | economic_daily | 禁用 |
| 22:00 | 每日提醒审计检查 | 禁用 |
| 22:00 | daily-autonomous-summary | 禁用 |
| 22:17 | daily_report | 禁用 |

**保留的Cron**：
- 09:00 每日晨报生成 → 并入晨间组
- 09:00 daily-progress-report → 并入晚间组（时间调整）
- 09:30 每日站会召开 → 保持独立

### 步骤3：测试验证

| 阶段 | 时间 | 验证内容 |
|------|------|----------|
| Day 1 | 实施后 | 观察合并后Cron执行效果，检查日志 |
| Day 2-3 | 48小时内 | 调优执行顺序和超时设置 |
| Day 7 | 1周后 | 评估Token节省效果，对比历史数据 |

---

## 🛡️ 回滚方案

### 自动备份策略

实施脚本会自动备份：
- 原Cron配置 → `backups/cron-pre-merge-YYYYMMDD.json`
- 保留7天，过期自动清理

### 一键回滚

```bash
# 回滚到合并前状态
./scripts/cron-daily-merge.sh --rollback

# 或手动回滚
claw cron merge-daily --rollback
```

### 回滚触发条件

- 合并后任务执行失败率 > 20%
- 关键报告未按时生成
- 用户明确要求回滚

---

## 📈 Token预算与收益

### 当前状态
- **当前余量**: ~45%
- **预估消耗**: 8K Token（实施过程）

### 长期收益
- **每日节省**: ~10K Token
- **月度节省**: ~300K Token
- **投资回收期**: 1天内

---

## 🔧 技术细节

### 任务依赖图

```
晨间组（09:00）:
├── 安全检查 ──┐
├── 资讯采集 ──┼──> 晨报生成
├── milestone ─┘
├── auto_maintenance（后台）
└── economic_daily（后台）

晚间组（22:00）:
├── 提醒审计检查
├── daily-autonomous-summary
├── daily-progress-report
└── daily_report
```

### 错误处理策略

1. **并行任务失败**：记录错误，继续执行后续任务
2. **顺序任务失败**：中断后续依赖任务，通知用户
3. **超时处理**：超过timeout自动终止，标记为失败

---

## 📝 附录

### A. 原Cron清单

<details>
<summary>点击查看完整原Cron列表</summary>

#### 晨间（09:00-09:30）
1. `daily-morning-report` - 每日晨报生成
2. `security-daily-check` - 每日安全检查
3. `milestone-daily-check` - 里程碑检查
4. `learning-morning` - 晨间学习
5. `kimi-search-daily` - 资讯采集
6. `auto-maintenance` - 系统维护（09:17）
7. `economic-daily` - 经济监测（09:17）
8. `daily-standup` - 每日站会（09:30）

#### 晚间（22:00-22:17）
1. `daily-progress-report` - 进度报告
2. `reminder-audit` - 提醒审计
3. `daily-autonomous-summary` - 自主摘要
4. `daily-report` - 详细日报（22:17）

</details>

### B. 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-03-15 | 初始方案设计 |
| 1.1 | 2026-03-15 | 添加回滚方案 |
| 1.2 | 2026-03-15 | 完善实施脚本和Token分析 |

### C. 参考文档

- [Cron优化最佳实践](./CRON_BEST_PRACTICES.md)
- [Token使用优化指南](./TOKEN_OPTIMIZATION.md)

---

## ✅ 审批记录

| 角色 | 签名 | 日期 | 意见 |
|------|------|------|------|
| 方案设计 | - | 2026-03-15 | 待审批 |
| 技术评审 | - | - | 待评审 |
| 实施确认 | - | - | 待确认 |

---

> **文档状态**: 🟡 待实施  
> **最后更新**: 2026-03-15 22:49 GMT+8  
> **维护者**: System Agent
