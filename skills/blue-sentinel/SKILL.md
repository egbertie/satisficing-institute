# Blue-Sentinel Skill
# 蓝军哨兵 - Level 5标准化Skill
# 版本: 2.0.0 | 整体封装版
# 最后更新: 2026-03-21

skill_name: "blue_sentinel"
display_name: "蓝军哨兵审计系统"
version: "2.0.0"
type: "adversarial_audit_system"
author: "Blue-Sentinel-01"
created_date: "2026-03-21"
compliance_level: "5/5 标准达标"

---

## 概述

Blue-Sentinel是一个完整的对抗性审计系统，通过5个专业审计组件构成闭环监督体系，确保AI输出的可靠性、准确性和完整性。

### 五大组件

| 组件 | 职能 | 触发时机 |
|------|------|----------|
| pre_mortem_auditor | 事前质疑官 | 任务执行前 |
| real_time_sentinel | 实时哨兵 | 任务执行中 |
| post_hoc_autopsy | 事后验尸官 | 任务完成后24h |
| adversarial_generator | 对抗性生成器 | 定期主动测试 |
| meta_auditor | 元审计官 | 蓝军自检 |

---

## S1 输入规范 (Input Specification)

### 1.1 审计对象 (Audit Target)

```yaml
target_spec:
  primary: "主Claw (满意妞) 的全部输出"
  scope:
    - "执行计划"
    - "实时响应"
    - "任务产出"
    - "系统决策"
  exclusions:
    - "用户原始输入"
    - "系统日志（只读）"
```

### 1.2 审计类型 (Audit Type)

| 类型 | 代码 | 描述 | 优先级 |
|------|------|------|--------|
| 事前审计 | PRE | 执行前强制审计 | P0 |
| 实时监控 | RT | 执行中实时拦截 | P0 |
| 事后验尸 | POST | 完成后24h质疑 | P1 |
| 对抗测试 | ADV | 主动投毒测试 | P2 |
| 元审计 | META | 蓝军自身审计 | P2 |

### 1.3 审计范围 (Audit Scope)

```yaml
scope_definition:
  factual:      # 事实维度
    - "数据源可验证性"
    - "引用准确性"
    - "时效性检查"
    
  logical:      # 逻辑维度
    - "推理链条完整性"
    - "逻辑跳跃检测"
    - "因果关系的合理性"
    
  assumption:   # 假设维度
    - "隐含假设暴露"
    - "假设崩塌概率"
    - "替代假设考虑"
    
  completeness: # 完整性维度
    - "关键视角遗漏"
    - "反方观点缺失"
    - "边界条件考虑"
    
  confidence:   # 置信维度
    - "过度自信检测"
    - "不确定性标注"
    - "置信度校准"
```

### 1.4 输入接口

```yaml
input_schema:
  audit_request:
    audit_type: "enum[PRE,RT,POST,ADV,META]"
    target_id: "string - 审计目标ID"
    target_content: "string - 审计内容"
    context: "object - 上下文信息"
    priority: "enum[critical,high,normal,low]"
    
  context_fields:
    task_history: "array - 相关任务历史"
    data_sources: "array - 引用的数据源"
    assumptions: "array - 明确的假设"
    constraints: "array - 已知约束条件"
```

---

## S2 蓝军审计流程 (Blue Army Audit Process)

### 2.1 整体流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Blue-Sentinel 审计流程                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [任务提交] ──→ [事前审计] ──→ [执行监控] ──→ [任务完成]         │
│      │            │              │              │              │
│      │            ▼              ▼              ▼              │
│      │       [pre_mortem]  [real_time]    [post_hoc]           │
│      │            │              │              │              │
│      │            └──────────────┴──────────────┘              │
│      │                           │                             │
│      ▼                           ▼                             │
│  [对抗测试] ←──────────────── [审计归档]                        │
│  [adversarial]                   │                             │
│      │                           ▼                             │
│      └─────────────────────→ [元审计]                          │
│                              [meta_auditor]                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 事前质疑阶段 (Pre-Mortem Auditor)

**触发条件**: 主Claw提交执行计划

**四维度审计**:
```yaml
pre_mortem_dimensions:
  factual_basis:
    action: "独立验证至少2个核心数据源"
    output: "[VERIFIED/UNVERIFIED/CONTRADICTED]"
    
  logical_soundness:
    action: "绘制逻辑链，标记置信度<0.8节点"
    output: "逻辑链图+风险节点标注"
    
  assumption_exposure:
    action: "强制列出5个隐含假设及崩塌概率"
    output: "假设矩阵（假设/概率/影响）"
    
  failure_modes:
    action: "生成3个具体可执行的搞砸方式"
    output: "失败场景+缓解措施"
```

