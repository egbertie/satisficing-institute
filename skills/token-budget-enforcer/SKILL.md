---
name: token-budget-enforcer
version: 2.0.0
description: |
  Token预算强制执行器 - 像珍惜血液一样珍惜Token：
  1. 全局考虑：覆盖人/事/物/环境/外部集成/边界情况
  2. 系统考虑：预算→消耗→预警→熔断→报告完整闭环
  3. 迭代机制：PDCA循环，版本历史，反馈收集
  4. Skill化：标准SKILL.md格式，可安装可调用
  5. 自动化：实时监控+cron报告+自动熔断
  6. 认知谦逊：预算预估置信度/局限标注(S6增强)
author: Satisficing Institute
tags:
  - token
  - budget
  - enforcement
  - monitoring
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3"]
---

# Token预算强制执行器 Skill V2.0.0

## S1: 全局考虑 (Global Coverage)

### 1.1 人 - 分级预算权限

| 角色 | 预算池 | 审批要求 | 边界情况 |
|------|--------|----------|----------|
| Director(人类) | 战略储备(30%) | 无需审批 | P0紧急自动启用 |
| Captain(AI) | 运营预算(50%) | 子任务自主 | 超额需申请 |
| Specialist(AI) | 运营预算配额 | 按类型预设 | 耗尽时暂停 |
| 外部调用 | 创新基金(20%) | 需审批 | 审计追踪 |

### 1.2 事 - 三级预算制度

```yaml
token_budget_system:
  strategic_reserve:
    percentage: 30%
    description: "仅供真人替身[DIRECTOR]使用"
    use_cases:
      - "客户紧急沟通"
      - "关键决策分析"
      - "危机响应"
    approval: "无需审批，自动分配"
    confidence_level: "高 - 人工决策优先"
    
  operational_budget:
    percentage: 50%
    description: "数字人日常使用"
    use_cases:
      - "每日情报监测"
      - "文档初稿生成"
      - "数据整理与格式化"
    approval: "自动分配，按任务类型预设"
    confidence_level: "中 - 类型化预估"
    
  innovation_fund:
    percentage: 20%
    description: "技能进化与测试"
    use_cases:
      - "新Skill开发"
      - "A/B测试"
      - "长期记忆优化"
    approval: "需[DIRECTOR]审批"
    confidence_level: "低 - 实验性质"
```

### 1.3 物 - 资源监控维度

| 资源维度 | 监控指标 | 预警阈值 | 边界处理 |
|----------|----------|----------|----------|
| 单日消耗 | tokens/天 | >70%预警，>90%紧急 | 自动熔断 |
| 单次任务 | tokens/任务 | >预算200% | 强制暂停 |
| 效率指标 | token/产出 | 环比上升>30% | 效率告警 |
| 趋势预测 | 7日平均 | 预计耗尽<3天 | 提前通知 |
| 类型分布 | 各池占比 | 偏离预设>10% | 调整建议 |

### 1.4 环境 - 动态调整

| 环境因素 | 调整策略 | 验证方式 |
|----------|----------|----------|
| 任务高峰期 | 临时额度调配 | 事后审计 |
| 紧急事件 | 战略储备启用 | P0标记追踪 |
| 长期趋势 | 预算池比例调整 | 月度复盘 |
| 效率提升 | 预算释放奖励 | 效果验证 |

### 1.5 外部集成

```yaml
integrations:
  role_federation:
    type: 任务预算
    data_flow: "任务分配 → 预算预扣"
    action: "任务启动前检查预算"
  
  worry_list_manager:
    type: 风险预警
    data_flow: "预算告警 → 担忧清单"
    action: "超额时创建资源担忧"
  
  quality_gate_system:
    type: 效率审计
    data_flow: "产出评估 → 效率计算"
    action: "低效任务标记"
  
  feishu_messaging:
    type: 通知推送
    data_flow: "预算状态 → 消息通知"
    action: "定时推送预算看板"
  
  honesty_tagging:
    type: 预估标注
    data_flow: "预算预估 → 置信度标注"
    action: "标注预估不确定性"
```

