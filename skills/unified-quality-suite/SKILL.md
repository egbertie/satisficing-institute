---
name: unified-quality-suite
description: Unified quality assessment and assurance suite. Replaces quality-assessment, quality-gate, assessment-tool-v2 with single integrated interface. Use for: quality evaluation, assessment automation, standards compliance, review workflows, performance scoring.
triggers: ["quality", "assessment", "evaluate", "review", "score", "质量", "评估"]
---

# Unified Quality Suite

**统一质量评估与保障套件** - 整合质量评估、审核、评分能力。

> 🎯 替代: quality-assessment + quality-gate + assessment-tool-v2

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **质量评估** | 多维度评分、权重配置、标准化 |
| **审核工作流** | 多级审核、意见汇总、决策支持 |
| **质量门禁** | 自动化检查、阻断策略、修复建议 |
| **标准合规** | 规范检查、最佳实践、合规报告 |
| **持续改进** | 趋势分析、根因分析、改进建议 |

---

## 快速开始

```bash
# 质量评估
quality-suite assess --target code/ --criteria readability,security,performance

# 设置质量门禁
quality-suite gate --config quality.yaml --block-on error

# 审核工作流
quality-suite review --item PR-123 --assignees "reviewer1,reviewer2"

# 生成报告
quality-suite report --period weekly --format html
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| quality-assessment | `quality-suite assess` |
| quality-gate | `quality-suite gate` |
| assessment-tool-v2 | `quality-suite` |

---

**自建替代计数**: +3
