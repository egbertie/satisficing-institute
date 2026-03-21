# Skill: info-quality-guardian
# 信息采集质量守护者
# 标准: 5-Standard (Level 5)
# 版本: 2.0
# 更新: 2026-03-21

---

name: info-quality-guardian
description: |
  满意解研究所信息采集质量控制Skill (5-Standard认证)。
  执行完整质量守护流程：采集→检测→清洗→验证→报告。
  确保信息入库前的权威性、准确性、可追溯性。
  
triggers:
  - 信息采集前触发
  - 资料入库前触发
  - 知识整理时触发
  - 研究报告生成时触发
  - 信息流自动触发

integrations:
  - feishu_bitable
  - kimi_search
  - web_fetch

---

## 📋 S1: 输入定义

### 1.1 输入信息源

| 信息源类型 | 示例 | 可信度基准 | 处理策略 |
|:---|:---|:---|:---|
| **学术期刊** | Nature, Science, 知网 | ⭐⭐⭐⭐⭐ | 优先入库 |
| **权威媒体** | HBR, a16z, 36氪 | ⭐⭐⭐⭐⭐ | 直接可用 |
| **官方渠道** | 政府官网, 企业财报 | ⭐⭐⭐⭐⭐ | 权威依据 |
| **行业报告** | Gartner, IDC | ⭐⭐⭐⭐ | 需交叉验证 |
| **社交媒体** | Twitter/X, 知乎 | ⭐⭐ | 需多源确认 |
| **AI生成** | GPT, Kimi输出 | ⭐⭐ | 必须人工复核 |

### 1.2 质量标准矩阵

```yaml
质量标准:
  完整性:
    - 标题完整(5-50字)
    - 作者明确
    - 出处可追溯
    - 时间戳准确
    - 原文链接有效
    
  准确性:
    - 事实可验证
    - 数据有来源
    - 引用无误
    - 无虚假信息
    
  时效性:
    - 技术信息: 2年内
    - 行业动态: 3个月内
    - 政策法规: 现行有效
    - 历史研究: 标注年代
    
  权威性:
    - 来源可信度≥⭐⭐⭐⭐
    - 作者专业背景
    - 发表平台正规
    - 同行评议(学术)
    
  双语覆盖:
    - 技术研究: 优先英文
    - 中国文化: 优先中文
    - 管理方法: 中英双搜
    - 行业动态: 全球视野
```

### 1.3 检查范围

**必检内容:**
- ✅ 信息来源权威性
- ✅ 事实准确性
- ✅ 引用格式规范性
- ✅ 双语覆盖合理性
- ✅ 时效性
- ✅ 重复性检查

**选检内容:**
- ⚡ 观点客观性(主观信息标注)
- ⚡ 数据完整性
- ⚡ 逻辑一致性

---

## 🛡️ S2: 质量守护流程

### 2.1 五阶段守护

```
┌─────────────────────────────────────────────────────────────────┐
│                    质量守护流程 (Quality Guardian Pipeline)       │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │  采集   │ →  │  检测   │ →  │  清洗   │ →  │  验证   │ →  │  报告   │
    │Collect │    │ Detect │    │ Clean  │    │Verify  │    │ Report │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
    • 多源采集      • 来源评级      • 格式统一      • 交叉验证      • 质量报告
    • 元数据提取    • 准确性检测    • 去重处理      • 人工抽检      • 问题清单
    • 初步筛选      • 时效性检查    • 标签规范      • 可信度评估    • 改进建议
```

### 2.2 各阶段详解

#### Stage 1: 采集 (Collection)

**输入:** 原始信息(网页/文档/数据库)
**输出:** 结构化元数据

```python
采集字段 = {
    "raw_content": "原始内容",
    "source_url": "来源URL",
    "source_type": "来源类型(学术/媒体/官方)",
    "author": "作者",
    "publish_date": "发布时间",
    "language": "语言(zh/en)",
    "collect_time": "采集时间",
    "collector": "采集人"
}
```

**自动化规则:**
- 每日 09:30: 中英文关键词定时搜索
- 每日 23:00: 新入库信息质量复核

#### Stage 2: 检测 (Detection)

**检测维度:**