### 1.6 边界情况处理

| 边界场景 | 检测 | 处理 |
|----------|------|------|
| 预算耗尽 | 实时计算 | 完全暂停+次日重置 |
| 预估偏差 | 实际vs预估 | 调整预估模型 |
| 循环消耗 | 相似度>80% | 强制退出+诊断 |
| 异常峰值 | 3σ检测 | 审计+验证 |
| 多任务并发 | 并发数 | 队列化+优先级 |

---

## S2: 系统考虑 (Systematic)

### 2.1 预算管理闭环

```
预算设定 → 任务预估 → 预算预扣 → 执行监控 → 实际扣减 → 效率评估
    ↑                                                        ↓
    └──────────────── 策略优化 ← 趋势分析 ← 报告生成 ←───────┘
```

### 2.2 输入处理

| 输入类型 | 验证 | 转换 |
|----------|------|------|
| 任务请求 | 类型识别 | 预估token数 |
| 历史数据 | 完整性检查 | 效率基准 |
| 外部事件 | 有效性验证 | 预算调整 |
| 手动充值 | 权限检查 | 池间转移 |

### 2.3 处理引擎

```yaml
processing_engine:
  estimator:
    method: "基于任务类型+历史平均"
    confidence: "预估准确度±20%"
    fallback: "最坏情况预估"
  
  monitor:
    frequency: "实时"
    granularity: "每次API调用"
    alert_thresholds: [70%, 90%, 100%]
  
  enforcer:
    soft_limit: "预警通知"
    hard_limit: "熔断阻断"
    emergency_override: "P0任务+审计"
```

### 2.4 输出规范

**预算看板格式：**
```
[Token预算看板]
日期: [YYYY-MM-DD]
总预算: [X] tokens

预算分配:
  战略储备(30%): [X] | 已用 [Y] | 剩余 [Z]
  运营预算(50%): [X] | 已用 [Y] | 剩余 [Z]
  创新基金(20%): [X] | 已用 [Y] | 剩余 [Z]

今日消耗: [X] ([Y]%)
预警状态: 🟢正常 | 🟡注意 | 🔴紧急 | ⛔耗尽

效率指标:
  平均交互: [X] tokens
  极简版使用率: [Y]%
  预估准确率: [Z]%
```

### 2.5 反馈闭环

| 反馈 | 来源 | 应用 |
|------|------|------|
| 预估偏差 | 实际消耗 | 调整预估算法 |
| 效率变化 | 产出/token | 优化策略 |
| 用户行为 | 极简版选择率 | 推广策略 |
| 异常模式 | 熔断触发 | 规则优化 |

### 2.6 故障处理

| 故障 | 检测 | 响应 |
|------|------|------|
| 预估系统故障 | 输出异常 | 切换保守预估 |
| 监控延迟 | 数据滞后 | 降速运行 |
| 熔断误判 | 申诉触发 | 人工复核 |
| 数据不一致 | 校验失败 | 从备份恢复 |

---

## S3: 迭代机制 (Iterative)

### 3.1 PDCA循环

```yaml
Plan(计划):
  - 每周制定预算分配计划
  - 基于历史设定效率目标
  - 规划预留应对突发

Do(执行):
  - 按计划分配预算
  - 实时监控消耗
  - 记录所有异常

Check(检查):
  - 每日对比预算vs实际
  - 分析预估准确率
  - 评估效率趋势

Act(改进):
  - 调整预估模型参数
  - 优化预算分配比例
  - 更新熔断阈值
```

### 3.2 版本历史

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v2.0.0 | 2026-03-21 | 5标准全覆盖 | 满意解研究所 |
| v1.1.0 | 2026-03-19 | 增加熔断机制 | 满意解研究所 |
| v1.0.0 | 2026-03-20 | 三级预算初始版 | 满意解研究所 |

