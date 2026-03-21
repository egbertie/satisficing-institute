# Universal Checklist Enforcer Skill

## Purpose
强制所有任务执行前通过5项核心检查，防止"做了白做"、"幻觉"、"执行不到位"

## 5-Standard Compliance

| Standard | Implementation |
|----------|----------------|
| 全局考虑 | 覆盖所有任务类型的通用验证层 |
| 系统考虑 | 检查→评估→通过/阻塞→记录→反馈闭环 |
| 迭代机制 | 根据任务失败模式更新检查项 |
| Skill化 | 元控制技能，所有任务前自动触发 |
| 自动化 | 每次任务执行前强制运行，无法跳过 |

## Commands
- `enforce` - 执行强制检查清单
- `report` - 生成检查历史报告
- `update` - 根据失败模式更新检查项

## Checklist Template (强制执行)

```yaml
checklist_v1:
  - id: C1
    name: "任务定义SMART检查"
    description: "目标是否具体/可衡量/可实现/相关/有时限"
    pass_criteria: 
      - "Specific: 明确说明要解决什么问题"
      - "Measurable: 有明确的完成标准"
      - "Achievable: 在给定资源内可完成"
      - "Relevant: 与战略目标相关"
      - "Time-bound: 有明确的deadline"
    block_on_fail: true
    
  - id: C2
    name: "输入完整性检查"
    description: "是否提供了所有必要文件/数据/上下文"
    pass_criteria:
      - "列出所有必需的输入项"
      - "明确标注缺失项（如有）"
      - "缺失项风险评估（阻塞/可延后）"
    block_on_fail: true
    
  - id: C3
    name: "幻觉预防检查"
    description: "关键数据是否标注来源和置信度"
    pass_criteria:
      - "每个事实标注来源（文档/网页/记忆/推理）"
      - "每个事实标注置信度（高/中/低）"
      - "置信度<中 的信息明确标注[待验证]"
    block_on_fail: false
    warning_threshold: 1
    
  - id: C4
    name: "深度检查"
    description: "是否使用MECE原则，无遗漏无重叠"
    pass_criteria:
      - "Mutually Exclusive: 各部分相互独立"
      - "Collectively Exhaustive: 完全穷尽无遗漏"
      - "至少3个维度分析"
      - "每个维度至少3个要点"
    block_on_fail: false
    
  - id: C5
    name: "闭环设计检查"
    description: "产出物的下一步行动明确"
    pass_criteria:
      - "明确下一步行动（Action）"
      - "明确负责人（Owner）"
      - "明确截止时间（Deadline）"
      - "明确成功标准（Success Criteria）"
    block_on_fail: true
```

## Output Format (强制)

```
[强制检查清单报告]
任务ID: [TASK-ID]
检查时间: [ISO8601]
检查员: universal-checklist-enforcer

| 检查项 | 状态 | 备注 |
|--------|------|------|
| C1 SMART | ✅/❌ | |
| C2 输入完整 | ✅/❌ | 缺失项: [list] |
| C3 幻觉预防 | ✅/⚠️ | 待验证项: [N] |
| C4 深度检查 | ✅/⚠️ | MECE评分: [X/10] |
| C5 闭环设计 | ✅/❌ | 下一步: [action] |

[综合评估]
阻塞项数: [N]
警告项数: [N]
检查结果: [PASS / BLOCK]

[如BLOCK]
阻塞原因: [详细说明]
需补充: [具体行动]

[如PASS]
允许进入执行阶段
建议关注: [警告项改进建议]
```

## Enforcement Rules

1. **不可跳过**: 任何任务必须完成检查清单，无例外
2. **阻塞强制**: 任一block_on_fail=true项未通过，任务状态强制设为[BLOCKED]
3. **记录强制**: 所有检查结果写入`memory/checklist_logs/`
4. **反馈强制**: 每周生成检查质量报告，识别高频失败项

## Cron

```json
{
  "jobs": [
    {
      "name": "checklist-quality-audit",
      "schedule": "47 18 * * 5",
      "command": "cd /root/.openclaw/workspace/skills/universal-checklist-enforcer && python3 scripts/enforcer.py report",
      "description": "每周五检查清单质量审计"
    }
  ]
}
```

## Integration

所有Skill必须在开头调用:
```yaml
pre_execution:
  - skill: universal-checklist-enforcer
    command: enforce
    blocking: true
```

## Version History

- v1.0 (2026-03-20): 初始5项检查清单

---

## S7: 对抗验证 (Devil's Advocate Views)

### 反方观点：这个Skill可能失效的场景

#### 观点1：检查清单本身成为形式主义
**提出者**: 蓝军
**论据**: 
- 强制执行可能导致"为了检查而检查"，而非真正提升质量
- 用户可能学会"填满表格"而非"深度思考"
- 检查时间可能超过任务执行时间，效率倒挂

**失效场景**:
```yaml
scenario: 检查清单疲劳
触发条件:
  - 连续10个任务都通过检查
  - 检查耗时 > 任务执行时间50%
  - 用户开始机械勾选而非深度思考
后果: 检查清单沦为形式，质量不升反降
```

#### 观点2：过度阻塞扼杀创新
**提出者**: 蓝军
**论据**:
- block_on_fail=true可能阻止必要的试错
- 创新任务往往不符合SMART（结果不确定）
- 可能导致"只做安全的事"

**失效场景**:
```yaml
scenario: 创新任务被阻塞
触发条件:
  - 探索性任务（如"试试新工具"）
  - 无法定义明确的Measurable标准
  - 强制要求SMART导致任务无法启动
后果: 系统倾向于保守，创新被抑制
```

#### 观点3：检查项更新滞后
**提出者**: 蓝军
**论据**:
- "根据失败模式更新"依赖人工发现
- 新型失败模式可能长时间不被识别
- 检查清单逐渐脱离实际风险

**失效场景**:
```yaml
scenario: 检查项老化
触发条件:
  - 连续30天检查项无更新
  - 实际任务失败原因不在检查清单中
  - 检查通过但任务仍失败
后果: 检查清单与实际风险脱节
```

### 缓解措施（已实施）

| 反方观点 | 缓解措施 |
|---------|----------|
| 形式主义 | 每周质量审计，识别"机械勾选"模式 |
| 过度阻塞 | C3/C4设置为warning而非block |
| 检查项老化 | 强制每周迭代机制，无更新需说明 |

### 失效预警指标

```yaml
warning_indicators:
  - metric: 检查通过率
    threshold: >95%持续1周
    meaning: 可能沦为形式
    action: 触发深度审计
    
  - metric: 检查/执行时间比
    threshold: >50%
    meaning: 效率倒挂
    action: 简化检查项
    
  - metric: 检查项更新频率
    threshold: <1次/周
    meaning: 可能老化
    action: 强制更新或审查必要性
```

### 认知谦逊声明

- [KNOWN] 本Skill基于历史失败模式设计，对未来新型失败模式的覆盖有限
- [INFERRED] 检查项的权重和阻塞设置基于经验，未经严格A/B测试验证
- [UNKNOWN] 长期使用对组织创新文化的具体影响尚不明确