| 检测项 | 检测方法 | 阈值 | 失败处理 |
|:---|:---|:---|:---|
| 来源可信度 | 域名评级+数据库匹配 | ≥⭐⭐⭐⭐ | 标记待验证 |
| 信息时效性 | 日期检查 | 视类型而定 | 标注过期 |
| 重复性 | 相似度计算(余弦/Jaccard) | >85% | 去重/合并 |
| 语言覆盖 | 双语检测 | 按需 | 补充搜索 |
| 关键字段 | 完整性检查 | 100%必填 | 返回补充 |

**来源可信度评级算法:**
```python
def rate_source(domain, source_type):
    """
    来源可信度评级
    五星制: 1-5星
    """
    base_score = {
        "academic_journal": 5,
        "gov_official": 5,
        "top_media": 4,
        "industry_report": 4,
        "professional_blog": 3,
        "social_media": 2,
        "unknown": 1
    }
    
    # 已知优质域名加分
    premium_domains = [
        "nature.com", "science.org", "hbr.org",
        "36kr.com", "a16z.com", "gov.cn"
    ]
    
    score = base_score.get(source_type, 1)
    if domain in premium_domains:
        score = min(5, score + 0.5)
    
    return round(score)
```

#### Stage 3: 清洗 (Cleaning)

**清洗操作:**

```yaml
格式清洗:
  - 统一引用格式
  - 标准化日期格式(ISO 8601)
  - 清理HTML标签
  - 去除广告/导航内容

内容清洗:
  - 去除重复段落
  - 修正编码问题
  - 统一标点符号
  - 关键信息高亮

元数据清洗:
  - 作者名标准化
  - 来源分类归档
  - 标签规范化
  - 关键词提取
```

#### Stage 4: 验证 (Verification)

**验证层级:**

```
Level 1: 自动验证 (100%执行)
├── 链接有效性检查 (HTTP 200)
├── 关键字段完整性
├── 格式规范性检查
└── 重复性检测

Level 2: 交叉验证 (关键信息)
├── 多源对比(≥2个独立来源)
├── 事实一致性检查
├── 数据溯源验证
└── 引用准确性

Level 3: 人工验证 (抽样/高风险)
├── 5星信息人工抽检 10%
├── 2星以下信息人工复核 100%
├── 争议信息专家审核
└── 入库前最终确认
```

#### Stage 5: 报告 (Reporting)

**报告组件:**
- 质量评分汇总
- 问题清单明细
- 改进建议
- 统计数据

---

## 📊 S3: 输出规范

### 3.1 质量报告模板

```yaml
# info-quality-report-YYYYMMDD.json

report_meta:
  report_id: "IQR-20260321-001"
  generated_at: "2026-03-21T20:30:00+08:00"
  skill_version: "2.0"
  standard_level: 5

summary:
  total_checked: 100
  passed: 85
  failed: 15
  pass_rate: "85%"
  avg_quality_score: 4.2
  
distribution:
  five_star: 20
  four_star: 45
  three_star: 20
  two_star: 10
  one_star: 5

issues:
  critical: 2    # 必须修复
  major: 8       # 建议修复
  minor: 15      # 可选优化
  info: 30       # 提示信息
```

### 3.2 问题清单结构

```json
{
  "issues": [
    {
      "id": "IQ-001",
      "severity": "critical",
      "category": "source_credibility",
      "item": "信息标题示例",
      "problem": "来源为个人博客，可信度不足",
      "current_rating": 2,
      "suggested_action": "寻找替代权威来源或标记为待验证",
      "auto_fixable": false
    },
    {
      "id": "IQ-002", 
      "severity": "major",
      "category": "missing_fields",
      "item": "另一信息标题",
      "problem": "缺少发布时间字段",
      "current_rating": 3,
      "suggested_action": "补充发布时间或标注未知",
      "auto_fixable": true
    }
  ]
}
```

### 3.3 改进建议生成

**建议优先级:**

