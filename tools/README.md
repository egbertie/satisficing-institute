# TRL 技术成熟度自评工具

满意解研究所 · 硬科技合伙人匹配决策系统

---

## 📋 工具简介

本工具基于 **NASA/DoD TRL 1-9 级标准**（符合中国国标 GB/T 22900-2009），针对**硬科技创业场景**进行优化，帮助创业者：

1. **快速自评**技术成熟度等级
2. **精准匹配**当前阶段最需要的合伙人角色
3. **科学决策**融资阶段和团队配置

---

## 🚀 快速开始

### 方式一：Web 版本（推荐，可视化界面）

```bash
python tools/trl_api.py
```

然后访问 http://localhost:8080

**功能特性：**
- 可视化问卷界面，8个维度评估
- 实时计算TRL等级
- 显示风险等级、融资阶段、合伙人匹配建议
- 响应式设计，支持移动端

### 方式二：命令行交互版

```bash
python tools/trl_assessment.py
```

按提示回答 8 个问题，自动生成详细评估报告。

### 方式三：API 调用（集成到系统）

```python
from tools.trl_api import TRLCalculator

answers = {
    "tech_stage": 5,      # 技术阶段
    "prototype": 5,       # 原型验证
    "test_env": 5,        # 测试环境
    "team": 5,            # 团队配置
    "customer": 5,        # 客户验证
    "supply_chain": 5,    # 供应链
    "ip": 5,              # 知识产权
    "funding": 5          # 资金需求
}

result = TRLCalculator.calculate(answers)
print(f"TRL 等级: {result['trl_level']} 级")
print(f"最需要的合伙人: {result['partner_need']}")
```

---

## 📊 TRL 等级速查表

| TRL | 等级名称 | 风险等级 | 融资阶段 | 最需要的合伙人 |
|-----|---------|---------|---------|---------------|
| 1 | 基本原理发现 | 极高 | 种子/天使 | 技术联合创始人 |
| 2 | 技术方案形成 | 很高 | 天使轮 | CTO、架构师 |
| 3 | 关键功能实验室验证 | 高 | Pre-A轮 | 工程合伙人 |
| 4 | 组件/实验板验证 | 中高 | A轮 | 硬件合伙人 |
| 5 | 相关环境组件验证 | 中 | A+轮 | 运营合伙人 |
| 6 | 系统/子系统原型验证 | 中低 | B轮 | 商业化合伙人 |
| 7 | 操作环境原型演示 | 低 | B+/C轮 | 行业专家 |
| 8 | 系统完成并通过测试 | 很低 | C/Pre-IPO | 运营/财务合伙人 |
| 9 | 实际任务成功应用 | 极低 | IPO/并购 | 战略合伙人 |

---

## 🎯 评估维度说明

本工具从 **8 个维度** 综合评估：

1. **技术研发** - 核心技术所处阶段
2. **原型验证** - 产品原型完成度
3. **测试环境** - 验证环境的真实性
4. **团队配置** - 技术与商业团队配比
5. **客户验证** - 客户接触和验证程度
6. **供应链** - 供应链和生产准备
7. **知识产权** - 专利布局情况
8. **资金需求** - 资金用途阶段

---

## 💡 使用场景

### 场景 1：创业者自评
> "我想知道自己的项目处于什么阶段，该找什么样的合伙人"

运行 `trl_assessment.py`，获得：
- TRL 等级判定
- 合伙人画像建议
- 股权分配参考
- 下一步行动计划

### 场景 2：投资人尽调
> "我需要快速判断项目技术成熟度"

调用 API 接口，获得标准化评估结果，辅助投资决策。

### 场景 3：孵化器/加速器
> "我需要为入驻企业评估并提供匹配服务"

集成 Web 版本，批量评估并生成匹配建议。

---

## 📁 文件说明

```
tools/
├── trl_assessment.py    # 交互式命令行版本
├── trl_api.py           # Web API 版本
└── README.md            # 本文件
```

---

## 🔧 API 文档

### 获取 TRL 等级列表
```bash
GET /api/trl/levels
```

### 获取评估问题
```bash
GET /api/trl/questions
```

### 提交评估
```bash
POST /api/trl/calculate
Content-Type: application/json

{
    "tech_stage": 5,
    "prototype": 5,
    "test_env": 5,
    "team": 5,
    "customer": 5,
    "supply_chain": 5,
    "ip": 5,
    "funding": 5
}
```

**响应示例：**
```json
{
    "trl_level": 5,
    "trl_name": "相关环境组件验证",
    "average_score": 5.0,
    "total_score": 40,
    "max_score": 72,
    "risk_level": "中",
    "funding_stage": "A+轮",
    "partner_need": "运营合伙人、市场验证专家",
    "dimension_scores": {...},
    "assessment_date": "2026-03-10 22:52:43"
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|-----|-----|-----|
| trl_level | int | TRL等级 1-9 |
| trl_name | string | 等级名称 |
| average_score | float | 平均得分 1.0-9.0 |
| total_score | int | 总分 |
| max_score | int | 满分（72分） |
| risk_level | string | 风险等级 |
| funding_stage | string | 适配融资阶段 |
| partner_need | string | 合伙人匹配建议 |
| dimension_scores | object | 各维度得分 |
| assessment_date | string | 评估时间 |

---

## 📚 参考标准

- **NASA**: Technology Readiness Level (TRL) Scale
- **DoD**: Technology Readiness Assessment (TRA) Deskbook
- **国标**: GB/T 22900-2009 科学技术研究项目评价通则

---

## 🛠️ 系统要求

- **Python**: 3.7+
- **依赖**: 无需额外依赖（仅使用标准库）

## 🔧 故障排除

### 端口被占用
如果启动时提示端口被占用，可以修改端口号：
```python
# 修改 trl_api.py 最后一行
run_server(port=8081)  # 使用其他端口
```

### 无法访问Web界面
1. 检查服务是否启动：`python tools/trl_api.py`
2. 检查防火墙设置
3. 使用 `http://127.0.0.1:8080` 替代 `localhost`

### API返回错误
- 确保Content-Type设置为 `application/json`
- 确保所有8个维度字段都存在
- 字段值范围为 1-9 的整数

---

## 🤝 满意解研究所

> **让技术找到对的人**

专注硬科技转化的合伙人匹配决策教练，结合左脑风控与右脑直觉，帮助创始人找到真正适合的合伙人。

---

**版本**: v1.1  
**更新**: 2026-03-10  
**状态**: ✅ 测试通过，生产就绪  
**作者**: 满意解研究所
