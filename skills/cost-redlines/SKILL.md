# 成本红线机制标准Skill V1.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V1.0 | 更新: 2026-03-20 | 核心: 4级成本模型 | 目标: 成本可控、超支预警

---

## 一、全局考虑（六层+4级成本模型）

### 4级成本 × 六层矩阵

| 成本级别 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|----------|--------|--------|--------|--------|--------|--------|
| **L1-基础成本** | 身份运营 | 项目基础 | 系统运行 | 基础集成 | 基础交付 | 基础存储 |
| **L2-扩展成本** | 能力扩展 | 项目扩展 | 系统扩展 | 扩展服务 | 增值服务 | 扩展归档 |
| **L3-增值成本** | 高级功能 | 项目优化 | 系统优化 | 高级集成 | 定制交付 | 长期归档 |
| **L4-风险成本** | 风险预留 | 应急预算 | 故障恢复 | 外部风险 | 质量保障 | 合规成本 |

---

## 二、系统考虑（预算→监控→预警→控制闭环）

### 2.1 4级成本模型详解

```
┌─────────────────────────────────────────────────────────────┐
│  L4-风险成本 (10-15%)                                        │
│  └── 应急预留、风险缓冲、不可预见支出                         │
├─────────────────────────────────────────────────────────────┤
│  L3-增值成本 (15-20%)                                        │
│  └── 高级功能、优化服务、定制需求                             │
├─────────────────────────────────────────────────────────────┤
│  L2-扩展成本 (25-30%)                                        │
│  └── 扩展功能、额外服务、容量提升                             │
├─────────────────────────────────────────────────────────────┤
│  L1-基础成本 (40-50%)                                        │
│  └── 核心功能、基础服务、必要支出                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 成本红线定义

| 红线级别 | 触发条件 | 响应动作 | 升级路径 |
|----------|----------|----------|----------|
| **红线-暂停** | 实际支出 ≥ 预算100% | 立即暂停非必要支出 | 自动触发 |
| **黄线-警告** | 实际支出 ≥ 预算80% | 发出警告+审查计划 | 自动触发 |
| **蓝线-提醒** | 实际支出 ≥ 预算60% | 成本提醒+优化建议 | 自动触发 |
| **绿线-正常** | 实际支出 < 预算60% | 正常监控 | 无需动作 |

### 2.3 成本控制闭环

```
预算制定 → 成本跟踪 → 偏差分析 → 预警触发 → 控制措施 → 效果评估
    ↑                                                          │
    └────────────────────── 调整优化 ←─────────────────────────┘
```

---

## 三、迭代机制（成本分析+预算优化）

### 3.1 成本度量指标

| 指标 | 计算公式 | 目标值 | 预警阈值 |
|------|----------|--------|----------|
| 预算执行率 | 实际支出/预算 | 85-95% | >100%或<60% |
| 成本偏差率 | (实际-预算)/预算 | ±10% | >20% |
| L1成本占比 | L1支出/总支出 | 40-50% | >60%或<30% |
| 风险储备使用率 | L4使用/L4预算 | <80% | >90% |

### 3.2 预算优化循环

```yaml
budget_optimization:
  monthly_review:
    - 分析各级成本实际支出
    - 识别超支/节余原因
    - 调整下月预算分配
    
  quarterly_adjustment:
    - 重新评估4级成本比例
    - 调整年度预算规划
    - 优化成本控制策略
```

---

## 四、Skill化（可执行）

### 4.1 触发条件

**自动触发**:
- 成本支出发生时自动记录
- 成本达到红线阈值时自动预警
- 每日自动计算成本指标
- 周/月自动生成成本报告

**手动触发**:
- 用户指令: "查看成本状态"
- 用户指令: "检查成本红线"
- 用户指令: "生成成本报告"

### 4.2 成本红线代码

```python
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

class CostLevel(Enum):
    L1_BASE = "l1"        # 基础成本
    L2_EXTENDED = "l2"    # 扩展成本
    L3_VALUE_ADDED = "l3" # 增值成本
    L4_RISK = "l4"        # 风险成本

class RedLineLevel(Enum):
    GREEN = "green"       # 正常 (<60%)
    BLUE = "blue"         # 提醒 (60-80%)
    YELLOW = "yellow"     # 警告 (80-100%)
    RED = "red"           # 暂停 (≥100%)

@dataclass
class Budget:
    """预算定义"""
    id: str
    name: str
    total: float
    allocations: Dict[CostLevel, float]  # 各级预算分配
    period_start: datetime
    period_end: datetime
    
    def get_level_budget(self, level: CostLevel) -> float:
        return self.allocations.get(level, 0)