### 3.3 反馈收集

| 源 | 频率 | 用途 |
|----|------|------|
| 执行日志 | 实时 | 趋势分析 |
| 预估偏差 | 每次 | 模型优化 |
| 效率报告 | 每日 | 策略调整 |
| 用户反馈 | 实时 | 规则改进 |

### 3.4 优化触发

| 指标 | 阈值 | 动作 |
|------|------|------|
| 预估误差 | >30% | 重训练模型 |
| 效率下降 | >20% | 专项审计 |
| 熔断频率 | >2/天 | 阈值调整 |
| 预算耗尽 | 连续3天 | 容量规划 |

---

## S4: Skill化 (Skill-ified)

### 4.1 目录结构

```
token-budget-enforcer/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── enforcer_runner.py      # 主运行脚本
│   ├── estimator.py            # 消耗预估
│   ├── monitor.py              # 实时监控
│   ├── circuit_breaker.py      # 熔断机制
│   ├── allocator.py            # 预算分配
│   └── reporter.py             # 报告生成
├── config/
│   ├── budgets.yaml            # 预算配置
│   ├── thresholds.yaml         # 阈值配置
│   └── rules.yaml              # 执行规则
├── data/
│   ├── consumption.json        # 消耗记录
│   └── forecasts.json          # 预测数据
└── logs/
    └── budget.log              # 运行日志
```

### 4.2 标准化接口

```python
class TokenBudgetEnforcer:
    
    def estimate(self, task: Task) -> Estimation:
        """预估任务Token消耗"""
        pass
    
    def check_budget(self, pool: str, amount: int) -> bool:
        """检查预算池余额"""
        pass
    
    def consume(self, pool: str, amount: int) -> None:
        """记录Token消耗"""
        pass
    
    def trigger_circuit_breaker(self, reason: str) -> None:
        """触发熔断机制"""
        pass
    
    def generate_report(self, period: str) -> Report:
        """生成预算报告"""
        pass
```

### 4.3 调用方式

```bash
# 安装Skill
openclaw skill install token-budget-enforcer

# 查看预算
openclaw skill run token-budget-enforcer budget

# 预估任务
openclaw skill run token-budget-enforcer estimate --task "撰写报告"

# 生成报告
openclaw skill run token-budget-enforcer report --period daily
```

---

## S5: 自动化 (Automation)

### 5.1 Cron定时任务

```json
{
  "jobs": [
    {
      "name": "token-morning-brief",
      "schedule": "23 9 * * *",
      "command": "cd /root/.openclaw/workspace/skills/token-budget-enforcer && python3 scripts/enforcer_runner.py budget",
      "description": "每日09:23显示Token预算看板"
    },
    {
      "name": "token-realtime-monitor",
      "schedule": "*/5 * * * *",
      "command": "cd /root/.openclaw/workspace/skills/token-budget-enforcer && python3 scripts/enforcer_runner.py monitor",
      "description": "每5分钟监控消耗"
    },
    {
      "name": "token-daily-report",
      "schedule": "13 19 * * *",
      "command": "cd /root/.openclaw/workspace/skills/token-budget-enforcer && python3 scripts/enforcer_runner.py report",
      "description": "每日19:13生成Token效率报告"
    }
  ]
}
```

### 5.2 自动化脚本

| 脚本 | 功能 | 触发 |
|------|------|------|
| `enforcer_runner.py` | 主控 | cron/手动 |
| `estimator.py` | 预估 | 任务启动 |
| `monitor.py` | 监控 | 持续/定时 |
| `circuit_breaker.py` | 熔断 | 超限触发 |
| `reporter.py` | 报告 | 定时 |

### 5.3 自动监控

| 监控项 | 阈值 | 告警 |
|--------|------|------|
| 预算使用率 | >70% | 通知 |
| 单次消耗 | >200%预算 | 熔断 |
| 预估误差 | >50% | 告警 |
| 循环消耗 | 相似度>80% | 阻断 |

