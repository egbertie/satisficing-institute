# Skill: Conversation Researcher - 对话研究专家

**Level 5** | 手动触发 + 多源深度研究 + 对抗验证 + 专业报告

---

## 1. Purpose / 技能用途

对特定主题进行**多源深度研究**，生成包含**摘要、发现、引用、建议**的专业研究报告。

- 用户提出研究主题/问题/关键词
- 自动进行多源搜索、信息整合、深度分析
- 输出结构化研究报告，标注局限性与来源偏见
- 进行对抗验证（多源交叉验证）

---

## 2. 7-Standard Compliance

| 标准 | 状态 | 说明 |
|------|------|------|
| S1 | ✅ | 接受研究主题/问题/关键词输入 |
| S2 | ✅ | 多源搜索→信息整合→深度分析 |
| S3 | ✅ | 输出研究报告（摘要→发现→引用→建议） |
| S4 | ✅ | 手动触发（/research 命令） |
| S5 | ✅ | 引用准确性检查（来源可追溯） |
| S6 | ✅ | 局限标注（时效性/来源偏见） |
| S7 | ✅ | 对抗验证（多源交叉验证≥3源） |

---

## 3. Usage / 使用方式

### 3.1 触发命令

```bash
# 直接执行研究
python3 skills/conversation-researcher/scripts/research-runner.py "研究主题"

# 或通过 RESEARCH_TOPIC 环境变量
export RESEARCH_TOPIC="人工智能在医疗领域的应用"
python3 skills/conversation-researcher/scripts/research-runner.py
```

### 3.2 输入格式

支持以下形式的研究请求：
- **主题**："新能源汽车电池技术"
- **问题**："为什么固态电池被认为是下一代电池技术？"
- **关键词**：["固态电池", "能量密度", "安全性", "量产时间"]

### 3.3 输出位置

```
output/
├── research-{timestamp}/
│   ├── report.md          # 完整研究报告
│   ├── summary.md         # 执行摘要
│   ├── sources.json       # 引用来源详情
│   ├── validation.md      # 对抗验证结果
│   └── limitations.md     # 局限性分析
```

---

## 4. Architecture / 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Conversation Researcher                    │
├─────────────────────────────────────────────────────────────┤
│  Input Layer (S1)                                            │
│  ├── 研究主题/问题/关键词解析                                   │
│  ├── 研究范围界定（深度/广度/时效）                             │
│  └── 搜索策略生成                                             │
├─────────────────────────────────────────────────────────────┤
│  Research Layer (S2)                                         │
│  ├── Multi-Source Search (≥3 sources)                        │
│  │   ├── Web Search (kimi_search)                            │
│  │   ├── News/Blogs (时效性)                                  │
│  │   └── Academic/Technical (深度性)                          │
│  ├── Information Integration                                  │
│  │   ├── 去重与关联                                           │
│  │   ├── 可信度评分                                           │
│  │   └── 时间线梳理                                           │
│  └── Deep Analysis                                            │
│      ├── 主题提取                                             │
│      ├── 观点聚类                                             │
│      ├── 争议点识别                                           │
│      └── 趋势判断                                             │
├─────────────────────────────────────────────────────────────┤
│  Validation Layer (S5, S6, S7)                               │
│  ├── Source Accuracy Check (S5)                              │
│  │   ├── URL有效性验证                                        │
│  │   ├── 来源权威性评估                                       │
│  │   └── 引用可追溯性                                         │
│  ├── Limitation Annotation (S6)                              │
│  │   ├── 时效性标注（信息时间戳）                              │
│  │   ├── 来源偏见分析                                         │
│  │   └── 信息完整性评估                                       │
│  └── Adversarial Validation (S7)                             │
│      ├── 多源交叉验证 (≥3源)                                  │
│      ├── 矛盾点识别                                           │
│      └── 共识度评分                                           │
├─────────────────────────────────────────────────────────────┤
│  Output Layer (S3)                                           │
│  ├── Executive Summary                                        │
│  ├── Key Findings                                             │
│  ├── Source Citations                                         │
│  └── Actionable Recommendations                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Configuration / 配置说明

### 5.1 搜索配置

```json
{
  "search": {
    "min_sources": 3,
    "max_sources": 10,
    "freshness": "py",        // pd: 24h, pw: 周, pm: 月, py: 年
    "include_content": true,   // 是否获取全文
    "timeout_ms": 30000
  }
}
```

### 5.2 验证配置

```json
{
  "validation": {
    "min_cross_validation": 3,     // 最少交叉验证源数
    "consensus_threshold": 0.6,    // 共识度阈值
    "authority_weights": {          // 来源权威性权重
      "academic": 1.0,
      "official": 0.9,
      "major_media": 0.8,
      "blog": 0.5,
      "unknown": 0.3
    }
  }
}
```

---

## 6. Report Structure / 报告结构

```markdown
# 研究报告: [主题]

**研究时间**: YYYY-MM-DD HH:MM
**研究范围**: [广度/深度/时效说明]
**共识度评分**: X% (基于N个来源)

---

## 执行摘要 (Executive Summary)

[3-5句话概括核心发现]

---

## 核心发现 (Key Findings)

### 1. [发现1标题]
**描述**: ...
**证据**: [来源引用]
**可信度**: ★★★★☆

### 2. [发现2标题]
...

---

## 来源引用 (Sources)

| # | 来源 | 标题 | 日期 | 权威性 | 状态 |
|---|------|------|------|--------|------|
| 1 | [URL] | ... | ... | ★★★★☆ | ✅已验证 |

---

## 建议 (Recommendations)

1. [可执行建议1]
2. [可执行建议2]
...

---

## 局限性与注意事项 (Limitations)

### 时效性
- [信息1]: [时间戳] [备注]

### 来源偏见
- [来源1]: [潜在偏见分析]

### 信息完整性
- [缺失信息说明]

---

## 对抗验证结果 (Validation)

### 交叉验证矩阵
| 观点 | 源1 | 源2 | 源3 | 共识度 |
|------|-----|-----|-----|--------|
| ...  | ✅  | ✅  | ⚠️  | 67%   |

### 矛盾点
- [矛盾描述]: [涉及来源]

---

*报告生成: conversation-researcher v2.0*
*验证状态: S5✅ S6✅ S7✅*
```

---

## 7. Manual Trigger / 手动触发

### 7.1 命令行触发

```bash
cd /root/.openclaw/workspace
python3 skills/conversation-researcher/scripts/research-runner.py "主题"
```

### 7.2 环境变量触发

```bash
export RESEARCH_TOPIC="主题"
export RESEARCH_DEPTH="deep"  # shallow/normal/deep
export RESEARCH_FRESHNESS="py" # pd/pw/pm/py
python3 skills/conversation-researcher/scripts/research-runner.py
```

---

## 8. Quality Checklist / 质量检查表

- [ ] S1: 输入解析成功
- [ ] S2: 至少3个不同来源
- [ ] S3: 报告结构完整
- [ ] S4: 支持手动触发
- [ ] S5: 所有引用可追溯
- [ ] S6: 局限性已标注
- [ ] S7: 多源交叉验证完成

---

## 9. Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0 | 2026-03-21 | 提升至5标准，完善7-S标准 |
| 1.0 | 2026-03-20 | 初始版本，基础框架 |

---

## 10. Related / 相关资源

- 依赖工具: `kimi_search`, `kimi_fetch`
- 输出目录: `skills/conversation-researcher/output/`
- 配置目录: `skills/conversation-researcher/config/`
