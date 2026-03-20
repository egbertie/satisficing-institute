# 满意解研究所灾备重建复刻实施方案 V1.0

> **文档版本**: V1.0  
> **创建日期**: 2026-03-10  
> **最后更新**: 2026-03-10  
> **文档状态**: ✅ 正式发布并生效  
> **RTO目标**: ≤ 2小时  
> **RPO目标**: ≤ 24小时（数据丢失不超过1天）

---

## 目录

1. [概述](#概述)
2. [灾备策略](#灾备策略)
3. [备份清单](#备份清单)
4. [恢复流程](#恢复流程)
5. [版本管理机制](#版本管理机制)
6. [每日更新检查清单](#每日更新检查清单)
7. [紧急联系](#紧急联系)
8. [附录](#附录)

---

## 概述

### 1.1 目的

本文档定义了满意解研究所的灾备重建复刻方案，确保在发生系统故障、数据丢失或其他灾难性事件时，能够快速恢复业务运营，最大限度地减少数据丢失和业务中断。

### 1.2 适用范围

本方案涵盖满意解研究所的所有核心数字资产，包括：
- AI组织运作所需的全部配置文件
- 组织架构与角色定义
- 知识库与研究成果
- 自动化脚本与定时任务
- API密钥与访问凭证

### 1.3 关键指标（SLA）

| 指标 | 目标值 | 实际值 | 说明 |
|------|--------|--------|------|
| **RTO** (恢复时间目标) | ≤ 2小时 | - | 从灾难发生到系统完全恢复的时间 |
| **RPO** (恢复点目标) | ≤ 24小时 | - | 允许的最大数据丢失时间窗口 |
| **备份成功率** | ≥ 99% | 100% | 每月备份任务成功执行的比例 |
| **恢复测试频率** | 每月1次 | - | 定期进行恢复演练的频率 |

---

## 灾备策略

### 2.1 备份架构

```
┌─────────────────────────────────────────────────────────┐
│                    满意解研究所                          │
│              (满意解研究所工作区)                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │  Config │ │  Docs   │ │ Memory  │ │ Skills  │       │
│  │ 配置    │ │ 文档    │ │ 记忆    │ │ 技能    │       │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │
│       └─────────────┴─────────┴─────────────┘            │
│                         │                               │
│              ┌──────────▼──────────┐                    │
│              │   backup-manager    │                    │
│              │    (备份管理器)      │                    │
│              └──────────┬──────────┘                    │
└─────────────────────────┼───────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │  /backups │   │  GitHub  │   │  Notion  │
    │  本地备份 │   │  代码仓库 │   │  知识库  │
    └──────────┘   └──────────┘   └──────────┘
    │每日 02:00│   │手动推送  │   │手动同步  │
    │自动执行  │   │         │   │         │
    └──────────┘   └──────────┘   └──────────┘
```

### 2.2 备份频率与策略

| 数据类型 | 备份频率 | 保留策略 | 存储位置 | 状态 |
|----------|----------|----------|----------|------|
| **核心配置文件** (.env, openclaw.json) | 每日 02:00 自动 | 保留30天 | 本地 + 加密备份 | ✅ 已配置 |
| **Markdown文档** (*.md) | 每日 02:00 自动 | 保留90天 | 本地 + GitHub | ✅ 已配置 |
| **记忆文件** (memory/) | 每日 02:00 自动 | 保留180天 | 本地 | ✅ 已配置 |
| **Skill文件** (skills/) | 每周日 03:00 自动 | 保留60天 | 本地 | ✅ 已配置 |
| **定时任务配置** (cron/) | 每日 02:00 自动 | 保留90天 | 本地 | ✅ 已配置 |
| **脚本文件** (scripts/) | 每日 02:00 自动 | 保留90天 | 本地 + GitHub | ✅ 已配置 |
| **备份自动清理** | 每日 04:00 自动 | - | - | ✅ 已配置 |

### 2.3 定时备份任务配置

已配置的定时任务（已添加到 `cron/jobs.json`）：

| 任务ID | 任务名称 | 执行时间 | 类型 | 状态 |
|--------|----------|----------|------|------|
| `backup-daily-001` | 每日自动备份 | 每天 02:00 | isolated | ✅ 已启用 |
| `backup-weekly-001` | 每周全量备份 | 每周日 03:00 | isolated | ✅ 已启用 |
| `backup-cleanup-001` | 备份自动清理 | 每天 04:00 | isolated | ✅ 已启用 |

### 2.4 手动备份命令

```bash
# 查看备份管理器帮助
python3 /root/.openclaw/workspace/scripts/backup-manager.py --help

# 执行每日备份
python3 /root/.openclaw/workspace/scripts/backup-manager.py backup --type daily

# 执行全量备份（所有分类）
python3 /root/.openclaw/workspace/scripts/backup-manager.py backup --type full

# 查看备份列表
python3 /root/.openclaw/workspace/scripts/backup-manager.py list

# 验证最新备份
python3 /root/.openclaw/workspace/scripts/backup-manager.py verify

# 清理过期备份
python3 /root/.openclaw/workspace/scripts/backup-manager.py cleanup

# 查看备份状态
python3 /root/.openclaw/workspace/scripts/backup-manager.py status
```

---

## 备份清单

### 3.1 备份存储结构

```
/backups/
├── daily/                    # 每日备份
│   └── YYYY-MM-DD/
│       ├── config/           # 核心配置
│       │   ├── .env
│       │   ├── openclaw.json
│       │   └── cron_jobs.json
│       ├── workspace-md/     # Markdown文档
│       ├── memory/           # 记忆文件
│       ├── skills/           # Skill文件
│       ├── scripts/          # 脚本文件
│       └── backup_manifest.json  # 备份清单
├── weekly/                   # 每周备份
├── monthly/                  # 每月备份
├── logs/                     # 备份日志
│   └── backup_YYYYMMDD.log
├── status/
│   └── latest.json           # 最新备份状态
└── archive/                  # 归档备份
```

### 3.2 核心配置文件清单

| 文件路径 | 重要性 | 备份方式 | 大小 | 最后备份 |
|----------|--------|----------|------|----------|
| `/root/.openclaw/workspace/.env` | ⭐⭐⭐⭐⭐ | 每日自动 | ~1KB | 2026-03-10 |
| `/root/.openclaw/openclaw.json` | ⭐⭐⭐⭐⭐ | 每日自动 | ~3KB | 2026-03-10 |
| `/root/.openclaw/cron/jobs.json` | ⭐⭐⭐⭐⭐ | 每日自动 | ~15KB | 2026-03-10 |

### 3.3 关键文档清单

**核心文档** (P0级 - 最高优先级):

| 文档 | 路径 | 重要性 | 说明 |
|------|------|--------|------|
| `AGENTS.md` | workspace/ | ⭐⭐⭐⭐⭐ | AI代理工作指南 |
| `SOUL.md` | workspace/ | ⭐⭐⭐⭐⭐ | 组织精神核心 |
| `USER.md` | workspace/ | ⭐⭐⭐⭐⭐ | 用户信息 |
| `MEMORY.md` | workspace/ | ⭐⭐⭐⭐⭐ | 长期记忆 |
| `ORGANIZATION.md` | workspace/ | ⭐⭐⭐⭐⭐ | 组织架构 |
| `DISASTER_RECOVERY_PLAN_V1.0.md` | docs/ | ⭐⭐⭐⭐⭐ | 本灾备方案 |

**角色文档** (18个角色定义文件):

| 角色 | 文件 | 重要性 |
|------|------|--------|
| MAIN | ROLE-main.md | ⭐⭐⭐⭐⭐ |
| PMO | ROLE-pmo.md | ⭐⭐⭐⭐⭐ |
| PROD | ROLE-prod.md | ⭐⭐⭐⭐⭐ |
| GAME | ROLE-game.md | ⭐⭐⭐⭐⭐ |
| SOUL | ROLE-soul.md | ⭐⭐⭐⭐⭐ |
| ... | 其他13个角色 | ⭐⭐⭐⭐ |

### 3.4 当前备份状态

```
📊 最新备份状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
上次备份: 2026-03-10
备份类型: daily
备份状态: success
文件数量: 96
更新时间: 2026-03-10T20:49:59
备份路径: /backups/daily/2026-03-10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 恢复流程

### 4.1 灾难分级与响应

| 级别 | 定义 | 响应时间 | RTO | 恢复优先级 |
|------|------|----------|-----|------------|
| **P0-紧急** | 完全不可用，数据全部丢失 | 15分钟 | 1小时 | 核心配置 > 记忆 > 文档 |
| **P1-严重** | 核心功能受损，API失效 | 30分钟 | 2小时 | 配置 > 定时任务 |
| **P2-一般** | 非核心功能受损 | 2小时 | 4小时 | 文档 > Skill |
| **P3-轻微** | 单个文件丢失 | 24小时 | 48小时 | 按需恢复 |

### 4.2 P0级灾难恢复流程（完整重建）

#### 阶段1: 灾难确认 (0-15分钟)

1. **确认灾难范围**
   ```bash
   # 检查系统状态
   openclaw status
   df -h
   ls -la /root/.openclaw/
   ls -la /backups/
   ```

2. **启动应急响应**
   - 通知指挥官（Egbertie）
   - 创建灾难恢复工单
   - 冻结所有非紧急操作

#### 阶段2: 恢复准备 (15-30分钟)

1. **确定恢复点**
   ```bash
   # 查看可用备份
   python3 /root/.openclaw/workspace/scripts/backup-manager.py list
   
   # 验证备份完整性
   python3 /root/.openclaw/workspace/scripts/backup-manager.py verify --date 2026-03-10
   ```

2. **准备恢复环境**
   - 确保目标环境可用
   - 验证存储空间充足（至少2GB）
   - 准备恢复脚本

#### 阶段3: 数据恢复 (30-60分钟)

**一键恢复命令：**
```bash
# 恢复到最新备份
python3 /root/.openclaw/workspace/scripts/backup-manager.py restore --date $(date +%Y-%m-%d) --type daily

# 或恢复到指定日期
python3 /root/.openclaw/workspace/scripts/backup-manager.py restore --date 2026-03-10 --type daily
```

**手动分步恢复（如自动恢复失败）：**

```bash
# 1. 恢复核心配置
BACKUP_DATE="2026-03-10"
BACKUP_DIR="/backups/daily/$BACKUP_DATE"

# 2. 恢复.env
cp "$BACKUP_DIR/config/.env" /root/.openclaw/workspace/.env
chmod 600 /root/.openclaw/workspace/.env

# 3. 恢复openclaw.json
cp "$BACKUP_DIR/config/openclaw.json" /root/.openclaw/openclaw.json
chmod 600 /root/.openclaw/openclaw.json

# 4. 恢复定时任务
cp "$BACKUP_DIR/config/cron_jobs.json" /root/.openclaw/cron/jobs.json
chmod 600 /root/.openclaw/cron/jobs.json

# 5. 恢复Markdown文档
cp -r "$BACKUP_DIR/workspace-md/"* /root/.openclaw/workspace/

# 6. 恢复记忆文件
cp -r "$BACKUP_DIR/memory/"* /root/.openclaw/workspace/memory/

# 7. 恢复Skills
cp -r "$BACKUP_DIR/skills/"* /root/.openclaw/workspace/skills/

# 8. 恢复脚本
cp -r "$BACKUP_DIR/scripts/"* /root/.openclaw/workspace/scripts/
```

#### 阶段4: 服务恢复 (60-75分钟)

```bash
# 1. 重启Gateway服务
openclaw gateway restart

# 2. 验证Gateway状态
openclaw gateway status

# 3. 验证定时任务
openclaw cron list

# 4. 测试API连接
# - Kimi API
# - GitHub Models
# - Jina AI
# - Perplexity
```

#### 阶段5: 功能验证 (75-90分钟)

**验证清单：**
- [ ] Gateway服务运行正常
- [ ] API密钥有效（测试Kimi/GitHub/Jina）
- [ ] 定时任务列表完整
- [ ] 核心文档可访问
- [ ] 记忆文件完整
- [ ] Skill功能正常
- [ ] 备份系统可运行

```bash
# 执行完整验证
python3 /root/.openclaw/workspace/scripts/backup-manager.py verify --full
```

#### 阶段6: 恢复报告 (90-120分钟)

生成恢复报告：
```bash
# 生成验证报告
python3 /root/.openclaw/workspace/scripts/backup-manager.py verify --report
```

报告内容：
- 灾难发生时间
- 恢复开始/完成时间
- 使用的备份版本
- 恢复的数据清单
- 验证结果
- 存在的问题（如有）

### 4.3 P1级灾难恢复（配置丢失）

**场景：.env 或 openclaw.json 丢失**

```bash
# 1. 查看最新可用备份
BACKUP_DATE=$(python3 /root/.openclaw/workspace/scripts/backup-manager.py list | head -2 | tail -1 | awk '{print $1}')

# 2. 恢复配置文件
BACKUP_DIR="/backups/daily/$BACKUP_DATE"
cp "$BACKUP_DIR/config/.env" /root/.openclaw/workspace/.env
cp "$BACKUP_DIR/config/openclaw.json" /root/.openclaw/openclaw.json

# 3. 验证
openclaw gateway restart
openclaw status
```

### 4.4 单文件恢复

```bash
# 恢复特定文件
python3 /root/.openclaw/workspace/scripts/backup-manager.py restore-file \
  --backup-date 2026-03-10 \
  --source-path memory/2026-03-10.md \
  --target-path /root/.openclaw/workspace/memory/2026-03-10.md
```

---

## 版本管理机制

### 5.1 版本号规则

采用语义化版本控制：

```
主版本号.次版本号.补丁号
  X    .    Y    .    Z
```

| 版本类型 | 递增条件 | 示例 |
|----------|----------|------|
| **主版本号 (X)** | 重大架构变更 | 1.0.0 → 2.0.0 |
| **次版本号 (Y)** | 功能新增、重大优化 | 1.0.0 → 1.1.0 |
| **补丁号 (Z)** | Bug修复、小调整 | 1.0.0 → 1.0.1 |

### 5.2 备份版本历史

备份版本记录位置：`/backups/status/version-history.json`

每次备份自动生成版本记录：
```json
{
  "version": "1.0.0",
  "date": "2026-03-10",
  "backup_id": "daily-20260310_204959",
  "changes": {
    "added": [],
    "modified": ["DISASTER_RECOVERY_PLAN_V1.0.md"],
    "deleted": [],
    "size_delta": "+15KB"
  },
  "integrity": {
    "checksum": "a1b2c3d4...",
    "verified": true
  }
}
```

---

## 每日更新检查清单

### 6.1 自动检查（已配置定时任务）

| 时间 | 检查项 | 任务ID | 状态 |
|------|--------|--------|------|
| 02:00 | 自动备份执行 | backup-daily-001 | ✅ |
| 04:00 | 过期备份清理 | backup-cleanup-001 | ✅ |
| 09:00 | 安全检查 | bc640356-84e1-4e07-a2d5-cb93dab7e9ef | ✅ |

### 6.2 手动检查项（每日建议执行）

```bash
# 每日检查脚本（保存为 daily-check.sh）
#!/bin/bash
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 满意解研究所每日备份检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. 检查备份状态
echo "📦 备份状态:"
python3 /root/.openclaw/workspace/scripts/backup-manager.py status

# 2. 检查磁盘空间
echo ""
echo "💾 磁盘空间:"
df -h /backups | tail -1

# 3. 检查Git同步
echo ""
echo "🔄 Git状态:"
cd /root/.openclaw/workspace && git status --short | wc -l | xargs echo "未提交文件数:"

# 4. 检查关键文件
echo ""
echo "🔐 关键文件:"
ls -la /root/.openclaw/workspace/.env /root/.openclaw/openclaw.json 2>/dev/null | awk '{print $9, $5 "bytes"}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "检查完成时间: $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

### 6.3 每周检查项

- [ ] 验证上周所有每日备份完整性
- [ ] 执行恢复演练测试
- [ ] 检查备份存储容量趋势
- [ ] 更新灾备文档（如有变更）
- [ ] 审查备份日志中的警告和错误

### 6.4 月度检查项

- [ ] 完整灾难恢复演练
- [ ] 备份策略审查与优化
- [ ] RTO/RPO指标评估
- [ ] 灾备文档版本更新

---

## 紧急联系

### 7.1 联系清单

| 角色 | 姓名/代号 | 联系方式 | 职责 |
|------|-----------|----------|------|
| **指挥官** | Egbertie | 飞书/微信 | 恢复决策、资源调配 |
| **系统管理员** | MAIN-主控AI | 工作区内 | 技术恢复执行 |
| **安全负责人** | SOUL-精神核心 | 工作区内 | 安全事件评估 |
| **备份管理员** | 定时任务系统 | 自动执行 | 备份与恢复执行 |

### 7.2 升级路径

```
发现问题
    │
    ▼
┌───────────────┐
│ 尝试自动恢复   │ ◄── backup-manager.py restore
└───────┬───────┘
        │ 失败
        ▼
┌───────────────┐
│ 通知MAIN-主控  │
│ 执行手动恢复   │
└───────┬───────┘
        │ 失败
        ▼
┌───────────────┐
│ 通知Egbertie  │
│ 决策升级      │
└───────────────┘
```

### 7.3 紧急恢复命令速查

```bash
# 最快恢复（最新备份）
python3 /root/.openclaw/workspace/scripts/backup-manager.py restore --date $(date +%Y-%m-%d)

# 查看可用备份
python3 /root/.openclaw/workspace/scripts/backup-manager.py list

# 验证系统状态
openclaw status && openclaw gateway status

# 重启服务
openclaw gateway restart
```

---

## 附录

### 附录A: 存储空间计算

| 数据类型 | 日均增量 | 30天总量 | 90天总量 |
|----------|----------|----------|----------|
| Markdown文档 | ~2MB | ~60MB | ~180MB |
| 记忆文件 | ~1MB | ~30MB | ~90MB |
| 配置文件 | ~0.1MB | ~3MB | ~9MB |
| Skill文件 | ~0.5MB | ~15MB | ~45MB |
| **总计** | **~3.6MB** | **~108MB** | **~324MB** |

**建议最小存储空间**: 2GB

### 附录B: 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| V1.0.0 | 2026-03-10 | 初始版本发布 | 灾备重建项目组 |
| V1.0.1 | 2026-03-10 | 补充定时任务配置、当前备份状态 | 灾备重建项目组 |

### 附录C: 相关文档链接

- [备份管理器脚本](../scripts/backup-manager.py)
- [定时任务配置](../.github/cron/jobs.json) （注：实际路径为 `/root/.openclaw/cron/jobs.json`）
- [工作区状态](WORKSPACE_STATUS.md)
- [MEMORY.md](MEMORY.md)

### 附录D: 灾备演练计划

**月度演练**：
1. 模拟配置文件丢失场景
2. 执行P1级恢复流程
3. 验证恢复后系统功能
4. 记录演练时间和问题

**季度演练**：
1. 模拟完整数据丢失场景
2. 执行P0级完整重建
3. 验证所有功能模块
4. 评估RTO/RPO达成情况
5. 更新恢复流程文档

---

**文档结束**

> 本文档由满意解研究所灾备重建项目组维护  
> 最后验证时间: 2026-03-10 20:50  
> 下次审查时间: 2026-04-10

---

## 执行确认

- [x] 备份目录初始化 (`/backups`)
- [x] 首次全量备份完成 (96个文件)
- [x] 定时备份任务配置 (3个任务)
- [x] 备份脚本功能验证
- [x] 文档更新完成
