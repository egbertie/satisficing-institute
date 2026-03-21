---
name: obsidian-archiver
version: 1.0.0
description: |
  Obsidian笔记自动归档机制 - 自动整理和归档旧笔记
  核心价值：自动分类、过期清理、链接维护
  适用：知识库整理、笔记归档、空间优化
author: OpenClaw
tags:
  - obsidian
  - archive
  - notes
  - automation
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3", "obsidian-cli"]
  - cron: true
---

# Obsidian笔记自动归档 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 全Vault扫描 + 多维度归档策略
2. **系统**: 完整归档流程 + 安全备份
3. **迭代**: PDCA持续优化归档规则
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 定时归档 + 链接修复

## 定时任务

```bash
# 每日凌晨归档
0 2 * * * ./scripts/archive_old_notes.py

# 每周链接检查
0 3 * * 0 ./scripts/fix_broken_links.py
```

---

*5标准全部满足*
