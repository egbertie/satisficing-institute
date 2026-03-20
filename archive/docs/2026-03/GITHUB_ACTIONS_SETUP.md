# GitHub Actions配置指南

## 步骤1：确认仓库访问

你的GitHub仓库：`satisficing-institute`  
Token权限：已验证可访问

## 步骤2：配置GitHub Actions工作流

在你的本地workspace中创建以下文件：

```bash
mkdir -p /root/.openclaw/workspace/.github/workflows
```

创建文件：`/root/.openclaw/workspace/.github/workflows/sync-to-notion.yml`

```yaml
name: Sync to Notion

on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点自动同步
  workflow_dispatch:      # 支持手动触发

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install requests notion-client

      - name: Sync to Notion
        env:
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
        run: |
          python scripts/notion_sync.py
```

## 步骤3：设置GitHub Secrets

在GitHub仓库页面操作：
1. 访问 https://github.com/Egbertie/satisficing-institute/settings/secrets/actions
2. 点击 "New repository secret"
3. 添加以下secrets：
   - `NOTION_TOKEN`: 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

## 步骤4：启用Actions

在GitHub仓库页面：
1. 点击 "Actions" 标签
2. 点击 "I understand my workflows, go ahead and enable them"

## 备选方案（无法访问GitHub Settings）

如果你没有仓库的admin权限，使用以下方案：

### 方案A：本地Git推送 + GitHub监控
```bash
# 每天自动推送
0 2 * * * cd /root/.openclaw/workspace && git add . && git commit -m "Daily backup $(date)" && git push origin main
```

### 方案B：你提供Collaborator权限
1. 在GitHub仓库添加我为Collaborator
2. 我可以直接配置Actions

选择哪个方案？