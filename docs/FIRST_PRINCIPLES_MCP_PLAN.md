# 第一性MCP自建方案：搜索即数据

**核心原则**: 不依赖外部MCP，用搜索+自动化自建数据管道
**成本**: 接近零（只用免费API和开源工具）
**优势**: 可控、可定制、无订阅费

---

## 🎯 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    数据需求层                              │
│  (合伙人背景/行业数据/专利/新闻/政策/专家)                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    搜索编排层 (n8n)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ 网页搜索  │ │ 学术搜索  │ │ 专利搜索  │ │ 新闻搜索  │    │
│  │ brave    │ │ scholar  │ │ google   │ │ rss+搜索  │    │
│  │ tavily   │ │ semantic │ │ patents  │ │ 聚合     │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    数据存储层 (DuckDB)                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐           │
│  │ 候选人_raw  │ │ 行业数据    │ │ 专家库      │           │
│  │ 专利数据    │ │ 新闻存档    │ │ 政策库      │           │
│  └────────────┘ └────────────┘ └────────────┘           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    能力输出层 (Skill)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ data-    │ │ patent-  │ │ company- │ │ research- │    │
│  │ analyst  │ │ assistant│ │ search   │ │ assistant│    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 第一阶段：搜索能力强化（Week 1）

### 1.1 多搜索引擎组合策略

**已有的搜索skill：**
- brave-search (免费API)
- tavily (免费额度)
- exa-web-search-free (免费)
- multi-search-engine (多引擎聚合)

**优化方案：**
```javascript
// n8n工作流：智能搜索路由
function routeSearch(query, type) {
  switch(type) {
    case '学术': return 'semantic-scholar';
    case '专利': return 'google-patents';
    case '新闻': return 'brave-news';
    case '公司': return 'brave + 天眼查搜索';
    default: return 'multi-engine';
  }
}
```

### 1.2 自建搜索聚合MCP

**创建 unified-search skill：**
```bash
skills/unified-search/
├── _meta.json
├── SKILL.md
├── search-router.js     # 智能路由
├── brave-client.js      # Brave API封装
├── tavily-client.js     # Tavily API封装
├── scholar-client.js    # Google Scholar封装
└── cache-manager.js     # 结果缓存（降本）
```

**核心功能：**
- 输入查询 → 自动选择最佳搜索引擎
- 结果聚合 → 去重、排序、摘要
- 缓存机制 → 相同查询24小时内直接返回缓存
- 成本控制 → 优先使用免费API

---

## 📦 第二阶段：数据管道搭建（Week 2）

### 2.1 n8n自动化工作流

**工作流1：候选人背景自动调查**
```
触发：Notion新增候选人
  ↓
并行搜索：
  - 公司信息（天眼查/企查查公开页）
  - 专利查询（Google Patents）
  - 学术成果（Google Scholar）
  - 新闻提及（Brave News）
  ↓
数据清洗 → DuckDB存储
  ↓
生成调查报告 → Notion更新
```

**工作流2：行业监控日报**
```
触发：每日9:00
  ↓
搜索：
  - "硬科技投资" + 今日
  - "政府补贴" + "初创企业"
  - "合伙人" + "融资"
  ↓
AI摘要 → 飞书推送
```

**工作流3：专家动态跟踪**
```
触发：每周一
  ↓
搜索专家名单：
  - 黎红雷最新论文/演讲
  - 罗汉最新研究
  - 谢宝剑最新政策分析
  ↓
生成专家周报 → Notion归档
```

### 2.2 DuckDB数据模型优化

**新增表：search_cache（搜索结果缓存）**
```sql
CREATE TABLE search_cache (
    id VARCHAR PRIMARY KEY,
    query VARCHAR NOT NULL,
    source VARCHAR, -- brave/tavily/scholar/patents
    results JSON, -- 完整结果
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- 24小时后过期
    hit_count INTEGER DEFAULT 1 -- 命中次数
);

-- 索引加速
CREATE INDEX idx_query ON search_cache(query);
CREATE INDEX idx_expires ON search_cache(expires_at);
```

**新增表：knowledge_graph（知识图谱）**
```sql
-- 存储人物、公司、专利、论文的关联关系
CREATE TABLE knowledge_graph (
    id VARCHAR PRIMARY KEY,
    entity_type VARCHAR, -- person/company/patent/paper
    entity_name VARCHAR,
    entity_data JSON,
    relationships JSON, -- 关联的其他实体
    last_updated TIMESTAMP
);
```

---

## 📦 第三阶段：能力封装（Week 3）

### 3.1 自建研究助手 Skill

**research-assistant（整合多源数据）**
```markdown
# research-assistant

## 能力
- 综合搜索：一键查询多个数据源
- 报告生成：自动整合搜索结果生成报告
- 竞品分析：输入公司名，自动收集竞品信息
- 专家画像：输入人名，自动收集学术/媒体曝光

## 使用
- research "硬科技投资趋势" → 综合报告
- expert "张三" → 人物画像
- company "硬科技初创A" → 公司调查报告
```

### 3.2 数据可视化看板

**dashboard enhancement：**
- 实时显示今日搜索次数、成本
- 候选人调查进度看板
- 行业热点词云
- 专家动态时间线

---

## 💰 成本控制策略

| 策略 | 效果 | 实施方式 |
|------|------|----------|
| **缓存优先** | 降本80% | DuckDB缓存24小时 |
| **免费API轮转** | 零成本 | brave + tavily + exa轮换 |
| **批量查询** | 降本50% | n8n批量处理而非实时 |
| **本地存储** | 零存储费 | DuckDB本地，不上云 |

**预估月成本：**
- 搜索API：$0-5（免费额度内）
- 存储：$0（本地DuckDB）
- n8n：$0（自托管）
- **总计：$0-5/月** vs 付费MCP $50-200/月

---

## 🚀 快速启动清单

### 今天可做（30分钟）
1. [ ] 验证已有搜索skill可用性
2. [ ] 创建 unified-search skill 框架
3. [ ] 配置n8n第一个工作流（候选人背景调查）

### 本周完成
4. [ ] 完成3个核心n8n工作流
5. [ ] 部署DuckDB缓存机制
6. [ ] 测试完整流程

### 下周优化
7. [ ] 创建research-assistant skill
8. [ ] 搭建数据可视化看板
9. [ ] 团队培训

---

## 🎯 预期效果

**对比购买MCP：**
| 维度 | 购买MCP | 自建方案 |
|------|---------|----------|
| 月成本 | $50-200 | $0-5 |
| 数据可控性 | 低（依赖第三方）| 高（本地存储）|
| 定制化 | 低（固定功能）| 高（按需定制）|
| 扩展性 | 受限 | 无限（自己开发）|
| 学习成本 | 低 | 中（需配置n8n）|

**核心优势：**
- 数据沉淀：所有搜索结果本地存储，形成专属数据库
- 精准定制：只获取我们需要的数据（合伙人相关）
- 零订阅费：一次搭建，长期免费使用

---

## ❓ 需要你确认

1. **优先级**：先做哪个工作流？
   - A. 候选人背景自动调查
   - B. 行业监控日报
   - C. 专家动态跟踪

2. **数据源**：最急需哪个数据源？
   - A. 专利数据（Google Patents）
   - B. 公司信息（天眼查类）
   - C. 学术成果（Google Scholar）
   - D. 新闻资讯

3. **API配置**：能否提供？
   - Brave API Key（免费申请）
   - Tavily API Key（免费额度）

**确认后立即开始Phase 1！** 🚀
