# Skill部署执行方案

**执行时间**：2026-03-09 20:05  
**执行状态**：ClawHub API限流，转为手动部署  
**部署目标**：github-integration + notion-integration + slack-integration

---

## 一、部署状态

### 自动安装受阻原因

| 尝试方式 | 结果 | 原因 |
|---------|------|------|
| clawhub install | ❌ 失败 | API Rate Limit |
| npx clawhub install | ❌ 失败 | API Rate Limit |
| git clone | ❌ 失败 | 需GitHub认证 |

### 解决方案

**转为手动部署 + 延时重试机制**

---

## 二、手动部署方案

### 2.1 github-integration 手动部署

**功能需求**：
- Git版本控制项目文档
- Webhook通知飞书
- PR管理重要变更

**部署步骤**：

```bash
# 步骤1：在GitHub创建私有仓库
# 仓库名：satisficing-institute-docs
# 类型：Private

# 步骤2：本地初始化Git仓库
cd /root/.openclaw/workspace
git init
git remote add origin https://github.com/[username]/satisficing-institute-docs.git

# 步骤3：创建.gitignore
cat > .gitignore << 'EOF'
# OpenClaw敏感数据
.openclaw/agents/*/auth-profiles.json
.openclaw/agents/*/tokens/
*.key
*.secret

# 临时文件
*.tmp
*.log
.DS_Store
EOF

# 步骤4：首次提交
git add .
git commit -m "Initial commit: Satisficing Institute project docs"
git push -u origin main
```

**Webhook配置**：
```bash
# 在GitHub仓库设置中添加Webhook
# Payload URL: [飞书Webhook地址]
# Content type: application/json
# Events: push, pull_request
```

---

### 2.2 notion-integration 手动部署

**功能需求**：
- 建立Notion知识库
- 33角色信息表
- 会议模板库

**部署步骤**：

```bash
# 步骤1：创建Notion Integration
# 访问：https://www.notion.so/my-integrations
# 创建新Integration，获取Token

# 步骤2：创建Notion工作空间
# 页面标题：满意解研究所知识库
# 结构：
# ├── 📚 项目文档
# │   ├── 战略核心
# │   ├── 组织架构
# │   └── 五路图腾
# ├── 👥 角色档案
# │   └── 33人信息表（数据库）
# ├── 📅 会议记录
# │   └── 模板库
# └── 📊 执行看板
#     └── 任务跟踪（看板视图）

# 步骤3：33角色信息表结构
# 数据库字段：
# - 角色编号（标题）
# - 角色名称（文本）
# - 所属层级（单选）
# - 五行属性（单选）
# - 核心职责（文本）
# - 当前状态（单选：运行中/待命/阻塞）
# - 本周任务（多选）
# - 负责人（人员）
# - 备注（文本）

# 步骤4：手动安装Notion Skill（延时重试）
# 等待ClawHub API恢复后执行：
# clawhub install notion-integration
```

---

### 2.3 slack-integration 手动部署

**功能需求**：
- AI角色Bot自动汇报
- 任务截止提醒
- 重要决策通知

**部署步骤**：

```bash
# 步骤1：创建Slack工作空间（或使用现有）
# 访问：https://slack.com/create

# 步骤2：创建频道结构
# #general - 综合讨论
# #announcements - 重要公告
# #ai-reports - AI角色汇报
# #daily-standup - 每日站会
# #decisions - 决策记录

# 步骤3：创建Slack App
# 访问：https://api.slack.com/apps
# 创建App，获取Bot Token

# 步骤4：配置Webhook
# 在飞书中配置Slack集成（双向通知）

# 步骤5：延时安装Slack Skill
# 等待ClawHub API恢复后执行：
# clawhub install slack-integration
```

---

## 三、延时重试计划

### 自动重试机制

已设置定时任务，每小时尝试安装一次：

```bash
#!/bin/bash
# /root/.openclaw/workspace/scripts/install-skills.sh

SKILLS=("github-integration" "notion-integration" "slack-integration")
LOG_FILE="/root/.openclaw/workspace/logs/skill-install.log"

for skill in "${SKILLS[@]}"; do
    if ! clawhub list | grep -q "$skill"; then
        echo "$(date): Trying to install $skill..." >> $LOG_FILE
        if clawhub install "$skill" --force 2>>$LOG_FILE; then
            echo "$(date): Successfully installed $skill" >> $LOG_FILE
        else
            echo "$(date): Failed to install $skill, will retry later" >> $LOG_FILE
        fi
    fi
done
```

### 手动安装检查点

| 时间点 | 操作 | 检查内容 |
|--------|------|---------|
| 3/10 09:00 | 首次重试 | clawhub API是否恢复 |
| 3/10 12:00 | 第二次重试 | 安装日志检查 |
| 3/10 18:00 | 第三次重试 | 如仍失败，使用npx方式 |
| 3/11 09:00 | 最终检查 | 必要时手动配置 |

---

## 四、临时替代方案

### 4.1 Git版本控制（无需Skill）

直接使用Git命令管理文档版本：

```bash
# 每日提交脚本
cd /root/.openclaw/workspace
git add .
git commit -m "Daily backup: $(date +%Y-%m-%d)"
git push origin main
```

### 4.2 Notion手动同步

定期导出飞书文档，手动上传至Notion：
- 每日导出关键文档
- 每周全面备份
- 重要文档双平台同步

### 4.3 飞书消息增强（无需Slack）

优化现有飞书消息功能：
- 使用message工具定时发送日报
- 设置cron任务自动提醒
- 利用飞书群机器人

---

## 五、立即执行项

### 5.1 今天可完成

- [x] 创建本地Git仓库
- [ ] 设置GitHub仓库（需用户GitHub账号）
- [ ] 创建Notion工作空间（需用户Notion账号）
- [ ] 设置首次提交

### 5.2 需要用户信息

1. **GitHub**：
   - 用户名
   - 是否创建新仓库？
   - 仓库名（建议：satisficing-institute）

2. **Notion**：
   - 是否已有Notion账号？
   - 工作空间名称（建议：满意解研究所）

3. **Slack**：
   - 是否已有Slack工作空间？
   - 是否需要新建？

---

## 六、预期完成时间

| 项目 | 自动安装 | 手动部署 | 预计完成 |
|------|---------|---------|---------|
| GitHub集成 | 受阻 | 今日可完成 | 3/10 |
| Notion双备份 | 受阻 | 需账号 | 3/11 |
| Slack增强 | 受阻 | 可选 | 3/12 |

---

**状态**：等待用户提供GitHub/Notion账号信息，或ClawHub API恢复  
**备选**：使用纯Git+飞书方案临时替代
