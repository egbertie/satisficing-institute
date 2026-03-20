# 工作空间组织规则 (WORKSPACE_ORGANIZATION_RULES)

版本: v1.0  
创建时间: 2026-03-18  
适用范围: /root/.openclaw/workspace/

---

## 一、文件夹命名规范

### 1.1 基本原则

| 规则 | 说明 | 示例 |
|------|------|------|
| **英文优先** | 使用英文命名，避免中文路径 | `archive/` 而非 `归档/` |
| **小写+连字符** | 小写字母，单词间用连字符 | `decision-theory/` |
| **无空格** | 不使用空格，用下划线或连字符 | `org_structure/` |
| **无特殊字符** | 仅使用字母、数字、连字符、下划线 | 禁止 `History}` |
| **语义明确** | 名称应准确反映内容 | `notion-sync/` 而非 `ns/` |

### 1.2 保留的核心文件夹

```
/root/.openclaw/workspace/
├── .workspace_optimization/   # 工作空间优化记录（隐藏）
├── .clawhub/                  # Clawhub 配置（隐藏）
├── .github/                   # GitHub 配置（隐藏）
├── .config/                   # 隐藏配置（环境变量等）
├── archive/                   # 归档文件
├── backups/                   # 备份数据
├── dashboard/                 # 仪表板
├── data/                      # 数据文件
├── database/                  # 数据库
├── disaster-recovery/         # 灾备（统一使用 disaster-recovery）
├── docs/                      # 文档中心
├── knowledge_base/            # 知识库
├── logs/                      # 日志文件
├── memory/                    # 记忆文件
├── n8n-workflows/             # n8n工作流
├── partner-match-system/      # 合伙人匹配系统
├── perceptual-intelligence/   # 感知智能
├── personas/                  # 角色定义
├── reports/                   # 报告文件
├── schemas/                   # 数据模式
├── scripts/                   # 脚本文件
├── skills/                    # 技能库
├── templates/                 # 模板文件
├── test_files/                # 测试文件
├── tools/                     # 工具集
└── workflows/                 # 工作流
```

### 1.3 禁止创建的一级文件夹

- 单字符文件夹（如 `1`, `!`）
- 包含特殊字符的文件夹（如 `History}`）
- 同名不同格式的文件夹（如 `config` 和 `.config` 应明确分工）
- 临时文件夹（使用 `/tmp` 或 `temp/`）

---

## 二、文件存放规则

### 2.1 一级目录文件限制

**原则**: 一级目录只保留核心配置文件，其他文件必须放入子目录。

**允许保留的一级文件**:

| 文件名 | 用途 |
|--------|------|
| `AGENTS.md` | 代理配置 |
| `BOOTSTRAP.md` | 启动配置（首次运行后删除） |
| `HEARTBEAT.md` | 心跳检查配置 |
| `IDENTITY.md` | 身份定义 |
| `MEMORY.md` | 长期记忆 |
| `README.md` | 项目说明 |
| `SOUL.md` | 核心设定 |
| `TASKS.md` | 任务列表 |
| `TOOLS.md` | 工具说明 |
| `USER.md` | 用户配置 |
| `.env*` | 环境变量 |
| `ORGANIZATION.md` | 组织架构 |
| `WORKSPACE_STATUS.md` | 工作空间状态 |

### 2.2 文件分类存放

| 文件类型 | 存放位置 | 示例 |
|----------|----------|------|
| 角色定义 | `personas/` | `ROLE-*.md` |
| 会议记录 | `docs/meetings/` | `MEETING_PROTOCOL.md` |
| 商业文档 | `docs/business/` | 商业计划、盈利模型 |
| 文化文档 | `docs/culture/` | 五路图腾、团队文化 |
| 决策文档 | `docs/decision/` | 感知力决策相关 |
| 飞书相关 | `docs/feishu/` | 飞书API文档 |
| 历史版本 | `docs/archive/` 或 `archive/` | V2.0, V2.1 旧版本 |
| 技能文档 | `archive/skills/` | skill*.md |
| Notion同步 | `archive/notion_sync_old/` | notion_*.py, notion_*.json |
| 压缩日志 | `archive/compression_logs/` | COMPRESSION_*.md |
| 测试文件 | `test_files/` | test_*.py |

