---
name: unified-assessment-suite
description: Unified assessment and evaluation suite. Replaces assessment-tool-v2, decision-quality-assessor, self-assessment-calibrator, satisficing-partner-decision with single integrated interface. Use for: performance assessment, decision evaluation, self-calibration, partner selection.
triggers: ["assessment", "evaluation", "calibration", "decision", "partner", "评估", "决策"]
---

# Unified Assessment Suite

**统一评估与决策套件** - 整合能力评估、决策质量、自我校准、伙伴选择。

> 🎯 替代: assessment-tool-v2 + decision-quality-assessor + self-assessment-calibrator + satisficing-partner-decision

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **能力评估** | 多维测评、能力模型、发展建议 |
| **决策评估** | 质量评分、偏见检测、结果预测 |
| **自我校准** | 置信度校准、反馈学习、偏差纠正 |
| **伙伴选择** | 匹配算法、满意度决策、风险评估 |
| **综合报告** | 评估汇总、趋势分析、改进计划 |

---

## 快速开始

```bash
# 能力评估
assess-suite skill evaluate --domain "数据分析" --method scenario --report detailed

# 决策质量评估
assess-suite decision quality --criteria clarity,information,alternatives --score

# 自我校准
assess-suite calibrate --predictions predictions.json --outcomes outcomes.json

# 伙伴选择
assess-suite partner select --candidates candidates.json --constraints "预算,时间" --satisfice
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| assessment-tool-v2 | `assess-suite skill` |
| decision-quality-assessor | `assess-suite decision` |
| self-assessment-calibrator | `assess-suite calibrate` |
| satisficing-partner-decision | `assess-suite partner` |

---

**自建替代计数**: +4
