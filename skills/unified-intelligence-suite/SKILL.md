---
name: unified-intelligence-suite
description: Unified information collection and intelligence suite. Replaces info-cleaner, info-collection-orchestrator, info-collection-workflow, info-distribution-router, info-quality-guardian, multi-source-search, smart-web-fetch, smart-web-scraper with single integrated interface. Use for: web scraping, data aggregation, content curation, quality filtering, information routing.
triggers: ["scrape", "crawl", "collect", "aggregate", "intelligence", "信息采集", "爬虫"]
---

# Unified Intelligence Suite

**统一信息采集与情报套件** - 整合信息收集、处理、分发能力。

> 🎯 替代: info-cleaner + info-collection-orchestrator + info-collection-workflow + info-distribution-router + info-quality-guardian + multi-source-search + smart-web-fetch + smart-web-scraper

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **网络采集** | 网页抓取、API采集、RSS订阅 |
| **多源聚合** | 搜索引擎、数据库、文件整合 |
| **质量过滤** | 去重、降噪、可信度评估 |
| **智能分发** | 路由规则、优先级、渠道选择 |
| **信息清洗** | 格式标准化、实体提取、分类标签 |

---

## 快速开始

```bash
# 配置采集任务
intel-suite collect --source "news.example.com" --schedule hourly --filter "AI|人工智能"

# 多源搜索聚合
intel-suite search --query "硬科技投资" --sources web,news,academic --aggregate

# 质量评估
intel-suite quality --input articles.json --score relevance,authority,freshness

# 信息路由
intel-suite route --input feed.json --rules "priority>8:urgent,tech:tech-channel"

# 清洗数据
intel-suite clean --input raw_data.json --dedup --normalize --output clean.json
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| info-cleaner | `intel-suite clean` |
| info-collection-orchestrator | `intel-suite collect` |
| info-collection-workflow | `intel-suite workflow` |
| info-distribution-router | `intel-suite route` |
| info-quality-guardian | `intel-suite quality` |
| multi-source-search | `intel-suite search` |
| smart-web-fetch | `intel-suite fetch` |
| smart-web-scraper | `intel-suite scrape` |

---

**自建替代计数**: +8
