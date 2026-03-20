# Skill整合优化方案 V1.0
## 第一性原理：从104个到12个核心套件

**核心原则**: 
- 一个功能只保留一个最优实现
- 特色功能独立保留
- 接口统一，内部可替换
- 全自建，可控可迭代

---

## 🎯 第一性分析

### Skill的本质
```
Skill = 输入 → 处理 → 输出
      = API封装 + 业务逻辑 + 输出格式化
```

### 我们的问题
| 问题 | 现状 | 目标 |
|------|------|------|
| 重复造轮子 | 6个搜索skill | 1个统一搜索 |
| 功能碎片化 | 6个飞书skill | 1个飞书套件 |
| 接口不统一 | 每个skill语法不同 | 统一调用方式 |
| 维护困难 | 104个skill | 12个核心套件 |

---

## 📦 整合方案：12个核心套件

### 1. unified-search（统一搜索）
**整合**: brave-search + tavily + firecrawl + multi-search + exa-web-search

**核心能力**:
- 智能路由：根据查询类型自动选择最佳引擎
- 结果聚合：多引擎结果去重、排序、摘要
- 本地缓存：DuckDB缓存，降本80%
- 统一接口：不管什么引擎，调用方式一样

**保留特色**:
- brave：速度快
- tavily：AI优化结果
- firecrawl：深度爬取
- exa：语义搜索

**实现方式**:
```javascript
// 统一接口
search({
  query: "硬科技投资趋势",
  type: "news",      // news/academic/patent/general
  engines: ["brave", "tavily"],  // 可选指定
  cache: true        // 默认启用缓存
})
```

---

### 2. data-suite（数据分析套件）
**整合**: data-analyst + chart-generator + duckdb-cli + automate-excel + csvtoexcel

**核心能力**:
- SQL查询（DuckDB）
- 数据可视化（图表生成）
- Excel/CSV处理
- 数据清洗转换

**统一接口**:
```javascript
analyze({
  source: "duckdb|excel|csv|notion",
  query: "SELECT * FROM candidates WHERE industry='硬科技'",
  visualize: "bar|line|pie",  // 可选
  output: "chart|table|report"
})
```

---

### 3. doc-suite（文档套件）
**整合**: markdown-converter + markdown-exporter + pdf-generator

**核心能力**:
- 格式转换（MD ↔ PDF ↔ Word ↔ PPT）
- 批量处理
- 模板渲染

**排除**: 飞书/Notion相关（单独成套件）

---

### 4. feishu-suite（飞书套件）
**整合**: feishu-messaging + doc-manager + docx-powerwrite + file-sender + send-file

**核心能力**:
- 消息发送（文本/图片/文件）
- 文档创建/编辑
- 多维表格操作
- 文件上传下载

**统一接口**:
```javascript
feishu({
  action: "send|create_doc|update_bitable|upload",
  target: "user_id|chat_id",
  content: {...}
})
```

---

### 5. notion-suite（Notion套件）
**整合**: notion + notion-api + notion-api-skill

**核心能力**:
- 数据库查询
- 页面创建/更新
- 块操作

---

### 6. meeting-suite（会议套件）
**整合**: ai-meeting-notes + meeting-to-action + effective-meeting

**核心能力**:
- 会议记录转录
- 自动生成摘要
- 提取行动项（责任人+截止日期）
- 会议纪要到Notion/飞书

**工作流**:
```
会议录音 → 转录 → AI摘要 → 行动项提取 → 同步到任务管理
```

---

### 7. copywriting-suite（文案套件）
**整合**: copywriting + copywriting-zh-pro + auto-redbook-skills

**核心能力**:
- 中英双语文案
- 小红书/公众号/朋友圈模板
- AIDA/PAS/FAB框架
- 标题公式100个

**特色保留**:
- 小红书emoji生成
- 中文语境优化
- 多平台适配

---

### 8. workflow-suite（工作流套件）
**整合**: n8n-workflow + agentic-workflow + cron-scheduling + info-collection

**核心能力**:
- n8n工作流设计
- 定时任务管理
- 信息自动采集
- 多步骤自动化

---

### 9. research-suite（研究套件）
**整合**: patent-assistant + company-search-kimi + business-model-canvas + swotpal

**核心能力**:
- 专利检索分析
- 公司背景调查
- 商业模式画布
- SWOT分析

**这是满意解研究所的核心！**

---

