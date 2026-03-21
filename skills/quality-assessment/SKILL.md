# Quality Assessment Skill (质量评估体系)

> **标准等级**: 5标准 (全局 | 系统 | 迭代 | Skill化 | 自动化)
>
> **版本**: V5.0 | 更新: 2026-03-21 | 覆盖标准: S1-S7

**定位说明**: 本Skill专注于**Skill运行时质量评估**（功能、性能、可靠性），与 `quality-assurance`（文档/代码静态合规审查）形成互补。

---

## 7标准执行规范 (S1-S7)

### S1: 输入定义 (Input)

**评估对象**:
| 类型 | 示例 | 评估目标 |
|------|------|----------|
| **Skill模块** | `task-coordinator`, `kimi-search` | 功能完整性与性能 |
| **脚本文件** | `.py`, `.sh`, `.js` | 代码质量与可维护性 |
| **配置文件** | `config.json`, `cron.json` | 配置有效性与合规性 |
| **交付物** | 测试报告、日志文件 | 准确性与完整性 |

**评估标准**: 可自定义评估标准（见 `/config/assessment-standards.json`）

**评估范围**:
```yaml
scope:
  functional:     # 功能维度
    - positive_tests    # 正例测试
    - negative_tests    # 负例测试
    - boundary_tests    # 边界测试
  performance:    # 性能维度
    - response_time     # 响应时间
    - throughput        # 吞吐量
    - resource_usage    # 资源占用
  reliability:    # 可靠性维度
    - error_handling    # 错误处理
    - fault_tolerance   # 容错能力
    - stability         # 稳定性
  maintainability: # 可维护性维度
    - code_quality      # 代码质量
    - documentation     # 文档完整性
    - test_coverage     # 测试覆盖率
```

### S2: 质量评估 (4维度递进)

**评估模型**:
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  符合性评估  │ →  │  有效性评估  │ →  │  可靠性评估  │ →  │  可维护性评估 │
│ (Compliance)│    │(Effectiveness)│    │  (Reliability)│    │(Maintainability)│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      ↓                  ↓                  ↓                  ↓
   满足规范要求      达成预期目标       持续稳定运行        易于维护迭代
   基础功能通过      业务价值实现       异常恢复能力        代码文档质量
```

#### 维度1: 符合性评估 (Compliance)
验证Skill是否满足基础规范要求

| 检查项 | 权重 | 评估标准 | 测试方法 |
|--------|------|----------|----------|
| **正例测试** | 40% | ≥95%为A, ≥85%为B, ≥70%为C, <70%为D | 至少10个正例场景 |
| **负例测试** | 30% | ≤5%误报为A, ≤15%为B, ≤30%为C, >30%为D | 至少10个负例场景 |
| **边界测试** | 30% | 边界条件处理正确率 | 5个边界场景 |

#### 维度2: 有效性评估 (Effectiveness)
验证Skill是否有效达成业务目标

| 检查项 | 权重 | 评估标准 | 测量方法 |
|--------|------|----------|----------|
| **任务完成率** | 50% | 完成目标任务的比率 | 实际任务执行统计 |
| **结果准确性** | 30% | 输出结果的准确率 | 人工抽检+自动化对比 |
| **用户满意度** | 20% | 基于反馈的评分 | 用户反馈统计 |

#### 维度3: 可靠性评估 (Reliability)
验证Skill在异常情况下的稳定运行能力

| 检查项 | 权重 | 评估标准 | 测试场景 |
|--------|------|----------|----------|
| **压力测试** | 40% | 100%/90%/70%/<70%通过率为A/B/C/D | 大规模/高并发/堆积场景 |
| **故障恢复** | 30% | 异常后自动恢复能力 | 模拟网络/服务故障 |
| **长期稳定** | 30% | 长时间运行无衰减 | 24小时连续运行 |

#### 维度4: 可维护性评估 (Maintainability)
评估Skill代码和文档的可维护程度

| 检查项 | 权重 | 评估标准 | 检查方法 |
|--------|------|----------|----------|
| **代码质量** | 25% | 复杂度、重复率、规范 | 静态代码分析 |
| **文档完整** | 25% | SKILL.md、注释覆盖率 | 文档检查清单 |
| **错误处理** | 25% | 异常捕获、日志记录 | 代码审查 |
| **可测试性** | 25% | 模块化、Mock支持 | 测试覆盖率 |

**综合权重**:
```
总分 = 符合性(30%) + 有效性(25%) + 可靠性(25%) + 可维护性(20%)
```

### S3: 输出评估报告 (Output)

**输出三件套**:
1. **评估报告** (Markdown): 整体质量评估、等级评定、置信度
2. **问题清单** (JSON): 结构化问题列表，可跟踪修复
3. **改进建议** (Markdown): 优先级排序的优化建议

**输出格式**:
```yaml
assessment_report:
  target: "task-coordinator"
  version: "v2.1"
  timestamp: "2026-03-21T19:00:00+08:00"
  
  # 等级评定
  overall_grade: "A"  # A+/A/B+/B/C/D
  overall_score: 91
  confidence_level: "高"
  
  # 各维度评分
  dimensions:
    compliance:
      score: 90
      grade: "A-"
      details:
        positive_test: { passed: 9, total: 10, rate: "90%" }
        negative_test: { passed: 9, total: 10, rate: "90%" }
        boundary_test: { passed: 5, total: 5, rate: "100%" }
    effectiveness:
      score: 88
      grade: "B+"
    reliability:
      score: 95
      grade: "A"
    maintainability:
      score: 90
      grade: "A-"
  
  # 问题清单
  issues:
    - id: "QA-001"
      severity: "High"
      dimension: "compliance"
      category: "边界测试"
      message: "极端阻塞堆积场景处理不完善"
      suggestion: "添加批量阻塞检测逻辑(>10个)"
      auto_fixable: true
    
  # 改进建议
  improvements:
    priority_high:
      - "降低学习模式识别阈值"
    priority_medium:
      - "完善未来任务处理策略"
    priority_low:
      - "优化代码注释覆盖率"
  
  # 历史对比
  history:
    previous_score: 86
    improvement: +5
    trend: "upward"
