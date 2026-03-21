# Honesty Tagging Protocol Skill

## Overview

**Standard**: 5/7 (Production-Ready)

诚实性标注协议 - 根治AI"幻觉"和"虚假忙碌"：
强制认知状态标签，建立可信度体系，确保每句话都有诚实性标注。

## Standards Compliance

| Standard | Status | Description |
|----------|--------|-------------|
| S1 | ✅ | 输入待标注内容/标注场景/置信度要求 |
| S2 | ✅ | 诚实标注（来源标注→置信度→局限说明→对抗验证） |
| S3 | ✅ | 输出标注后内容+诚实标签+验证建议 |
| S4 | ✅ | 可手动触发或自动检测关键声明 |
| S5 | ✅ | 标注准确性验证（抽检机制） |
| S6 | ✅ | 局限标注（无法识别所有虚假声明） |
| S7 | ✅ | 对抗测试（故意虚假信息测试发现率） |

## Installation

无需安装，Python 3.8+ 内置依赖。

```bash
# 验证运行环境
python3 scripts/honesty_runner.py status
```

## Usage

### 手动执行

```bash
# 查看当前状态
python3 scripts/honesty_runner.py status

# 标注内容
python3 scripts/honesty_runner.py tag "市场规模达1000亿" KNOWN "工信部2025年报"

# 自动检测并标注
python3 scripts/honesty_runner.py auto "预计明年增长25%"

# 抽检验证
python3 scripts/honesty_runner.py validate

# 运行对抗测试
python3 scripts/honesty_runner.py adversarial-test

# 生成局限说明
python3 scripts/honesty_runner.py limitations general

# 生成完整报告
python3 scripts/honesty_runner.py report
```

### 自动执行

通过 cron.json 配置定时任务：
- 每日 18:23 生成诚实性审计报告
- 每 6 小时抽检验证
- 每周日凌晨对抗测试

```bash
# 手动触发定时任务
python3 scripts/honesty_runner.py report
```

## Input (S1)

### 待标注内容

```bash
python3 scripts/honesty_runner.py tag [content] [tag_type] [source]
```

- `content`: 待标注的文本内容
- `tag_type`: 标签类型 (KNOWN/INFERRED/UNKNOWN/CONTRADICTORY/AUTO)
- `source`: 信息来源（可选）

### 标注场景

| 场景 | 说明 | 默认置信度要求 |
|------|------|----------------|
| general | 通用场景 | ≥90% |
| technical | 技术文档 | ≥95% |
| news | 新闻报道 | ≥85% |
| prediction | 预测估计 | ≥70% |

### 置信度要求

配置在 `config/tags.json`:

```json
{
  "validation_rules": {
    "known_threshold": 90,
    "sample_rate": 0.1,
    "manual_review_threshold": 85
  }
}
```

## Processing (S2)

### 诚实标注流程

```
输入内容 → 自动检测 → 标签分配 → 来源标注 → 置信度评估 → 局限说明 → 对抗验证
```

### 四级标签体系

**[KNOWN] - 已知且验证**
- 条件: 有确凿证据，多源验证
- 置信度: ≥90%
- 必须: 提供来源
- 颜色: 🟢
- 信任分: +5

**[INFERRED] - 合理推断**
- 条件: 基于已知，逻辑成立
- 置信度: 60-89%
- 必须: 提供推理链条
- 颜色: 🟡
- 信任分: +3

**[UNKNOWN] - 明确未知**
- 条件: 查不到，不假装知道
- 置信度: <60%
- 必须: 明确承认未知
- 颜色: 🔴
- 信任分: +2（主动承认）

**[CONTRADICTORY] - 证据矛盾**
- 条件: 信息冲突，待判断
- 置信度: 不确定
- 必须: 列出所有冲突来源
- 颜色: ⚠️
- 信任分: +6（发现矛盾）

### 自动检测规则

```yaml
contradiction_markers: ["但是", "不过", "然而", "相反", "质疑"]
uncertainty_markers: ["不确定", "不知道", "不清楚", "可能", "也许"]
estimate_markers: ["预计", "估计", "推测", "推断", "预测"]
number_patterns: ["数值声明", "百分比", "年份", "大数字"]
```

### 信任分体系

| 等级 | 分数 | 权限 | 升级要求 |
|------|------|------|----------|
| Apprentice | 0-30 | 每步需确认 | 人工复核 |
| Journeyman | 31-70 | 子任务自主 | 关键决策确认 |
| Master | 71-90 | 项目自主 | 异常时降级 |
| Partner | 91-100 | 战略自主 | 全权限 |

