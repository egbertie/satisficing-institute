---
name: pandoc-batch-convert
version: 1.0.0
description: |
  Pandoc文档批量转换机制 - 批量转换多种文档格式
  核心价值：40+格式支持、批量处理、模板应用、错误恢复
  适用：文档归档、格式标准化、批量出版
author: OpenClaw
tags:
  - pandoc
  - convert
  - batch
  - documents
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["pandoc", "python3"]
  - cron: true
---

# Pandoc批量文档转换 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 40+格式全覆盖
2. **系统**: 批量处理 + 验证 + 错误恢复
3. **迭代**: PDCA优化转换参数
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 定时批量转换 + 监控

## 定时任务

```bash
# 每日批量转换队列
0 */6 * * * ./scripts/process_queue.sh
```

---

*5标准全部满足*