```

**等级划分**:

| 等级 | 分数范围 | 说明 | 建议 |
|------|----------|------|------|
| **A+** | 95-100 | 卓越 | 可直接上线，作为标杆 |
| **A** | 90-94 | 优秀 | 可上线，轻微优化建议 |
| **B+** | 85-89 | 良好 | 可上线，有优化空间 |
| **B** | 80-84 | 合格 | 可上线，需修复已知问题 |
| **C** | 70-79 | 及格 | 建议修复后再上线 |
| **D** | <70 | 不合格 | 需重大改进 |

### S4: 触发机制 (Trigger)

**触发方式**:
| 方式 | 命令 | 使用场景 |
|------|------|----------|
| **手动触发** | `./assess-skill.sh <skill-name>` | 开发完成后评估 |
| **批量评估** | `./assess-skill.sh --batch` | 评估所有Skill |
| **对比评估** | `./assess-skill.sh --compare <v1> <v2>` | 版本对比 |
| **定时评估** | Cron每周一09:00 | 持续质量监控 |

**CI/CD集成**:
```bash
# 发布门控 - 要求A级才能发布
./assess-skill.sh --ci --gate=A <skill-name>

# 回归测试 - 对比上一版本
./assess-skill.sh --regression <skill-name>
```

### S5: 评估标准一致性验证 (Checklist)

**动态检查清单** (根据评估对象自动选择):

#### 5.1 Skill评估检查清单
```markdown
## Skill评估检查清单
- [ ] S1: 评估对象明确 (名称/版本/路径)
- [ ] S1: 评估范围定义 (功能/性能/可靠性/可维护性)
- [ ] S2: 符合性评估完成 (正例/负例/边界)
- [ ] S2: 有效性评估完成 (完成率/准确性/满意度)
- [ ] S2: 可靠性评估完成 (压力/故障/稳定)
- [ ] S2: 可维护性评估完成 (代码/文档/错误/测试)
- [ ] S3: 评估报告生成 (等级评定/问题清单/改进建议)
- [ ] S4: 触发机制配置 (手动/批量/定时)
- [ ] S5: 本检查清单通过验证
- [ ] S6: 局限性已标注
- [ ] S7: 对抗验证完成 (交叉评估一致性)
```

#### 5.2 脚本评估检查清单
```markdown
## 脚本评估检查清单
- [ ] 语法: 可正确执行无错误
- [ ] 功能: 完成预期任务
- [ ] 性能: 响应时间在可接受范围
- [ ] 错误处理: 异常捕获与日志
- [ ] 输入验证: 参数检查
- [ ] 输出格式: 结构化可解析
```

#### 5.3 配置评估检查清单
```markdown
## 配置评估检查清单
- [ ] 格式: JSON/YAML格式正确
- [ ] 必填: 所有必填字段存在
- [ ] 值域: 值在有效范围内
- [ ] 引用: 路径/依赖正确存在
- [ ] 兼容: 与现有系统兼容
```

### S6: 局限性标注 (Limitations)

**明确声明以下评估限制**:

| 局限类型 | 说明 | 建议处理方式 |
|----------|------|--------------|
| **主观评估偏差** | 部分维度依赖评估者经验判断，存在主观性 | 多评估者交叉验证 |
| **测试覆盖不足** | 测试用例无法穷尽所有场景 | 持续补充测试用例 |
| **环境依赖** | 性能评估受测试环境影响 | 多次测试取平均/标准化环境 |
| **业务场景变化** | 评估标准需随业务演进 | 定期回顾更新标准 |
| **AIGC输出波动** | AI生成内容的稳定性无法完全保证 | 多次采样评估 |

**置信度标注**:
```
【置信度: 高】基于完整测试数据和明确标准
【置信度: 中】基于部分测试数据或经验判断
【置信度: 低】信息不完整或存在主观判断
```

### S7: 对抗验证 (Adversarial Validation)

**交叉评估验证一致性**:

```bash
# 运行对抗验证测试
./assess-adversarial-test.sh
```

**验证原理**:
1. **多评估者测试**: 同一对象由不同评估者独立评估
2. **一致性计算**: 计算评估结果的一致性评分
3. **偏差分析**: 识别评估标准理解偏差

**一致性阈值**:
| 一致性等级 | 评分差异 | 说明 |
|------------|----------|------|
| 🔵 高度一致 | ≤5分 | 评估标准理解一致，结果可信 |
| 🟢 基本一致 | 6-10分 | 评估标准理解基本一致，可接受 |
| 🟡 存在差异 | 11-15分 | 存在标准理解差异，需校准 |
| 🔴 严重分歧 | >15分 | 评估标准理解分歧，需重新审视 |

**交叉评估报告**:
```yaml
cross_validation:
  assessors: ["assessor_A", "assessor_B", "assessor_C"]
  scores: [91, 89, 92]
  mean_score: 90.7
  std_deviation: 1.25
  consistency: "高度一致"
  
  dimension_comparison:
    compliance: { scores: [90, 88, 91], consistency: "高度一致" }
    effectiveness: { scores: [88, 87, 89], consistency: "高度一致" }
    reliability: { scores: [95, 94, 95], consistency: "高度一致" }
    maintainability: { scores: [90, 89, 91], consistency: "高度一致" }
