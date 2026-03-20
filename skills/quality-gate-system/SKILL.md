---
name: quality-gate-system
version: 2.0.0
description: |
  质量门禁系统 - 研究/内容/代码的自动化质量检查：
  1. 全局考虑：覆盖人/事/物/环境/外部集成/边界情况
  2. 系统考虑：检查→评分→决策→反馈完整闭环
  3. 迭代机制：PDCA循环，版本历史，反馈收集
  4. Skill化：标准SKILL.md格式，可安装可调用
  5. 自动化：全自动检查+cron监控+自动报告
  6. 认知谦逊：检查结果置信度/局限标注(S6增强)
  7. 对抗验证：假阳性/假阴性分析(S7增强)
author: Satisficing Institute
tags:
  - quality
  5. automation
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3"]
---

# 质量门禁系统 Skill V2.0.0

## S1: 全局考虑 (Global Coverage)

### 1.1 人 - 质量干系人

| 干系人 | 质量关注点 | 权限 | 边界情况 |
|--------|------------|------|----------|
| Director | 战略质量、合规 | 最高决策 | 豁免权 |
| Captain | 任务质量、效率 | 质量通过权 | 降级放行 |
| Auditor | 检查执行、标准 | 否决权 | 强制阻断 |
| Specialist | 专业质量 | 自检权 | 申诉权 |
| 外部审计 | 独立验证 | 查阅权 | 报告权 |

### 1.2 事 - 五维质量检查

| 维度 | 检查内容 | 权重 | 边界情况 |
|------|----------|------|----------|
| **真实性** | 数据分级标注、来源可验证 | 25% | 无法验证时标记 |
| **溯源性** | 引用完整性、链接有效性 | 25% | 断链标记+存档 |
| **逻辑性** | 因果推断正确性、一致性 | 20% | 矛盾标记 |
| **完整性** | 要素全覆盖、无遗漏 | 15% | 缺失清单 |
| **可复现** | 方法论详细程度 | 15% | 步骤缺失标记 |

### 1.3 物 - 内容类型适配

| 内容类型 | 检查重点 | 通过阈值 | 特殊处理 |
|----------|----------|----------|----------|
| 研究报告 | 溯源性+逻辑性 | 80分 | 引用验证 |
| 营销文案 | 真实性+完整性 | 75分 | 合规检查 |
| 代码提交 | 可复现+逻辑性 | 85分 | 自动测试 |
| 文档更新 | 完整性+溯源性 | 70分 | 版本对比 |
| Skill文件 | 标准化+完整性 | 90分 | 5标准检查 |

### 1.4 环境 - 质量上下文

| 环境因素 | 调整策略 | 验证 |
|----------|----------|------|
| 紧急程度 | P0可降级通过 | 事后审计 |
| 领域特性 | 领域规则加载 | 专家复核 |
| 历史质量 | 信任分调整阈值 | 趋势分析 |
| 外部依赖 | 依赖项检查 | 可用性验证 |

### 1.5 外部集成

```yaml
integrations:
  honesty_tagging:
    type: 认知状态
    data_flow: "标注检查 → 质量评分"
    action: "验证KNOWN/INFERRED准确性"
  
  token_budget_enforcer:
    type: 效率监控
    data_flow: "产出/token → 效率评估"
    action: "低效内容标记"
  
  role_federation:
    type: 任务质量
    data_flow: "任务输出 → 质量检查"
    action: "阻断低质量输出"
  
  feishu_messaging:
    type: 通知推送
    data_flow: "检查结果 → 消息通知"
    action: "推送质量报告"
  
  git_workflow:
    type: CI/CD
    data_flow: "代码提交 → 自动检查"
    action: "阻断不合规提交"
```

### 1.6 边界情况处理

| 边界场景 | 检测 | 处理 |
|----------|------|------|
| 检查工具故障 | 超时/异常 | 人工接管+标记 |
| 标准冲突 | 多标准矛盾 | 优先级仲裁 |
| 内容过大 | 大小检测 | 分段检查+抽样 |
| 新类型内容 | 类型未知 | 通用检查+标记 |
| 豁免请求 | 人工申请 | 审计追踪+授权 |

---

## S2: 系统考虑 (Systematic)

### 2.1 质量门禁流程

