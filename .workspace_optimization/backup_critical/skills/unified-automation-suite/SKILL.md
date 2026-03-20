---
name: unified-automation-suite
description: Unified automation and workflow suite. Replaces n8n-workflow-automation, playwright-automation, agentic-workflow-automation, cron-scheduling with single integrated interface. Use for: web automation, scheduled tasks, workflow orchestration, E2E testing, data pipeline.
triggers: ["automation", "workflow", "schedule", "cron", "playwright", "n8n", "自动化", "定时任务"]
---

# Unified Automation Suite

**统一自动化工作流套件** - 整合各类自动化工具。

> 🎯 替代: n8n-workflow-automation + playwright-automation + agentic-workflow-automation + cron-scheduling

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **Web自动化** | 浏览器控制、表单填写、数据抓取 |
| **工作流编排** | 可视化流程、条件分支、错误处理 |
| **定时任务** | Cron表达式、调度管理、监控告警 |
| **E2E测试** | 测试用例、报告生成、回归测试 |
| **数据管道** | ETL流程、数据同步、批量处理 |

---

## 快速开始

```bash
# 创建自动化工作流
auto-suite workflow create --name "数据同步" --trigger schedule --cron "0 9 * * *"

# Web自动化脚本
auto-suite web --script login.js --url https://example.com

# 定时任务
auto-suite cron add --name "每日备份" --schedule "0 2 * * *" --command "backup.sh"

# E2E测试
auto-suite test run --suite regression --browser chrome --report html

# 数据管道
auto-suite pipeline create --name "ETL" --steps extract,transform,load
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| n8n-workflow-automation | `auto-suite workflow` |
| playwright-automation | `auto-suite web` |
| agentic-workflow-automation | `auto-suite agent` |
| cron-scheduling | `auto-suite cron` |

---

**自建替代计数**: +4