```

---

## 5标准执行规范

### 一、全局考虑 (质量全链路)

#### 1.1 质量评估链路
```
[评估输入] → [标准加载] → [多维测试] → [评分计算] → [报告生成] → [改进跟踪] → [历史对比]
     ↑                                                                            ↓
     └──────────────────────── [质量反馈循环] ←───────────────────────────────────┘
```

#### 1.2 三层覆盖
| 层级 | 覆盖内容 | 检查点 |
|------|----------|--------|
| L1: 基础评估 | 所有Skill必须完成符合性评估 | 每次Skill更新后 |
| L2: 深度评估 | 核心Skill进行全维度评估 | Skill重要更新时 |
| L3: 持续监控 | 质量趋势跟踪 | 定期回顾 |

### 二、系统考虑 (闭环设计)

#### 2.1 评估闭环
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  评估计划   │ →  │ 测试执行   │ →  │ 评分计算   │ →  │ 报告生成   │
│             │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      ↑                                                       ↓
      └───────────────────────────────────────────────────────┘
                          ↓ 问题修复后
                   ┌─────────────┐
                   │  重新评估   │ ← 验证改进效果
                   │  (回归测试) │
                   └─────────────┘
```

#### 2.2 评估矩阵
| 检查项 | 触发条件 | 阈值 | 自动动作 | 人工介入 |
|--------|----------|------|----------|----------|
| 符合性检查 | Skill更新 | 通过率<70% | 标记需修复 | 确认修复方案 |
| 性能检查 | 每次评估 | 响应>1s | 标记性能问题 | 优化建议 |
| 可靠性检查 | 核心Skill | 通过率<90% | 告警 | 分析原因 |
| 交叉验证 | A级评估 | 差异>10分 | 标记需复核 | 确认最终评分 |

### 三、迭代机制 (PDCA)