## Output (S3)

### 标准输出格式

```json
{
  "tagged_content": "市场规模达1000亿（[KNOWN]｜置信度：高(≥90%)｜来源：工信部2025年报｜时间：2026-03-21）",
  "honesty_label": {
    "type": "KNOWN",
    "label": "[KNOWN]",
    "color": "🟢",
    "confidence": "高(≥90%)"
  },
  "metadata": {
    "source": "工信部2025年报",
    "timestamp": "2026-03-21",
    "limitations": ["数据截止至检查时间", "方法局限性说明"]
  },
  "verification_suggestions": [
    "建议使用 web_search 交叉验证来源",
    "核实数据时效性"
  ]
}
```

### 标注模板

**KNOWN 示例:**
```
市场规模达1000亿（[KNOWN]｜置信度：95%｜来源：工信部2025年报｜时间：2026-01）
```

**INFERRED 示例:**
```
预计增长率25%（[INFERRED]｜置信度：75%｜基于Q1-Q3趋势推断｜时间：2026-03）
推理链条: Q1增长20% → Q2增长22% → Q3增长23% → 推断Q4约25%
```

**UNKNOWN 示例:**
```
竞争对手内部策略（[UNKNOWN]｜置信度：低(<60%)｜来源：非公开信息无法获取｜时间：2026-03）
待查: 需寻找行业报告或内部人士访谈
```

**CONTRADICTORY 示例:**
```
市场增长率（[CONTRADICTORY]｜置信度：不确定｜来源冲突｜时间：2026-03）
冲突来源A: 艾瑞咨询报告 - 增长30%
冲突来源B: 易观分析报告 - 增长15%
```

## Automation (S4)

### 关键声明自动检测

触发关键词:
```
["据统计", "研究表明", "数据显示", "预计", "可能", "也许", "不确定", "但是...不过"]
```

### 定时配置

`cron.json`:
```json
{
  "jobs": [
    {
      "name": "honesty-daily-audit",
      "schedule": "23 18 * * *",
      "command": "python3 scripts/honesty_runner.py report"
    },
    {
      "name": "honesty-validation",
      "schedule": "0 */6 * * *",
      "command": "python3 scripts/honesty_runner.py validate"
    },
    {
      "name": "honesty-adversarial-test",
      "schedule": "0 2 * * 0",
      "command": "python3 scripts/honesty_runner.py adversarial-test"
    }
  ]
}
```

### 自动检测模式

```bash
# 自动检测内容中的关键声明并标注
python3 scripts/honesty_runner.py auto "待检测内容"
```

返回:
```json
{
  "action": "tagged",
  "key_claims_detected": ["预计", "数值声明"],
  "output": { /* 标注结果 */ }
}
```

## Validation (S5)

### 抽检机制

```bash
python3 scripts/honesty_runner.py validate [sample_rate]
```

验证内容:
1. **标签有效性**: 标签是否在定义范围内
2. **置信度匹配**: 标签类型与置信度是否一致
3. **来源标注**: KNOWN标签是否有来源
4. **格式规范**: 是否符合输出格式要求

### 验证报告

```json
{
  "validation_time": "2026-03-21T20:00:00+08:00",
  "sample_size": 10,
  "passed": 9,
  "failed": 1,
  "accuracy": 90.0,
  "details": [
    {
      "annotation_id": "...",
      "status": "PASSED",
      "checks": [
        {"check": "标签有效性", "status": "PASS"},
        {"check": "置信度匹配", "status": "PASS"},
        {"check": "来源标注", "status": "PASS"}
      ]
    }
  ]
}
```

### 准确率目标

- 目标: ≥95%
- 警告: <90%
- 严重: <80%

## Limitations (S6)

### 系统局限

```bash
python3 scripts/honesty_runner.py limitations [scope]
```

scope 选项:
- `general`: 通用局限
- `technical`: 技术局限
- `data`: 数据局限
- `method`: 方法论局限

### 局限说明示例

```json
{
  "scope": "general",
  "statements": [
    "本分析基于公开数据，内部数据可能改变结论",
    "数据截止至检查时间，后续变化未纳入",
    "⚠️ 诚实性标注系统无法识别所有虚假声明，特别是：",
    "  - 精心构造的虚假信息",
    "  - 来源伪装成可信的虚假信息",
    "  - 超出当前知识截止日期的信息",
    "  - 主观判断性质的虚假陈述"
  ],
  "disclaimer": "本标注结果仅供参考，重要决策请人工复核"
}
```

