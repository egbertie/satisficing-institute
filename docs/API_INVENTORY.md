# 满意解研究所 · API 清单 V1.0

**更新日期**: 2026-03-10  
**维护人**: Egbertie + Kimi Claw  
**用途**: 硬科技合伙人匹配决策系统

---

## API 总览

| 序号 | API | 用途 | 状态 | 免费额度 | 使用策略 |
|------|-----|------|------|---------|---------|
| 1 | **Kimi API** | 主要对话/中文处理 | ✅ 活跃 | Allegretto 限额内 | 主要对话接口 |
| 2 | **GitHub Models** | GPT-4o/DeepSeek | ✅ 活跃 | 50次/天 (GPT-4o) | 复杂编程任务 |
| 3 | **Jina AI** | 网页提取/搜索 | ✅ 活跃 | 100万 tokens | 网页内容提取 |
| 4 | **Perplexity** | AI 搜索 | ✅ 已配置 | 约 300次/月 | 实时信息搜索 |
| 5 | **Claude (Anthropic)** | 复杂推理 | 🟡 备用（403地区限制） | 需付费额度 | 备用推理引擎 |
| | | | | | **注释**: 使用GitHub Models GPT-4o替代，今晚/明天解决403 |
| 6 | **Notion** | 知识库管理 | ✅ 活跃 | 无限制 | 文档同步 |
| 7 | **Figma** | 设计协作 | 🔗 链接已存 | 免费版 | 组织架构图 |

---

## 详细配置

### 1. Kimi API
```yaml
Provider: 月之暗面
API Key: sk-kimi-Sx52rk... (内置)
Base URL: https://api.kimi.com/coding
状态: 使用中 (当前对话)
用途: 
  - 主要对话接口
  - 中文处理
  - 代码生成
```

### 2. GitHub Models
```yaml
Provider: Microsoft/GitHub
API Key: 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
Base URL: https://models.github.ai/inference
免费额度:
  - GPT-4o: 10 RPM, 50 RPD
  - DeepSeek-R1: 15 RPM, 150 RPD
验证状态: ✅ 已验证并活跃使用中 (2026-03-10)
测试响应: "你好！有什么可以帮助你的吗？"
用途:
  - Claude替代方案（403问题）
  - 复杂编程任务
  - GPT-4o主力推理
```

### 3. Jina AI
```yaml
Provider: Jina AI
API Key: jina_448e2c72ff414835b8b35eebf13d7840C9XK6Je9WwRIikSJVfRM44tYoZD8
免费额度: 100万 tokens
验证状态: ✅ 已验证并活跃使用中 (2026-03-10)
验证测试:
  - r.jina.ai/http://github.com - 成功提取GitHub首页
  - s.jina.ai/OpenClaw - 成功搜索
用途:
  - r.jina.ai/{URL} - 网页提取
  - s.jina.ai/{query} - 网页搜索
  - g.jina.ai/{fact} - 事实核查
```

### 4. Perplexity API
```yaml
Provider: Perplexity AI
API Key: sk-ofRU1F9plRRXyeL6qN5NH3dNXEXp7JaNunA2IEXuSwhY73dd
Base URL: https://api.perplexity.ai
免费额度: Pro 用户 $5/月 约 300次搜索
状态: ✅ 已配置并验证可用
验证日期: 2026-03-10
模型: sonar, sonar-pro, sonar-reasoning
用途:
  - AI实时搜索
  - 市场研究
  - 竞品分析
```

### 5. Claude API (Anthropic)
```yaml
Provider: Anthropic
API Key: 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
状态: 🟡 备用（403地区限制）
用途: 复杂推理/长文本处理 (备用)
替代方案: 使用GitHub Models GPT-4o替代，今晚/明天解决403问题
```

### 6. Notion API
```yaml
Provider: Notion
API Key: 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
工作空间: 满意解研究所
验证状态: ✅ 已验证 (2026-03-10)
用途: 
  - 知识库双备份
  - 文档同步
  - 协作空间
```

### 7. GitHub (备用 Token)
```yaml
Token: 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
状态: 已保存
用途: 备用/其他仓库访问
```

### 8. Figma
```yaml
URL: https://www.figma.com/board/x6Bk2j76Au9ZKH7RlfPM2k/满意解组织架构V2.2
用途: 组织架构图可视化
```

---

## 配置文件位置

```
/root/.openclaw/workspace/.env
```

### 环境变量加载方式

```bash
# 手动加载
export $(cat /root/.openclaw/workspace/.env | xargs)

# 在 Python 中使用
from dotenv import load_dotenv
load_dotenv('/root/.openclaw/workspace/.env')
```

---

## 使用优先级

### 对话/中文处理
1. Kimi API (主要)
2. GitHub Models GPT-4o (复杂任务)
3. Claude (备用)

### 信息搜索
1. Perplexity (AI搜索)
2. Jina AI (网页提取)
3. Kimi Search (内置)

### 知识管理
1. Notion (主要)
2. GitHub (版本控制)
3. 飞书 (备用)

---

## 成本控制策略

| 优先级 | API | 策略 |
|-------|-----|------|
| P0 | Kimi API | 限额内使用，超额预警 |
| P1 | GitHub Models | 免费额度优先 |
| P2 | Perplexity | $5/月额度规划 |
| P3 | Claude | 按需使用 |

---

## 更新日志

| 日期 | 操作 | 操作人 |
|------|------|--------|
| 2026-03-10 | 创建清单，配置所有 API | Kimi Claw |
| 2026-03-10 | 验证 GitHub Models | Kimi Claw |
| 2026-03-10 | 验证 Jina AI | Kimi Claw |
| 2026-03-10 | 验证 Notion | Kimi Claw |

---

## 待办

- [ ] Perplexity 额度监控
- [ ] Claude 额度充值
- [ ] Notion 同步完成验证
- [ ] GitHub 远程仓库配置

---

**文档版本**: V1.0  
**下次更新**: 有新增 API 或配置变更时
