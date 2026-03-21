# Quality Assurance Skill (质量保证审查)

> **标准等级**: 5标准 (全局 | 系统 | 迭代 | Skill化 | 自动化) + 7标准 (S1-S7)
>
> 版本: V2.0 | 更新: 2026-03-21 | 覆盖规则: 8-9

---

## 7标准执行规范 (S1-S7)

### S1: 输入定义 (Input)
**输入**: 待审查的文档 / 代码 / 交付物
- **文档**: SKILL.md, AGENTS.md, 设计文档, API文档等
- **代码**: Python, Shell, JavaScript, YAML, JSON等
- **交付物**: 配置文件, 脚本, 报告等

**输入要求**:
- 提供文件路径或内容
- 明确审查目标（语法/逻辑/格式/合规）
- 标注审查优先级

### S2: 多维度检查 (Check)
**四维检查模型**:
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   语法检查   │ →  │   逻辑检查   │ →  │   格式检查   │ →  │   标准合规   │
│  (Syntax)   │    │  (Logic)    │    │  (Format)   │    │ (Compliance)│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      ↓                  ↓                  ↓                  ↓
   语法错误          逻辑漏洞           格式不一致          标准偏离
   语法规范          逻辑一致性         排版规范           隐性规则
```

| 维度 | 检查内容 | 工具/方法 | 严重级别 |
|------|----------|-----------|----------|
| **语法** | 语法错误、拼写错误、无效字符 | `shellcheck`, `python -m py_compile`, 正则检查 | 🔴 Critical |
| **逻辑** | 逻辑一致性、条件完备性、边界处理 | 静态分析、代码走查 | 🟠 High |
| **格式** | 缩进、换行、命名规范、注释 | `prettier`, `black`, 自定义规则 | 🟡 Medium |
| **合规** | 5标准、7标准、隐性规则、内部规范 | 规则引擎、检查清单 | 🟡 Medium |

### S3: 输出报告 (Output)
**输出三件套**:
1. **审查报告** (Markdown): 整体质量评估、置信度评级
2. **问题清单** (JSON): 结构化问题列表，可跟踪修复
3. **修复建议** (Patch): 可直接应用的修复代码

**输出格式**:
```yaml
review_report:
  target: "文件路径"
  timestamp: "2026-03-21T18:38:00+08:00"
  overall_grade: "A/B/C/D"  # A=优秀, B=良好, C=需改进, D=不合格
  confidence_level: "高/中/低"
  issues:
    - id: "QA-001"
      severity: "Critical/High/Medium/Low"
      category: "Syntax/Logic/Format/Compliance"
      line: 42
      message: "问题描述"
      suggestion: "修复建议"
      auto_fixable: true/false
  summary:
    total: 10
    critical: 1
    high: 2
    medium: 4
    low: 3
    auto_fixable: 7
