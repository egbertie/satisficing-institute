---
name: info-collection-quality
version: 1.0.0
description: |
  信息采集与质量控制体系 - 确保信息准确、完整、可追溯
  采集→清洗→验证→存储全流程管控
author: Satisficing Institute
tags:
  - information-collection
  - quality-control
  - data-management
  - verification
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3"]
---

# 📡 信息采集与质量控制体系 V1.0.0

## 🎯 功能概述

### 质量控制流程
1. **采集** - 多源信息获取
2. **清洗** - 去重、格式化
3. **验证** - 事实核查
4. **存储** - 结构化归档

### 核心功能
- 信息来源分级
- 自动事实核查
- 质量评分系统

## 🚀 使用方法

### 信息质量评估
```
用户: 评估这条信息的质量
      来源: 行业报告 / 数据: 2025年市场规模100亿

AI: 📊 信息质量评估
   
   来源评级: 🟡 二级来源(行业报告)
   可信度: 75%
   
   验证结果:
   ├─ 数据一致性: ✅ 与其他报告相符
   ├─ 来源可追溯: ✅ 报告有明确出处
   └─ 时效性: ⚠️ 数据为2025年预测
   
   使用建议:
   └─ 引用时标注"据XX报告显示"
```

---

*版本: v1.0.0 | 创建: 2026-03-15*