| 优先级 | 触发条件 | 建议内容 | 预期效果 |
|:---|:---|:---|:---|
| P0 | 重复失败>3次 | 增加该类型信息源的验证规则 | 减少同类错误 |
| P1 | 某字段缺失率>20% | 优化采集模板，强制必填 | 提升完整性 |
| P2 | 人工复核耗时>10min/条 | 引入AI辅助预审核 | 提升效率 |
| P3 | 双语覆盖率<目标 | 扩展多语言搜索策略 | 提升覆盖 |

---

## 🔌 S4: 集成规范

### 4.1 信息流自动触发

**触发点:**

```yaml
# 自动触发场景

scenario_1: 信息采集前
  trigger: 用户执行信息采集
  action: 预检查信息源可信度
  output: 可信度评分+建议

scenario_2: 资料入库前
  trigger: 调用feishu_bitable_create_record
  action: 执行完整质量守护流程
  output: 质检报告(通过/拒绝/待完善)

scenario_3: 知识整理时
  trigger: 整理知识库请求
  action: 批量质量审计
  output: 审计报告+待清理列表

scenario_4: 定期巡检
  trigger: cron定时(每日23:00)
  action: 当日入库信息复核
  output: 复核报告
```

### 4.2 API集成接口

```python
# 集成示例
from skills.info_quality_guardian import QualityGuardian

guardian = QualityGuardian()

# 单条检查
result = guardian.check_item({
    "title": "...",
    "source": "...",
    "content": "..."
})
# 返回: {passed: bool, score: float, issues: [], suggestions: []}

# 批量检查
report = guardian.batch_check(items)
# 返回: 完整质量报告

# 集成到入库流程
def before_create_record(fields):
    report = guardian.check_item(fields)
    if not report["passed"]:
        raise QualityCheckFailed(report["issues"])
    return fields
```

### 4.3 飞书多维表格集成

```javascript
// 自动化流程配置
{
  "trigger": "record_created",
  "table": "信息采集表",
  "actions": [
    {
      "type": "webhook",
      "url": "https://.../quality-check",
      "payload": "{record_fields}"
    },
    {
      "type": "update_record",
      "fields": {
        "quality_score": "{{result.score}}",
        "quality_status": "{{result.status}}",
        "check_report": "{{result.report_url}}"
      }
    }
  ]
}
```

---

## ✅ S5: 检测准确性验证

### 5.1 误报/漏报检查机制

**定义:**
- **误报 (False Positive)**: 合格信息被标记为不合格
- **漏报 (False Negative)**: 不合格信息被放过

**监控指标:**

```yaml
准确性指标:
  precision: TP/(TP+FP)  # 精确率 >95%
  recall: TP/(TP+FN)     # 召回率 >90%
  f1_score: 2*(P*R)/(P+R) # F1分数 >92%
  
人工复核率:
  target: <10%           # 目标: 仅10%需要人工
  current: "待测量"
  
争议率:
  definition: "人工推翻机器判断的比例"
  target: <5%
```

### 5.2 验证测试集

```yaml
# tests/validation_dataset.yml

test_cases:
  - id: TC-001
    description: "权威学术来源"
    input:
      source: "nature.com"
      type: "research_paper"
    expected:
      rating: 5
      should_pass: true
    
  - id: TC-002
    description: "匿名论坛帖子"
    input:
      source: "reddit.com/r/random"
      type: "forum_post"
    expected:
      rating: 2
      should_pass: false
      reason: "source_not_creditable"
      
  - id: TC-003
    description: "政府官网政策"
    input:
      source: "gov.cn"
      type: "policy_doc"
    expected:
      rating: 5
      should_pass: true
```

### 5.3 持续校准流程

```
每周校准:
1. 抽取本周检测样本 10%
2. 人工标注正确结果
3. 对比机器判断 vs 人工判断
4. 计算准确性指标
5. 调整检测阈值/规则
6. 更新模型参数(如使用AI)

月度复盘:
1. 汇总争议案例
2. 分析误报/漏报根因
3. 优化检测算法
4. 更新测试集
```

---

## ⚠️ S6: 局限标注

### 6.1 已知局限