```

### S4: 触发机制 (Trigger)
**触发方式**:
| 方式 | 命令 | 使用场景 |
|------|------|----------|
| **手动触发** | `./qa-review.sh <file>` | 开发过程中自检查 |
| **批量审查** | `./qa-review.sh --batch <dir>` | 目录批量审查 |
| **发布集成** | `./qa-review.sh --ci <commit>` | CI/CD流水线 |
| **定时扫描** | Cron每日扫描 | 持续质量保证 |

**发布门控**:
```bash
# CI/CD集成示例
./qa-review.sh --ci --gate=A  # 要求A级才能发布
./qa-review.sh --ci --block-on=Critical,High  # Critical/High级别阻断发布
```

### S5: 检查清单验证 (Checklist)
**动态检查清单** (根据文件类型自动选择):

#### 5.1 SKILL.md 专用检查清单
```markdown
## SKILL.md 检查清单
- [ ] S1: 输入定义明确 (待审查物、目标)
- [ ] S2: 多维度检查覆盖 (语法→逻辑→格式→合规)
- [ ] S3: 输出报告完整 (报告+清单+建议)
- [ ] S4: 触发机制清晰 (手动/自动/CI集成)
- [ ] S5: 检查清单可验证 (本清单通过)
- [ ] S6: 局限性明确标注
- [ ] S7: 对抗测试覆盖 (错误植入与发现)
- [ ] 5标准: 全局/系统/迭代/Skill化/自动化
- [ ] 隐性规则: 规则8(置信度标注) / 规则9(交叉验证)
```

#### 5.2 代码检查清单
```markdown
## 代码检查清单
- [ ] 语法: 无编译/解释错误
- [ ] 语法: 无未定义变量/函数
- [ ] 逻辑: 边界条件处理
- [ ] 逻辑: 异常处理完备
- [ ] 格式: 缩进一致
- [ ] 格式: 命名规范
- [ ] 合规: 符合项目规范
```

#### 5.3 配置文件检查清单
```markdown
## 配置文件检查清单
- [ ] 语法: JSON/YAML/INI格式正确
- [ ] 语法: 无重复键
- [ ] 逻辑: 必填字段存在
- [ ] 逻辑: 值在有效范围内
- [ ] 格式: 缩进正确
- [ ] 合规: 路径正确且存在
```

### S6: 局限性标注 (Limitations)
**明确声明以下无法自动检测的内容**:

| 局限类型 | 说明 | 建议处理方式 |
|----------|------|--------------|
| **业务逻辑正确性** | 无法判断算法是否满足业务需求 | 人工评审 + 测试用例验证 |
| **安全漏洞深度检测** | 无法替代专业安全审计 | 结合 `bandit`, `snyk` 等工具 |
| **性能优化建议** | 无法准确评估性能瓶颈 | 结合性能测试工具 |
| **设计模式合理性** | 无法判断架构设计优劣 | 架构师评审 |
| **语义正确性** | 无法确保文档描述准确 | 领域专家审核 |

### S7: 对抗测试 (Adversarial Testing)
**错误植入与发现率测试**:

```bash
# 运行对抗测试套件
./qa-adversarial-test.sh
```

**测试原理**:
1. **植入阶段**: 在测试样本中故意植入已知错误
2. **检测阶段**: 运行QA审查工具
3. **评估阶段**: 统计发现率

**植入错误类型**:
| 类型 | 示例 | 预期检测 |
|------|------|----------|
| 语法错误 | 缺失括号、拼写错误 | 100% |
| 逻辑错误 | 死代码、无限循环 | 90%+ |
| 格式错误 | 缩进混乱、多余空格 | 100% |
| 合规偏离 | 缺少S1-S7章节 | 100% |

**发现率阈值**:
- 🔴 **不合格**: < 80%
- 🟡 **待改进**: 80% - 90%
- 🟢 **达标**: 90% - 95%
- 🔵 **优秀**: ≥ 95%

---

## 5标准执行规范

### 一、全局考虑 (质量全链路)

#### 1.1 质量保证链路
```
[内容生成] → [置信度评估] → [置信度标注] → [重要性判断] → [交叉验证] → [最终输出]
     ↑                                                                      ↓
     └───────────────────── [质量反馈循环] ←───────────────────────────────┘
```

#### 1.2 三层覆盖
| 层级 | 覆盖内容 | 检查点 |
|------|----------|--------|
| L1: 基础质量 | 所有输出标注置信度 | 每次输出前 |
| L2: 决策质量 | 重要决策建议交叉验证 | 输出决策建议时 |
| L3: 持续改进 | 质量反馈与迭代 | 定期回顾 |

### 二、系统考虑 (闭环设计)

#### 2.1 质量保证闭环
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  内容生成   │ →  │ 置信度评估  │ →  │ 置信度标注  │ →  │ 重要性判断  │
│             │    │ (内部评估)  │    │ (输出标注)  │    │ (决策建议?) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                ↓
                        ┌───────────────────────────────────────┐
                        ↓                                       │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  质量反馈   │ ←  │  最终输出   │ ←  │  交叉验证   │←─────────┘
│  (迭代优化) │    │  (含标注)   │    │  (2+模型)   │ (重要决策)
└─────────────┘    └─────────────┘    └─────────────┘
```