### 2.3 命名冲突解决

当出现同名文件夹时：

1. **保留最新版本**作为主文件夹
2. **将旧版本内容**移入 `主文件夹/archive/`
3. **删除**旧文件夹

示例:
```
# 合并前
disaster-recovery/        # 较新，保留
disaster_recovery/        # 较旧，合并后删除

# 合并后
disaster-recovery/
└── archive/
    └── disaster_recovery_backup/   # 原 disaster_recovery 内容
```

---

## 三、定期清理机制

### 3.1 清理频率

| 清理类型 | 频率 | 执行时间 |
|----------|------|----------|
| **空文件夹清理** | 每周 | 周日 23:00 |
| **日志归档** | 每月 | 每月1日 |
| **旧备份清理** | 每季度 | 季度首月1日 |
| **完整整理** | 每月 | 每月15日 |

### 3.2 清理检查清单

```bash
# 1. 检查空文件夹
find . -type d -empty | grep -v ".git"

# 2. 检查大文件（>10MB）
find . -type f -size +10M | head -20

# 3. 检查重复文件（按名称）
find . -type f -name "*.md" | sort | uniq -d

# 4. 检查松散文件
find . -maxdepth 1 -type f | wc -l
# 目标: < 30 个
```

### 3.3 自动清理脚本

建议创建 `scripts/workspace-cleanup.sh`:

```bash
#!/bin/bash
# workspace-cleanup.sh - 工作空间自动清理脚本

WORKSPACE="/root/.openclaw/workspace"
cd "$WORKSPACE"

# 1. 删除空文件夹（排除.git）
find . -type d -empty | grep -v ".git" | xargs -r rmdir -p 2>/dev/null

# 2. 清理旧日志（保留30天）
find logs/ -type f -mtime +30 -delete 2>/dev/null

# 3. 清理临时文件
find . -name "*.tmp" -o -name "*.temp" | xargs -r rm -f

# 4. 生成清理报告
echo "清理完成: $(date)" >> logs/workspace_cleanup.log
```

---

## 四、禁止事项

### 4.1 严禁行为

| 禁止事项 | 说明 | 后果 |
|----------|------|------|
| ❌ 一级目录存放临时文件 | 临时文件必须使用 `/tmp` 或 `temp/` | 文件丢失风险 |
| ❌ 创建单字符文件夹 | 禁止 `1`, `!`, `a` 等无意义名称 | 维护困难 |
| ❌ 文件夹名含特殊字符 | 禁止 `}`, `{`, `|`, `&` 等 | 命令执行错误 |
| ❌ 同名不同格式文件夹 | 禁止 `folder` 和 `folder_` 并存 | 内容分散 |
| ❌ 直接删除 `.git` | 版本控制数据 | 不可逆损失 |
| ❌ 删除 `memory/` 或 `docs/` | 核心数据目录 | 数据丢失 |

### 4.2 谨慎操作

以下操作需要备份:

- 删除任何非空文件夹
- 重命名核心文件 (AGENTS.md, SOUL.md 等)
- 合并文件夹前确认内容
- 批量移动文件

### 4.3 推荐操作

```bash
# ✅ 删除前备份
cp -r folder/ .workspace_optimization/backup/folder_backup_$(date +%Y%m%d)/

# ✅ 使用 trash 而非 rm
mv file.txt ~/.trash/

# ✅ 批量操作前测试
find . -name "*.tmp" | head -5  # 先查看，再删除

# ✅ 记录变更
echo "$(date): 删除 folder/" >> .workspace_optimization/change.log
```

---

## 五、新增内容规范

### 5.1 新增文件夹流程

1. **检查是否已存在**相似文件夹
2. **遵循命名规范**（小写+连字符）
3. **创建 README.md** 说明用途
4. **更新**本规则文档（如必要）

