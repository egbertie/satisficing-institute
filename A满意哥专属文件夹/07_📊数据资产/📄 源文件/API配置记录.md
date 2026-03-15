# API配置记录

> 记录各种API服务的配置信息和使用说明
> 最后更新：2026-03-13

---

## GitHub Models - GPT-4o 配置

### 基本信息

| 项目 | 内容 |
|------|------|
| **服务名称** | GitHub Models |
| **提供商** | GitHub (Microsoft Azure) |
| **模型** | GPT-4o / GPT-4o-mini |
| **配置日期** | 2026-03-13 |
| **任务ID** | TODO-001 |

### 申请流程

#### 1. 访问GitHub Models市场
- **URL**: https://github.com/marketplace/models
- 点击 "Get early access" 申请入口
- 填写申请表单并提交
- **审核时间**: 通常3-5个工作日

#### 2. 创建GitHub Token

访问 https://github.com/settings/tokens

建议使用 **Fine-grained tokens**（最低权限）：

| 配置项 | 建议值 |
|--------|--------|
| Token name | `GitHub Models` |
| Expiration | 90天或1年 |
| Repository access | Public Repositories (read-only) |

#### 3. API配置参数

| 参数 | 值 |
|------|-----|
| **API Base URL** | `https://models.inference.ai.azure.com` |
| **API Key** | 你的GitHub Token |
| **模型名称** | `gpt-4o` 或 `gpt-4o-mini` |

### 使用限制

| 限制项 | GPT-4o | GPT-4o-mini |
|--------|--------|-------------|
| 请求数/分钟 | ≤10 | ≤20 |
| 请求数/天 | ≤50 | ≤150 |
| 并发数 | 2 | 2 |
| 输入Token | 8,000 | 8,000 |
| 输出Token | 4,000 | 4,000 |

### 代码示例

#### Python

```python
import requests

# API配置
API_URL = "https://models.inference.ai.azure.com/chat/completions"
API_KEY = "your_github_token_here"  # 替换为你的GitHub Token
MODEL = "gpt-4o"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": "你好，请介绍一下自己。"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

response = requests.post(API_URL, headers=headers, json=data)
result = response.json()
print(result['choices'][0]['message']['content'])
```

#### JavaScript/Node.js

```javascript
const axios = require('axios');

const API_URL = 'https://models.inference.ai.azure.com/chat/completions';
const API_KEY = 'your_github_token_here';  // 替换为你的GitHub Token
const MODEL = 'gpt-4o';

async function chat() {
    const response = await axios.post(API_URL, {
        model: MODEL,
        messages: [
            { role: 'system', content: '你是一个有用的助手。' },
            { role: 'user', content: '你好，请介绍一下自己。' }
        ],
        temperature: 0.7,
        max_tokens: 1000
    }, {
        headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json'
        }
    });
    
    console.log(response.data.choices[0].message.content);
}

chat().catch(console.error);
```

#### cURL

```bash
curl -X POST "https://models.inference.ai.azure.com/chat/completions" \
  -H "Authorization: Bearer your_github_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "system", "content": "你是一个有用的助手。"},
      {"role": "user", "content": "你好，请介绍一下自己。"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### 可用模型列表

GitHub Models市场提供以下主要模型：

| 模型 | 描述 |
|------|------|
| `gpt-4o` | OpenAI旗舰多模态模型 |
| `gpt-4o-mini` | GPT-4o轻量版，更快更便宜 |
| `o1-preview` | OpenAI推理模型预览版 |
| `o1-mini` | OpenAI轻量推理模型 |
| `Llama-3.1-405B` | Meta开源大模型 |
| 更多模型 | 访问GitHub Models市场查看 |

### 注意事项

1. **免费额度**: 个人开发者免费使用，有每日调用限制
2. **生产环境**: 建议迁移至Azure付费服务以获得更高配额
3. **Token安全**: 切勿将GitHub Token硬编码在代码中，使用环境变量
4. **迁移路径**: GitHub Models → Azure OpenAI Service 无需修改代码，仅更换API Key

### 测试验证

运行以下命令测试API是否正常工作：

```bash
# 设置环境变量
export GITHUB_TOKEN="your_github_token_here"

# 运行测试脚本（见下方test_github_models.py）
python3 test_github_models.py
```

### 相关文件

- 测试脚本：`/root/.openclaw/workspace/scripts/test_github_models.py`

---

## 更新记录

| 日期 | 更新内容 | 更新人 |
|------|----------|--------|
| 2026-03-13 | 创建GitHub Models配置文档 | AI助手 |