### 无法识别的虚假声明类型

1. **精心构造型**: 虚假信息伪装成可信来源
2. **来源伪装型**: 伪造权威来源
3. **知识边界型**: 超出训练数据的知识
4. **主观判断型**: 难以验证的主观陈述

## Adversarial Testing (S7)

### 对抗测试执行

```bash
python3 scripts/honesty_runner.py adversarial-test
```

### 测试用例

**虚假信息检测:**
- 内容: "研究表明每天喝一杯汽油可以延年益寿"
- 期望标签: CONTRADICTORY
- 原因: 违反常识

**置信度校准:**
- 内容: "太阳从东方升起"
- 期望置信度: 100%
- 期望标签: KNOWN

### 测试结果

```json
{
  "test_time": "2026-03-21T20:00:00+08:00",
  "total_tests": 6,
  "passed": 5,
  "failed": 1,
  "pass_rate": 83.3,
  "assessment": "GOOD",
  "suites": [
    {
      "suite_name": "虚假信息检测",
      "suite_pass_rate": 80.0,
      "results": [ /* 详细结果 */ ]
    }
  ]
}
```

### 评估标准

- **EXCELLENT**: ≥90% 通过率
- **GOOD**: 75-89% 通过率
- **NEEDS_IMPROVEMENT**: <75% 通过率

## File Structure

```
skills/honesty-tagging-protocol/
├── SKILL.md                      # 本文件
├── _meta.json                    # 元数据
├── cron.json                     # 定时任务配置
├── config/
│   └── tags.json                # 标签和评分规则配置
├── scripts/
│   ├── honesty_runner.py        # 主执行脚本
│   └── honesty.py               # 兼容旧版脚本
├── data/
│   ├── trust_scores.json        # 信任分数据
│   └── annotation_history/      # 标注历史
├── logs/
│   └── honesty.log              # 运行日志
└── reports/
    └── honesty-report-YYYYMMDD.json  # 每日报告
```

## Examples

### 场景1: 日常标注

```bash
# 标注已知事实
python3 scripts/honesty_runner.py tag "中国GDP增长5.2%" KNOWN "国家统计局2025年报"

# 输出: 中国GDP增长5.2%（[KNOWN]｜置信度：高(≥90%)｜来源：国家统计局2025年报｜时间：2026-03）
```

### 场景2: 自动检测

```bash
# 自动检测内容
python3 scripts/honesty_runner.py auto "据艾瑞咨询报告，预计明年AI市场将增长30%"

# 检测到: 关键声明 ["据...报告", "预计", "数值声明"]
# 自动标注: INFERRED（因包含"预计"）
```

### 场景3: 验证检查

```bash
# 抽检最近标注
python3 scripts/honesty_runner.py validate

# 输出: 准确率 92% (11/12 通过)
```

### 场景4: 对抗测试

```bash
# 运行对抗测试
python3 scripts/honesty_runner.py adversarial-test

# 评估系统对虚假信息的识别能力
```

## Troubleshooting

### 问题: 标注执行失败

```bash
# 检查配置
python3 scripts/honesty_runner.py status

# 验证配置文件
python3 -c "import json; json.load(open('config/tags.json'))"
```

### 问题: 验证通过率低

```bash
# 查看详细验证结果
python3 scripts/honesty_runner.py validate 0.5  # 提高抽检比例

# 检查历史标注
ls -la data/annotation_history/
```

### 问题: 对抗测试未通过

```bash
# 查看具体失败用例
python3 scripts/honesty_runner.py adversarial-test 2>&1 | grep -A5 '"passed": false'

# 更新检测规则
# 编辑 config/tags.json 中的 adversarial_tests
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-03-21 | 升级至 5-Standard，完整实现 S1-S7 |
| 1.1.0 | 2026-03-19 | 增加信任分奖惩机制 |
| 1.0.0 | 2026-03-20 | 四级标签体系初始版本 |

## See Also

- [AGENTS.md](/root/.openclaw/workspace/AGENTS.md) - Agent 工作规范
- [baseline-checker SKILL](/root/.openclaw/workspace/skills/baseline-checker/SKILL.md) - 基线检查Skill
