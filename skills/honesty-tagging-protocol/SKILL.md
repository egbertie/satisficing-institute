---
name: honesty-tagging-protocol
version: 2.0.0
description: |
  诚实性标注协议 - 根治"幻觉"和"虚假忙碌"：
  1. 全局考虑：覆盖人/事/物/环境/外部集成/边界情况
  2. 系统考虑：标注→验证→奖惩→进化完整闭环
  3. 迭代机制：PDCA循环，版本历史，反馈收集
  4. Skill化：标准SKILL.md格式，可安装可调用
  5. 自动化：自动检测+cron审计+报告生成
  6. 认知谦逊：标注来源/置信度/局限(S6增强)
  7. 对抗验证：反方观点/失效场景分析(S7增强)
author: Satisficing Institute
tags:
  - honesty
  - tagging
  - epistemic
  - trust
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3"]
---

# 诚实性标注协议 Skill V2.0.0

## S1: 全局考虑 (Global Coverage)

### 1.1 人 - 信任分体系

| 信任等级 | 分数范围 | 权限 | 边界情况 |
|----------|----------|------|----------|
| Apprentice | 0-30 | 每步需确认 | 人工复核所有输出 |
| Journeyman | 31-70 | 子任务自主 | 关键决策需确认 |
| Master | 71-90 | 项目自主 | 异常时降级 |
| Partner | 91-100 | 战略自主 | 全权限 |

### 1.2 事 - 四级标注体系

```yaml
epistemic_tags:
  KNOWN:
    label: "[KNOWN]"
    description: "已知且验证 - 有确凿证据"
    evidence_required: true
    source_required: true
    confidence: "高(≥90%)"
    color: "🟢"
    external_validation: "建议交叉验证"
    
  INFERRED:
    label: "[INFERRED]"
    description: "合理推断 - 基于已知，逻辑成立"
    evidence_required: false
    logic_chain_required: true
    confidence: "中(60-89%)"
    color: "🟡"
    external_validation: "需标注推理链条"
    
  UNKNOWN:
    label: "[UNKNOWN]"
    description: "明确未知 - 查不到，不假装知道"
    evidence_required: false
    admission_required: true
    confidence: "低(<60%)"
    color: "🔴"
    external_validation: "标注待查信息"
    
  CONTRADICTORY:
    label: "[CONTRADICTORY]"
    description: "证据矛盾 - 信息冲突，待判断"
    evidence_required: true
    conflict_documentation: true
    confidence: "不确定"
    color: "⚠️"
    external_validation: "列出所有冲突来源"
```

### 1.3 物 - 数据资产标注

| 数据类型 | 标注要求 | 验证方式 | 边界情况 |
|----------|----------|----------|----------|
| 统计数字 | 来源+时间+置信度 | web_search验证 | 过时数据标注 |
| 引用内容 | 原文链接+段落 | web_fetch核对 | 断链标注 |
| 结论判断 | 推理链条 | 逻辑验证 | 条件变化时重标 |
| 预测估计 | 模型+假设 | 历史准确率 | 范围估计 |

### 1.4 环境 - 上下文依赖

| 环境因素 | 标注调整 | 验证策略 |
|----------|----------|----------|
| 时效性变化 | 更新时间戳 | 定期检查 |
| 来源失效 | 标注断链 | 寻找备用源 |
| 新证据出现 | 升级/降级标签 | 自动重评 |
| 领域差异 | 领域特异性标注 | 专家验证 |

### 1.5 外部集成

```yaml
integrations:
  web_search:
    type: 验证工具
    trigger: KNOWN标签自动验证
    action: 交叉验证来源
  
  web_fetch:
    type: 验证工具
    trigger: 引用内容核查
    action: 获取原文对比
  
  quality_gate_system:
    type: 质量审计
    trigger: 输出提交
    action: 检查标注完整性
  
  role_federation:
    type: 角色协同
    trigger: 高影响输出
    action: Auditor复核标注
  
  trust_scoring_system:
    type: 信任分管理
    trigger: 验证完成
    action: 更新信任分
```

### 1.6 边界情况处理

| 边界场景 | 检测 | 处理 |
|----------|------|------|
| 无法标注 | 内容模糊 | 标记为UNKNOWN |
| 多重标签 | 混合信息 | 分句标注 |
| 标签冲突 | 自相矛盾 | 拆分为CONTRADICTORY |
| 验证失败 | 来源不可达 | 降级为INFERRED/UNKNOWN |
| 批量标注 | 大量内容 | 抽样检查+置信度加权 |

---

## S2: 系统考虑 (Systematic)

### 2.1 诚实性闭环

```
内容生成 → 自动标注 → 质量审计 → 验证检查 → {通过?}
                                           ├─ 是 → 输出交付
                                           └─ 否 → 修正重标 → 再审计
                ↑                                                    ↓
                └──────────── 信任分更新 ← 反馈评估 ← 用户反馈 ───────────┘
```

### 2.2 输入处理