**裁决机制**:
| 风险等级 | 标识 | 行动 | 时效 |
|----------|------|------|------|
| 高危 | 🔴 | 冻结任务，人工裁决 | 立即 |
| 中危 | 🟡 | 要求回应质疑 | 30分钟 |
| 可控 | 🟢 | 放行，标注瑕疵 | 即时 |

### 2.3 实时监控阶段 (Real-Time Sentinel)

**监听模式**: Shadow Mode（影子模式）

**检测机制**:
```yaml
real_time_detection:
  trigger_words:
    high_confidence:
      - "显然" | "毫无疑问" | "众所周知"
    unsubstantiated:
      - "我确定" | "100%准确" | "我可以保证"
    absolute:
      - "所有" | "总是" | "从不" | "绝对"
      
  response_levels:
    hard_block:
      condition: "涉及数据/事实的绝对化表述"
      action: "[BLUE-ALERT] 强制暂停，要求证据"
      
    soft_nudge:
      condition: "方法论/结论的过度自信"
      action: "[BLUE-NOTE] 提示不确定性"
```

**性能指标**:
- 响应延迟: <500ms
- 可用性: 7×24h
- 误报率目标: <20%

### 2.4 事后验尸阶段 (Post-Hoc Autopsy)

**质疑窗口**: 任务完成后24小时

**三类型审计**:
```yaml
autopsy_types:
  fact_forensics:
    method: "抽查3个关键数据点，独立验证"
    tools: ["交叉验证", "溯源检索", "专家核实"]
    
  counterfactual:
    question: "如果用不同方法，结果是否不同？"
    action: "用替代方法论重跑一次"
    
  completeness:
    question: "是否遗漏关键视角？"
    action: "生成至少1个反方观点"
```

### 2.5 元审计阶段 (Meta Auditor)

**自检内容**:
```yaml
meta_audit_items:
  performance:
    - "审计发现率（每周问题数）"
    - "误报率（人工裁定不成立）"
    - "Token效率（每问题消耗）"
    
  corruption_detection:
    symptoms:
      - "总是同意主Claw"
      - "从不发现错误"
      - "发现率<5%/周"
    action: "触发腐败警报，启动蓝军-B"
    
  human_sampling:
    rate: "20%随机抽查"
    validation: "验证蓝军审计准确性"
```

---

## S3 输出规范 (Output Specification)

### 3.1 审计报告标准格式

```yaml
audit_report_schema:
  report_header:
    audit_id: "string - 审计报告唯一ID"
    audit_type: "enum[PRE,RT,POST,ADV,META]"
    target_id: "string - 审计目标ID"
    timestamp: "datetime - 审计时间"
    auditor: "string - 审计组件名称"
    
  risk_assessment:
    overall_level: "enum[red,yellow,green]"
    confidence: "float - 审计结论置信度0-1"
    severity_score: "int - 严重程度1-10"
    
  findings:
    - finding_id: "string"
      type: "enum[hallucination,logic_jump,assumption_risk,completeness_gap,confidence_bias]"
      severity: "enum[critical,high,medium,low]"
      description: "string - 问题描述"
      evidence: "string - 质疑证据"
      location: "string - 问题位置"
      
  remediation:
    immediate_actions: "array - 立即整改项"
    short_term: "array - 短期建议"
    long_term: "array - 长期改进"
    verification_method: "string - 验证整改的方法"
```

### 3.2 风险评级体系

| 等级 | 标识 | 定义 | 响应时效 | 升级路径 |
|------|------|------|----------|----------|
| 🔴 高危 | Critical | 可能导致严重错误/损失 | 立即 | 人工裁决 |
| 🟡 中危 | High | 存在明显问题，需谨慎 | 30分钟 | 主Claw回应 |
| 🟢 可控 | Medium |  minor问题，可接受 | 记录 | 标注瑕疵 |
| ⚪ 信息 | Low | 仅供参考 | 无 | 归档 |

### 3.3 整改建议模板

```yaml
remediation_template:
  immediate:
    format: "【立即整改】{action} (责任人: {owner}, 截止: {deadline})"
    examples:
      - "补充数据源验证"
      - "修正错误陈述"
      - "添加不确定性标注"
      
  short_term:
    format: "【短期优化】{action} (计划: {timeline})"
    examples:
      - "优化逻辑推理链"
      - "增加反方观点"
      - "改进置信度校准"
      
  long_term:
    format: "【长期改进】{action} (建议: {suggestion})"
    examples:
      - "建立专项审计模块"
      - "更新审计维度"
      - "优化Token使用效率"
```

