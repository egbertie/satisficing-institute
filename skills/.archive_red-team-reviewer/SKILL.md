---
name: red-team-reviewer
version: 1.0.0
description: |
  蓝军审查机制 - 自动执行批判性审查，发现潜在问题
  核心价值：事实核查、逻辑漏洞、风险评估、改进建议
  适用：内容审查、方案评估、风险预警
author: OpenClaw
tags:
  - red-team
  - review
  - audit
  - critique
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3"]
  - cron: false
---

# 蓝军审查 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 4维度全覆盖（事实/逻辑/风险/改进）
2. **系统**: 审查 → 报告 → 跟踪闭环
3. **迭代**: PDCA优化审查质量
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 一键触发审查流程

## 审查维度

| 维度 | 检查内容 | 权重 |
|------|----------|------|
| 事实核查 | 数据准确性 | 30% |
| 逻辑漏洞 | 论证完整性 | 30% |
| 风险评估 | 潜在问题 | 25% |
| 改进建议 | 优化方向 | 15% |

---

*5标准全部满足*