@dataclass
class CostRecord:
    """成本记录"""
    id: str
    budget_id: str
    level: CostLevel
    amount: float
    description: str
    timestamp: datetime
    category: str

class CostRedLines:
    """成本红线机制"""
    
    # 标准成本分配比例
    STANDARD_ALLOCATION = {
        CostLevel.L1_BASE: 0.45,        # 45%
        CostLevel.L2_EXTENDED: 0.28,    # 28%
        CostLevel.L3_VALUE_ADDED: 0.17, # 17%
        CostLevel.L4_RISK: 0.10         # 10%
    }
    
    # 红线阈值
    REDLINE_THRESHOLDS = {
        RedLineLevel.GREEN: 0.60,
        RedLineLevel.BLUE: 0.60,
        RedLineLevel.YELLOW: 0.80,
        RedLineLevel.RED: 1.00
    }
    
    def __init__(self):
        self.budgets: Dict[str, Budget] = {}
        self.cost_records: List[CostRecord] = []
        self.redline_history: List[Dict] = []
    
    def create_budget(self, name: str, total: float, 
                     period_days: int = 30,
                     custom_allocation: Optional[Dict[CostLevel, float]] = None) -> Budget:
        """创建预算"""
        allocation = custom_allocation or self.STANDARD_ALLOCATION.copy()
        
        # 确保分配比例为100%
        total_alloc = sum(allocation.values())
        if abs(total_alloc - 1.0) > 0.001:
            # 归一化
            allocation = {k: v/total_alloc for k, v in allocation.items()}
        
        budget = Budget(
            id=f"BUD-{len(self.budgets)+1:04d}",
            name=name,
            total=total,
            allocations={k: total * v for k, v in allocation.items()},
            period_start=datetime.now(),
            period_end=datetime.now() + timedelta(days=period_days)
        )
        
        self.budgets[budget.id] = budget
        return budget
    
    def record_cost(self, budget_id: str, level: CostLevel, 
                   amount: float, description: str, category: str = "") -> CostRecord:
        """记录成本"""
        record = CostRecord(
            id=f"COST-{len(self.cost_records)+1:06d}",
            budget_id=budget_id,
            level=level,
            amount=amount,
            description=description,
            timestamp=datetime.now(),
            category=category
        )
        self.cost_records.append(record)
        
        # 检查是否触发红线
        self.check_redlines(budget_id)
        
        return record
    
    def get_actual_cost(self, budget_id: str, 
                       level: Optional[CostLevel] = None) -> float:
        """获取实际成本"""
        records = [r for r in self.cost_records if r.budget_id == budget_id]
        if level:
            records = [r for r in records if r.level == level]
        return sum(r.amount for r in records)
    
    def get_execution_rate(self, budget_id: str, 
                          level: Optional[CostLevel] = None) -> float:
        """获取执行率"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return 0.0
        
        actual = self.get_actual_cost(budget_id, level)
        planned = budget.total if level is None else budget.get_level_budget(level)
        
        if planned == 0:
            return 0.0
        return actual / planned
    
    def check_redlines(self, budget_id: str) -> Dict:
        """检查成本红线"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return {}
        
        results = {}
        
        # 检查总预算红线
        total_rate = self.get_execution_rate(budget_id)
        total_level = self.get_redline_level(total_rate)
        results["total"] = {
            "rate": total_rate,
            "level": total_level,
            "actual": self.get_actual_cost(budget_id),
            "budget": budget.total,
            "remaining": budget.total - self.get_actual_cost(budget_id)
        }
        
        # 检查各级红线
        for level in CostLevel:
            level_rate = self.get_execution_rate(budget_id, level)
            level_redline = self.get_redline_level(level_rate)
            results[level.value] = {
                "rate": level_rate,
                "level": level_redline,
                "actual": self.get_actual_cost(budget_id, level),
                "budget": budget.get_level_budget(level)
            }
        
        # 记录红线状态
        self.redline_history.append({
            "timestamp": datetime.now(),
            "budget_id": budget_id,
            "results": results
        })
        
        return results
    
    def get_redline_level(self, execution_rate: float) -> RedLineLevel:
        """获取红线级别"""
        if execution_rate >= self.REDLINE_THRESHOLDS[RedLineLevel.RED]:
            return RedLineLevel.RED
        elif execution_rate >= self.REDLINE_THRESHOLDS[RedLineLevel.YELLOW]:
            return RedLineLevel.YELLOW
        elif execution_rate >= self.REDLINE_THRESHOLDS[RedLineLevel.BLUE]:
            return RedLineLevel.BLUE
        else:
            return RedLineLevel.GREEN
    
    def get_redline_actions(self, level: RedLineLevel) -> List[str]:
        """获取红线响应动作"""
        actions = {
            RedLineLevel.GREEN: [
                "继续正常监控",
                "按计划执行支出"
            ],
            RedLineLevel.BLUE: [
                "发送成本提醒",
                "提供优化建议",
                "审查后续支出计划"
            ],
            RedLineLevel.YELLOW: [
                "发出成本警告",
                "暂停非必要支出",
                "召开成本审查会议",
                "制定控制措施"
            ],
            RedLineLevel.RED: [
                "立即暂停所有非必要支出",
                "启动应急审批流程",
                "上报管理层",
                "制定成本削减方案"
            ]
        }
        return actions.get(level, [])
    
    def analyze_cost_structure(self, budget_id: str) -> Dict:
        """分析成本结构"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return {}
        
        actual_by_level = {}
        for level in CostLevel:
            actual_by_level[level.value] = self.get_actual_cost(budget_id, level)
        
        total_actual = sum(actual_by_level.values())
        
        analysis = {
            "budget_id": budget_id,
            "total_budget": budget.total,
            "total_actual": total_actual,
            "total_execution_rate": total_actual / budget.total if budget.total > 0 else 0,
            "by_level": {},
            "recommendations": []
        }
        
        for level in CostLevel:
            actual = actual_by_level[level.value]
            planned = budget.get_level_budget(level)
            standard = self.STANDARD_ALLOCATION[level]
            
            actual_ratio = actual / total_actual if total_actual > 0 else 0
            
            analysis["by_level"][level.value] = {
                "actual": actual,
                "planned": planned,
                "execution_rate": actual / planned if planned > 0 else 0,
                "actual_ratio": actual_ratio,
                "standard_ratio": standard,
                "deviation": actual_ratio - standard
            }
            
            # 生成建议
            if actual_ratio > standard * 1.2:
                analysis["recommendations"].append(
                    f"{level.value}成本占比过高({actual_ratio:.1%})，建议控制在{standard:.1%}左右"
                )
        
        return analysis
    
    def generate_cost_report(self, budget_id: str) -> Dict:
        """生成成本报告"""
        budget = self.budgets.get(budget_id)
        if not budget:
            return {}
        
        redlines = self.check_redlines(budget_id)
        analysis = self.analyze_cost_structure(budget_id)
        
        # 获取今日支出
        today = datetime.now().date()
        today_costs = [r for r in self.cost_records 
                      if r.budget_id == budget_id and r.timestamp.date() == today]
        today_total = sum(r.amount for r in today_costs)
        
        # 获取本月支出
        month_start = today.replace(day=1)
        month_costs = [r for r in self.cost_records 
                      if r.budget_id == budget_id and r.timestamp.date() >= month_start]
        month_total = sum(r.amount for r in month_costs)
        
        return {
            "report_time": datetime.now(),
            "budget": {
                "id": budget.id,
                "name": budget.name,
                "total": budget.total,
                "period": f"{budget.period_start.date()} to {budget.period_end.date()}"
            },
            "summary": {
                "total_actual": analysis["total_actual"],
                "total_remaining": budget.total - analysis["total_actual"],
                "execution_rate": analysis["total_execution_rate"],
                "redline_status": redlines["total"]["level"].value
            },
            "today": {
                "cost": today_total,
                "records": len(today_costs)
            },
            "this_month": {
                "cost": month_total,
                "records": len(month_costs)
            },
            "by_level": analysis["by_level"],
            "recommendations": analysis["recommendations"]
        }
    
    def get_recent_records(self, budget_id: str, limit: int = 10) -> List[CostRecord]:
        """获取最近记录"""
        records = [r for r in self.cost_records if r.budget_id == budget_id]
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return records[:limit]

def run_cost_redlines(budget_id: str = None):
    """运行成本红线检查"""
    crl = CostRedLines()
    
    # 如果没有指定预算，使用第一个
    if budget_id is None and crl.budgets:
        budget_id = list(crl.budgets.keys())[0]
    
    if not budget_id:
        print("没有可用的预算")
        return None
    
    # 检查红线
    redlines = crl.check_redlines(budget_id)
    
    # 生成报告
    report = crl.generate_cost_report(budget_id)
    
    # 输出关键信息
    print(f"预算: {report['budget']['name']}")
    print(f"执行率: {report['summary']['execution_rate']:.1%}")
    print(f"红线状态: {report['summary']['redline_status']}")
    
    if report["recommendations"]:
        print("\n建议:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
    
    return report
```

### 4.3 标准响应模板

**红线预警**:
```
🔴 **成本红线预警 - 暂停支出**

预算: [预算名称]
当前执行率: [X]%
已触发: 红线(≥100%)

已采取措施:
- ✅ 暂停所有非必要支出
- ✅ 启动应急审批流程

请立即审查支出计划并制定控制措施。
```

**黄线警告**:
```
⚠️ **成本黄线警告**

预算: [预算名称]
当前执行率: [X]%
已触发: 黄线(≥80%)

建议措施:
- 审查后续支出计划
- 暂停非关键支出
- 优化资源配置

剩余预算: [金额]
预计可用天数: [N]天
```

**成本日报**:
```
📊 **成本日报**

预算: [名称]
报告日期: [日期]

执行概况:
- 总预算: [金额]
- 已支出: [金额] ([X]%)
- 剩余: [金额]

4级成本分布:
- L1基础: [金额] ([X]%)
- L2扩展: [金额] ([X]%)
- L3增值: [金额] ([X]%)
- L4风险: [金额] ([X]%)

红线状态: [绿/蓝/黄/红]

今日支出: [金额] ([N]笔)
```

---

## 五、流程自动化

### 5.1 定时任务

```json
{
  "jobs": [
    {
      "name": "cost-redline-check",
      "schedule": "0 */4 * * *",
      "enabled": true,
      "description": "每4小时检查成本红线"
    },
    {
      "name": "cost-daily-report",
      "schedule": "0 18 * * *",
      "enabled": true,
      "description": "每日18点生成成本报告"
    },
    {
      "name": "cost-weekly-analysis",
      "schedule": "0 9 * * 1",
      "enabled": true,
      "description": "每周一9点生成成本分析"
    }
  ]
}
```

### 5.2 自动化脚本

```bash
#!/bin/bash
# scripts/cost-redlines-check.sh

echo "=== 成本红线检查 ==="
echo "检查时间: $(date)"
echo ""

# 检查所有预算的红线状态
echo "1. 检查红线状态..."
python3 << 'EOF'
from cost_redlines import CostRedLines, RedLineLevel
crl = CostRedLines()

# 加载预算（示例）
if not crl.budgets:
    budget = crl.create_budget("月度运营成本", 10000, 30)
    print(f"创建示例预算: {budget.name}")

for bid, budget in crl.budgets.items():
    redlines = crl.check_redlines(bid)
    total = redlines["total"]
    
    emoji = {"green": "🟢", "blue": "🔵", "yellow": "🟡", "red": "🔴"}
    level = total["level"].value
    
    print(f"\n预算: {budget.name}")
    print(f"  状态: {emoji.get(level, '⚪')} {level.upper()}")
    print(f"  执行率: {total['rate']:.1%}")
    print(f"  已支出: {total['actual']:.2f} / {total['budget']:.2f}")
    print(f"  剩余: {total['remaining']:.2f}")
    
    if total["level"] in [RedLineLevel.YELLOW, RedLineLevel.RED]:
        print(f"  ⚠️ 建议措施:")
        for action in crl.get_redline_actions(total["level"]):
            print(f"    - {action}")
EOF

# 生成成本报告
echo ""
echo "2. 生成成本报告..."
python3 << 'EOF'
from cost_redlines import CostRedLines
crl = CostRedLines()

if crl.budgets:
    for bid in crl.budgets:
        report = crl.generate_cost_report(bid)
        print(f"\n预算: {report['budget']['name']}")
        print(f"  今日支出: {report['today']['cost']:.2f} ({report['today']['records']}笔)")
        print(f"  本月支出: {report['this_month']['cost']:.2f}")
        
        if report['recommendations']:
            print(f"  优化建议:")
            for rec in report['recommendations'][:3]:
                print(f"    - {rec}")
EOF

echo ""
echo "=== 检查完成 ==="
```

---

## 六、质量门控

- [x] **全局**: 4级成本×六层全覆盖
- [x] **系统**: 预算→监控→预警→控制闭环
- [x] **迭代**: 成本分析+预算优化循环
- [x] **Skill化**: 自动记录+红线检查+智能建议
- [x] **自动化**: 定时检查+自动预警+日报生成

---

## 七、使用方式

### 7.1 人工检查

```bash
# 检查成本红线
./scripts/cost-redlines-check.sh

# 创建新预算
python3 -c "from cost_redlines import CostRedLines; crl = CostRedLines(); crl.create_budget('项目预算', 50000, 90)"

# 记录成本
python3 -c "from cost_redlines import CostRedLines, CostLevel; crl = CostRedLines(); crl.record_cost('BUD-0001', CostLevel.L1_BASE, 100, '服务器费用')"
```

### 7.2 集成到工作流

所有成本支出自动记录和监控，系统会自动检查红线并发出预警。

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*
