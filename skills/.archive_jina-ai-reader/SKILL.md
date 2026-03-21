---
name: jina-ai-reader
description: 使用Jina AI Reader免费提取网页内容并总结。1000次/天免费额度。
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["JINA_API_KEY"] },
        "emoji": "📄",
      },
  }

# Jina AI Reader Skill

免费提取网页正文内容，自动转换为Markdown格式。

## 使用前提

需要设置环境变量：
```bash
export JINA_API_KEY=jina_xxxxxxxx
```

## 免费额度

- **1000次/天**（非常够用！）
- 完全免费
- 无需付费升级

## 功能

### 1. 网页内容提取
输入URL，自动提取正文内容，去除广告和干扰。

### 2. 自动总结
提取核心内容，生成结构化摘要。

### 3. 多语言支持
支持中英文等多种语言网页。

## 使用场景

- **案例研究员**：快速获取网页资料
- **EEO**：专家文章速读
- **内容总监**：竞品内容分析
- **研究员**：行业报告提取

## 使用方式

```
输入：提取 https://xxx.com 的内容
输出：结构化Markdown内容
```

## 成本控制

- 完全免费
- 1000次/天额度充足
- 批量处理，一次提取多个URL
