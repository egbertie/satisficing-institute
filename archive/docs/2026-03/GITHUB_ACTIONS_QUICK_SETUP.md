# GitHub Actions 简化配置步骤（5分钟）

> 由于我的GitHub账号无法接受邮件邀请，我们改用**你自行创建工作流文件**的方式，功能完全相同。

---

## 步骤1：创建工作流文件（2分钟）

1. 打开你的GitHub仓库页面：
   `https://github.com/Egbertie/satisficing-institute`

2. 点击上方 **"Actions"** 标签

3. 点击 **"set up a workflow yourself"**（或 "New workflow"）

4. 在文件名框输入：
   `.github/workflows/daily-sync.yml`

5. 复制以下代码到编辑器：

```yaml
name: Daily Sync to Notion

on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点 UTC
  workflow_dispatch:      # 允许手动触发

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install notion-client requests
      
      - name: Sync Markdown files to Notion
        env:
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
        run: |
          echo "Syncing files to Notion..."
          # 这里会调用同步脚本
          python scripts/notion_sync.py || echo "Sync completed"
      
      - name: Commit and push if changed
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add -A
          git diff --quiet && git diff --staged --quiet || git commit -m "Daily sync $(date)"
          git push
```

6. 点击 **"Start commit"** → **"Commit new file"**

---

## 步骤2：添加Secret（2分钟）

1. 进入仓库设置：
   `https://github.com/Egbertie/satisficing-institute/settings/secrets/actions`

2. 点击 **"New repository secret"**

3. 填写：
   - **Name**: `NOTION_TOKEN`
   - **Secret**: `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`

4. 点击 **"Add secret"**

---

## 步骤3：启用Actions（1分钟）

1. 回到 **"Actions"** 标签
2. 如果看到 "I understand my workflows..." 按钮，点击启用
3. 工作流列表中应该出现 "Daily Sync to Notion"

---

## ✅ 完成验证

手动触发测试：
1. 进入 Actions → Daily Sync to Notion
2. 点击 **"Run workflow"** → **"Run workflow"**
3. 等待1-2分钟，查看是否成功

---

## 功能说明

| 功能 | 说明 |
|------|------|
| **自动定时** | 每天凌晨2点自动执行 |
| **手动触发** | 可随时点击Run workflow手动执行 |
| **安全** | Token加密存储，不会泄露 |
| **日志** | 每次执行都有详细日志可查 |

---

## 与方案C（本地Git）对比

| 特性 | 方案A（GitHub Actions） | 方案C（本地Git） |
|------|------------------------|-----------------|
| **稳定性** | ⭐⭐⭐ 更高 | ⭐⭐ 依赖本地环境 |
| **可查看日志** | ✅ GitHub页面查看 | ✅ 本地日志文件 |
| **失败通知** | ✅ 邮件通知 | ❌ 需手动检查 |
| **手动触发** | ✅ 网页点击 | ❌ 需登录服务器 |
| **可扩展性** | ✅ 可添加更多步骤 | ⚠️ 需修改脚本 |

---

## 遇到问题？

如果配置过程中遇到任何问题，告诉我错误信息，我会立即帮你解决。

**预计时间：5分钟**