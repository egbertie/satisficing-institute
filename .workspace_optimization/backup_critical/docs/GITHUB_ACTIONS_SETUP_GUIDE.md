# GitHub Actions 配置指引

## 步骤1：创建GitHub Personal Access Token

1. 登录 https://github.com
2. 点击右上角头像 → Settings
3. 左侧菜单最下方 → Developer settings
4. 左侧 → Personal access tokens → Tokens (classic)
5. 点击 Generate new token (classic)
6. 填写信息：
   - Note: `满意解研究所-Actions部署`
   - Expiration: `No expiration` (或自定义)
   - 勾选权限：
     - ✅ `repo` (完整仓库访问)
     - ✅ `workflow` (Actions工作流)
     - ✅ `write:packages` (如果需要)

7. 点击 Generate token
8. **复制生成的Token**（只显示一次！）

## 步骤2：将Token提供给我

将Token发送给我，我会立即配置到环境变量中：
```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

## 步骤3：我将自动完成的工作

收到Token后，我会立即：

1. **创建工作流文件**：`.github/workflows/` 目录下
2. **配置自动化任务**：
   - 每日自动备份所有文档到GitHub Release
   - 自动同步Notion（每日02:00执行）
   - Markdown文件自动检查（链接、格式）
   - 自动通知（同步成功/失败）

3. **配置Secrets**：
   - NOTION_TOKEN
   - 其他API Keys

## 步骤4：验证配置

配置完成后，你可以在GitHub仓库页面：
1. 点击 Actions 标签
2. 查看工作流运行状态
3. 检查首次运行结果

## 安全配置建议

⚠️ **重要**：
- Token不要分享给第三方
- 定期轮换Token（建议每3个月）
- 仅授予最小必要权限
- 在GitHub Secrets中存储，不硬编码

## 预计完成时间

- 你提供Token：1分钟
- 我完成配置：5分钟
- **总计：10分钟内完成GitHub Actions配置**

---
*准备就绪后立即发送Token，我会立即处理*