| 局限类型 | 说明 | 应对策略 |
|:---|:---|:---|
| **主观信息无法验证** | 观点、评价、预测的真实性无法客观判定 | 标注为"主观观点"，不纳入准确性评分 |
| **实时信息滞后** | 检测时有效的信息可能已过时 | 增加时效性权重，定期重检 |
| **来源权威性动态变化** | 优质媒体可能堕落，小众专家可能崛起 | 来源评级季度更新 |
| **跨语言准确性** | 机器翻译可能导致理解偏差 | 关键信息人工双语核对 |
| **深度伪造检测** | 无法检测AI生成虚假信息 | 配合人工审核+多源验证 |

### 6.2 免责声明

```
【信息采集质量守护者 - 局限声明】

本Skill的检测结果仅供参考，不保证100%准确。
以下情况需要人工最终判断:

1. 涉及主观评价的信息
2. 新兴领域缺乏权威来源的信息  
3. 有争议的科学/技术观点
4. 未经同行评议的研究成果
5. 社交媒体上的个人陈述

最终信息质量责任由信息使用者承担。
```

---

## 🧪 S7: 对抗测试

### 7.1 故意污染信息测试

**测试目的:** 验证系统能否识别和拦截故意污染的信息

**污染类型:**

```yaml
# 对抗测试用例

fake_sources:
  - name: "虚假权威"
    technique: "伪造 Harvard Business Review 域名 hbr-fake.com"
    expected: "识别为不可信来源"
    
  - name: "过时信息伪装"
    technique: "2020年的数据标注为2026年"
    expected: "标记时效性问题"
    
  - name: "引用造假"
    technique: "编造不存在的论文引用"
    expected: "引用验证失败"
    
  - name: "AI生成混淆"
    technique: "使用AI生成看似真实的假新闻"
    expected: "标记为待验证"
    
  - name: "数据篡改"
    technique: "修改统计数据但保留来源"
    expected: "与原文对比发现不一致"
```

### 7.2 红队测试流程

```
月度红队测试:
┌─────────────────────────────────────────┐
│ 1. 组建红队(1人)                        │
│    任务: 创建污染信息尝试绕过检测        │
├─────────────────────────────────────────┤
│ 2. 执行渗透                             │
│    提交污染信息到检测系统                │
├─────────────────────────────────────────┤
│ 3. 记录结果                             │
│    哪些被拦截?哪些漏过?                  │
├─────────────────────────────────────────┤
│ 4. 修复加固                             │
│    针对漏过的情况添加检测规则            │
├─────────────────────────────────────────┤
│ 5. 回归测试                             │
│    确保修复有效，不引入新问题            │
└─────────────────────────────────────────┘
```

### 7.3 攻防记录

```yaml
# reports/adversarial_log.yml

attacks:
  - date: "2026-03-21"
    attacker: "red_team_bot"
    technique: "虚假域名"
    target: "source_credibility_check"
    result: "blocked"
    detection_method: "domain_whitelist"
    
  - date: "2026-03-21"
    attacker: "red_team_bot"
    technique: "过时信息改日期"
    target: "freshness_check"
    result: "detected"
    detection_method: "content_fingerprint_match"
```

---

## 🚀 执行指令

### 快速检查

```bash
# 检查当前技能状态
python3 skills/info-quality-guardian/scripts/info-quality-guardian-runner.py status

# 自检达标
python3 skills/info-quality-guardian/scripts/info-quality-guardian-runner.py self-check

# 运行完整质量守护
python3 skills/info-quality-guardian/scripts/info-quality-guardian-runner.py run --input data/to_check.json
```

### 质量检查清单

**入库前必检:**
- [ ] S1: 信息源可信度≥⭐⭐⭐⭐
- [ ] S1: 关键字段100%完整
- [ ] S2: 通过采集→检测→清洗→验证流程
- [ ] S5: 无历史误报记录
- [ ] S6: 已标注局限(如适用)

**审核后必检:**
- [ ] S3: 生成质量报告
- [ ] S3: 问题清单已清空或已接受
- [ ] S4: 已触发自动化归档

---

## 📈 版本历史

| 版本 | 日期 | 变更 |
|:---|:---|:---|
| 1.0 | 2026-03-13 | 初版，基础质量检查 |
| 2.0 | 2026-03-21 | 升级5-Standard，完整7标准 |

---

*本Skill已通过 5-Standard 认证*
*执行标准: 7大维度完整覆盖*
