# Cron Optimization Manager

基于第一性原理的Cron优化管理工具

## 功能

- `merge-daily`: Daily Cron合并优化
- `analyze`: Cron使用分析
- `optimize`: 智能优化建议

## 用法

```bash
claw cron merge-daily --analyze     # 分析当前Cron状态
claw cron merge-daily --execute     # 执行合并
claw cron merge-daily --rollback    # 回滚合并
claw cron merge-daily --status      # 查看状态
```

## 第一性原理

1. **执行开销第一性**: 减少调度次数，降低Token消耗
2. **任务亲和性第一性**: 同时间段、同性质任务合并
3. **时间体验第一性**: 保持关键任务的时间准确性

## 方案

采用**双Cron架构**:
- **晨间统一Cron** (09:00): 合并6个检查/采集任务
- **晚间统一Cron** (22:00): 合并4个报告/审计任务

预期节省: Token -28%, 调度次数 -67%

## 文档

详见: `docs/CRON_DAILY_MERGE_V1.2.md`
