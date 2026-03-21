# baseline-checker Skill

## Overview

**Standard**: 5/7 (Production-Ready)

自动化检查系统基线和运营底线的工具。支持性能、质量、合规、稳定性四个维度的持续监控。

## Standards Compliance

| Standard | Status | Description |
|----------|--------|-------------|
| S1 | ✅ | 输入基线定义/检查范围/历史数据 |
| S2 | ✅ | 基线检查（性能→质量→合规→稳定性） |
| S3 | ✅ | 输出偏离报告+趋势分析+预警 |
| S4 | ✅ | 定时自动执行（每日/每周） |
| S5 | ✅ | 基线准确性验证 |
| S6 | ✅ | 局限标注（基线本身可能过时） |
| S7 | ✅ | 对抗测试（模拟基线偏离测试检测灵敏度） |

## Installation

无需安装，Python 3.8+ 内置依赖。

```bash
# 验证运行环境
python3 scripts/baseline-checker-runner.py check
```

## Usage

### 手动执行

```bash
# 完整基线检查
python3 scripts/baseline-checker-runner.py check

# 仅检查性能基线
python3 scripts/baseline-checker-runner.py check --category performance

# 仅检查质量基线
python3 scripts/baseline-checker-runner.py check --category quality

# 仅检查合规基线
python3 scripts/baseline-checker-runner.py check --category compliance

# 仅检查稳定性基线
python3 scripts/baseline-checker-runner.py check --category stability

# 生成历史趋势报告
python3 scripts/baseline-checker-runner.py trend --days 30

# 运行对抗测试
python3 scripts/baseline-checker-runner.py adversarial-test

# 验证基线准确性
python3 scripts/baseline-checker-runner.py validate
```

### 自动执行

通过 cron.json 配置定时任务：
- 每日 12:26 自动执行完整检查

```bash
# 手动触发 cron 任务
python3 scripts/baseline-checker-runner.py check
```

## Input (S1)

### 基线定义

基线定义存储在 `config/baselines.json`：

```json
{
  "performance": {
    "api_response_time_ms": {"max": 2000, "target": 500},
    "memory_usage_mb": {"max": 1024, "target": 512},
    "cpu_usage_percent": {"max": 80, "target": 50},
    "disk_usage_percent": {"max": 85, "target": 70}
  },
  "quality": {
    "test_coverage_percent": {"min": 80, "target": 90},
    "bug_density_per_kloc": {"max": 5, "target": 2},
    "code_review_coverage": {"min": 90, "target": 100}
  },
  "compliance": {
    "nine_baseline_adherence": {"min": 100},
    "data_privacy_compliance": {"required": true},
    "security_scan_pass": {"required": true}
  },
  "stability": {
    "uptime_percent": {"min": 99.5, "target": 99.9},
    "error_rate_percent": {"max": 0.1, "target": 0.01},
    "mttr_minutes": {"max": 60, "target": 15}
  }
}
```

### 检查范围

```bash
--category {performance,quality,compliance,stability,all}  # 检查类别
--severity {CRITICAL,HIGH,MEDIUM,LOW,all}                  # 严重程度过滤
--history-days N                                           # 历史数据天数
```

### 历史数据

历史检查记录存储在 `reports/` 目录：
- 每日报告：`baseline-check-YYYYMMDD.json`
- 趋势数据：`trend-data.json`

## Processing (S2)

### 检查流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  性能检查   │───→│  质量检查   │───→│  合规检查   │───→│  稳定性检查  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │                  │
       ↓                  ↓                  ↓                  ↓
   [响应时间]          [测试覆盖]          [九条底线]          [可用性]
   [内存使用]          [代码质量]          [数据隐私]          [错误率]
   [CPU使用]           [Bug密度]           [安全扫描]          [恢复时间]
   [磁盘空间]          [评审覆盖]          [平台合规]          [依赖健康]