### 10. decision-suite（决策套件）
**保留独立**: satisficing-partner-decision（核心IP）
**整合**: decision-frameworks + decision-governance

**核心能力**:
- 合伙人评估决策
- 决策框架（AHP、决策树等）
- 决策治理（四层把关）

**这是我们的核心资产，保持独立！**

---

### 11. git-suite（Git套件）
**整合**: git + git-essentials
**独立保留**: github

**核心能力**:
- 本地Git操作
- 分支管理
- 提交规范

---

### 12. media-suite（媒体套件）
**整合**: audio-handler + ffmpeg-video-editor + video-frames

**核心能力**:
- 音频处理
- 视频剪辑
- 帧提取
- 格式转换

---

## 📊 整合效果

| 维度 | 整合前 | 整合后 | 效果 |
|------|--------|--------|------|
| Skill数量 | 104个 | 12个套件 | **-88%** |
| 搜索类 | 6个 | 1个 | 统一入口 |
| 飞书类 | 6个 | 1个 | 统一接口 |
| 会议类 | 4个 | 1个 | 流程整合 |
| 文案类 | 3个 | 1个 | 多语言支持 |
| 维护成本 | 高 | 低 | 可控 |
| 学习成本 | 高 | 低 | 统一语法 |

---

## 🚀 实施路线图

### Phase 1：核心搜索（Week 1）
**目标**: unified-search 套件
- [ ] 分析6个搜索skill的优劣
- [ ] 设计统一接口
- [ ] 实现智能路由
- [ ] DuckDB缓存层

### Phase 2：数据+文档（Week 2）
**目标**: data-suite + doc-suite
- [ ] 整合data-analyst + chart-generator
- [ ] 整合markdown相关skill
- [ ] 统一数据流转接口

### Phase 3：协作工具（Week 3）
**目标**: feishu-suite + notion-suite + meeting-suite
- [ ] 整合飞书6个skill
- [ ] 整合Notion 3个skill
- [ ] 整合会议3个skill

### Phase 4：业务核心（Week 4）
**目标**: research-suite + decision-suite + copywriting-suite
- [ ] 整合研究分析类skill
- [ ] 优化decision-suite（保留独立）
- [ ] 整合文案类skill

### Phase 5：工作流+其他（Week 5）
**目标**: workflow-suite + git-suite + media-suite
- [ ] 整合n8n相关skill
- [ ] 整合git相关skill
- [ ] 整合媒体处理skill

---

## 💡 整合原则

### 保留独立的情况
1. **核心IP**: satisficing-partner-decision（满意解方法论）
2. **外部依赖重**: github（API特殊）
3. **特色鲜明**: auto-redbook-skills（小红书专用）

### 合并规则
1. **功能重叠>70%** → 合并
2. **接口相似** → 统一
3. **数据来源相同** → 合并

### 淘汰规则
1. **30天未使用** → 评估淘汰
2. **被新skill完全替代** → 淘汰
3. **外部服务停止** → 淘汰

---

## 🎯 最终目标

### 12个核心套件
```
unified-search    → 所有搜索需求
data-suite        → 所有数据处理
doc-suite         → 所有文档转换
feishu-suite      → 所有飞书操作
notion-suite      → 所有Notion操作
meeting-suite     → 所有会议处理
copywriting-suite → 所有文案生成
workflow-suite    → 所有自动化
research-suite    → 所有研究分析
decision-suite    → 所有决策支持（核心IP）
git-suite         → 所有版本控制
media-suite       → 所有媒体处理
```

### 使用体验
```javascript
// 以前：需要知道用哪个skill
brave-search "硬科技"
tavily-search "硬科技"

// 以后：统一接口
search "硬科技" --type news

// 以前：飞书操作分散
feishu-messaging --send
doc-manager --create

// 以后：统一接口
feishu --action send
doc-suite --action create
```

---

## ❓ 需要你确认

1. **优先级**：先从哪个套件开始整合？
   - A. unified-search（搜索最常用）
   - B. research-suite（业务核心）
   - C. meeting-suite（马上能用）

2. **保留策略**：以下skill是否保留独立？
   - satisficing-partner-decision → **必须保留**（核心IP）
   - auto-redbook-skills → ？（小红书专用，有特色）
   - github → ？（API特殊，建议保留）

3. **整合深度**：
   - A. 浅整合：只是统一接口，内部还是调用原skill
   - B. 深整合：重写核心逻辑，完全自建

**确认后开始Phase 1！** 🚀
