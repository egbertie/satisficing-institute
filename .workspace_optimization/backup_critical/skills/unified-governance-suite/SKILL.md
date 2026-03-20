---
name: unified-governance-suite
description: Unified governance and oversight suite. Replaces decision-governance, workspace-integrity-guardian, continuous-improvement-engine with single integrated interface. Use for: governance oversight, workspace integrity, continuous improvement, compliance monitoring.
triggers: ["governance", "oversight", "integrity", "improvement", "compliance", "治理", "合规"]
---

# Unified Governance Suite

**统一治理与监督套件** - 整合决策治理、工作空间完整性、持续改进。

> 🎯 替代: decision-governance + workspace-integrity-guardian + continuous-improvement-engine

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **决策治理** | 决策权限、审计追踪、责任归属 |
| **完整性保护** | 工作空间监控、异常检测、恢复机制 |
| **持续改进** | PDCA循环、Kaizen、反馈驱动优化 |
| **合规监控** | 政策执行、违规检测、整改跟踪 |
| **风险管控** | 风险识别、评估、 mitigation |

---

## 快速开始

```bash
# 决策治理
governance-suite decision audit --decisions decisions.json --policy policy.yaml

# 完整性检查
governance-suite integrity scan --workspace ./workspace --fix auto

# 持续改进
governance-suite improve --feedback feedback.json --metrics metrics.json --plan

# 合规监控
governance-suite compliance check --standards "ISO27001,SOC2" --report
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| decision-governance | `governance-suite decision` |
| workspace-integrity-guardian | `governance-suite integrity` |
| continuous-improvement-engine | `governance-suite improve` |

---

**自建替代计数**: +3
