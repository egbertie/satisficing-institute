# Skill部署执行手册

**部署时间**：2026-03-09 20:05  
**执行状态**：API限流，改用分步安装+手动指南  
**部署目标**：github-integration + notion-integration + slack-integration

---

## 一、安装状态

| Skill | 状态 | 备注 |
|-------|------|------|
| github-integration | ⏳ 等待安装 | API限流，稍后重试 |
| notion-integration | ⏳ 等待安装 | API限流，稍后重试 |
| slack-integration | ⏳ 等待安装 | API限流，稍后重试 |

---

## 二、手动安装指南

### 方法1：命令行安装（推荐）

在服务器终端执行以下命令：

```bash
# 1. 进入工作目录
cd /root/.openclaw/workspace

# 2. 安装 GitHub Integration
clawhub install github-integration

# 3. 安装 Notion Integration
clawhub install notion-integration

# 4. 安装 Slack Integration
clawhub install slack-integration

# 5. 验证安装
clawhub list

# 6. 重启OpenClaw生效
systemctl restart openclaw
```

### 方法2：离线安装（网络受限时）

```bash
# 1. 访问 https://clawhub.ai/ 搜索目标Skill
# 2. 点击"Download zip"下载
# 3. 上传至服务器 ~/.openclaw/workspace/skills/
# 4. 解压
unzip github-integration-v1.0.0.zip -d ~/.openclaw/workspace/skills/github-integration

# 5. 重启生效
systemctl restart openclaw
```

---

## 三、配置指南

### 3.1 GitHub Integration 配置

#### 步骤1：创建GitHub仓库
1. 访问 https://github.com/new
2. 仓库名称：`satisficing-institute`（或私人偏好名称）
3. 设置为 **Private**（敏感文档）
4. 勾选 "Add a README file"

#### 步骤2：获取Token
1. GitHub → Settings → Developer settings → Personal access tokens
2. 生成Token，权限勾选：
   - `repo`（完整仓库权限）
   - `workflow`（GitHub Actions）

#### 步骤3：配置OpenClaw
```bash
# 设置环境变量
export GITHUB_TOKEN="your_token_here"
export GITHUB_REPO="your_username/satisficing-institute"
```

#### 步骤4：初始化同步
```bash
# 将现有文档推送至GitHub
# 在workspace目录执行
git init
git add .
git commit -m "Initial commit: 满意解研究所文档"
git branch -M main
git remote add origin https://github.com/$GITHUB_REPO.git
git push -u origin main
```

#### 步骤5：Webhook配置（自动通知）
1. GitHub仓库 → Settings → Webhooks → Add webhook
2. Payload URL: `https://your-webhook-endpoint`（如使用飞书/Slack）
3. Content type: `application/json`
4. 选择事件：Pushes, Pull requests

---

### 3.2 Notion Integration 配置

#### 步骤1：创建Notion集成
1. 访问 https://www.notion.so/my-integrations
2. 点击 "New integration"
3. 名称："满意解研究所"
4. 关联工作区：选择你的工作区
5. 复制 **Internal Integration Token**

#### 步骤2：创建知识库结构
```
满意解研究所（Workspace）
├── 📚 知识资产
│   ├── 五路图腾体系
│   ├── 核心专家档案
│   └── 项目愿景
├── 👥 角色管理
│   ├── 33人组织架构
│   ├── 角色工作档案
│   └── 专家网络
├── 📋 执行跟踪
│   ├── 任务看板
│   ├── 会议纪要
│   └── 里程碑
└── 🎨 品牌资产
    ├── 视觉规范
    ├── 官宣材料
    └── 图片资产
```

#### 步骤3：连接OpenClaw
```bash
export NOTION_TOKEN="your_notion_token"
export NOTION_DATABASE_ID="your_database_id"
```

#### 步骤4：数据迁移
使用Notion Web Clipper或手动导入关键文档

---

### 3.3 Slack Integration 配置

