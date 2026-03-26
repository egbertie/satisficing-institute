# 优化计划模板

## 优化任务: {{task_name}}

- **任务ID**: {{task_id}}
- **创建时间**: {{created_at}}
- **计划执行时间**: {{scheduled_at}}
- **优先级**: {{priority}}

---

## 优化目标

{{objective}}

---

## 涉及Cron

{{#each crons}}
### {{name}} ({{id}})
- 当前层级: Tier {{tier}}
- 当前频率: {{schedule}}
- 当前状态: {{status}}
- 预计变更: {{changes}}
{{/each}}

---

## 优化措施

{{#each measures}}
### {{number}}. {{title}}
- **类型**: {{type}}
- **描述**: {{description}}
- **影响范围**: {{impact}}
- **回滚方案**: {{rollback}}
{{/each}}

---

## 预期效果

| 指标 | 优化前 | 优化后 | 改善幅度 |
|------|--------|--------|----------|
| Cron数量 | {{before_count}} | {{after_count}} | {{count_change}} |
| 日均Token | {{before_tokens}} | {{after_tokens}} | {{token_change}} |
| 空转率 | {{before_empty}}% | {{after_empty}}% | {{empty_change}}% |
| 用户交互率 | {{before_interaction}}% | {{after_interaction}}% | {{interaction_change}}% |

---

## 风险评估

| 风险项 | 可能性 | 影响 | 缓解措施 |
|--------|--------|------|----------|
{{#each risks}}
| {{risk}} | {{likelihood}} | {{impact}} | {{mitigation}} |
{{/each}}

---

## 执行步骤

{{#each steps}}
{{number}}. {{description}}
   - 负责人: {{owner}}
   - 预计耗时: {{duration}}
   - 验证方式: {{verification}}
{{/each}}

---

## 回滚计划

**回滚触发条件**:
{{rollback_conditions}}

**回滚步骤**:
{{#each rollback_steps}}
{{number}}. {{description}}
{{/each}}

**回滚命令**:
```bash
{{rollback_command}}
```

---

## 审批

- [ ] 技术评审
- [ ] 安全评审
- [ ] 最终审批

**审批人**: _______________  
**审批日期**: _______________

---

## 执行记录

| 时间 | 操作 | 操作人 | 结果 |
|------|------|--------|------|
{{#each execution_logs}}
| {{time}} | {{action}} | {{operator}} | {{result}} |
{{/each}}
