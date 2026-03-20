---
name: data-quality-auditor
version: 1.0.0
description: |
  数据质量审计器 - 自动化数据质量检查和报告：
  1. 全局考虑：覆盖完整性、一致性、准确性、及时性
  2. 系统考虑：扫描→检查→评分→报告→建议闭环
  3. 迭代机制：根据问题分布优化检查规则
  4. Skill化：标准接口，可扩展新检查项
  5. 流程自动化：自动执行质量审计
author: Satisficing Institute
tags:
  - data-quality
  - audit
  - validation
  - monitoring
requires:
  - model: "kimi-coding/k2p5"
  - cron: true
---

# 数据质量审计器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 检查维度

| 维度 | 检查项 | 示例 |
|------|--------|------|
| **完整性** | 空值/缺失 | NULL检查 |
| **一致性** | 格式/标准 | 日期格式统一 |
| **准确性** | 异常值/范围 | 数值范围检查 |
| **及时性** | 更新频率 | 数据新鲜度 |
| **唯一性** | 重复记录 | 主键重复 |

### 1.2 问题分级

| 级别 | 说明 |
|------|------|
| 🔴 Critical | 影响业务决策 |
| 🟡 Warning | 需要关注 |
| 🟢 OK | 质量良好 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 审计流程

```
数据源连接 → 扫描表结构 → 执行检查 → 评分 → 生成报告 → 提出建议
```

---

## 标准3: 迭代机制（Iterative）

根据问题分布优化检查规则和阈值。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
data-quality-auditor/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── audit_table.py          # 表审计
│   ├── check_completeness.py   # 完整性检查
│   ├── check_consistency.py    # 一致性检查
│   └── generate_report.py      # 报告生成
└── rules/
    └── quality_rules.yaml
```

### 4.2 调用接口

```python
from data_quality_auditor import QualityAuditor

auditor = QualityAuditor()

# 审计数据表
report = auditor.audit(table="users")
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 Cron配置

```bash
# 每日数据质量审计
0 8 * * * cd /workspace && openclaw skill run data-quality-auditor audit --table users
```

### 5.2 使用方法

```bash
# 审计数据表
openclaw skill run data-quality-auditor audit --table users

# 生成质量报告
openclaw skill run data-quality-auditor report --table users
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 5大质量维度覆盖 | ✅ |
| **2. 系统** | 扫描→检查→报告闭环 | ✅ |
| **3. 迭代** | 规则优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动审计+报告 | ✅ |

---

*版本: v1.0.0*  
*来源: data-analyst散落机制提取*  
*创建: 2026-03-20*
