# GitHub Models 配置指南

## 快速配置（2分钟）

### 1. 获取GitHub Token
访问 https://github.com/settings/tokens
- 点击 "Generate new token (classic)"
- 勾选权限：至少包含 `read:packages`
- 生成后复制Token

### 2. 配置环境变量
```bash
export GITHUB_TOKEN="你的GitHub Token"
```

### 3. 测试连接
```bash
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://models.github.com/models
```

### 4. 可用模型（免费）
- `gpt-4o` - 主要使用（能力强，免费额度充足）
- `gpt-4o-mini` - 轻量任务
- `phi-4` - 微软模型
- `mistral-large` - Mistral模型

### 5. 在OpenClaw中使用
在需要调用GitHub Models的地方，使用：
```
model: github/gpt-4o
```

---

**当前状态**：Token余量4%，已禁用14个非必要Cron。
**建议**：立即配置GitHub Token，然后启动V1.1百科全书生成。
