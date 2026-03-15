# 决策模式标注数据集（示例）

> 从22年经验中提取的决策点标注
> 格式：YAML
> 用途：训练价值网络、模式学习

---

## 案例1：银行时期核心客户邀请创业

### 基本信息

```yaml
case_id: CASE-001
case_title: "银行时期核心客户邀请创业"
client_name: "Egbertie"
decision_date: "2018-03"
industry: "金融科技"
case_summary: "银行核心客户（科技公司CEO）邀请参与AI创业项目，48小时内决定"
```

### 决策点1：是否参与创业项目

```yaml
decision_point:
  dp_id: DP-001-01
  dp_sequence: 1
  total_dps: 3

context:
  description: "银行核心客户（科技公司CEO）邀请参与AI创业项目，担任联合创始人"
  time_background: "2018年3月，银行工作期间"
  location: "深圳"
  stakeholders: ["我", "客户（科技公司CEO）", "银行"]
  trigger: "客户正式提出邀请"
  decision_type: "是否参与"

information_completeness:
  score: 0.3
  known_factors:
    - "客户信任度高（3年合作关系）"
    - "AI行业前景好"
    - "团队大致规模（10人左右）"
  unknown_factors:
    - "详细财务状况"
    - "核心技术细节"
    - "其他合伙人背景"
    - "具体业务模式"

time_pressure:
  level: "高"
  deadline: "48小时内"
  reason: "客户需要快速启动，机会窗口有限"
  opportunity_cost: "可能失去首发优势"

interest_conflict:
  my_interests:
    - "合规性（银行员工身份）"
    - "职业安全"
    - "长期发展"
    - "稳定收入"
  their_interests:
    - "快速启动"
    - "资源整合"
    - "银行背景背书"
    - "我的技术判断"
  conflict_points:
    - "合规要求 vs 快速启动需求"
    - "稳定收入 vs 创业风险"
  coordination_possible: false

cognitive_biases:
  - type: "损失厌恶"
    severity: "高"
    description: "害怕失去银行的稳定工作和收入"
    evidence: "反复权衡银行职位的安全感"
  - type: "禀赋效应"
    severity: "中"
    description: "高估与客户3年关系的价值"
    evidence: "认为客户关系是独特优势"
  - type: "现状偏见"
    severity: "高"
    description: "倾向于维持银行工作的现状"
    evidence: "对改变现状有强烈抵触"
  - type: "锚定效应"
    severity: "中"
    description: "银行薪资成为心理锚点"
    evidence: "反复比较创业收入与银行收入"

intuition_signal:
  body_reaction: "胃部不适，隐隐作痛"
  emotion: "焦虑，有种说不出的不安"
  description: "总觉得哪里不对，但又说不上来"
  intensity: "强"
  timing: "客户提出邀请时立即出现"
  persistence: "持续48小时未消退"

rational_analysis:
  methods_used:
    - "SWOT分析"
    - "风险矩阵"
    - "专家咨询（罗汉教授）"
  swot_summary:
    strengths: ["客户信任", "行业经验"]
    weaknesses: ["跨行业", "缺乏技术背景"]
    opportunities: ["AI风口", "先发优势"]
    threats: ["合规风险", "团队未知"]
  risk_assessment: "高风险"
  expert_advice: "罗汉教授建议谨慎，风险不可控"
  conclusion: "理性分析建议拒绝"

final_decision:
  choice: "拒绝"
  reason: "时机不成熟，风险不可控，直觉强烈不适"
  basis: "直觉主导"  # 直觉占70%，理性占30%
  confidence: 0.85
  alternative_considered: "提议先作为顾问参与，观察3个月"
  alternative_rejected: "客户要求全职投入"

outcome_feedback:
  short_term: "未参与，继续银行工作，客户关系维持"
  medium_term: "听说项目进展缓慢，融资困难"
  long_term: "项目6个月后失败，团队解散，客户回归大厂"
  expected_outcome: "项目可能失败"
  actual_outcome: "项目确实失败"
  outcome_match: true
  lessons_learned:
    - "直觉不适是重要的警告信号"
    - "时间压力下的决策风险更高"
    - "信息不完备时应更谨慎"
  conclusion: "决策正确"

pattern_extraction:
  pattern: "直觉不适 + 时间压力 + 跨行业 + 信息不完备 = 拒绝"
  pattern_type: "风险规避型"
  conditions:
    - type: "直觉信号"
      description: "身体或情绪的强烈不适"
      weight: "高"
    - type: "时间压力"
      description: "决策时间 < 48小时"
      weight: "高"
    - type: "领域跨度"
      description: "跨行业或跨职能"
      weight: "中"
    - type: "信息缺口"
      description: "关键信息缺失 > 50%"
      weight: "中"
  recommendation: "拒绝或要求延长时间收集信息"
  evidence_count: 1
  accuracy_rate: 1.0
  similar_cases: []

training_labels:
  decision_quality: 1.0  # 基于结果评估为正确决策
  pattern_type: "风险规避型"
  risk_level: "高"
  urgency_level: "高"
  complexity_level: "中"
  outcome_alignment: "预期与实际一致"

metadata:
  annotated_by: "满意妞"
  annotated_at: "2026-03-15"
  verified: false
  notes: "典型案例，直觉与理性一致，决策质量高"
  tags: ["创业邀请", "跨行业", "时间压力", "直觉信号"]
```

### 决策点2：是否作为顾问参与