### 5.2 新增文件流程

1. **判断是否属于**现有分类
2. **一级目录仅限**核心配置文件
3. **业务文档放入** `docs/` 子目录
4. **脚本放入** `scripts/`

---

## 六、故障恢复

### 6.1 备份位置

所有整理操作前会在以下位置创建备份:

```
.workspace_optimization/
├── backup_YYYYMMDD_HHMMSS/     # 完整备份
├── backup_critical/             # 关键文件备份
└── phase1_before_report.md      # 整理前状态
```

### 6.2 恢复命令

```bash
# 恢复特定文件
cp .workspace_optimization/backup_critical/AGENTS.md ./

# 恢复整个目录
cp -r .workspace_optimization/backup_*/skills ./
```

---

## 七、文件生命周期管理（新增）

### 7.1 文件流转标准流程

所有文件必须遵循以下生命周期：

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   接收/     │ →  │   暂存区    │ →  │   处理/     │ →  │   归档/     │
│   下载      │    │   Staging   │    │   加工      │    │   删除      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                  │                  │                  │
   downloads/       staging/            各工作目录        archive/ 或删除
   外部来源         临时存放            正式编辑          永久保存
```

### 7.2 暂存区规范

**暂存区位置**: `/root/.openclaw/workspace/staging/`

| 子目录 | 用途 | 清理频率 | 负责人 |
|--------|------|----------|--------|
| `downloads-inbox/` | 从downloads移入的待处理文件 | 每日 | 内容管理员 |
| `to-process/` | 需要人工处理的文件 | 每周 | 内容管理员 |
| `to-archive/` | 待归档的文件 | 每日 | 内容管理员 |
| `temp/` | 临时文件 | 每日自动清理 | 系统 |

**暂存区使用规则**:
1. 文件在暂存区停留不超过7天
2. 超过7天未处理的文件自动标记为待清理
3. 临时文件(`temp/`)每日凌晨自动清空
4. 禁止在暂存区直接编辑文件

### 7.3 文件处理SOP

#### 下载文件处理流程

```bash
# Step 1: 每日检查downloads目录
ls -la /root/openclaw/kimi/downloads/

