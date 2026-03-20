---
name: worry-list-manager
version: 2.0.0
description: |
  担忧清单管理器 - 从被动响应到主动预警：
  1. 全局考虑：覆盖人/事/物/环境/外部集成/边界情况
  2. 系统考虑：收集→评估→预警→行动→复盘完整闭环
  3. 迭代机制：PDCA循环，版本历史，反馈收集与模型优化
  4. Skill化：标准SKILL.md格式，可安装可调用
  5. 自动化：cron定时推送+自动扫描+报告生成
author: Satisficing Institute
tags:
  - worry
  - risk
  - early-warning
  - automation
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3"]
---

# 担忧清单管理器 Skill V2.0.0

## S1: 全局考虑 (Global Coverage)

### 1.1 人 - 干系人管理

| 干系人类型 | 关注重点 | 通知方式 | 边界情况 |
|------------|----------|----------|----------|
| Director(人类) | 战略风险、重大决策 | 飞书/邮件 | 紧急时电话 |
| Captain(AI) | 任务冲突、资源瓶颈 | 系统内通知 | 升级至Director |
| Specialist(AI) | 专业能力缺口 | 任务分配时提示 | 培训建议 |
| Auditor(AI) | 质量风险、合规问题 | 审计报告 | 强制阻断 |
| 外部专家 | 领域专业知识 | 邮件/会议 | 定期同步 |

### 1.2 事 - 担忧分类体系

```yaml
worry_categories:
  unresolved_concerns:
    priority: P0
    examples:
      - "专家资料仍未补齐"
      - "API配置状态未知"
      - "案例库进度严重滞后"
    escalation: "24小时内必须处理"
    
  upcoming_deadlines:
    priority: P1
    warning_threshold: "3天内到期"
    escalation_threshold: "1天内到期"
    examples:
      - "项目里程碑截止"
      - "客户交付日期"
      - "合规检查日期"
    
  missed_opportunities:
    priority: P2
    examples:
      - "客户提到的潜在需求"
      - "行业趋势中的切入点"
      - "可复用的方法论沉淀"
    review_cycle: "每周回顾"
    
  resource_risks:
    priority: P1
    examples:
      - "Token预算即将耗尽"
      - "API配额不足"
      - "存储空间告警"
    auto_monitor: true
    
  external_dependencies:
    priority: P1
    examples:
      - "第三方服务不稳定"
      - "外部专家响应延迟"
      - "政策变化风险"
    monitor_source: "外部监控"
```

### 1.3 物 - 资源担忧监控

| 资源类型 | 监控指标 | 预警阈值 | 边界情况处理 |
|----------|----------|----------|--------------|
| Token预算 | 每日消耗率 | >70%预警，>90%紧急 | 自动熔断+申请战略储备 |
| API配额 | 剩余配额比例 | <30%预警 | 切换备用API/降频 |
| 存储空间 | 使用率 | >80%预警 | 自动归档+清理 |
| 计算资源 | CPU/内存 | >85%预警 | 任务队列化+扩容 |
| 网络带宽 | 传输速率 | <50%预警 | 压缩传输+离线处理 |

### 1.4 环境 - 外部环境监测

| 环境因素 | 监测来源 | 预警类型 | 应对策略 |
|----------|----------|----------|----------|
| 政策变化 | 政府公告/行业媒体 | 合规风险 | 规则更新+培训 |
| 竞品动态 | 竞品监控工具 | 机会/威胁 | 策略调整 |
| 技术趋势 | 论文/开源社区 | 能力缺口 | 学习计划 |
| 市场波动 | 行业报告 | 业务风险 | 预案启动 |
| 节假日 | 日历系统 | 资源可用性 | 提前安排 |

### 1.5 外部集成

```yaml
integrations:
  token_budget_enforcer:
    type: 资源监控
    data_flow: "预算告警 → 担忧清单"
    action: "自动创建资源担忧项"
  
  quality_gate_system:
    type: 质量监控
    data_flow: "质量异常 → 担忧清单"
    action: "自动创建质量担忧项"
  
  role_federation:
    type: 任务监控
    data_flow: "任务延迟 → 担忧清单"
    action: "自动创建进度担忧项"
  
  feishu_messaging:
    type: 通知推送
    data_flow: "担忧清单 → 消息通知"
    action: "定时推送担忧简报"
  
  calendar_system:
    type: 截止日期
    data_flow: "日历事件 → 担忧清单"
    action: "自动创建截止担忧项"
```

### 1.6 边界情况处理

| 边界场景 | 检测机制 | 处理策略 |
|----------|----------|----------|
| 担忧过多(每日新增>20) | 计数器 | 批量归类+优先级重排 |
| 担忧过期(超过7天未处理) | 时间戳检查 | 自动归档+复盘分析 |
| 重复担忧 | 相似度检测 | 合并+频次记录 |
| 虚假告警 | 反馈验证 | 调整阈值+模型优化 |
| 系统性风险 | 模式识别 | 升级至Director+专项应对 |