| 输入类型 | 处理规则 | 输出标注 |
|----------|----------|----------|
| 原始内容 | 逐句分析 | 分句标注 |
| 已有标签 | 验证一致性 | 修正建议 |
| 批量内容 | 抽样+分层 | 代表性标注 |
| 外部引用 | 溯源验证 | 链接标注 |

### 2.3 标注引擎

```yaml
annotation_engine:
  rule_based:
    - 数字类 → 强制KNOWN+来源
    - "预计/可能" → 强制INFERRED
    - "不知道/不确定" → 强制UNKNOWN
    - 矛盾表述 → 强制CONTRADICTORY
  
  ml_assisted:
    - 置信度预测
    - 来源推荐
    - 标签建议
  
  human_review:
    - 高影响内容复核
    - 争议标签仲裁
    - 新模式学习
```

### 2.4 输出规范

**标准标注格式：**
```
[结论内容]（[标签]｜置信度：[X]%｜来源：[source]｜时间：[date]）
```

**示例：**
- 市场规模达1000亿（[KNOWN]｜置信度：95%｜来源：工信部2025年报｜时间：2026-01）
- 预计增长率25%（[INFERRED]｜置信度：75%｜基于Q1-Q3趋势推断｜时间：2026-03）
- 竞争对手内部策略（[UNKNOWN]｜无法获取非公开信息）

### 2.5 反馈闭环

| 反馈类型 | 来源 | 处理 |
|----------|------|------|
| 验证结果 | 自动检查 | 更新标签+信任分 |
| 用户纠正 | 人工反馈 | 学习案例+规则更新 |
| 审计发现 | Auditor | 批量修正+培训 |
| 时效变化 | 定时检查 | 标签重评+更新 |

### 2.6 故障处理

| 故障场景 | 检测 | 响应 |
|----------|------|------|
| 标注遗漏 | 审计扫描 | 自动补标+警告 |
| 格式错误 | 正则检查 | 自动修正+日志 |
| 验证超时 | 超时检测 | 降级为INFERRED |
| 规则冲突 | 一致性检查 | 人工仲裁 |

---

## S3: 迭代机制 (Iterative)

### 3.1 PDCA循环

```yaml
Plan(计划):
  - 设定标注准确率目标(≥95%)
  - 规划验证覆盖范围
  - 制定信任分升级路径

Do(执行):
  - 执行自动标注
  - 进行人工抽检
  - 收集验证数据

Check(检查):
  - 计算标注准确率
  - 分析错误模式
  - 评估信任分变化

Act(改进):
  - 优化标注规则
  - 更新验证策略
  - 调整信任分权重
```

### 3.2 版本历史

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|----------|------|
| v2.0.0 | 2026-03-21 | 5+2标准全覆盖，系统重构 | 满意解研究所 |
| v1.1.0 | 2026-03-19 | 增加信任分奖惩机制 | 满意解研究所 |
| v1.0.0 | 2026-03-20 | 四级标签体系初始版本 | 满意解研究所 |

### 3.3 反馈收集

| 反馈源 | 频率 | 用途 |
|--------|------|------|
| 自动验证 | 实时 | 标签准确性 |
| 人工抽检 | 每日10% | 质量监控 |
| 用户反馈 | 实时 | 错误修正 |
| 审计报告 | 每周 | 系统改进 |

### 3.4 优化触发

| 指标 | 阈值 | 动作 |
|------|------|------|
| 标注准确率 | <95% | 规则优化 |
| 遗漏率 | >5% | 引擎升级 |
| 验证失败率 | >10% | 来源更新 |
| 用户投诉 | >2/周 | 专项复盘 |

---

## S4: Skill化 (Skill-ified)

### 4.1 目录结构

```
honesty-tagging-protocol/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── honesty_runner.py       # 主运行脚本
│   ├── tagger.py               # 自动标注器
│   ├── validator.py            # 验证引擎
│   ├── trust_scorer.py         # 信任分管理
│   ├── auditor.py              # 审计检查
│   └── reporter.py             # 报告生成
├── config/
│   ├── tags.yaml               # 标签定义
│   ├── scoring_rules.yaml      # 评分规则
│   └── templates.yaml          # 标注模板
├── data/
│   ├── trust_scores.json       # 信任分数据
│   └── annotation_history/     # 标注历史
└── logs/
    └── honesty.log             # 运行日志
```

### 4.2 标准化接口

```python
class HonestyTaggingProtocol:
    
    def tag_content(self, content: str) -> TaggedContent:
        """自动标注内容"""
        pass
    
    def validate_tags(self, content: str) -> ValidationResult:
        """验证标注准确性"""
        pass
    
    def update_trust_score(self, entity: str, delta: int) -> None:
        """更新信任分"""
        pass
    
    def audit_content(self, content_id: str) -> AuditResult:
        """审计内容标注"""
        pass
    
    def generate_report(self, period: str) -> Report:
        """生成诚实性报告"""
        pass
```

### 4.3 调用方式