```
内容输入 → 类型识别 → 五维检查 → 综合评分 → {≥阈值?}
  ├─ 是 → 标记通过 → 进入下一环节
  └─ 否 → 生成反馈 → 返回修改
                ↓
         效果追踪 ← 质量统计 ← 定期复盘
```

### 2.2 输入处理

| 输入类型 | 验证 | 转换 |
|----------|------|------|
| 文本内容 | 格式+编码 | 标准化文本 |
| 结构化数据 | Schema验证 | 内部格式 |
| 代码文件 | 语法检查 | AST解析 |
| 混合内容 | 组件分离 | 分别处理 |

### 2.3 检查引擎

```yaml
inspection_engine:
  dimension_reality:
    - 来源验证 (web_search/web_fetch)
    - 数据新鲜度检查
    - 偏见检测
  
  dimension_traceability:
    - 链接有效性检查
    - 引用格式验证
    - 去重检测
  
  dimension_logic:
    - 一致性检查
    - 因果链验证
    - 矛盾检测
  
  dimension_completeness:
    - 要素清单核对
    - 模板匹配
    - 缺失检测
  
  dimension_reproducibility:
    - 步骤完整性
    - 参数明确性
    - 环境说明
```

### 2.4 分级处理机制

| 评分区间 | 处理动作 | 人工介入 |
|----------|----------|----------|
| 90-100 | 自动通过 | 无需 |
| 75-89 | 自动通过+标记建议 | 可选 |
| 60-74 | 自动标记+等待确认 | 建议 |
| <60 | 自动拒绝+详细反馈 | 必须 |

### 2.5 反馈闭环

| 反馈类型 | 来源 | 应用 |
|----------|------|------|
| 修改结果 | 重新提交 | 验证改进 |
| 申诉反馈 | 人工申诉 | 规则优化 |
| 误报标记 | 用户标记 | 阈值调整 |
| 漏报发现 | 事后发现 | 检查项补充 |

### 2.6 故障处理

| 故障 | 检测 | 响应 |
|------|------|------|
| 检查超时 | 计时器 | 降级检查+告警 |
| 规则错误 | 验证失败 | 回滚规则 |
| 数据源失效 | 连接检测 | 切换备用源 |
| 评分异常 | 范围检查 | 人工复核 |

---

## S3: 迭代机制 (Iterative)

### 3.1 PDCA循环

```yaml
Plan(计划):
  - 每周制定质量目标
  - 设定通过率/准确率目标
  - 规划检查规则更新

Do(执行):
  - 执行自动化检查
  - 收集检查数据
  - 记录异常情况

Check(检查):
  - 统计通过率/误报率/漏报率
  - 分析质量问题模式
  - 评估检查效果

Act(改进):
  - 调整检查阈值
  - 优化检查规则
  - 更新维度权重
```

### 3.2 版本历史

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v2.0.0 | 2026-03-21 | 5+2标准全覆盖 | 满意解研究所 |
| v1.1.0 | 2026-03-19 | 增加CI/CD集成 | 满意解研究所 |
| v1.0.0 | 2026-03-20 | 五维检查初始版 | 满意解研究所 |

### 3.3 反馈收集

| 源 | 频率 | 用途 |
|----|------|------|
| 检查结果 | 每次 | 质量统计 |
| 申诉记录 | 每次 | 规则优化 |
| 趋势分析 | 每周 | 策略调整 |
| 外部审计 | 每月 | 体系改进 |

### 3.4 优化触发

| 指标 | 阈值 | 动作 |
|------|------|------|
| 误报率 | >10% | 阈值调整 |
| 漏报率 | >5% | 检查项补充 |
| 通过率骤降 | >20% | 专项审计 |
| 申诉率 | >15% | 规则重审 |

---

## S4: Skill化 (Skill-ified)

### 4.1 目录结构

```
quality-gate-system/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── quality_runner.py       # 主运行脚本
│   ├── dimension_reality.py    # 真实性检查
│   ├── dimension_traceability.py # 溯源性检查
│   ├── dimension_logic.py      # 逻辑性检查
│   ├── dimension_completeness.py # 完整性检查
│   ├── dimension_reproducibility.py # 可复现检查
│   ├── scorer.py               # 综合评分
│   └── reporter.py             # 报告生成
├── config/
│   ├── dimensions.yaml         # 维度配置
│   ├── thresholds.yaml         # 阈值配置
│   └── content_types.yaml      # 内容类型
├── rules/
│   └── quality_rules.yaml      # 检查规则
└── logs/
    └── quality.log             # 运行日志
```

