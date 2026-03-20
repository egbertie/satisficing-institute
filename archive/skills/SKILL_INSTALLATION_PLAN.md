# Skill 批量安装计划 V1.0

> **策略**: 系统化安装，集中处理，成本优先  
> **原则**: Kimi包月优先，其他模型按需调用  
> **创建时间**: 2026-03-14

---

## 📊 当前状态

| 类别 | 数量 |
|------|------|
| 已安装 | 4个 (adwords, github, zipcracker, archive-handler) |
| 待安装 | 21个 |
| **总计** | **25个** |

---

## 🎯 安装优先级（成本敏感版）

### P0 - 立即安装（高价值 + 零成本）

| Skill | 用途 | 成本 | 决策 |
|-------|------|------|------|
| **automate-excel** | Excel自动化处理 | 本地Python，零API成本 | ✅ 安装 |
| **csvtoexcel** | CSV/Excel转换 | 本地处理，零成本 | ✅ 安装 |
| **copywriting** | 文案写作（与adwords互补）| 纯提示词，零成本 | ✅ 安装 |
| **audio-handler** | 音频处理（剪辑/转换）| 本地工具，零成本 | ✅ 安装 |
| **cron-scheduling** | 定时任务增强 | 系统已有，零成本 | ✅ 安装 |
| **duckdb-cli-ai-skills** | 数据分析（DuckDB）| 本地数据库，零成本 | ✅ 安装 |

**P0 安装批次**: 6个skill，预计今晚 23:00 开始批量安装

---

### P1 - 评估后安装（需权衡价值/成本）

| Skill | 用途 | 成本/风险 | 决策 |
|-------|------|----------|------|
| **notion** | Notion文档操作 | 需Notion API（免费额度）| ⏳ 待评估 |
| **brave-search** | 网页搜索 | 需Brave API key（免费）| ⏳ 待评估 |
| **canva-connect** | Canva设计 | 需Canva API + OAuth | ⏳ 待评估 |
| **auto-redbook-skills** | 小红书自动化 | 需平台API，可能违规 | ⏳ 暂缓 |
| **bilibili-subtitle-download** | B站字幕下载 | 场景有限 | ⏳ 暂缓 |
| **dingtalk-feishu-cn** | 钉钉/飞书集成 | 需企业认证 | ⏳ 暂缓 |

**P1 评估标准**:
- 是否刚需？
- API成本是否可接受？
- 与现有体系是否冲突？

---

### P2 - 暂缓/不安装（高成本/低价值/复杂）

| Skill | 原因 | 决策 |
|-------|------|------|
| **agent-orchestrator** | 复杂度高，与现有cron体系冲突 | ⏳ 暂缓，自建替代 |
| **agents-manager** | 过于复杂，Node.js依赖 | ⏳ 暂缓 |
| **agent-task-tracker** | 与TASK_MASTER重复 | ❌ 不安装 |
| **ai-image-generation** | 需外部API（FLUX等），成本高 | ⏳ 暂缓 |
| **ai-lmage-for-file-repair** | 场景小众，需AI API | ⏳ 暂缓 |
| **antigravity-image-gen** | 需外部API，成本高 | ⏳ 暂缓 |
| **attribution-engine** | 用途不明 | ❌ 不安装 |
| **audio-cog** | 与audio-handler重复 | ❌ 不安装 |
| **design-assets** | 用途不明 | ⏳ 暂缓 |
| **elite-longterm-memory** | 与现有memory体系冲突 | ⏳ 暂缓 |

---

## 💰 成本控制策略

### 模型使用优先级

```
决策流程:
任务产生
    ↓
能否用Kimi完成？ ──是──→ 使用Kimi（包月，零边际成本）
    ↓ 否
是否需要高精尖？ ──否──→ 使用国产模型（MiniMax/Moonshot，便宜）
    ↓ 是
是否涉及客户最终决策？ ──是──→ 必须人工复核，AI仅辅助
    ↓ 否
使用Claude/GPT-4（按需付费，贵但精准）
```

### 成本分级

| 优先级 | 模型 | 成本 | 使用场景 |
|:---:|:---|:---|:---|
| 1 | **Kimi** | ¥0（包月）| 日常对话、中文处理、代码生成 |
| 2 | **MiniMax/Moonshot** | ¥极低 | 标准分析、数据处理 |
| 3 | **GPT-4** | $中等 | 复杂推理、英文内容 |
| 4 | **Claude Opus** | $高 | 高精尖代码、深度分析 |

### 每日预算控制

- **Kimi**: 无限制（已包月）
- **其他模型合计**: 控制在 ¥50/天 以内
- **紧急情况下**: 可临时突破，需记录原因

---

## 📅 安装时间表

### 第一阶段（今晚 23:00 - 明早 06:00）| P0批次
- [ ] automate-excel
- [ ] csvtoexcel
- [ ] copywriting
- [ ] audio-handler
- [ ] cron-scheduling
- [ ] duckdb-cli-ai-skills

### 第二阶段（本周内）| P1评估
- [ ] notion（评估API成本）
- [ ] brave-search（申请免费API key）
- [ ] canva-connect（评估OAuth复杂度）

### 第三阶段（选择性）| P2决策
- 根据实际需要，决定是否安装P2技能
- 优先自建替代方案

---

## 🔄 安装流程（每个skill）

1. **安全审计**（5分钟）
   - 读取SKILL.md
   - 检查网络依赖
   - 检查权限范围

2. **成本评估**（2分钟）
   - 是否需要外部API？
   - 是否有免费额度？
   - 是否可用本地替代？

3. **功能测试**（10分钟）
   - 安装到skills/目录
   - 执行基本功能测试
   - 验证无错误

4. **文档记录**（3分钟）
   - 更新MEMORY.md
   - 记录到信赖清单

**单skill平均耗时**: 20分钟

---

## 📈 预期成果

- **今晚完成**: 6个P0 skill安装
- **本周完成**: 3-5个P1 skill评估+安装
- **累计**: 13-15个可用skill（超过一半）

---

*计划制定: 2026-03-14 11:30*  
*下次更新: P0批次安装完成后*
