---
name: unified-notion-suite
description: Unified Notion workspace management suite. Replaces notion, notion-api, notion-api-skill with single integrated interface. Use for: page management, database operations, content sync, template creation, workspace automation.
triggers: ["notion", "workspace", "database", "page", "note", "知识库"]
---

# Unified Notion Suite

**统一Notion工作空间套件** - 整合所有Notion相关操作。

> 🎯 替代: notion + notion-api + notion-api-skill

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **页面管理** | 创建、编辑、归档、发布 |
| **数据库操作** | 查询、插入、更新、删除 |
| **内容同步** | 双向同步、批量导入导出 |
| **模板系统** | 快速创建标准化页面 |
| **自动化** | Webhook触发、定时任务 |

---

## 快速开始

```bash
# 创建页面
notion-suite page create --title "项目计划" --parent "Projects"

# 数据库查询
notion-suite db query --database "Tasks" --filter "Status=Done"

# 批量导入
notion-suite import --file data.csv --database "Inventory"

# 同步到本地
notion-suite sync --workspace "MyWorkspace" --local ./notion-backup/
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| notion | `notion-suite` |
| notion-api | `notion-suite api` |
| notion-api-skill | `notion-suite` |

---

**自建替代计数**: +3
