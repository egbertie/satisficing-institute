---
name: tdd-compliance-checker
version: 1.0.0
description: |
  TDD合规性检查机制 - 验证开发流程是否遵循测试驱动开发
  核心价值：自动检查TDD流程、生成合规报告、违规预警
  适用：代码审查、流程审计、质量保证
author: OpenClaw
tags:
  - tdd
  - compliance
  - checker
  - quality
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3", "git"]
  - cron: true
---

# TDD合规检查 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 全提交历史检查
2. **系统**: 检查 → 报告 → 改进闭环
3. **迭代**: PDCA优化检查规则
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 定时检查 + 提交前钩子

## 检查维度

| 检查项 | 说明 | 风险等级 |
|--------|------|----------|
| 先测后码 | 测试提交早于实现 | 高 |
| 测试覆盖 | 新功能必有测试 | 高 |
| 小步提交 | 每次绿测试后提交 | 中 |

## 定时任务

```bash
# 每日合规检查
0 18 * * * ./scripts/check_tdd.py
```

---

*5标准全部满足*
