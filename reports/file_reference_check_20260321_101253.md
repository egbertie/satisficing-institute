# 全局文件引用一致性检查报告
**检查时间**: 2026-03-21 10:12:53
**检查维度**: 4维检查法 - 维度3（文件引用一致性）

## 📊 总体统计

| 指标 | 数值 |
|------|------|
| 扫描文件数 | 1935 |
| 发现引用数 | 3650 |
| 失效引用 | 2751 |
| 版本问题 | 0 |
| 循环引用 | 0 |
| **健康度评分** | **62.3/100** |

## 🔴 失效引用清单（P0严重/P1一般）

| 源文件 | 引用路径 | 类型 | 严重级别 |
|--------|----------|------|----------|
| ./TASK_MASTER.md | docs/MEETING_PROTOCOL_V1.md | doc_ref | P0 |
| ./TASK_MASTER.md | docs/MEETING_PROTOCOL_V1.md | doc_ref | P0 |
| ./TASK_MASTER.md | docs/DISASTER_RECOVERY_V1.md | doc_ref | P0 |
| ./TASK_MASTER.md | docs/DISASTER_RECOVERY_V1.md | doc_ref | P0 |
| ./TASK_MASTER.md | docs/DISASTER_RECOVERY_V1.md | doc_ref | P0 |
| ./memory/2026-03-13.md | docs/DISASTER_RECOVERY_V1.md | doc_ref | P0 |
| ./memory/2026-03-13.md | docs/DISASTER_RECOVERY_V1.md | doc_ref | P0 |
| ./memory/2026-03-13.md | docs/DISASTER_RECOVERY_V1.md | doc_ref | P0 |
| ./memory/2026-03-16.md | docs/GITHUB_MODELS_SETUP.md | doc_ref | P0 |
| ./memory/2026-03-13-过期任务补救报告.md | docs/DISASTER_RECOVERY_V1.md | doc_ref | P0 |
| ./memory/2026-03-13-过期任务补救报告.md | docs/DISASTER_RECOVERY_V1.md | doc_ref | P0 |
| ./memory/2026-03-13_小时协调检查报告_1724.md | docs/DISASTER_RECOVERY_V1.md | doc_ref | P0 |
| ./memory/2026-03-13_小时协调检查报告_1724.md | docs/INTERNAL_MEETING_PROTOCOL_V1.md | doc_ref | P0 |
| ./memory/conversation-summary-2026-03-15.md | docs/SKILL_MANAGEMENT_RULES.md | doc_ref | P0 |
| ./.workspace_optimization/phase4_after_report.md | docs/WORKSPACE_ORGANIZATION_RULES.md | doc_ref | P0 |
| ./.workspace_optimization/phase4_after_report.md | docs/WORKSPACE_ORGANIZATION_RULES.md | doc_ref | P0 |
| ./.workspace_optimization/operation_log.md | docs/WORKSPACE_ORGANIZATION_RULES.md | doc_ref | P0 |
| ./.workspace_optimization/operation_log.md | docs/WORKSPACE_ORGANIZATION_RULES.md | doc_ref | P0 |
| ./docs/FINAL_CLEANUP_REPORT.md | docs/*.md | doc_ref | P0 |
| ./docs/PROMISE_STANDARDIZATION_REPORT.md | skills/global-file-governance/SKILL.md | skill_ref | P0 |
| ./docs/PROMISE_STANDARDIZATION_REPORT.md | skills/promise-management-system/SKILL.md | skill_ref | P0 |
| ./docs/PROMISE_STANDARDIZATION_REPORT.md | skills/backup-disaster-recovery/SKILL.md | skill_ref | P0 |
| ./docs/PROMISE_STANDARDIZATION_REPORT.md | skills/team-execution-culture/SKILL.md | skill_ref | P0 |
| ./docs/PROMISE_STANDARDIZATION_REPORT.md | skills/security-continuous-improvement/SKILL.md | skill_ref | P0 |
| ./docs/PROMISE_STANDARDIZATION_REPORT.md | skills/heartbeat-protocol/SKILL.md | skill_ref | P0 |
| ./docs/PROMISE_STANDARDIZATION_REPORT.md | skills/knowledge-extraction/SKILL.md | skill_ref | P0 |
| ./docs/5STANDARD_AUDIT_REPORT.md | skills/7x24-autonomous-system/SKILL.md | skill_ref | P0 |
| ./docs/5STANDARD_AUDIT_REPORT.md | skills/decision-safety-redlines/SKILL.md | skill_ref | P0 |
| ./docs/5STANDARD_AUDIT_REPORT.md | skills/team-execution-culture/SKILL.md | skill_ref | P0 |
| ./docs/5STANDARD_AUDIT_REPORT.md | skills/first-principle-enforcer/SKILL.md | skill_ref | P0 |
| ./docs/5STANDARD_AUDIT_REPORT.md | skills/continuous-improvement/SKILL.md | skill_ref | P0 |
| ./docs/5STANDARD_AUDIT_REPORT.md | skills/content-consistency-governance/SKILL.md | skill_ref | P0 |
| ./docs/5STANDARD_AUDIT_REPORT.md | skills/knowledge-extraction/SKILL.md | skill_ref | P0 |
| ./docs/5STANDARD_AUDIT_REPORT.md | skills/file-integrity-checker/SKILL.md | skill_ref | P0 |
| ./docs/5STANDARD_AUDIT_REPORT.md | skills/closed-loop-enforcer/SKILL.md | skill_ref | P0 |
| ./docs/5STANDARD_AUDIT_REPORT.md | skills/expert-profile-manager/SKILL.md | skill_ref | P0 |
| ./docs/PHASE3_EXECUTION_MASTER.md | docs/STRATEGY_SINGLE_SOURCE.md | doc_ref | P0 |
| ./docs/PHASE3_EXECUTION_MASTER.md | docs/EXPERT_SINGLE_SOURCE.md | doc_ref | P0 |
| ./docs/PROMISE_CATCHUP_REPORT.md | docs/WECOM_BACKUP_V2_2026-03-20.md | doc_ref | P0 |
| ./docs/SCATTERED_MECHANISMS_BATCH3.md | skills/pdf-document-parser/SKILL.md | skill_ref | P0 |
| ./docs/SCATTERED_MECHANISMS_BATCH3.md | skills/mermaid-chart-generator/SKILL.md | skill_ref | P0 |
| ./docs/SCATTERED_MECHANISMS_BATCH3.md | skills/multi-search-rotator/SKILL.md | skill_ref | P0 |
| ./docs/SCATTERED_MECHANISMS_BATCH3.md | skills/rss-news-fetcher/SKILL.md | skill_ref | P0 |
| ./docs/SCATTERED_MECHANISMS_BATCH3.md | skills/notion-db-sync/SKILL.md | skill_ref | P0 |
| ./docs/SCATTERED_MECHANISMS_BATCH3.md | skills/obsidian-archiver/SKILL.md | skill_ref | P0 |
| ./docs/SCATTERED_MECHANISMS_BATCH3.md | skills/pandoc-batch-convert/SKILL.md | skill_ref | P0 |
| ./docs/SCATTERED_MECHANISMS_BATCH3.md | skills/patent-filing-generator/SKILL.md | skill_ref | P0 |
| ./docs/SCATTERED_MECHANISMS_BATCH3.md | skills/partner-assessment/SKILL.md | skill_ref | P0 |
| ./docs/SCATTERED_MECHANISMS_BATCH3.md | skills/n8n-idempotency-checker/SKILL.md | skill_ref | P0 |
| ./docs/SCATTERED_MECHANISMS_BATCH3.md | skills/n8n-hitl-queue/SKILL.md | skill_ref | P0 |
| ... | ... | ... | 还有 2701 项 |

## 🔧 修复建议

### 高优先级（P0）
- 修复核心引用路径（skills/、docs/等关键目录）
- 检查文件移动或重命名导致的链接断裂

### 中优先级（P1）
- 修复内部文档引用
- 更新相对路径引用

### 修复命令示例
```bash
# 查找所有失效引用
grep -r "](skills/" /root/.openclaw/workspace --include="*.md" | grep -v ".archive_"

# 批量替换（谨慎使用）
# sed -i 's/旧路径/新路径/g' 文件.md
```

## 📈 健康度评估

**62.3分** - 🟠 一般：需要关注和修复