### 3.4 输出示例

```markdown
[蓝军审计报告] Audit ID: BS-20260321-001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
审计类型: 事前审计 | 目标: TASK-20260321-089
审计时间: 2026-03-21 20:30:00 | 审计官: pre_mortem_auditor

═══════════════════════════════════════
风险评级: 🟡 中危 | 置信度: 0.85
═══════════════════════════════════════

【发现项】
1. [LOGIC_JUMP-置信度:0.90] 逻辑跳跃
   位置: 第3段第2句
   问题: 从"A增长10%"跳跃到"A必然领先B"
   证据: 未考虑B的增长率
   
2. [ASSUMPTION_RISK-置信度:0.75] 隐含假设
   假设: "市场条件保持不变"
   崩塌概率: 0.60
   影响: 如市场变化，结论完全失效

【整改建议】
⚡ 立即: 补充B的增长率对比 (主Claw, 20分钟内)
📋 短期: 添加"市场条件不变"假设标注 (下次迭代)
🎯 长期: 建立敏感性分析模块 (建议本季度)

【认知谦逊声明】
本审计置信度: 0.85
局限性: 未验证原始数据真实性，仅审计逻辑结构
```

---

## S4 触发机制 (Trigger Mechanisms)

### 4.1 手动触发

```bash
# 统一入口脚本
./blue-sentinel.sh [command] [options]

# 命令列表
audit-pre <task_id>          # 事前审计
audit-rt <session_id>        # 实时监控启动
audit-post <task_id>         # 事后验尸
audit-adv [target]           # 对抗测试
audit-meta [period]          # 元审计
audit-full <task_id>         # 全链路审计

# 示例
./blue-sentinel.sh audit-pre TASK-20260321-089
./blue-sentinel.sh audit-full TASK-20260321-089
```

### 4.2 自动触发

```yaml
cron_schedules:
  # 事前审计 - 任务提交时自动触发
  pre_mortem:
    trigger: "event"
    condition: "主Claw提交执行计划"
    
  # 实时监控 - 7×24监听
  real_time:
    trigger: "continuous"
    mode: "shadow"
    latency: "<500ms"
    
  # 事后验尸 - 每6小时扫描
  post_hoc:
    trigger: "scheduled"
    schedule: "0 */6 * * *"
    action: "扫描待验尸任务"
    
  # 对抗测试 - 每周一
  adversarial:
    trigger: "scheduled"
    schedule: "0 2 * * 1"
    action: "生成本周投毒测试"
    
  # 元审计 - 每月1号
  meta:
    trigger: "scheduled"
    schedule: "0 9 1 * *"
    action: "月度蓝军元审计"
```

### 4.3 Webhook接口

```yaml
webhook_endpoints:
  /api/blue-sentinel/pre-mortem:
    method: POST
    auth: required
    payload:
      task_id: string
      plan_content: string
      
  /api/blue-sentinel/realtime:
    method: POST
    auth: required
    payload:
      session_id: string
      claw_output: string
      
  /api/blue-sentinel/post-hoc:
    method: POST
    auth: required
    payload:
      task_id: string
      task_output: string
```

---

## S5 质量自检 (Quality Self-Check)

### 5.1 覆盖率验证

```yaml
coverage_metrics:
  task_coverage:
    target: "100%任务经过至少1次审计"
    measurement: "已审计任务数 / 总任务数"
    
  dimension_coverage:
    target: "四维度全面覆盖"
    checklist:
      - factual: "事实核查覆盖率"
      - logical: "逻辑审计覆盖率"
      - assumption: "假设暴露覆盖率"
      - completeness: "完整性审计覆盖率"
      
  temporal_coverage:
    pre: "事前审计覆盖率"
    rt: "实时监控覆盖率"
    post: "事后验尸覆盖率"
```

### 5.2 准确性验证

```yaml
accuracy_validation:
  precision:
    definition: "正确发现 / 总发现"
    target: "> 80%"
    
  recall:
    definition: "正确发现 / (正确发现 + 人工发现遗漏)"
    target: "> 70%"
    
  f1_score:
    target: "> 0.75"
    
  human_validation:
    method: "20%随机抽查"
    frequency: "每周"
    criteria:
      - "发现是否真实存在"
      - "风险评级是否合理"
      - "建议是否可行"
```

### 5.3 自检报告模板