#### 2.2 质量检查矩阵
| 检查项 | 触发条件 | 阈值 | 自动动作 | 人工介入 |
|--------|----------|------|----------|----------|
| 置信度标注 | 所有AI输出 | - | 自动附加置信度标签 | 无需介入 |
| 重要性判断 | 输出决策建议 | - | 识别为重要决策 | 确认重要性 |
| 交叉验证触发 | 重要决策建议 | - | 启动多模型验证 | 等待验证结果 |
| 置信度不一致 | 多模型置信度差异 | >30% | 标记需人工复核 | 人工判断 |

### 三、迭代机制 (PDCA)

#### 3.1 每周质量分析
| 迭代维度 | 检查内容 | 优化动作 |
|----------|----------|----------|
| 置信度准确性 | 高置信度错误率 | 调整评估标准 |
| 低置信度处理 | 低置信度输出比例 | 改进信息收集 |
| 交叉验证效率 | 验证耗时与效果 | 优化验证流程 |
| 模型一致性 | 多模型一致性率 | 识别模型偏差 |
| 用户反馈 | 质量投诉/修正 | 针对性改进 |

#### 3.2 置信度评估标准
| 置信度等级 | 定义 | 使用场景 | 建议动作 |
|------------|------|----------|----------|
| 🔴 低 (Low) | 信息不完整/不确定 | 推测、假设、不完整信息 | 建议验证/补充信息 |
| 🟡 中 (Medium) | 有一定依据但非绝对 | 一般性建议、常见场景 | 可接受但注意边界 |
| 🟢 高 (High) | 信息充分、逻辑严密 | 基于明确证据/标准答案 | 可信赖 |
| 🔵 已验证 (Verified) | 多模型交叉验证一致 | 重要决策、关键建议 | 高度可信 |

### 四、Skill化 (可执行)

#### 4.1 触发条件

**自动触发**:
- 每次AI输出时（自动附加置信度）
- 输出决策建议时（触发重要性判断）
- 识别为重要决策时（启动交叉验证）

**手动触发**:
```bash
# 审查单个文件
./skills/quality-assurance/scripts/qa-review.sh <file>

# 批量审查目录
./skills/quality-assurance/scripts/qa-review.sh --batch <dir>

# CI/CD集成
./skills/quality-assurance/scripts/qa-review.sh --ci --gate=A

# 对抗测试
./skills/quality-assurance/scripts/qa-adversarial-test.sh

# 手动进行交叉验证
./skills/quality-assurance/scripts/cross-validate.sh "决策内容"

# 查看质量报告
./skills/quality-assurance/scripts/quality-report.sh

# 检查置信度统计
./skills/quality-assurance/scripts/confidence-stats.sh
```

#### 4.2 执行流程
```yaml
quality_assurance:
  # S1-S7 审查流程
  review_process:
    trigger: "file_submitted_or_manual"
    steps:
      - identify_file_type          # S1: 识别输入类型
      - load_checklist              # S5: 加载对应检查清单
      - syntax_check                # S2: 语法维度
      - logic_check                 # S2: 逻辑维度
      - format_check                # S2: 格式维度
      - compliance_check            # S2: 合规维度
      - generate_report             # S3: 生成报告
      - generate_fix_suggestions    # S3: 修复建议
      - run_adversarial_test        # S7: 对抗测试
    output:
      - review_report.md
      - issues.json
      - fixes.patch

  confidence_labeling:
    trigger: "before_output"
    steps:
      - assess_information_completeness
      - assess_source_reliability
      - assess_logic_soundness
      - determine_confidence_level
      - format_confidence_label
      - prepend_to_output
    
  importance_assessment:
    trigger: "output_contains_recommendation"
    steps:
      - classify_output_type
      - if_decision_recommendation:
          - assess_importance_level
          - if_important:
              - trigger_cross_validation
          - else:
              - output_with_confidence_only
  
  cross_validation:
    trigger: "important_decision_detected"
    steps:
      - select_validation_models
      - send_to_secondary_model
      - collect_secondary_response
      - compare_responses
      - calculate_consistency_score
      - if_high_consistency:
          - label_as_verified
      - if_low_consistency:
          - flag_for_human_review
          - present_both_responses
      - generate_validation_report
  
  quality_review:
    trigger: "daily_scheduled"
    steps:
      - compile_confidence_distribution
      - identify_low_confidence_patterns
      - analyze_cross_validation_results
      - generate_improvement_suggestions
```

