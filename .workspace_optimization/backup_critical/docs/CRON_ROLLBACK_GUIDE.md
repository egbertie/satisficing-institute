# Daily Cron 合并 - 回滚方案

> 版本: 1.2  
> 创建: 2026-03-15  
> 关联文档: [CRON_DAILY_MERGE_V1.2.md](./CRON_DAILY_MERGE_V1.2.md)

---

## 🚨 何时需要回滚

### 必须回滚的情况

| 情况 | 判断标准 | 响应时间 |
|------|----------|----------|
| 关键任务失败 | 晨报/日报连续2天未生成 | 立即 |
| 执行失败率过高 | 任务失败率 > 20% | 24小时内 |
| 用户体验严重下降 | 用户明确要求恢复 | 立即 |
| 数据不一致 | 合并后报告数据错误 | 立即 |

### 建议回滚的情况

- Token节省效果未达预期（节省 < 15%）
- 新Cron执行时间超过预期50%
- 维护困难度显著增加

---

## 🔄 回滚方法

### 方法1：一键回滚（推荐）

```bash
# 使用shell脚本
./scripts/cron-daily-merge.sh --rollback

# 或使用Python工具
python skills/cron-optimization-manager/cron_optimizer.py merge-daily --rollback
```

### 方法2：手动回滚

```bash
# 步骤1: 禁用合并后的Cron
claw cron disable morning-batch-check
claw cron disable evening-batch-report

# 步骤2: 启用原独立Cron
claw cron enable security-daily-check
claw cron enable milestone-daily-check
claw cron enable kimi-search-daily
claw cron enable auto-maintenance
claw cron enable economic-daily
claw cron enable reminder-audit
claw cron enable daily-autonomous-summary
claw cron enable daily-report
```

### 方法3：从备份恢复

```bash
# 查找备份
ls -la backups/cron-pre-merge-*.json

# 查看最新备份内容
cat backups/cron-pre-merge-$(date +%Y%m%d)*.json

# 手动根据备份恢复（如需）
```

---

## 📋 回滚流程

```
┌─────────────────┐
│   发现问题      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     是    ┌─────────────────┐
│ 是否严重问题?   │──────────>│   立即回滚      │
└────────┬────────┘           └────────┬────────┘
         │ 否                         │
         ▼                            ▼
┌─────────────────┐           ┌─────────────────┐
│ 观察1-2天       │           │ 执行回滚脚本    │
└────────┬────────┘           └────────┬────────┘
         │                            │
         ▼                            ▼
┌─────────────────┐           ┌─────────────────┐
│ 问题持续?       │────是────>│  验证回滚结果   │
└────────┬────────┘           └────────┬────────┘
         │ 否                         │
         ▼                            ▼
┌─────────────────┐           ┌─────────────────┐
│  保持合并状态   │           │  通知用户       │
└─────────────────┘           └─────────────────┘
```

---

## ✅ 回滚后验证清单

### 功能验证

- [ ] 每日晨报正常生成（09:00）
- [ ] 每日安全检查正常执行（09:00）
- [ ] milestone检查正常（09:00）
- [ ] Kimi Search资讯采集正常（09:00）
- [ ] auto_maintenance正常执行（09:17）
- [ ] economic_daily正常执行（09:17）
- [ ] 每日站会提醒正常（09:30）
- [ ] 每日进度报告正常（22:00）
- [ ] 提醒审计检查正常（22:00）
- [ ] daily-autonomous-summary正常（22:00）
- [ ] daily_report正常（22:17）

### 性能验证

- [ ] 各Cron执行时间在预期范围内
- [ ] 无重复执行或遗漏执行
- [ ] Token消耗恢复正常水平

---

## 🗄️ 备份策略

### 自动备份

合并脚本会自动创建备份：
- 位置: `backups/cron-pre-merge-YYYYMMDD_HHMMSS.json`
- 保留期: 7天
- 自动清理: 过期备份自动删除

### 备份内容

```json
{
  "backup_time": "2026-03-15T22:49:00",
  "version": "1.2",
  "old_crons": [...],
  "keep_crons": [...],
  "new_crons": [...]
}
```

---

## 📞 联系与支持

如有问题，请参考：
- 主文档: `docs/CRON_DAILY_MERGE_V1.2.md`
- 实施脚本: `scripts/cron-daily-merge.sh`
- Skill工具: `skills/cron-optimization-manager/`

---

> ⚠️ **注意**: 回滚后如需再次合并，需重新执行合并流程。