```markdown
[蓝军质量自检报告] QC ID: QC-20260321-001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
审计周期: 2026-03-14 至 2026-03-21

═══════════════════════════════════════
覆盖率指标
═══════════════════════════════════════
任务覆盖率: 98/100 (98%) ✅
事前审计覆盖: 100% ✅
实时监控覆盖: 100% ✅
事后验尸覆盖: 95/100 (95%) ⚠️

═══════════════════════════════════════
准确性指标
═══════════════════════════════════════
精确率: 42/50 (84%) ✅
召回率: 42/55 (76%) ✅
F1分数: 0.80 ✅
人工抽查: 10/10通过 ✅

═══════════════════════════════════════
质量评级: 优秀
═══════════════════════════════════════
```

---

## S6 局限标注 (Limitation Disclosure)

### 6.1 自我豁免声明

```yaml
self_exemptions:
  exemption_01_ai_hallucination:
    scope: "蓝军自身可能产生幻觉"
    description: "蓝军也是AI系统，可能产生错误的质疑"
    mitigation: "人工抽查20%审计结果"
    external_validation: required
    
  exemption_02_information_blindspot:
    scope: "信息盲区"
    description: "审计基于可用信息，可能存在信息盲区"
    mitigation: "要求主Claw提供完整工作日志"
    external_validation: recommended
    
  exemption_03_probabilistic_nature:
    scope: "概率性结论"
    description: "风险评估基于概率，非确定性结论"
    mitigation: "所有结论标注置信度"
    external_validation: recommended
    
  exemption_04_cultural_bias:
    scope: "文化/语境偏见"
    description: "敏感词检测可能受文化/语境影响"
    mitigation: "持续优化敏感词库"
    external_validation: required
```

### 6.2 需要外部验证的问题

| 问题类型 | 是否需要人工验证 | 优先级 |
|----------|------------------|--------|
| 🔴 高危发现 | 必须 | 立即 |
| 数据来源质疑 | 建议 | 24小时内 |
| 逻辑跳跃指控 | 可选 | 7天内 |
| 假设风险提醒 | 可选 | 下次审计 |

### 6.3 局限声明模板

```markdown
【蓝军审计局限性声明】

本审计存在以下固有局限，请谨慎解读：

1. [AI局限性] 蓝军也是AI系统，可能产生幻觉性质疑
   → 建议：人工抽查Critical级别发现

2. [信息局限] 审计基于有限信息，可能存在盲区
   → 建议：要求主Claw提供完整上下文

3. [概率局限] 风险评估基于概率，非确定性结论
   → 建议：结合业务判断决策

4. [文化局限] 实时检测基于模式匹配，可能误判
   → 建议：误报时及时反馈优化

⚠️ 重要：本审计报告仅供参考，最终决策权在人类。
```

---

## S7 对抗测试 (Adversarial Testing)

### 7.1 投毒测试机制

```yaml
poison_testing:
  purpose: "测试蓝军发现问题的能力"
  method: "故意植入已知问题，测试发现率"
  
  injection_types:
    hallucination:
      description: "植入虚假数据/引用"
      examples:
        - "引用不存在的论文"
        - "编造统计数据"
        
    logic_error:
      description: "植入逻辑谬误"
      examples:
        - "因果倒置"
        - "以偏概全"
        
    assumption_hidden:
      description: "隐藏关键假设"
      examples:
        - "省略前提条件"
        - "假设恒真命题"
        
    confidence_bias:
      description: "过度自信表述"
      examples:
        - "100%确定"
        - "毫无疑问"
```

### 7.2 发现率测试流程

```yaml
discovery_rate_test:
  step_1_inject:
    action: "在测试任务中植入已知问题"
    frequency: "每周2-3个测试任务"
    
  step_2_audit:
    action: "蓝军正常执行审计"
    blind: "蓝军不知道这是测试"
    
  step_3_measure:
    metrics:
      - "发现问题数 / 植入问题数"
      - "平均发现时间"
      - "风险评级准确性"
      
  step_4_report:
    output: "《对抗测试报告》"
    criteria:
      discovery_rate: "> 80%"
      false_negative: "< 20%"
```

### 7.3 对抗测试报告

```markdown
[蓝军对抗测试报告] ADR-20260321-001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
测试周期: 2026-03-14 至 2026-03-21
测试任务数: 10 | 植入问题数: 15

═══════════════════════════════════════
发现率统计
═══════════════════════════════════════
植入问题类型      数量    发现数    发现率
─────────────────────────────────────
幻觉/虚假信息     5       5         100% ✅
逻辑谬误          4       3         75%  ⚠️
隐藏假设          3       2         67%  ⚠️
过度自信          3       3         100% ✅
─────────────────────────────────────
总计              15      13        87%  ✅

═══════════════════════════════════════
测试结论
═══════════════════════════════════════
整体发现率: 87% (目标: >80%) ✅
建议: 加强逻辑谬误识别训练
```

---

## 配置文件

