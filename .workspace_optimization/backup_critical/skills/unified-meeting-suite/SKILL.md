---
name: unified-meeting-suite
description: Unified meeting management and productivity suite. Replaces effective-meeting, weekly-meeting, meeting-to-action, ai-meeting-notes with single integrated interface. Use for: meeting scheduling, agenda management, note-taking, action items tracking, meeting analytics.
triggers: ["meeting", "会议", "schedule", "agenda", "notes", "action items", "例会"]
---

# Unified Meeting Suite

**统一会议管理套件** - 整合会议全流程管理。

> 🎯 替代: effective-meeting + weekly-meeting + meeting-to-action + ai-meeting-notes

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **会议安排** | 日程冲突检测、会议室预订 |
| **议程管理** | 模板库、时间分配、议题跟踪 |
| **智能记录** | 语音转文字、AI摘要、关键点提取 |
| **行动项** | 自动提取、责任人分配、进度跟踪 |
| **数据分析** | 会议效率、时间分布、决策统计 |

---

## 快速开始

```bash
# 安排会议
meeting-suite schedule --title "周会" --participants "team@company.com" --duration 60

# 生成议程
meeting-suite agenda --template weekly --topics "进度,问题,计划"

# 会议记录
meeting-suite notes --record --ai-summary --extract-actions

# 行动项跟踪
meeting-suite actions --list --owner "me" --status pending

# 会议分析
meeting-suite analytics --period last-month
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| effective-meeting | `meeting-suite` |
| weekly-meeting | `meeting-suite schedule --recurring weekly` |
| meeting-to-action | `meeting-suite notes --extract-actions` |
| ai-meeting-notes | `meeting-suite notes --ai-summary` |

---

**自建替代计数**: +4