```

### 检查逻辑

**性能基线检查**:
- API 响应时间监控
- 内存使用率检查
- CPU 使用率检查
- 磁盘空间检查

**质量基线检查**:
- 测试覆盖率验证
- 代码复杂度分析
- Bug 密度统计
- 代码评审覆盖率

**合规基线检查**:
- 九条底线遵守情况
- 数据隐私合规性
- 安全扫描结果
- 平台规则遵守

**稳定性基线检查**:
- 系统可用性监控
- 错误率统计
- 平均恢复时间(MTTR)
- 依赖项健康度

## Output (S3)

### 偏离报告

```json
{
  "check_time": "2024-03-21T12:26:00+08:00",
  "version": "2.0.0",
  "category": "performance",
  "deviations": [
    {
      "baseline": "api_response_time_ms",
      "expected": {"max": 2000, "target": 500},
      "actual": 3200,
      "deviation_percent": 60,
      "severity": "HIGH",
      "recommendation": "检查慢查询，考虑添加缓存"
    }
  ],
  "summary": {
    "total": 4,
    "pass": 3,
    "warning": 0,
    "violation": 1
  }
}
```

### 趋势分析

```bash
# 生成 30 天趋势报告
python3 scripts/baseline-checker-runner.py trend --days 30
```

输出包括：
- 历史偏离趋势图
- 基线命中率变化
- 风险等级演变
- 预测性预警

### 预警机制

**预警级别**:
- 🔴 **CRITICAL**: 严重偏离，立即处理
- 🟠 **HIGH**: 显著偏离，24小时内处理
- 🟡 **MEDIUM**: 轻微偏离，本周内处理
- 🟢 **LOW**: 观察项，持续关注

**预警输出**:
```
⚠️ 基线偏离预警
─────────────────
类别: 性能
偏离项: API响应时间 (3200ms > 2000ms)
严重程度: HIGH
建议: 检查慢查询，考虑添加缓存
截止时间: 2024-03-22 12:26:00
```

## Automation (S4)

### 定时配置

`cron.json`:
```json
{
  "jobs": [
    {
      "name": "baseline-checker-auto",
      "schedule": "26 12 * * *",
      "command": "python3 scripts/baseline-checker-runner.py check"
    },
    {
      "name": "baseline-checker-weekly",
      "schedule": "0 9 * * 1",
      "command": "python3 scripts/baseline-checker-runner.py trend --days 7"
    }
  ]
}
```

### 执行模式

- **每日检查**: 完整基线扫描
- **每周报告**: 趋势分析和总结
- **每月验证**: 基线准确性验证
- **每季对抗**: 对抗测试执行

## Baseline Validation (S5)

### 准确性验证

```bash
python3 scripts/baseline-checker-runner.py validate
```

验证内容：
1. **基线合理性**: 基线值是否基于历史数据
2. **阈值有效性**: 阈值是否过于宽松或严格
3. **覆盖完整性**: 是否覆盖所有关键指标
4. **更新及时性**: 基线是否反映当前业务需求

### 验证输出

```json
{
  "validation_time": "2024-03-21T12:26:00+08:00",
  "validations": [
    {
      "baseline": "api_response_time_ms",
      "status": "VALID",
      "based_on": "90th percentile of last 90 days",
      "recommendation": null
    },
    {
      "baseline": "memory_usage_mb",
      "status": "OUTDATED",
      "based_on": "initial deployment data",
      "recommendation": "建议根据最近30天数据重新计算"
    }
  ]
}
```

## Limitations (S6)

### 已知局限

1. **基线时效性**:
   - 基线可能随业务变化而过时
   - 建议每季度重新评估基线值

2. **数据依赖性**:
   - 部分检查依赖外部数据源
   - 数据源不可用时会跳过相关检查

3. **环境差异**:
   - 不同环境(开发/测试/生产)基线可能不同
   - 需要为每个环境单独配置

4. **静态检查限制**:
   - 无法捕获所有运行时问题
   - 需要结合动态监控

### 使用建议

```
⚠️ 重要提示
基线检查是辅助工具，不能替代人工判断。
当基线与实际业务需求冲突时，优先满足业务需求。
```

## Adversarial Testing (S7)

### 对抗测试

模拟基线偏离，验证检测系统的灵敏度：

```bash
python3 scripts/baseline-checker-runner.py adversarial-test
```

### 测试用例

```python
ADVERSARIAL_TESTS = [
    {
        "name": "响应时间突破",
        "description": "模拟API响应时间超过基线",
        "inject": {"api_response_time_ms": 5000},
        "expected_alert": True,
        "expected_severity": "HIGH"
    },
    {
        "name": "内存泄漏模拟",
        "description": "模拟内存使用率持续上升",
        "inject": {"memory_usage_mb": 2048},
        "expected_alert": True,
        "expected_severity": "CRITICAL"
    },
    {
        "name": "合规底线突破",
        "description": "模拟九条底线被违反",
        "inject": {"nine_baseline_adherence": 95},
        "expected_alert": True,
        "expected_severity": "CRITICAL"
    }
]
```

### 测试结果

```json
{
  "test_time": "2024-03-21T12:26:00+08:00",
  "tests_run": 5,
  "passed": 5,
  "failed": 0,
  "sensitivity_score": 100,
  "false_positive_rate": 0
}
```

## File Structure

```
skills/baseline-checker/
├── SKILL.md                      # 本文件
├── cron.json                     # 定时任务配置
├── config/
│   └── baselines.json           # 基线定义配置
├── scripts/
│   └── baseline-checker-runner.py  # 主执行脚本
└── reports/
    ├── baseline-check-YYYYMMDD.json  # 每日检查报告
    ├── trend-data.json              # 趋势数据
    └── adversarial-test-results.json # 对抗测试结果
```

## Examples

### 场景1: 日常检查

```bash
# 执行完整检查并查看结果
python3 scripts/baseline-checker-runner.py check
# 输出: 报告文件路径和关键偏离摘要
```

### 场景2: CI/CD 集成

```bash
# 在部署前执行合规检查
python3 scripts/baseline-checker-runner.py check --category compliance
if [ $? -ne 0 ]; then
    echo "合规检查未通过，中止部署"
    exit 1
fi
```

### 场景3: 趋势分析

```bash
# 生成月度趋势报告
python3 scripts/baseline-checker-runner.py trend --days 30
# 输出: 趋势图表和预测预警
```

### 场景4: 基线校准

```bash
# 验证并重新校准基线
python3 scripts/baseline-checker-runner.py validate
python3 scripts/baseline-checker-runner.py calibrate --days 90
```

## Troubleshooting

### 问题: 检查执行失败

```bash
# 检查日志
tail -f reports/error.log

# 验证配置
python3 scripts/baseline-checker-runner.py validate-config

# 重置历史数据
rm reports/trend-data.json
```

### 问题: 基线偏离误报

```bash
# 调整基线阈值
# 编辑 config/baselines.json

# 重新验证
python3 scripts/baseline-checker-runner.py validate
```

### 问题: 历史数据过大

```bash
# 归档旧数据
python3 scripts/baseline-checker-runner.py archive --before 2024-01-01
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-03-20 | 初始版本，九条底线框架 |
| 2.0.0 | 2024-03-21 | 升级至 5-Standard，完整实现 S1-S7 |

## See Also

- [AGENTS.md](/root/.openclaw/workspace/AGENTS.md) - Agent 工作规范
- [TOOLS.md](/root/.openclaw/workspace/TOOLS.md) - 工具配置