#### 4.3 产出标准
| 产出物 | 格式 | 位置 | 质量要求 |
|--------|------|------|----------|
| 审查报告 | Markdown | `reports/qa/` | 含S1-S7评估 |
| 问题清单 | JSON | `reports/qa/issues/` | 结构化、可跟踪 |
| 修复补丁 | Patch | `reports/qa/fixes/` | 可直接应用 |
| 置信度标注 | 文本标签 | 输出内容 | 每个输出都有 |
| 交叉验证报告 | Markdown | `memory/quality/cross-validation/` | 验证结果+一致性评分 |
| 质量统计 | JSON | `memory/quality/stats.json` | 置信度分布+趋势 |
| 周质量报告 | Markdown | `memory/quality/weekly-reports/` | 分析+改进建议 |
| 对抗测试报告 | Markdown | `reports/qa/adversarial/` | 发现率统计 |

### 五、流程自动化 (Cron集成)

#### 5.1 Cron配置
```json
{
  "version": "2.0.0",
  "skill_name": "quality-assurance",
  "description": "质量保证协议 - 7标准审查 + 定时统计 + 周报",
  "jobs": [
    {
      "name": "quality-stats-update",
      "schedule": "0 */6 * * *",
      "enabled": true,
      "command": "/root/.openclaw/workspace/skills/quality-assurance/scripts/confidence-stats.sh",
      "timeout": 60,
      "description": "每6小时更新质量统计数据"
    },
    {
      "name": "weekly-quality-report",
      "schedule": "0 20 * * 0",
      "enabled": true,
      "command": "/root/.openclaw/workspace/skills/quality-assurance/scripts/quality-report.sh weekly",
      "timeout": 120,
      "description": "每周日20:00生成质量周报"
    },
    {
      "name": "daily-adversarial-test",
      "schedule": "0 3 * * *",
      "enabled": true,
      "command": "/root/.openclaw/workspace/skills/quality-assurance/scripts/qa-adversarial-test.sh",
      "timeout": 180,
      "description": "每日凌晨运行对抗测试"
    },
    {
      "name": "skill-quality-scan",
      "schedule": "0 9 * * 1",
      "enabled": true,
      "command": "/root/.openclaw/workspace/skills/quality-assurance/scripts/qa-review.sh --batch /root/.openclaw/workspace/skills/",
      "timeout": 300,
      "description": "每周一扫描所有Skill质量"
    }
  ]
}
```

#### 5.2 自动化脚本
见 `scripts/` 目录:
- `qa-review.sh` - 主审查脚本 (S1-S7)
- `qa-adversarial-test.sh` - 对抗测试脚本 (S7)
- `confidence-stats.sh` - 置信度统计
- `quality-report.sh` - 质量报告生成
- `cross-validate.sh` - 交叉验证记录

#### 5.3 异常处理
| 异常类型 | 检测方式 | 自动响应 | 人工介入 |
|----------|----------|----------|----------|
| 审查失败 | 脚本退出码非0 | 记录错误日志 | 检查脚本/环境 |
| 发现率下降 | 对抗测试发现率<80% | 告警通知 | 优化检测规则 |
| 低置信度集中 | 低置信度比例>30% | 提醒改进信息收集 | 补充信息源 |
| 验证不一致 | 模型间差异>30% | 标记人工复核 | 人工判断 |
| 质量下降 | 问题反馈增加 | 生成分析报告 | 调整策略 |

---

## 质量门控

### 7标准自检清单 (S1-S7)
- [x] **S1 输入定义**: 明确待审查文档/代码/交付物
- [x] **S2 多维度检查**: 语法→逻辑→格式→合规
- [x] **S3 输出报告**: 审查报告+问题清单+修复建议
- [x] **S4 触发机制**: 手动触发+CI集成+定时扫描
- [x] **S5 检查清单**: SKILL/代码/配置专用清单可验证
- [x] **S6 局限标注**: 业务逻辑/安全/性能等无法自动检测项
- [x] **S7 对抗测试**: 错误植入与发现率≥90%

