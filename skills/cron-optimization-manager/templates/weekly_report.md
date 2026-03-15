# Cron效率周报

**统计周期**: {{week_start}} 至 {{week_end}}  
**生成时间**: {{timestamp}}

---

## 执行概览

| 指标 | 本周数据 | 上周数据 | 变化 |
|------|----------|----------|------|
| 总执行次数 | {{total_executions}} | {{last_week_executions}} | {{execution_change}} |
| 总Token消耗 | {{total_tokens}} | {{last_week_tokens}} | {{token_change}} |
| 成功率 | {{success_rate}}% | {{last_week_success_rate}}% | {{success_change}} |
| 日均Token | {{daily_avg_tokens}} | {{last_week_daily_avg}} | {{daily_change}} |

---

## Cron效率排名

### Top 5 最高效

| 排名 | Cron名称 | 执行次数 | Token消耗 | 效率评分 |
|------|----------|----------|-----------|----------|
{{#each top_efficient}}
| {{rank}} | {{name}} | {{executions}} | {{tokens}} | {{score}} |
{{/each}}

### Top 5 需优化

| 排名 | Cron名称 | 问题 | 建议措施 |
|------|----------|------|----------|
{{#each need_optimize}}
| {{rank}} | {{name}} | {{issue}} | {{suggestion}} |
{{/each}}

---

## 层级分布

| 层级 | 数量 | 占比 | 本周执行 |
|------|------|------|----------|
| Tier 1 (自动) | {{tier1_count}} | {{tier1_pct}}% | {{tier1_executions}} |
| Tier 2 (确认) | {{tier2_count}} | {{tier2_pct}}% | {{tier2_executions}} |
| Tier 3 (阻断) | {{tier3_count}} | {{tier3_pct}}% | {{tier3_executions}} |

---

## 预警事件

{{#if alerts}}
{{#each alerts}}
### ⚠️ {{level}}: {{title}}
- **类型**: {{type}}
- **描述**: {{message}}
- **建议**: {{suggestion}}
{{/each}}
{{else}}
本周无预警事件 🎉
{{/if}}

---

## 优化建议

{{#each optimization_suggestions}}
### {{number}}. {{cron_name}}
- **问题**: {{issue}}
- **建议**: {{suggestion}}
- **预期效果**: {{expected_impact}}
- **优先级**: {{priority}}
{{/each}}

---

## 下周计划

- [ ] {{task_1}}
- [ ] {{task_2}}
- [ ] {{task_3}}
- [ ] {{task_4}}

---

## 附注

*本报告由Cron优化管理器自动生成*  
*如有问题，请联系系统管理员*