### 4.2 标准化接口

```python
class QualityGate:
    
    def check(self, content: str, content_type: str) -> CheckResult:
        """检查内容质量"""
        pass
    
    def batch_check(self, contents: List[str], content_type: str) -> List[CheckResult]:
        """批量检查"""
        pass
    
    def get_score(self, check_id: str) -> Score:
        """获取检查分数"""
        pass
    
    def generate_report(self, check_id: str) -> Report:
        """生成检查报告"""
        pass
    
    def update_rules(self, dimension: str, rules: dict) -> None:
        """更新检查规则"""
        pass
```

### 4.3 调用方式

```bash
# 安装Skill
openclaw skill install quality-gate-system

# 检查内容
openclaw skill run quality-gate-system check --file report.md --type research

# 批量检查
openclaw skill run quality-gate-system batch-check --dir ./docs/ --type document

# 生成报告
openclaw skill run quality-gate-system report --check-id Q-001
```

---

## S5: 自动化 (Automation)

### 5.1 Cron定时任务

```json
{
  "jobs": [
    {
      "name": "quality-gate-daily-scan",
      "schedule": "43 10 * * *",
      "command": "cd /root/.openclaw/workspace/skills/quality-gate-system && python3 scripts/quality_runner.py scan",
      "description": "每日10:43扫描待检查内容"
    },
    {
      "name": "quality-gate-trend-analysis",
      "schedule": "7 23 * * *",
      "command": "cd /root/.openclaw/workspace/skills/quality-gate-system && python3 scripts/quality_runner.py trend",
      "description": "每日23:07生成质量趋势分析"
    },
    {
      "name": "quality-gate-weekly-report",
      "schedule": "27 22 * * 0",
      "command": "cd /root/.openclaw/workspace/skills/quality-gate-system && python3 scripts/quality_runner.py weekly",
      "description": "每周日22:27生成质量周报"
    }
  ]
}
```

### 5.2 自动化脚本

| 脚本 | 功能 | 触发 |
|------|------|------|
| `quality_runner.py` | 主控 | cron/手动 |
| `dimension_*.py` | 维度检查 | 内容提交 |
| `scorer.py` | 综合评分 | 检查完成 |
| `reporter.py` | 报告 | 定时/按需 |

### 5.3 自动监控

| 监控项 | 阈值 | 告警 |
|--------|------|------|
| 待检查积压 | >50 | 处理告警 |
| 检查失败率 | >5% | 技术告警 |
| 通过率异常 | 波动>20% | 质量告警 |
| 平均检查时间 | >30s | 性能告警 |

---

## S6: 认知谦逊 (Epistemic Humility)

### 6.1 检查结果置信度

| 检查类型 | 置信度 | 说明 |
|----------|--------|------|
| 自动验证 | 高 | 来源可访问 |
| 模式匹配 | 中 | 规则匹配度 |
| 启发式检测 | 低 | 建议人工复核 |

### 6.2 局限性声明

```yaml
quality_limitations:
  automation: "自动检查有假阳性/假阴性"
  source_access: "外部来源可能临时不可达"
  domain_knowledge: "专业领域需专家复核"
  context_understanding: "语义理解有局限"
```

---

## S7: 对抗验证 (Adversarial Validation)

### 7.1 假阳性/假阴性分析

| 类型 | 定义 | 缓解措施 |
|------|------|----------|
| 假阳性 | 合格内容被误判 | 申诉机制+阈值调整 |
| 假阴性 | 不合格内容通过 | 抽检+补充规则 |
| 边界模糊 | 标准不明确 | 人工仲裁+标准细化 |

### 7.2 对抗测试

定期执行：
1. 已知问题内容检测率测试
2. 已知优质内容误杀率测试
3. 极端/边界内容处理测试
4. 新类型内容适应性测试

---

## 附录：命令参考

| 命令 | 功能 | 示例 |
|------|------|------|
| `check [file]` | 检查内容 | `check report.md` |
| `batch-check [dir]` | 批量检查 | `batch-check ./docs` |
| `score [id]` | 查看分数 | `score Q-001` |
| `report [id]` | 生成报告 | `report Q-001` |

---

*版本: v2.0.0*  
*更新日期: 2026-03-21*  
*作者: 满意解研究所*
