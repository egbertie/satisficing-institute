---
name: unified-content-suite
description: Unified content generation and curation suite. Replaces ai-social-media-content, news-summary, chart-generator, rss-ai-reader with single integrated interface. Use for: content creation, news aggregation, data visualization, social media automation, RSS curation.
triggers: ["content", "generate", "news", "chart", "social media", "内容生成", "社媒"]
---

# Unified Content Suite

**统一内容生成与策划套件** - 整合内容创作、新闻、图表生成。

> 🎯 替代: ai-social-media-content + news-summary + chart-generator + rss-ai-reader

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **社媒内容** | 多平台内容生成、排期发布 |
| **新闻聚合** | RSS订阅、AI摘要、个性化推荐 |
| **数据可视化** | 图表生成、报表、Dashboard |
| **内容策划** | 选题规划、内容日历、趋势分析 |
| **自动发布** | 定时发布、多平台同步 |

---

## 快速开始

```bash
# 生成社媒内容
content-suite social --platform xiaohongshu --topic "职场效率" --count 5

# 新闻摘要
content-suite news --sources "tech,finance" --summary ai --digest daily

# 图表生成
content-suite chart --data sales.csv --type line --title "销售趋势" --output chart.png

# RSS管理
content-suite rss add --url https://example.com/feed --category tech
content-suite rss digest --period daily --ai-summary

# 内容日历
content-suite calendar --create --month 2024-04 --topics "AI,科技,生活"
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| ai-social-media-content | `content-suite social` |
| news-summary | `content-suite news` |
| chart-generator | `content-suite chart` |
| rss-ai-reader | `content-suite rss` |

---

**自建替代计数**: +4