### 5标准自检清单
- [x] **全局考虑**: 覆盖所有输出+决策建议
- [x] **系统考虑**: 置信度标注→交叉验证→反馈闭环
- [x] **迭代机制**: 每周质量分析+改进
- [x] **Skill化**: 可触发、可执行、有产出
- [x] **流程自动化**: Cron统计+报告+对抗测试

### 执行验证
```bash
# 审查单个文件
./skills/quality-assurance/scripts/qa-review.sh <file>

# 批量审查
./skills/quality-assurance/scripts/qa-review.sh --batch <dir>

# CI集成
./skills/quality-assurance/scripts/qa-review.sh --ci --gate=A

# 运行对抗测试
./skills/quality-assurance/scripts/qa-adversarial-test.sh

# 查看质量日志
ls -la memory/quality/

# 查看置信度统计
./skills/quality-assurance/scripts/confidence-stats.sh

# 生成质量报告
./skills/quality-assurance/scripts/quality-report.sh daily
./skills/quality-assurance/scripts/quality-report.sh weekly

# 创建交叉验证记录
./skills/quality-assurance/scripts/cross-validate.sh "重要决策内容"
```

---

## 置信度评估指南

### 评估维度
| 维度 | 评估问题 | 评分标准 |
|------|----------|----------|
| 信息完整度 | 是否有足够信息支撑结论？ | 完整(高)/部分(中)/缺失(低) |
| 来源可靠性 | 信息来源是否可靠？ | 权威(高)/一般(中)/不确定(低) |
| 逻辑严密性 | 推理过程是否严谨？ | 严密(高)/合理(中)/推测(低) |
| 经验验证 | 是否符合已知经验？ | 符合(高)/部分(中)/新情况(低) |

### 置信度判定规则
- **高**: 3-4个维度均为高
- **中**: 1-2个维度为中，无低
- **低**: 任一维度为低，或多个为中
- **已验证**: 多模型一致性确认后升级

---

## 使用方式

### 在对话中使用

**所有输出前自动添加**:
```
【置信度: 高】信息基于... / 逻辑推导...

[正文内容]
```

**重要决策建议**:
```
【置信度: 中 | 🔍需交叉验证】
这是一个重要决策建议，建议进行交叉验证。

[建议内容]

---
待验证: 请用另一模型询问相同问题确认
```

**交叉验证完成**:
```
【置信度: 高 | ✅已验证】
模型A与模型B结论一致，已交叉验证。

[结论内容]
```

### 质量审查命令
```bash
# 审查SKILL.md
./skills/quality-assurance/scripts/qa-review.sh skills/my-skill/SKILL.md

# 审查代码
./skills/quality-assurance/scripts/qa-review.sh scripts/my-script.sh

# 批量审查所有Skill
./skills/quality-assurance/scripts/qa-review.sh --batch skills/

# CI集成（阻断低质量发布）
./skills/quality-assurance/scripts/qa-review.sh --ci --gate=A --block-on=Critical,High

# 运行对抗测试
./skills/quality-assurance/scripts/qa-adversarial-test.sh

# 查看今日置信度统计
./skills/quality-assurance/scripts/confidence-stats.sh

# 生成质量报告
./skills/quality-assurance/scripts/quality-report.sh daily
./skills/quality-assurance/scripts/quality-report.sh weekly

# 创建交叉验证记录
./skills/quality-assurance/scripts/cross-validate.sh "重要决策内容"
```

---

## 覆盖的隐性规则

| 规则编号 | 规则内容 | 触发条件 |
|----------|----------|----------|
| 规则8 | 所有AI输出必须标注置信度 | 每次输出时 |
| 规则9 | 重要决策建议需至少2个模型交叉验证 | 决策建议输出时 |

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*
*7标准合规: ✅ S1 | ✅ S2 | ✅ S3 | ✅ S4 | ✅ S5 | ✅ S6 | ✅ S7*
*覆盖规则: 8(置信度标注) | 9(交叉验证)*