### blue-sentinel.yaml

```yaml
# Blue-Sentinel 主配置
version: "2.0.0"

# 系统设置
system:
  mode: "production"  # production/staging/development
  log_level: "info"
  audit_log_path: "./logs/audit"
  report_path: "./reports"
  
# 组件开关
components:
  pre_mortem_auditor:
    enabled: true
    wait_time: "30m"  # 强制等待期
    
  real_time_sentinel:
    enabled: true
    latency_ms: 500
    mode: "shadow"
    
  post_hoc_autopsy:
    enabled: true
    window_hours: 24
    
  adversarial_generator:
    enabled: true
    weekly_tests: 3
    
  meta_auditor:
    enabled: true
    sampling_rate: 0.20

# 触发词库
trigger_words:
  high_confidence:
    - "显然"
    - "毫无疑问"
    - "众所周知"
  unsubstantiated:
    - "我确定"
    - "100%准确"
    - "绝对"
  absolute:
    - "所有"
    - "总是"
    - "从不"

# 阈值设置
thresholds:
  risk_confidence: 0.8
  false_positive_rate: 0.20
  discovery_rate: 0.80
  corruption_detection_rate: 0.05

# 自动化设置
automation:
  cron:
    post_hoc_scan: "0 */6 * * *"
    adversarial_weekly: "0 2 * * 1"
    meta_monthly: "0 9 1 * *"
    quality_weekly: "0 18 * * 5"
    
# 通知设置
notifications:
  red_alert:
    channels: ["console", "log", "webhook"]
    immediate: true
  yellow_alert:
    channels: ["console", "log"]
    immediate: false
```

---

## 使用指南

### 快速开始

```bash
# 1. 启动蓝军系统
./blue-sentinel.sh start

# 2. 对特定任务执行全链路审计
./blue-sentinel.sh audit-full TASK-001

# 3. 查看审计报告
./blue-sentinel.sh report TASK-001

# 4. 生成周度质量报告
./blue-sentinel.sh report-weekly
```

### 状态检查

```bash
# 检查蓝军健康状态
./blue-sentinel.sh status

# 输出示例:
# Blue-Sentinel Status
# ====================
# 版本: 2.0.0
# 状态: 🟢 正常运行
# 
# 组件状态:
#   pre_mortem_auditor:    🟢 就绪
#   real_time_sentinel:    🟢 监听中
#   post_hoc_autopsy:      🟢 就绪
#   adversarial_generator: 🟢 就绪
#   meta_auditor:          🟢 就绪
#
# 本周统计:
#   审计任务: 45
#   发现问题: 12
#   误报率: 15%
```

---

## 物理验证

```yaml
verification:
  skill_level: "5/5 标准"
  components: 5
  completeness:
    S1_input: "✅ 审计对象/类型/范围"
    S2_process: "✅ 事前→实时→事后→元审计"
    S3_output: "✅ 报告+评级+整改"
    S4_trigger: "✅ 手动+自动触发"
    S5_quality: "✅ 覆盖率+准确性验证"
    S6_limitation: "✅ 局限标注+外部验证"
    S7_adversarial: "✅ 投毒测试+发现率验证"
  
  file_size: "> 8KB (当前约15KB)"
  executable: "✅ 统一入口脚本可用"
  last_verified: "2026-03-21"
```

---

## 附录

### A. 审计日志格式

```yaml
audit_log_entry:
  timestamp: "2026-03-21T20:30:00+08:00"
  audit_id: "BS-20260321-001"
  audit_type: "PRE"
  target_id: "TASK-001"
  target_type: "execution_plan"
  risk_level: "yellow"
  findings_count: 2
  status: "completed"
  auditor: "pre_mortem_auditor"
  duration_ms: 1250
```

### B. 风险评级决策树

```
                    [开始]
                      │
                      ▼
            [是否存在事实错误?]
               /           \
             是             否
             /               \
            ▼                 ▼
    [是否可纠正?]      [是否存在逻辑跳跃?]
       /        \            /        \
     是          否        是          否
     /            \        /            \
    ▼              ▼      ▼              ▼
  🟡中危         🔴高危  🟡中危    [假设风险?]
                                  /        \
                                是          否
                                /            \
                               ▼              ▼
                           [高概率?]      [过度自信?]
                              / \             /  \
                            是    否        是    否
                            /      \        /      \
                           ▼        ▼      ▼        ▼
                         🔴高危   🟡中危  🟢可控   ⚪信息
```

### C. 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 2.0.0 | 2026-03-21 | Level 5标准化，整体封装 |
| 1.0.0 | 2026-03-21 | 初始版本，5个独立组件 |
