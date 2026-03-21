# EEO Interview Runner Skill

## Purpose
管理EEO（Early Engagement Officer）首次访谈全流程

## 5-Standard Compliance

| Standard | Implementation |
|----------|----------------|
| 全局考虑 | 覆盖访谈前/中/后全流程 |
| 系统考虑 | 预约→准备→执行→复盘→跟进闭环 |
| 迭代机制 | 每次访谈后自动优化问卷 |
| Skill化 | 标准化接口：run/schedule/follow-up |
| 自动化 | Cron每日检查预约状态 |

## Commands
- `run` - 执行访谈
- `schedule` - 预约访谈
- `follow-up` - 访谈后跟进

## Cron
每日09:00检查是否有待执行访谈
