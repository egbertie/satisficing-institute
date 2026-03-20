---
name: unified-collaboration-suite
description: Unified collaboration and task management suite. Replaces p0-collaboration-suite, p1-collaboration-suite, cross-skill-orchestrator, task-coordinator with single integrated interface. Use for: team collaboration, task coordination, cross-skill orchestration, project management.
triggers: ["collaboration", "task", "coordinate", "orchestrate", "project", "协作", "任务"]
---

# Unified Collaboration Suite

**统一协作与任务管理套件** - 整合团队协作、任务协调、Skill编排。

> 🎯 替代: p0-collaboration-suite + p1-collaboration-suite + cross-skill-orchestrator + task-coordinator

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **任务协调** | 任务分配、进度跟踪、依赖管理 |
| **跨Skill编排** | 工作流定义、数据流转、错误处理 |
| **团队协作** | 角色权限、沟通集成、文档共享 |
| **项目管理** | 里程碑、甘特图、资源分配 |
| **自动化协作** | 触发器、机器人、智能提醒 |

---

## 快速开始

```bash
# 任务协调
collab-suite task create --title "数据分析" --assignee team --deadline 2024-04-01

# 跨Skill编排
collab-suite orchestrate --workflow analysis_pipeline --skills search,extract,report

# 项目管理
collab-suite project create --name "Q2目标" --milestones planning,execution,review
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| p0-collaboration-suite | `collab-suite` |
| p1-collaboration-suite | `collab-suite` |
| cross-skill-orchestrator | `collab-suite orchestrate` |
| task-coordinator | `collab-suite task` |

---

**自建替代计数**: +4
