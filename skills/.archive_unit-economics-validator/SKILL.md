---
name: unit-economics-validator
version: 1.0.0
description: |
  单位经济学验证器 - 计算并验证CAC、LTV、回本周期等关键指标：
  1. 全局考虑：覆盖CAC、LTV、Payback Period、LTV/CAC Ratio
  2. 系统考虑：数据输入→计算→验证→建议生成闭环
  3. 迭代机制：根据实际数据校准模型参数
  4. Skill化：标准接口，可嵌入任何商业分析流程
  5. 流程自动化：自动计算并验证单位经济学健康度
author: Satisficing Institute
tags:
  - unit-economics
  - cac
  - ltv
  - validation
requires:
  - model: "kimi-coding/k2p5"
---

# 单位经济学验证器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 核心指标

| 指标 | 公式 | 健康阈值 |
|------|------|----------|
| **CAC** | 营销销售费用/新客户数 | - |
| **LTV** | ARPU × 平均客户寿命 | - |
| **LTV/CAC** | LTV ÷ CAC | >3 |
| **Payback Period** | CAC ÷ 月ARPU | <12月 |

### 1.2 验证规则

| 规则 | 条件 | 建议 |
|------|------|------|
| LTV/CAC < 3 | 不健康 | 提高价格或降低CAC |
| Payback > 12月 | 不健康 | 优化转化或减少流失 |
| CAC > 3月ARPU | 不健康 | 优化营销渠道 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 验证流程

```
数据输入 → 指标计算 → 健康检查 → 问题识别 → 改进建议 → 报告生成
```

---

## 标准3: 迭代机制（Iterative）

根据实际运营数据校准模型参数。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
unit-economics-validator/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── calculate_metrics.py    # 指标计算
│   ├── validate_health.py      # 健康验证
│   └── generate_suggestions.py # 建议生成
└── rules/
    └── health_thresholds.yaml
```

### 4.2 调用接口

```python
from unit_economics_validator import UnitEconomicsValidator

validator = UnitEconomicsValidator()

# 验证单位经济学
result = validator.validate(
    cac=100,
    arpu=50,
    lifespan=24
)
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 验证单位经济学
openclaw skill run unit-economics-validator validate \
  --cac 100 \
  --arpu 50 \
  --lifespan 24
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 核心指标全覆盖 | ✅ |
| **2. 系统** | 计算→验证→建议闭环 | ✅ |
| **3. 迭代** | 参数校准机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动计算+验证 | ✅ |

---

*版本: v1.0.0*  
*来源: business-model-canvas散落机制提取*  
*创建: 2026-03-20*