# Step 2: 将新文件移入暂存区
mv /root/openclaw/kimi/downloads/*.docx staging/downloads-inbox/

# Step 3: 分类决策
# - 临时文件 → staging/temp/ → 7天后删除
# - 待处理 → staging/to-process/ → 人工处理
# - 正式文档 → 按类型归档到对应目录

# Step 4: 更新索引
scripts/update-file-index.sh
```

#### 解读摘要生成流程

1. **生成前**: 在 `docs/RESEARCH_DIGEST_TRACKER.md` 登记
2. **生成时**: 统一存放在 `A满意哥专属文件夹/03_📋研究任务/`
3. **命名规范**: `{研究主题}_解读摘要_V{版本}.md`
4. **生成后**: 更新追踪表状态，执行 `update-file-index.sh`

---

## 八、版本控制规范（新增）

### 8.1 版本号规则

**版本号格式**: `V{主版本}.{次版本}`

| 版本变更 | 规则 | 示例 |
|----------|------|------|
| 重大更新 | 主版本+1 | V1.0 → V2.0 |
| 次要更新 | 次版本+1 | V1.0 → V1.1 |
| 修正错误 | 次版本+1 | V1.0 → V1.1 |

**文件命名示例**:
```
# ✅ 正确
满意解研究所V1.0.md
满意解研究所V1.1.md
QPMS算法效度验证研究_解读摘要_V1.md

# ❌ 错误
满意解研究所V0.3.docx  (零散版本号)
满意解研究所新版本.md  (无版本号)
满意解研究所(最终版).md (使用括号)
```

### 8.2 版本归档策略

**当前版本**: 保留在活跃目录
**历史版本**: 移入 `archive/` 目录

```
docs/
├── current-document.md        # 当前版本 (软链接或副本)
└── archive/
    ├── current-document_V1.0.md   # 历史版本
    ├── current-document_V0.9.md
    └── README.md                  # 版本说明
```

### 8.3 版本冲突解决

当发现同一文件的多个版本时：

1. **识别最新版本**: 比较修改时间或版本号
2. **合并差异**: 如有需要，合并各版本的有用内容
3. **归档旧版本**: 将旧版本移入 `archive/`
4. **保留唯一当前版本**: 确保活跃目录只有一份当前版本
5. **更新索引**: 同步更新文件索引

---

## 九、定期清理机制（强化）

### 9.1 清理任务清单

| 任务 | 频率 | 执行时间 | 执行方式 | 检查命令 |
|------|------|----------|----------|----------|
| 空文件夹清理 | 每日 | 23:00 | Cron | `find . -type d -empty \| wc -l` |
| Temp目录清理 | 每日 | 00:00 | Cron | `ls staging/temp/ \| wc -l` |
| Downloads监控 | 每日 | 23:30 | Cron | `ls downloads/ \| wc -l` |
| 日志归档 | 每周 | 周日 23:00 | 脚本 | `find logs/ -mtime +30` |
| 大文件检查 | 每周 | 周一 09:00 | 人工 | `find . -size +10M` |
| 重复文件检测 | 每周 | 周二 09:00 | 脚本 | `fdupes -r .` |
| 命名规范审计 | 每周 | 周三 09:00 | 脚本 | `check-naming-convention.sh` |
| 完整文件审计 | 每月 | 15日 | 人工+脚本 | 见审计清单 |
| 旧备份清理 | 每季度 | 首月1日 | 人工 | `ls backups/` |

### 9.2 自动化清理脚本

```bash
#!/bin/bash
# scripts/auto-cleanup.sh - 自动化清理脚本

WORKSPACE="/root/.openclaw/workspace"
REPORT="$WORKSPACE/logs/cleanup-$(date +%Y%m%d).log"

echo "=== 自动清理报告 $(date) ===" > "$REPORT"

# 1. 清理空文件夹（排除.git和关键目录）
EMPTY_BEFORE=$(find "$WORKSPACE" -type d -empty 2>/dev/null | grep -v ".git" | wc -l)
find "$WORKSPACE" -type d -empty 2>/dev/null | grep -v ".git" | grep -v "backup" | \
    xargs -r rmdir -p 2>/dev/null
EMPTY_AFTER=$(find "$WORKSPACE" -type d -empty 2>/dev/null | grep -v ".git" | wc -l)
echo "空文件夹清理: $EMPTY_BEFORE → $EMPTY_AFTER" >> "$REPORT"

# 2. 清理临时文件
TEMP_COUNT=$(find "$WORKSPACE" -name "*.tmp" -o -name "*.temp" 2>/dev/null | wc -l)
find "$WORKSPACE" -name "*.tmp" -delete 2>/dev/null
find "$WORKSPACE" -name "*.temp" -delete 2>/dev/null
echo "临时文件清理: $TEMP_COUNT 个" >> "$REPORT"

# 3. 清理staging/temp
if [ -d "$WORKSPACE/staging/temp" ]; then
    TEMP_FILES=$(ls "$WORKSPACE/staging/temp" 2>/dev/null | wc -l)
    rm -rf "$WORKSPACE/staging/temp/"*
    echo "staging/temp 清理: $TEMP_FILES 个文件" >> "$REPORT"
fi

# 4. 检查downloads目录
DOWNLOADS_COUNT=$(ls /root/openclaw/kimi/downloads/ 2>/dev/null | wc -l)
echo "downloads目录: $DOWNLOADS_COUNT 个文件" >> "$REPORT"
if [ $DOWNLOADS_COUNT -gt 500 ]; then
    echo "⚠️ 警告: downloads目录文件过多，请人工处理" >> "$REPORT"
fi

echo "清理完成: $(date)" >> "$REPORT"
```

### 9.3 月度审计清单

```markdown
# 月度文件管理审计清单

## 结构审计
- [ ] 空文件夹数量 < 5 个 (当前: ___)
- [ ] 重复文件夹已合并
- [ ] 层级深度不超过5层
- [ ] 暂存区已清空

## 文件审计
- [ ] downloads文件数 < 200 (当前: ___)
- [ ] 一级目录松散文件 < 20 (当前: ___)
- [ ] 重复README.md < 10 (当前: ___)
- [ ] 临时文件已清理

## 规范审计
- [ ] 新文件命名合规率 = 100%
- [ ] 版本号使用规范
- [ ] 归档文件已正确分类
- [ ] 索引文件已更新

## 技术审计
- [ ] 自动化脚本运行正常
- [ ] 备份完整性验证通过
- [ ] 文件索引可正常访问
- [ ] 清理日志无异常

## 改进项
- [ ] 本月发现问题: ___________
- [ ] 改进措施: ___________
- [ ] 责任人: ___________
```

---

## 十、责任分工（新增）

### 10.1 角色定义

| 角色 | 职责 | 权限 | 频率 |
|------|------|------|------|
| **系统管理员** | 部署维护自动化脚本、处理技术故障、监控系统运行 | 读写所有目录 | 按需 |
| **内容管理员** | 审核downloads内容、决定文件去留、执行归档操作 | 读写非隐藏目录 | 每日 |
| **审计员** | 执行定期审计、生成审计报告、监督规范执行 | 只读访问 | 每周/每月 |
| **普通用户** | 遵守命名规范、正确归档文件、及时清理临时文件 | 限定目录写入 | 每次操作 |

### 10.2 任务分配矩阵

| 任务 | 系统管理员 | 内容管理员 | 审计员 | 工具/Cron |
|------|:----------:|:----------:|:------:|:---------:|
| 空文件夹清理 | - | - | 检查 | ✅ Cron |
| Downloads整理 | - | 执行 | 监督 | - |
| 命名规范执行 | - | 监督 | 审计 | - |
| 索引更新 | 部署 | - | 检查 | ✅ 脚本 |
| 月度审计 | 支持 | 配合 | 执行 | - |
| 备份验证 | 执行 | - | 检查 | ✅ Cron |
| 脚本维护 | 执行 | - | - | - |

### 10.3 异常处理流程

**发现文件丢失**:
1. 立即报告给系统管理员
2. 检查 `.workspace_optimization/backup_critical/`
3. 检查 Git 历史记录
4. 必要时从备份恢复

**发现命名违规**:
1. 记录违规文件位置
2. 通知内容管理员
3. 限期整改
4. 更新命名规范文档（如需）

**发现大量重复文件**:
1. 运行重复文件检测脚本
2. 评估重复原因
3. 制定清理方案
4. 执行清理并更新索引

---

## 十一、更新记录

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|----------|--------|
| v1.0 | 2026-03-18 | 初始版本 | 工作空间优化工具 |
| v1.1 | 2026-03-18 | 新增文件生命周期管理、版本控制规范、强化清理机制、责任分工 | 文件管理审计工具 |

---

## 附录A: 快速检查命令

```bash
# === 基础统计 ===
echo "总文件数: $(find /root/.openclaw/workspace -type f | wc -l)"
echo "总文件夹数: $(find /root/.openclaw/workspace -type d | wc -l)"
echo "空文件夹数: $(find /root/.openclaw/workspace -type d -empty | grep -v '.git' | wc -l)"
echo "downloads文件数: $(ls /root/openclaw/kimi/downloads/ 2>/dev/null | wc -l)"
echo "一级目录松散文件: $(find /root/.openclaw/workspace -maxdepth 1 -type f | wc -l)"

# === 空文件夹检查 ===
find /root/.openclaw/workspace -type d -empty | grep -v ".git"

# === 大文件检查 ===
find /root/.openclaw/workspace -type f -size +10M | head -20

# === 重复文件名检查 ===
find /root/.openclaw/workspace -type f -name "*.md" | sed 's|.*/||' | sort | uniq -c | sort -rn | head -10

