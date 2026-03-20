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