---

## S2: 系统考虑 (Systematic)

### 2.1 担忧管理闭环

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   收集      │ → │   评估      │ → │   预警      │ → │   行动      │ → │   复盘      │
│  Collect    │    │  Evaluate   │    │   Alert     │    │   Act       │    │  Review     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       ↑                                                                            ↓
       └──────────────────────────────── 反馈优化 ← 效果评估 ← 行动结果 ────────────────┘
```

### 2.2 输入处理

| 输入源 | 输入格式 | 验证规则 | 转换处理 |
|--------|----------|----------|----------|
| 系统监控 | JSON事件 | Schema验证 | 标准化担忧项 |
| 人工录入 | 自然语言 | 关键词提取 | 分类+优先级 |
| 外部API | Webhook | 签名验证 | 去重+合并 |
| 定时扫描 | 内部状态 | 阈值对比 | 自动生成 |

### 2.3 评估引擎

```yaml
evaluation_engine:
  impact_scoring:
    high: 10    # 影响战略/客户/合规
    medium: 5   # 影响效率/质量
    low: 1      # 影响便利/体验
  
  urgency_scoring:
    immediate: 10   # <24h
    soon: 5         # 1-3天
    later: 1        # >3天
  
  probability_scoring:
    certain: 10     # >80%
    likely: 5       # 50-80%
    possible: 1     # <50%
  
  priority_calculation: "(impact × 0.4) + (urgency × 0.4) + (probability × 0.2)"
```

### 2.4 输出规范

| 输出类型 | 格式 | 内容要求 |
|----------|------|----------|
| 担忧项 | 结构化数据 | ID/分类/优先级/描述/来源/时间戳 |
| 预警通知 | Markdown | 🔴🟡🟢分级+行动建议 |
| 日报 | 汇总表格 | 新增/处理中/已解决/逾期统计 |
| 趋势报告 | 图表+文字 | 趋势分析+预测+建议 |

### 2.5 反馈闭环

| 反馈类型 | 收集方式 | 处理动作 |
|----------|----------|----------|
| 担忧解决确认 | 任务完成时标记 | 归档+效果评估 |
| 误报反馈 | 用户标记 | 调整评估模型 |
| 漏报反馈 | 事后发现 | 补充监控规则 |
| 处理效果 | 后续跟踪 | 优化处理流程 |

### 2.6 故障处理

| 故障场景 | 检测 | 自动响应 | 升级 |
|----------|------|----------|------|
| 扫描失败 | 超时检测 | 重试3次 | 人工检查 |
| 评估模型异常 | 输出异常 | 切换备用模型 | 技术团队 |
| 通知发送失败 | 回调检测 | 换渠道重试 | 告警 |
| 数据丢失 | 校验失败 | 从备份恢复 | 紧急处理 |

---

## S3: 迭代机制 (Iterative)

### 3.1 PDCA循环

```yaml
Plan(计划):
  - 每周生成担忧管理计划
  - 设定预警准确率目标(≥85%)
  - 规划资源投入

Do(执行):
  - 按计划执行扫描和评估
  - 记录所有操作日志
  - 收集用户反馈

Check(检查):
  - 每日统计准确率/召回率
  - 每周分析趋势
  - 每月评估整体效果

Act(改进):
  - 根据数据调整阈值
  - 优化评估算法
  - 更新分类体系
```

### 3.2 版本历史

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|----------|------|
| v2.0.0 | 2026-03-21 | 5标准全覆盖，系统重构 | 满意解研究所 |
| v1.1.0 | 2026-03-18 | 增加自动扫描功能 | 满意解研究所 |
| v1.0.0 | 2026-03-15 | 初始版本，基础担忧清单 | 满意解研究所 |

### 3.3 反馈收集机制

| 反馈源 | 频率 | 内容 | 处理 |
|--------|------|------|------|
| 用户标记 | 实时 | 误报/漏报标记 | 实时调整模型 |
| 解决确认 | 每次解决 | 解决方式/耗时 | 优化处理流程 |
| 趋势分析 | 每周 | 类型分布/趋势 | 调整监控重点 |
| 满意度调查 | 每月 | 整体满意度 | 重大改进决策 |

### 3.4 优化触发条件

| 指标 | 阈值 | 优化动作 |
|------|------|----------|
| 预警准确率 | <85% | 调整评估权重 |
| 召回率 | <90% | 增加监控维度 |
| 误报率 | >15% | 提高阈值/增加过滤 |
| 平均处理时间 | >预期2倍 | 优化处理流程 |
| 用户满意度 | <4.0/5 | 专项改进计划 |

---

## S4: Skill化 (Skill-ified)

### 4.1 目录结构

```
worry-list-manager/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── worry_runner.py         # 主运行脚本
│   ├── collector.py            # 担忧收集器
│   ├── evaluator.py            # 评估引擎
│   ├── alerter.py              # 预警推送
│   ├── tracker.py              # 跟踪管理
│   └── reporter.py             # 报告生成
├── config/
│   ├── categories.yaml         # 分类定义
│   ├── thresholds.yaml         # 阈值配置
│   └── templates.yaml          # 通知模板
├── data/
│   ├── worries.json            # 担忧数据库
│   └── history/                # 历史归档
└── logs/
    └── worry.log               # 运行日志