# === 命名规范检查 ===
find /root/.openclaw/workspace -name "*[📄📑🔥✅📋📚🔴🎨🔄🔧📦👥🧠💡📊🖼️📈🧭💻🚀📝]*" 2>/dev/null | head -20

# === 文件夹大小 ===
du -sh /root/.openclaw/workspace/* | sort -h | tail -20

# === 最近修改文件 ===
find /root/.openclaw/workspace -type f -mtime -1 | head -20
```

## 附录B: 紧急修复指南

### B.1 文件丢失应急

```bash
# 1. 检查备份目录
ls -la /root/.openclaw/workspace/.workspace_optimization/backup_critical/

# 2. 检查Git历史
cd /root/.openclaw/workspace
git log --diff-filter=D --summary | grep delete | head -20

# 3. 从Git恢复
git checkout HEAD^ -- path/to/deleted/file
```

### B.2 快速清理空文件夹

```bash
# 查看将要删除的空文件夹
find /root/.openclaw/workspace/A满意哥专属_folder -type d -empty | grep -v ".git"

# 执行删除（谨慎操作）
find /root/.openclaw/workspace/A满意哥专属_folder -type d -empty | grep -v ".git" | xargs -r rmdir -p 2>/dev/null
```

### B.3 Downloads目录紧急清理

```bash
# 1. 创建紧急备份
mkdir -p /root/.openclaw/workspace/staging/downloads-backup-$(date +%Y%m%d)
cp -r /root/openclaw/kimi/downloads/* /root/.openclaw/workspace/staging/downloads-backup-$(date +%Y%m%d)/

# 2. 按类型分类（手动检查后再删除）
mkdir -p /root/.openclaw/workspace/staging/by-type/{documents,images,scripts,others}
mv /root/openclaw/kimi/downloads/*.{docx,doc,md} /root/.openclaw/workspace/staging/by-type/documents/ 2>/dev/null
mv /root/openclaw/kimi/downloads/*.{png,jpg,jpeg,gif} /root/.openclaw/workspace/staging/by-type/images/ 2>/dev/null
mv /root/openclaw/kimi/downloads/*.{py,sh,js} /root/.openclaw/workspace/staging/by-type/scripts/ 2>/dev/null
```

### B.4 索引重建

```bash
# 如果文件索引损坏，重新生成
cd /root/.openclaw/workspace
scripts/update-file-index.sh
echo "索引已重建: $(date)" >> logs/index-rebuild.log
```

## 附录C: 文件管理检查清单

### C.1 每日检查

- [ ] Downloads目录文件数 < 500
- [ ] 空文件夹数量 < 10
- [ ] 自动化脚本运行正常
- [ ] 临时文件已清理

### C.2 每周检查

- [ ] 所有新文件命名合规
- [ ] 暂存区已清空
- [ ] 重复文件名已处理
- [ ] 大文件（>10MB）有明确用途

### C.3 每月检查

- [ ] 完整执行月度审计清单
- [ ] 更新文件索引
- [ ] 归档旧版本文件
- [ ] 备份完整性验证
- [ ] 审查并更新本规则文档

## 附录D: 参考文档

| 文档 | 路径 | 用途 |
|------|------|------|
| 漏洞诊断报告 | `docs/FILE_MANAGEMENT_AUDIT_REPORT.md` | 详细的漏洞分析 |
| 系统性解决方案 | `docs/FILE_MANAGEMENT_SOLUTION.md` | 解决方案和执行计划 |
| 安全持续改进 | `docs/SECURITY_CONTINUOUS_IMPROVEMENT.md` | 安全机制设计 |
| Downloads索引 | `docs/DOWNLOADS_INDEX.md` | Downloads目录内容索引 |
| 研究追踪表 | `docs/RESEARCH_DIGEST_TRACKER.md` | 解读摘要追踪 |
| 文件索引 | `docs/FILE_INDEX.md` | 核心文件索引 |

---

*本文档最后更新: 2026-03-18*  
*下次Review: 2026-04-01*
