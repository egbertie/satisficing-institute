# API 配置指南

## 1. GitHub Models API (免费)

### 获取步骤：
1. 登录 GitHub → 右上角头像 → **Settings**
2. 左侧菜单 → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. 点击 **Generate new token (classic)**
4. 填写：
   - **Note**: `GitHub Models API`
   - **Expiration**: 90 days (或更长)
   - **Scopes**: 勾选 `models` (关键！)
5. 点击 **Generate token** → **立即复制保存**（只显示一次！）

### 配置信息：
```bash
export GITHUB_TOKEN="你的token"
export GITHUB_MODELS_BASE_URL="https://models.github.ai/inference"
```

### 支持模型：
- `gpt-4o` (推荐)
- `gpt-4o-mini`
- `deepseek-r1`
- `llama-3.1-405b`
- `phi-4`

### 速率限制：
- GPT-4o: 10次/分钟, 50次/天
- DeepSeek-R1: 15次/分钟, 150次/天

---

## 2. Perplexity API (每月$5免费积分)

### 获取步骤：
1. 访问 https://www.perplexity.ai/settings/api
2. 登录 Perplexity 账号（Pro 用户每月自动获 $5 积分）
3. 绑定信用卡（验证用，不会扣费）
4. 点击 **Generate API Key**
5. 复制保存 Key

### 配置信息：
```bash
export PERPLEXITY_API_KEY="你的key"
export PERPLEXITY_BASE_URL="https://api.perplexity.ai"
```

### 支持模型：
- `sonar` (轻量级搜索)
- `sonar-pro` (高级搜索)
- `sonar-reasoning` (推理增强)

### 免费额度：
- Pro 用户：每月 $5 免费积分
- 约 300 次搜索/月

---

## 3. Jina AI API (免费，无需注册)

### 获取步骤（最简单）：
1. 访问 https://jina.ai/reader
2. 点击 **Get API Key for Free**
3. 无需注册，直接显示 API Key
4. 复制保存

### 配置信息：
```bash
export JINA_API_KEY="你的key"
```

### 功能：
- **Reader API**: `r.jina.ai/https://网址` → 提取网页内容为 Markdown
- **Search API**: `s.jina.ai/搜索词` → AI 搜索
- **Fact Check**: `g.jina.ai/陈述` → 事实核查

### 免费额度：
- 新用户：100万 tokens
- 无 API Key：每分钟 20 次请求
- 有 API Key：每分钟 200 次请求

---

## 一键配置脚本

获取所有 Key 后，运行以下命令配置到环境：

```bash
# 添加到 ~/.bashrc
echo 'export GITHUB_TOKEN="你的github_token"' >> ~/.bashrc
echo 'export PERPLEXITY_API_KEY="你的perplexity_key"' >> ~/.bashrc
echo 'export JINA_API_KEY="你的jina_key"' >> ~/.bashrc

# 立即生效
source ~/.bashrc
```

---

## 验证配置

```bash
# 测试 GitHub Models
curl -X POST "https://models.github.ai/inference/chat/completions" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"你好"}]}'

# 测试 Jina Reader
curl "https://r.jina.ai/https://github.com"

# 测试 Perplexity
curl -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"sonar","messages":[{"role":"user","content":"你好"}]}'
```