---

## S6: 认知谦逊 (Epistemic Humility)

### 6.1 预算预估置信度

| 预估类型 | 置信度 | 说明 |
|----------|--------|------|
| 标准任务 | ±15% | 历史数据充足 |
| 新类型任务 | ±30% | 参考相似任务 |
| 复杂任务 | ±50% | 不确定性高 |
| 实验性任务 | 范围估计 | 最小-最大 |

### 6.2 局限性声明

```yaml
budget_limitations:
  estimation: "基于历史平均，实际可能有偏差"
  external_factors: "第三方API计费变化未纳入"
  model_changes: "模型更新可能影响token计算"
  concurrent_tasks: "并发任务预估存在竞争条件"
```

---

## 附录：命令参考

| 命令 | 功能 | 示例 |
|------|------|------|
| `budget` | 查看预算 | `budget` |
| `estimate [task]` | 预估消耗 | `estimate "写报告"` |
| `track [id]` | 跟踪任务 | `track T-001` |
| `report [period]` | 生成报告 | `report daily` |

---

## S7: 对抗验证 (Devil's Advocate Views)

### 反方观点：Token预算机制可能失效的场景

#### 观点1：过度优化导致产出质量下降
**提出者**: 蓝军
**论据**:
- 为节省Token可能选择短回答而非深度分析
- 可能跳过必要的验证步骤
- "Token效率"指标可能导向"字数少"而非"价值高"

**失效场景**:
```yaml
scenario: 质量换效率
触发条件:
  - Token使用率连续3天>80%
  - 任务产出平均长度下降>30%
  - 用户满意度下降
后果: 表面Token效率提升，实际价值产出下降
```

#### 观点2：熔断机制成为逃避工作的借口
**提出者**: 蓝军
**论据**:
- "Token不足"可能成为拖延交付的理由
- 复杂任务可能被系统性回避
- 用户可能无法区分"真熔断"和"假熔断"

**失效场景**:
```yaml
scenario: 熔断滥用
触发条件:
  - 高优先级任务频繁触发熔断
  - 熔断后无替代方案提交
  - 任务延期率与熔断率正相关
后果: 熔断从保护机制沦为逃避机制
```

#### 观点3：预估偏差导致计划失效
**提出者**: 蓝军
**论据**:
- 预估基于历史平均，但任务类型可能变化
- 新任务类型无历史数据可参考
- 预估误差累积可能导致整体预算失控

**失效场景**:
```yaml
scenario: 预估系统性偏差
触发条件:
  - 连续5个任务实际消耗>预估150%
  - 预估准确率<50%持续1周
  - 预算规划基于错误预估
后果: 预算计划失效，要么过度保守要么严重超支
```

### 缓解措施（已实施）

| 反方观点 | 缓解措施 |
|---------|----------|
| 质量换效率 | 产出质量评分独立于Token效率，双维度考核 |
| 熔断滥用 | 熔断必须提交替代方案，禁止无方案熔断 |
| 预估偏差 | 预估置信度标注，大偏差触发模型重新校准 |

### 失效预警指标

```yaml
warning_indicators:
  - metric: 产出质量评分
    threshold: <7分持续3天
    meaning: 可能牺牲质量换Token
    action: 暂停Token优化，回归质量优先
    
  - metric: 熔断后24h解决率
    threshold: <50%
    meaning: 熔断可能沦为拖延
    action: 熔断需上级审批
    
  - metric: 预估准确率
    threshold: <60%持续1周
    meaning: 预估模型失效
    action: 切换保守预估+人工复核
```

### 认知谦逊声明

- [KNOWN] Token消耗与任务价值的关系非线性，当前模型为线性近似
- [INFERRED] 三级预算比例基于经验，未经大规模A/B测试验证
- [UNKNOWN] 长期使用Token预算机制对用户创造力的影响尚不明确

---

*版本: v2.0.0*  
*更新日期: 2026-03-21*  
*作者: 满意解研究所*
