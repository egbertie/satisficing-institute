---
name: quick-ref-lookup
version: 1.0.0
description: |
  快速参考查询机制 - 7维度评估体系速查工具
  核心价值：即时查询、标准化参考、风险预警
  适用：现场评估、快速决策、培训参考
author: OpenClaw
tags:
  - quick-reference
  - lookup
  - assessment
  - decision
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3"]
  - cron: false
---

# 快速参考查询 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 7维度全覆盖
2. **系统**: 查询 → 返回 → 建议闭环
3. **迭代**: PDCA持续更新参考数据
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 即时响应查询请求

## 查询类型

| 类型 | 内容 | 响应时间 |
|------|------|----------|
| 完整参考卡 | 全部维度 | <1s |
| 单维度查询 | 特定维度 | <500ms |
| 风险判定 | 分数→建议 | <500ms |

---

*5标准全部满足*
