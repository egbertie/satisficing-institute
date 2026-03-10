# 满意解研究所 · 信息收集Skill体系全面建设计划

## 一、现状评估结果

### 现有能力（薄弱）
- ✅ Jina AI API - 有配置但无封装
- ✅ Perplexity API - 有配置但无定时任务
- ✅ 基础web_search工具
- ⚠️ 夜间经验萃取框架（待完善）

### 关键缺口（7大缺失）
1. ❌ 统一的网页抓取Skill
2. ❌ 智能搜索编排Skill
3. ❌ 信息去重和清洗Skill
4. ❌ 知识图谱构建Skill
5. ❌ 自动信息监控Skill
6. ❌ 信息可信度评估Skill
7. ❌ 多语言信息处理Skill

---

## 二、完整Skill体系建设方案

### Phase 1: 基础抓取层（3天）

#### Skill 1: 智能网页抓取器 (smart-web-scraper)
**功能**: 统一封装所有网页抓取能力
**核心能力**:
- 支持Jina AI API（已配置）
- 支持本地抓取（requests+beautifulsoup）
- 支持动态页面（selenium备用）
- 自动重试和容错
- 内容提取（正文/标题/作者/时间）
- 图片/文档下载

**输出格式**:
```json
{
  "url": "...",
  "title": "...",
  "content": "...",
  "author": "...",
  "publish_time": "...",
  "images": [...],
  "metadata": {...}
}
```

**文件**: `skills/smart-web-scraper/`

---

#### Skill 2: 多源搜索编排器 (multi-source-search)
**功能**: 整合多个搜索API，统一输出
**支持源**:
- Brave Search（网页搜索）
- Perplexity AI（深度搜索）
- Kimi Search（中文搜索）
- Google Custom Search（备用）

**智能编排**:
- 根据查询类型自动选择最佳源
- 并行查询多个源
- 结果去重和排序
- 来源可信度标记

**输出格式**:
```json
{
  "query": "...",
  "sources_used": ["brave", "perplexity"],
  "results": [
    {
      "title": "...",
      "url": "...",
      "snippet": "...",
      "source": "brave",
      "credibility": "high",
      "timestamp": "..."
    }
  ]
}
```

**文件**: `skills/multi-source-search/`

---

### Phase 2: 信息处理层（3天）

#### Skill 3: 信息清洗与去重器 (info-cleaner)
**功能**: 清洗和去重收集的信息
**核心能力**:
- 文本清洗（去除广告/导航/重复）
- 内容去重（相似度检测）
- 格式标准化
- 编码统一（UTF-8）
- 敏感信息过滤

**去重算法**:
- SimHash
- MinHash
- 向量相似度

**文件**: `skills/info-cleaner/`

---

#### Skill 4: 知识提取引擎 (knowledge-extractor)
**功能**: 从文本中提取结构化知识
**核心能力**:
- 实体识别（人名/机构/地点/时间）
- 关系抽取（A与B的关系）
- 事件提取（谁/何时/何地/做什么）
- 关键词提取
- 主题分类
- 情感分析

**输出格式**:
```json
{
  "entities": [...],
  "relations": [...],
  "events": [...],
  "keywords": [...],
  "topics": [...],
  "sentiment": "positive/negative/neutral"
}
```

**文件**: `skills/knowledge-extractor/`

---

#### Skill 5: 信息可信度评估器 (credibility-assessor)
**功能**: 评估信息来源和内容的可信度
**评估维度**:
- 来源权威性（域名/机构/作者）
- 发布时间（时效性）
- 引用情况（被引用次数）
- 内容一致性（与其他来源对比）
- 语言客观性（主观/客观）

**评分标准**:
- A级（高可信）：权威媒体/学术论文/官方数据
- B级（中可信）：行业媒体/专家博客/报告
- C级（低可信）：自媒体/论坛/未经验证

**文件**: `skills/credibility-assessor/`

---

### Phase 3: 监控与积累层（4天）

#### Skill 6: 自动信息监控器 (auto-info-monitor)
**功能**: 7×24小时监控指定信息源
**监控类型**:
- RSS订阅监控
- 网页变更监控
- 社交媒体监控（Twitter/微博）
- 新闻源监控
- 学术文献监控（arXiv/Google Scholar）

**监控机制**:
- 定时抓取（每30分钟-每24小时）
- 变更检测（diff算法）
- 重要度评估
- 自动摘要
- 即时通知

**输出**:
- 变更报告
- 每日摘要
- 紧急预警

**文件**: `skills/auto-info-monitor/`

---

#### Skill 7: 知识图谱构建器 (knowledge-graph-builder)
**功能**: 将提取的知识构建为图谱
**核心能力**:
- 实体链接（消歧）
- 关系推理
- 图谱可视化（Mermaid/D3.js）
- 图谱查询
- 知识推理

**存储**:
- 图数据库（Neo4j）或
- 嵌入式存储（NetworkX+DuckDB）

**文件**: `skills/knowledge-graph-builder/`

---

#### Skill 8: 多语言处理器 (multilingual-processor)
**功能**: 处理多语言信息
**核心能力**:
- 语言检测
- 机器翻译（中英互译）
- 跨语言搜索
- 多语言摘要
- 文化适应性调整

**支持语言**:
- 中文（简/繁）
- 英文
- 日文
- 韩文
- 德文
- 法文

**文件**: `skills/multilingual-processor/`

---

## 三、实施时间表

### Week 1: 基础层
- Day 1-2: 智能网页抓取器
- Day 3: 多源搜索编排器
- Day 4-5: 测试和优化
- Day 6-7: 集成测试

### Week 2: 处理层
- Day 1-2: 信息清洗与去重器
- Day 3-4: 知识提取引擎
- Day 5: 信息可信度评估器
- Day 6-7: 测试和优化

### Week 3: 监控层
- Day 1-3: 自动信息监控器
- Day 4-5: 知识图谱构建器
- Day 6-7: 多语言处理器

### Week 4: 集成与优化
- Day 1-3: 所有Skill集成
- Day 4-5: 性能优化
- Day 6-7: 全面测试

---

## 四、统一接口设计

所有信息收集Skill统一接口:

```python
# 输入
{
  "task": "scrape|search|monitor|extract",
  "source": "url|query|rss",
  "params": {...},
  "output_format": "json|markdown|html"
}

# 输出
{
  "status": "success|partial|error",
  "data": {...},
  "metadata": {
    "source": "...",
    "timestamp": "...",
    "credibility": "...",
    "processing_time": "..."
  }
}
```

---

## 五、关键技术指标

| 指标 | 目标 |
|------|------|
| 网页抓取成功率 | >95% |
| 搜索响应时间 | <3秒 |
| 信息去重准确率 | >98% |
| 知识提取召回率 | >85% |
| 可信度评估准确率 | >90% |
| 监控延迟 | <30分钟 |
| 多语言支持 | 6种语言 |

---

## 六、立即启动（今晚）

### 今晚任务（3月11日凌晨）
1. ✅ 创建智能网页抓取器框架
2. ✅ 封装Jina AI API
3. ✅ 测试基础抓取功能
4. ⏳ 明早测试多URL批量抓取

### 明日任务（3月11日白天）
1. 完成智能网页抓取器
2. 开始多源搜索编排器
3. 测试搜索整合

---

**立即开始创建第一个Skill：智能网页抓取器！** 🚀