```

### 4.2 标准化接口

```python
class WorryListManager:
    
    def add_worry(self, content: str, category: str, source: str) -> WorryID:
        """添加新的担忧项"""
        pass
    
    def evaluate_worries(self) -> List[EvaluatedWorry]:
        """评估所有未处理担忧"""
        pass
    
    def push_alert(self, priority: str = None) -> None:
        """推送预警通知"""
        pass
    
    def track_resolution(self, worry_id: WorryID, resolution: str) -> None:
        """跟踪担忧解决"""
        pass
    
    def generate_report(self, period: str) -> Report:
        """生成周期报告"""
        pass
    
    def scan_system(self) -> List[Worry]:
        """扫描系统生成担忧"""
        pass
```

### 4.3 调用方式

```bash
# 安装Skill
openclaw skill install worry-list-manager

# 添加担忧
openclaw skill run worry-list-manager add --content "API配额不足" --category resource

# 查看担忧清单
openclaw skill run worry-list-manager list --priority P0

# 推送晨间简报
openclaw skill run worry-list-manager push

# 生成报告
openclaw skill run worry-list-manager report --period daily

# 扫描系统
openclaw skill run worry-list-manager scan
```

---

## S5: 自动化 (Automation)

### 5.1 Cron定时任务

```json
{
  "jobs": [
    {
      "name": "worry-list-morning-push",
      "schedule": "17 9 * * *",
      "command": "cd /root/.openclaw/workspace/skills/worry-list-manager && python3 scripts/worry_runner.py push",
      "description": "每日09:17推送担忧清单简报"
    },
    {
      "name": "worry-list-system-scan",
      "schedule": "0 */4 * * *",
      "command": "cd /root/.openclaw/workspace/skills/worry-list-manager && python3 scripts/worry_runner.py scan",
      "description": "每4小时扫描系统状态"
    },
    {
      "name": "worry-list-daily-report",
      "schedule": "53 23 * * *",
      "command": "cd /root/.openclaw/workspace/skills/worry-list-manager && python3 scripts/worry_runner.py report",
      "description": "每日23:53生成担忧日报"
    },
    {
      "name": "worry-list-weekly-review",
      "schedule": "37 22 * * 0",
      "command": "cd /root/.openclaw/workspace/skills/worry-list-manager && python3 scripts/worry_runner.py weekly",
      "description": "每周日22:37生成周回顾"
    }
  ]
}
```

### 5.2 自动化脚本

| 脚本 | 功能 | 触发方式 |
|------|------|----------|
| `worry_runner.py` | 主控脚本 | cron/手动 |
| `collector.py` | 多源数据收集 | 定时/事件 |
| `evaluator.py` | 智能评估 | 收集后自动 |
| `alerter.py` | 分级预警推送 | 高优先级时 |
| `tracker.py` | 状态跟踪 | 持续监控 |
| `reporter.py` | 报告生成 | 定时触发 |

### 5.3 自动监控与告警

| 监控项 | 阈值 | 告警方式 |
|--------|------|----------|
| 新增担忧数(1h) | >10 | 紧急通知 |
| P0担忧未处理 | >4h | 升级告警 |
| 担忧逾期率 | >20% | 日报高亮 |
| 扫描失败 | 连续2次 | 技术告警 |
| 准确率下降 | <80% | 质量告警 |

### 5.4 自动报告生成

| 报告类型 | 频率 | 内容 | 接收者 |
|----------|------|------|--------|
| 晨间简报 | 每日09:17 | 今日关注+行动建议 | Director |
| 扫描报告 | 每4小时 | 新增担忧+状态变化 | 系统日志 |
| 日报 | 每日23:53 | 统计+趋势+建议 | Director |
| 周报 | 每周日22:37 | 深度分析+优化建议 | Director |

---

## 附录：命令参考

| 命令 | 功能 | 示例 |
|------|------|------|
| `add [content]` | 添加担忧 | `add "API配额不足"` |
| `list [options]` | 查看清单 | `list --priority P0` |
| `push` | 推送简报 | `push` |
| `scan` | 系统扫描 | `scan` |
| `resolve [id]` | 标记解决 | `resolve W-001` |
| `report [period]` | 生成报告 | `report weekly` |

---

*版本: v2.0.0*  
*更新日期: 2026-03-21*  
*作者: 满意解研究所*