#### 步骤1：创建Slack工作区（如没有）
1. 访问 https://slack.com/create
2. 名称："满意解研究所"
3. 完成创建流程

#### 步骤2：创建机器人
1. 访问 https://api.slack.com/apps
2. 点击 "Create New App" → "From scratch"
3. 名称："满意妞"（主控AI）
4. 选择工作区

#### 步骤3：配置权限
在 "OAuth & Permissions" 中添加以下权限：
- `chat:write`（发送消息）
- `chat:write.public`（公开频道）
- `channels:read`（读取频道）
- `users:read`（读取用户）

#### 步骤4：安装应用到工作区
1. 点击 "Install to Workspace"
2. 复制 **Bot User OAuth Token**

#### 步骤5：配置OpenClaw
```bash
export SLACK_TOKEN="xoxb-your-bot-token"
export SLACK_CHANNEL="#general"  # 默认频道
```

#### 步骤6：创建频道结构
```
#general      - 综合通知
#peo-eoo      - PEO+EEO协调
#announce     - 官宣进展
#content      - 内容生产
#meetings     - 会议纪要
#alerts       - 紧急通知
```

---

## 四、验证安装

### 验证命令
```bash
# 1. 检查已安装Skill
clawhub list

# 2. 检查环境变量
echo $GITHUB_TOKEN
echo $NOTION_TOKEN
echo $SLACK_TOKEN

# 3. 测试GitHub连接
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# 4. 测试Notion连接
curl -H "Authorization: Bearer $NOTION_TOKEN" https://api.notion.com/v1/users

# 5. 测试Slack连接
curl -H "Authorization: Bearer $SLACK_TOKEN" https://slack.com/api/auth.test
```

---

## 五、自动化配置

### 5.1 GitHub → 飞书通知

创建 `.github/workflows/notify-feishu.yml`：
```yaml
name: Notify Feishu
on:
  push:
    branches: [main]
  pull_request:
    types: [opened, closed]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Send to Feishu
        run: |
          curl -X POST "$FEISHU_WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d '{
              "msg_type": "text",
              "content": {
                "text": "GitHub更新：${{ github.event.head_commit.message }}"
              }
            }'
```

### 5.2 Notion → 任务同步

设置Notion Automation：
- 当任务状态变更为"已完成" → 发送飞书通知
- 当截止日期临近 → 发送提醒

### 5.3 Slack → AI角色汇报

配置AI角色定期汇报：
```bash
# PEO每日汇报
0 18 * * * openclaw session send "PEO日报" --channel slack

# EEO访谈后汇报
# 访谈结束自动触发
```

---

## 六、故障排查

### 常见问题

#### Q1: 安装时显示"Rate limit exceeded"
**解决**：等待1-2分钟后重试，或改用离线安装

#### Q2: GitHub推送失败
**解决**：
```bash
# 检查Token权限
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# 检查仓库地址
git remote -v

# 重新配置
 git remote set-url origin https://$GITHUB_TOKEN@github.com/username/repo.git
```

#### Q3: Notion API返回401
**解决**：
- 确认Integration已关联到对应页面
- 在Notion页面 → Share → 添加Integration

#### Q4: Slack消息发送失败
**解决**：
- 确认Bot已加入目标频道
- 检查Token权限是否包含`chat:write`

---

## 七、下一步行动

### 立即执行（今天）
- [ ] 安装三个Skill（限流恢复后）
- [ ] 创建GitHub仓库
- [ ] 创建Notion集成

### 本周内完成
- [ ] 完成GitHub初始同步
- [ ] 建立Notion知识库结构
- [ ] 配置Slack频道

### 持续优化
- [ ] 设置自动化通知
- [ ] 建立数据同步规则
- [ ] 定期备份检查

---

**部署负责**：系统管理员  
**配置协助**：PEO + 满意妞  
**验收标准**：三个Skill正常运行，数据同步无误