#### 3.1 每周质量分析
| 迭代维度 | 检查内容 | 优化动作 |
|----------|----------|----------|
| 评估标准准确性 | 评分与实际表现一致性 | 调整评估标准 |
| 测试用例覆盖 | 未覆盖场景比例 | 补充测试用例 |
| 交叉验证一致性 | 多评估者一致性率 | 校准评估标准 |
| 改进效果追踪 | 修复后评分提升 | 验证改进有效性 |
| 历史趋势 | 质量趋势变化 | 识别系统性问题 |

#### 3.2 评估标准演进
| 阶段 | 标准版本 | 主要更新 |
|------|----------|----------|
| v1.0 | 基础标准 | 功能测试为主 |
| v2.0 | 扩展标准 | 增加性能/可靠性 |
| v3.0 | 完整标准 | 增加可维护性 |
| v4.0 | 优化标准 | 细化评分维度 |
| v5.0 | 成熟标准 | S1-S7完整规范 |

### 四、Skill化 (可执行)

#### 4.1 触发条件

**自动触发**:
- Skill更新后自动评估符合性
- 核心Skill变更触发全维度评估
- 版本发布前自动评估

**手动触发**:
```bash
# 评估单个Skill
./skills/quality-assessment/scripts/assess-skill.sh <skill-name>

# 批量评估所有Skill
./skills/quality-assessment/scripts/assess-skill.sh --batch

# 对比两个版本
./skills/quality-assessment/scripts/assess-skill.sh --compare <v1> <v2>

# 回归测试
./skills/quality-assessment/scripts/assess-skill.sh --regression <skill-name>

# CI集成（阻断低质量发布）
./skills/quality-assessment/scripts/assess-skill.sh --ci --gate=A <skill-name>

# 运行对抗验证
./skills/quality-assessment/scripts/assess-adversarial-test.sh

# 查看质量报告
./skills/quality-assessment/scripts/quality-report.sh

# 查看趋势分析
./skills/quality-assessment/scripts/trend-analysis.sh
```

#### 4.2 执行流程
```yaml
quality_assessment:
  # S1-S7 评估流程
  assessment_process:
    trigger: "skill_updated_or_manual"
    steps:
      - identify_assessment_target      # S1: 识别评估对象
      - load_assessment_standards       # S1: 加载评估标准
      - define_assessment_scope         # S1: 定义评估范围
      - run_compliance_tests            # S2: 符合性测试
      - run_effectiveness_tests         # S2: 有效性测试
      - run_reliability_tests           # S2: 可靠性测试
      - run_maintainability_tests       # S2: 可维护性测试
      - calculate_scores                # S2: 计算各维度得分
      - generate_assessment_report      # S3: 生成评估报告
      - identify_improvements           # S3: 识别改进点
      - run_cross_validation            # S7: 交叉验证
      - update_history                  # 更新历史记录
    output:
      - assessment_report.md
      - issues.json
      - improvements.md
      - cross_validation_report.md
  
  regression_test:
    trigger: "after_fix"
    steps:
      - run_previous_failed_tests
      - compare_scores
      - verify_improvements
      - update_report
  
  batch_assessment:
    trigger: "weekly_scheduled"
    steps:
      - discover_all_skills
      - run_assessment_for_each
      - aggregate_results
      - generate_ranking
      - identify_systemic_issues
```

#### 4.3 产出标准
| 产出物 | 格式 | 位置 | 质量要求 |
|--------|------|------|----------|
| 评估报告 | Markdown | `reports/assessment/` | 含S1-S7评估 |
| 问题清单 | JSON | `reports/assessment/issues/` | 结构化、可跟踪 |
| 改进建议 | Markdown | `reports/assessment/improvements/` | 优先级排序 |
| 交叉验证报告 | Markdown | `reports/assessment/cross-validation/` | 一致性评分 |
| 质量趋势 | JSON | `memory/quality/trends.json` | 历史趋势 |
| 排行榜 | Markdown | `reports/assessment/ranking.md` | Skill质量排名 |
| 周质量报告 | Markdown | `memory/quality/weekly-reports/` | 分析+改进建议 |
| 对抗验证报告 | Markdown | `reports/assessment/adversarial/` | 一致性统计 |

### 五、流程自动化 (Cron集成)