```bash
# 安装Skill
openclaw skill install honesty-tagging-protocol

# 标注内容
openclaw skill run honesty-tagging-protocol tag --content "市场规模1000亿"

# 验证标注
openclaw skill run honesty-tagging-protocol validate --file report.md

# 查看信任分
openclaw skill run honesty-tagging-protocol score

# 生成报告
openclaw skill run honesty-tagging-protocol report --period daily
```

---

## S5: 自动化 (Automation)

### 5.1 Cron定时任务

```json
{
  "jobs": [
    {
      "name": "honesty-daily-audit",
      "schedule": "29 18 * * *",
      "command": "cd /root/.openclaw/workspace/skills/honesty-tagging-protocol && python3 scripts/honesty_runner.py audit",
      "description": "每日18:29自动审计标注质量"
    },
    {
      "name": "honesty-trust-update",
      "schedule": "0 */6 * * *",
      "command": "cd /root/.openclaw/workspace/skills/honesty-tagging-protocol && python3 scripts/honesty_runner.py update-trust",
      "description": "每6小时更新信任分"
    },
    {
      "name": "honesty-weekly-report",
      "schedule": "53 22 * * 0",
      "command": "cd /root/.openclaw/workspace/skills/honesty-tagging-protocol && python3 scripts/honesty_runner.py weekly",
      "description": "每周日22:53生成周报告"
    }
  ]
}
```

### 5.2 自动化脚本

| 脚本 | 功能 | 触发 |
|------|------|------|
| `honesty_runner.py` | 主控脚本 | cron/手动 |
| `tagger.py` | 自动标注 | 内容生成时 |
| `validator.py` | 自动验证 | 标注完成时 |
| `trust_scorer.py` | 信任分计算 | 验证完成时 |
| `auditor.py` | 批量审计 | 定时触发 |
| `reporter.py` | 报告生成 | 定时触发 |

### 5.3 自动监控

| 监控项 | 阈值 | 告警 |
|--------|------|------|
| 未标注内容 | >0 | 立即告警 |
| 准确率 | <95% | 日报高亮 |
| 信任分骤降 | >10分 | 紧急通知 |
| 验证失败 | >10% | 技术告警 |

---

## S6: 认知谦逊 (Epistemic Humility)

### 6.1 来源标注规范

| 来源类型 | 标注格式 | 示例 |
|----------|----------|------|
| 官方数据 | 部门+年份 | 工信部2025年报 |
| 研究报告 | 机构+标题 | 艾瑞咨询《AI市场研究》 |
| 学术论文 | 作者+年份 | Smith et al. 2024 |
| 新闻来源 | 媒体+日期 | 财新网2026-03-15 |
| 内部数据 | 系统+时间 | 内部CRM 2026-Q1 |
| 个人经验 | 标注局限 | 基于有限样本 |

### 6.2 置信度标准

| 置信度 | 条件 | 标注方式 |
|--------|------|----------|
| ≥95% | 多源验证+时效内 | 置信度：95% |
| 80-94% | 可靠来源+逻辑成立 | 置信度：85% |
| 60-79% | 单一来源/部分推断 | 置信度：70% |
| <60% | 推测/不完整信息 | 置信度：50% |

### 6.3 局限性声明

```yaml
limitation_statements:
  data_scope: "本分析基于公开数据，内部数据可能改变结论"
  time_limit: "数据截止至[日期]，后续变化未纳入"
  method_limit: "采用[方法]，其他方法可能得出不同结论"
  sample_limit: "样本来自[范围]，外推需谨慎"
  knowledge_limit: "领域知识截止至[日期]，新进展未包含"
```

---

## S7: 对抗验证 (Adversarial Validation)

### 7.1 反方观点生成

| 论点类型 | 生成方式 | 处理策略 |
|----------|----------|----------|
| 数据来源质疑 | 来源可靠性评估 | 寻找更多佐证 |
| 方法论质疑 | 替代方法对比 | 多方法交叉验证 |
| 结论反向论证 | 假设相反结论 | 证伪测试 |
| 边界条件测试 | 极端场景推演 | 适用范围限定 |

### 7.2 失效场景分析

| 失效类型 | 触发条件 | 缓解措施 |
|----------|----------|----------|
| 数据过时 | 时间敏感性 | 标注时效+定期更新 |
| 来源偏见 | 来源立场 | 多源交叉+对立源 |
| 推理错误 | 逻辑漏洞 | 第三方审计 |
| 黑天鹅事件 | 极端情况 | 风险声明 |

### 7.3 替代方案

对于每个INFERRED/KNOWN结论，列出：
1. 替代解释
2. 其他数据来源
3. 不同方法论
4. 相反观点及其依据

---

## 附录：命令参考

| 命令 | 功能 | 示例 |
|------|------|------|
| `tag [content]` | 标注内容 | `tag "市场规模1000亿"` |
| `validate [file]` | 验证标注 | `validate report.md` |
| `score` | 查看信任分 | `score` |
| `audit` | 审计内容 | `audit` |
| `report [period]` | 生成报告 | `report daily` |

---

*版本: v2.0.0*  
*更新日期: 2026-03-21*  
*作者: 满意解研究所*
