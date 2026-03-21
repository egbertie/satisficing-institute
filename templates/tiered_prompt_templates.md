---
name: tiered-prompt-templates
version: 1.0.0
description: 分级提示词模板系统 - 降低Token消耗
---

# 分级提示词模板系统

## 使用指南

根据任务复杂度和Token预算选择合适级别：
- **L1**: 极简版 (<100 tokens) - 日常简单任务
- **L2**: 标准版 (200-400 tokens) - 常规任务
- **L3**: 完整版 (按需) - 复杂任务/首次使用

---

## L1 - 极简模板

### 通用执行模板
```markdown
# {task_type}
**输入**: {input}
**输出**: {expected_output}
**约束**: {constraints}
执行。
```
*Token: ~60*

### Skill执行模板
```markdown
# {skill_name} - 执行
输入: {input_data}
要求: {requirements}
输出格式: {format}
```
*Token: ~50*

### 代码审查模板
```markdown
审查: {file_path}
检查: 语法|逻辑|规范
输出: 问题列表+修复建议
```
*Token: ~40*

### 数据分析模板
```markdown
分析: {data_source}
目标: {analysis_goal}
输出: 关键发现+建议
```
*Token: ~45*

---

## L2 - 标准模板

### 通用执行模板
```markdown
# {task_type} 执行规范

## 输入
- 类型: {input_type}
- 格式: {input_format}
- 示例: {input_example}

## 处理流程
1. {step_1}
2. {step_2}
3. {step_3}

## 输出要求
- 格式: {output_format}
- 约束: {constraints}
- 质量: {quality_criteria}
```
*Token: ~300*

### Skill开发模板
```markdown
# Skill开发规范

## 需求
- 名称: {skill_name}
- 功能: {function_description}
- 标准: 5/7标准

## 结构
1. SKILL.md (文档)
2. config.yaml (配置)
3. scripts/ (脚本)
4. tests/ (测试)

## 检查项
- [ ] S1-S7完整
- [ ] 示例可运行
- [ ] 错误处理
```
*Token: ~350*

### 质量审查模板
```markdown
# 质量审查 - {target_type}

## 检查维度
| 维度 | 权重 | 方法 |
|------|------|------|
| 语法 | 25% | 静态检查 |
| 逻辑 | 35% | 代码走查 |
| 规范 | 20% | 规则匹配 |
| 性能 | 20% | 复杂度分析 |

## 输出
1. 评分 (A/B/C/D)
2. 问题清单
3. 修复建议
```
*Token: ~380*

### 报告生成模板
```markdown
# 报告生成 - {report_type}

## 数据源
- 日志: {log_source}
- 指标: {metrics}
- 时间范围: {time_range}

## 内容结构
1. 执行摘要
2. 关键发现
3. 趋势分析
4. 建议措施

## 格式要求
- 语言: 中文
- 图表: 必要时
- 长度: {length_limit}
```
*Token: ~320*

---

## L3 - 完整模板

### Skill完整开发模板
```markdown
---
name: {skill_name}
version: 1.0.0
standard: 5|7
tags: [{tags}]
---

# {skill_name} Skill

## 概述
{detailed_description}

## S1: 输入规范
### 输入参数
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| {param1} | {type} | {required} | {default} | {description} |

### 输入示例
```json
{input_example}
```

## S2: 处理流程
### 流程图
```
[输入] → [验证] → [处理] → [验证] → [输出]
```

### 详细步骤
1. **步骤1**: {step_detail_1}
2. **步骤2**: {step_detail_2}
3. **步骤3**: {step_detail_3}

### 异常处理
| 异常类型 | 处理方式 | 日志级别 |
|----------|----------|----------|
| {exception1} | {handler1} | {level1} |

## S3: 输出规范
### 输出格式
```json
{output_schema}
```

### 输出示例
```json
{output_example}
```

## S4: 触发方式
### 手动触发
```bash
{manual_command}
```

### 自动触发
```yaml
# cron.yaml
cron: {schedule}
```

## S5: 验证方法
### 检查清单
- [ ] {check_item_1}
- [ ] {check_item_2}
- [ ] {check_item_3}

### 测试用例
| 用例ID | 输入 | 预期输出 | 验证方式 |
|--------|------|----------|----------|
| TC001 | {input1} | {output1} | 自动 |

## S6: 局限标注
1. {limitation_1}
2. {limitation_2}
3. {limitation_3}

## S7: 对抗测试
### 测试场景
| 场景 | 异常输入 | 预期行为 |
|------|----------|----------|
| {scenario1} | {bad_input1} | {expected1} |

## 附录
### 依赖项
- {dependency_1}
- {dependency_2}

### 变更历史
| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | {date} | 初始版本 |
```
*Token: ~1,500-2,500*

---

## 模板选择决策树

```
任务开始
  │
  ├─ Token预算 < 30% ? ──→ L1 极简版
  │
  ├─ 首次执行/复杂任务 ? ──→ L3 完整版
  │
  └─ 常规任务 ──→ L2 标准版
```

---

## Token节省效果

| 使用场景 | 原Token | 优化后 | 节省率 |
|----------|---------|--------|--------|
| 日常查询 | 800 | 60 | 92% |
| Skill执行 | 1,200 | 300 | 75% |
| 代码审查 | 1,000 | 400 | 60% |
| 报告生成 | 2,000 | 350 | 82% |
| **日均综合** | **15,000** | **4,500** | **70%** |

---

## 使用建议

1. **默认使用L2**: 平衡信息量与Token消耗
2. **紧急任务用L1**: 快速响应，节省Token
3. **复杂任务用L3**: 确保完整性
4. **建立习惯**: 用户可使用 /brief /normal /detail 指令切换

---

*模板版本: 1.0.0*  
*最后更新: 2026-03-21*