```yaml
decision_point:
  dp_id: DP-001-02
  dp_sequence: 2
  total_dps: 3
  
context:
  description: "被拒绝后，客户提议以顾问身份参与"
  decision_type: "是否接受"

information_completeness:
  score: 0.5
  
time_pressure:
  level: "中"
  deadline: "1周内"

cognitive_biases:
  - type: "互惠原则"
    severity: "中"
    description: "觉得拒绝全职后再拒绝顾问不合适"

intuition_signal:
  body_reaction: "轻微不适"
  emotion: "犹豫"
  intensity: "中"

final_decision:
  choice: "婉拒"
  reason: "担心边界不清，影响银行工作"
  confidence: 0.75

outcome_feedback:
  conclusion: "决策正确"
  
pattern_extraction:
  pattern: "直觉不适即使减弱但仍存在 = 继续拒绝"
  pattern_type: "边界保护型"
```

---

## 案例2：孵化器项目合伙人选择

```yaml
case_id: CASE-002
case_title: "孵化器项目合伙人选择"
client_name: "Egbertie"
decision_date: "2019-06"
industry: "企业服务"
case_summary: "参与孵化器项目，需要从3个候选人中选择合伙人"
```

### 决策点1：选择哪位候选人

```yaml
decision_point:
  dp_id: DP-002-01
  dp_sequence: 1
  total_dps: 2

context:
  description: "孵化器项目需要选择技术合伙人，3个候选人"
  decision_type: "多选一"

information_completeness:
  score: 0.6
  known_factors:
    - "3位候选人的技术背景"
    - "过往项目经历"
    - "初步沟通印象"
  unknown_factors:
    - "实际工作能力"
    - "团队配合度"
    - "长期承诺"

time_pressure:
  level: "中"
  deadline: "2周内"

cognitive_biases:
  - type: "光环效应"
    severity: "中"
    description: "被候选人A的名校背景吸引"
  - type: "可得性启发"
    severity: "中"
    description: "候选人B最近的项目更容易回忆"

intuition_signal:
  body_reaction: "与候选人C交流时感到放松"
  emotion: "候选人A有压迫感，候选人B有距离感，候选人C有亲近感"
  description: "候选人C给人'对的人'的感觉"
  intensity: "中"

rational_analysis:
  methods_used: ["评分卡", "背景调查", "模拟项目讨论"]
  score_card:
    - candidate: "A"
      tech: 9
      communication: 6
      reliability: 7
      total: 22
    - candidate: "B"
      tech: 7
      communication: 7
      reliability: 6
      total: 20
    - candidate: "C"
      tech: 8
      communication: 9
      reliability: 8
      total: 25
  conclusion: "理性分析支持候选人C"

final_decision:
  choice: "候选人C"
  reason: "理性评分最高，直觉也认同"
  basis: "平衡"  # 理性50%，直觉50%
  confidence: 0.8

outcome_feedback:
  short_term: "合作顺利启动，沟通高效"
  medium_term: "项目进展顺利，团队配合良好"
  long_term: "合作2年，项目成功退出"
  conclusion: "决策正确"

pattern_extraction:
  pattern: "理性评分高 + 直觉舒适 = 选择"
  pattern_type: "数据驱动型"
  conditions:
    - "多维度评分系统显示明显优势"
    - "直觉信号与理性一致"
    - "有充足时间验证"
  recommendation: "选择"
  accuracy_rate: 1.0

training_labels:
  decision_quality: 1.0
  pattern_type: "数据驱动型"
  risk_level: "中"
  urgency_level: "中"
```

---

## 数据统计

### 标注概况

| 指标 | 数值 |
|------|------|
| 案例总数 | 2（示例） |
| 决策点总数 | 3（示例） |
| 平均信息完备度 | 0.47 |
| 高时间压力占比 | 33% |
| 直觉主导决策占比 | 33% |
| 理性主导决策占比 | 0% |
| 平衡决策占比 | 67% |
| 决策正确率 | 100% |

### 模式分布

| 模式类型 | 数量 | 占比 |
|----------|------|------|
| 风险规避型 | 1 | 33% |
| 边界保护型 | 1 | 33% |
| 数据驱动型 | 1 | 33% |

### 认知偏差分布

| 偏差类型 | 出现次数 | 平均严重程度 |
|----------|----------|--------------|
| 损失厌恶 | 1 | 高 |
| 禀赋效应 | 1 | 中 |
| 现状偏见 | 1 | 高 |
| 锚定效应 | 1 | 中 |
| 互惠原则 | 1 | 中 |
| 光环效应 | 1 | 中 |
| 可得性启发 | 1 | 中 |

---

## 使用说明

### 训练价值网络

```python
from dataset import DecisionPatternDataset

# 加载数据集
dataset = DecisionPatternDataset("decision-patterns.yaml")

# 提取特征和标签
features = dataset.extract_features([
    "information_completeness",
    "time_pressure",
    "cognitive_biases",
    "intuition_signal"
])

labels = dataset.extract_labels("decision_quality")

# 训练模型
trainer = ValueNetworkTrainer()
model = trainer.train(features, labels)
```

### 模式查询

```python
# 查询相似模式
similar_patterns = dataset.find_similar(
    context="创业邀请",
    biases=["损失厌恶"],
    intuition="不适"
)

# 获取模式推荐
recommendation = dataset.get_recommendation(
    pattern_type="风险规避型",
    conditions=["直觉不适", "时间压力"]
)
```

---

*数据集版本：v0.1（示例）*
*创建时间：2026-03-15*
*完整数据集目标：500个决策点*
