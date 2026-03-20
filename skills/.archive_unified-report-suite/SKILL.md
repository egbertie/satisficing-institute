---
name: unified-report-suite
description: Unified reporting and documentation suite. Replaces weekly-report-generator, email-daily-summary, weekly-meeting with single integrated interface. Use for: automated reports, daily summaries, meeting minutes, documentation generation.
triggers: ["report", "summary", "documentation", "weekly", "daily", "报告", "周报"]
---

# Unified Report Suite

**统一报告与文档套件** - 整合报告生成、日报摘要、会议记录。

> 🎯 替代: weekly-report-generator + email-daily-summary + weekly-meeting

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **周报生成** | 数据汇总、进度跟踪、自动生成 |
| **日报摘要** | 邮件聚合、要点提取、定时发送 |
| **会议记录** | 议程管理、纪要生成、行动项跟踪 |
| **文档模板** | 标准化模板、批量生成、版本管理 |
| **分发渠道** | 邮件、消息、云端同步 |

---

## 快速开始

```bash
# 周报生成
report-suite weekly --period last-week --data jira,git,calendar --output report.md

# 日报摘要
report-suite daily --sources email,calendar,tasks --delivery slack --time 18:00

# 会议记录
report-suite meeting --recording meeting.mp3 --participants "Alice,Bob" --output minutes.md
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| weekly-report-generator | `report-suite weekly` |
| email-daily-summary | `report-suite daily` |
| weekly-meeting | `report-suite meeting` |

---

**自建替代计数**: +3