#### 5.1 Cron配置
```json
{
  "version": "2.0.0",
  "skill_name": "quality-assessment",
  "description": "质量评估体系 - S1-S7完整评估 + 定时扫描 + 趋势分析",
  "jobs": [
    {
      "name": "skill-assessment-weekly",
      "schedule": "0 9 * * 1",
      "enabled": true,
      "command": "/root/.openclaw/workspace/skills/quality-assessment/scripts/assess-skill.sh --batch",
      "timeout": 600,
      "description": "每周一09:00批量评估所有Skill"
    },
    {
      "name": "quality-trend-update",
      "schedule": "0 */6 * * *",
      "enabled": true,
      "command": "/root/.openclaw/workspace/skills/quality-assessment/scripts/trend-analysis.sh",
      "timeout": 120,
      "description": "每6小时更新质量趋势数据"
    },
    {
      "name": "weekly-assessment-report",
      "schedule": "0 20 * * 0",
      "enabled": true,
      "command": "/root/.openclaw/workspace/skills/quality-assessment/scripts/quality-report.sh weekly",
      "timeout": 120,
      "description": "每周日20:00生成质量周报"
    },
    {
      "name": "cross-validation-test",
      "schedule": "0 4 * * 1",
      "enabled": true,
      "command": "/root/.openclaw/workspace/skills/quality-assessment/scripts/assess-adversarial-test.sh",
      "timeout": 180,
      "description": "每周一凌晨运行交叉验证测试"
    }
  ]
}
```

#### 5.2 自动化脚本
见 `scripts/` 目录:
- `assess-skill.sh` - 主评估脚本 (S1-S7)
- `assess-adversarial-test.sh` - 交叉验证脚本 (S7)
- `trend-analysis.sh` - 趋势分析脚本
- `quality-report.sh` - 质量报告生成
- `quality-assessment-runner.py` - Python执行器

#### 5.3 异常处理
| 异常类型 | 检测方式 | 自动响应 | 人工介入 |
|----------|----------|----------|----------|
| 评估失败 | 脚本退出码非0 | 记录错误日志 | 检查脚本/环境 |
| 一致性不足 | 交叉验证差异>10分 | 告警通知 | 校准评估标准 |
| 质量下降 | 评分较上版本下降 | 提醒关注 | 分析原因 |
| 趋势恶化 | 连续两周下降 | 生成分析报告 | 调整策略 |

---

## 7标准自检清单 (S1-S7)

- [x] **S1 输入定义**: 明确评估对象/标准/范围
- [x] **S2 质量评估**: 符合性→有效性→可靠性→可维护性 四维递进
- [x] **S3 输出报告**: 评估报告+等级评定+改进建议
- [x] **S4 触发机制**: 手动/批量/定时/CI集成
- [x] **S5 标准一致性**: 动态检查清单可验证
- [x] **S6 局限标注**: 主观评估偏差等局限性
- [x] **S7 对抗验证**: 交叉评估验证一致性

## 5标准自检清单

- [x] **全局考虑**: 覆盖所有Skill质量评估
- [x] **系统考虑**: 评估→报告→改进→验证闭环
- [x] **迭代机制**: 每周质量分析+标准演进
- [x] **Skill化**: 可触发、可执行、有产出
- [x] **流程自动化**: Cron定时评估+趋势分析

## 执行验证

```bash
# 评估单个Skill
./skills/quality-assessment/scripts/assess-skill.sh task-coordinator

# 批量评估
./skills/quality-assessment/scripts/assess-skill.sh --batch

# 版本对比
./skills/quality-assessment/scripts/assess-skill.sh --compare v2.0 v2.1

# 回归测试
./skills/quality-assessment/scripts/assess-skill.sh --regression task-coordinator

# CI集成（要求A级）
./skills/quality-assessment/scripts/assess-skill.sh --ci --gate=A task-coordinator

# 运行对抗验证
./skills/quality-assessment/scripts/assess-adversarial-test.sh

# 查看趋势
./skills/quality-assessment/scripts/trend-analysis.sh

# 生成质量报告
./skills/quality-assessment/scripts/quality-report.sh weekly
```

---

## 历史评估记录

### task-coordinator v2.1 (2026-03-12) - 优化后 ⭐

| 维度 | 评分 | 备注 |
|------|------|------|
| 符合性 | 90% (A-) | 正例90%/负例90%/边界100% |
| 有效性 | 88% (B+) | 任务完成率/准确性良好 |
| 可靠性 | 95% (A) | 压力测试100%通过 |
| 可维护性 | 90% (A-) | 代码/文档/测试良好 |
| **综合评分** | **A- (91分)** | **优化后提升5分** |

**优化内容**:
- 添加批量阻塞检测 (>10个阻塞任务)
- 降低学习模式识别阈值
- 优化决策优先级顺序

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*
*7标准合规: ✅ S1 | ✅ S2 | ✅ S3 | ✅ S4 | ✅ S5 | ✅ S6 | ✅ S7*
