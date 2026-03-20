# Token节流控制器标准Skill V2.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V2.0 | 更新: 2026-03-20 | 核心: Token分层自动调控

---

## 一、全局考虑（六层+三级节流）

### 节流层级 × 六层矩阵

| 层级 | Token阈值 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|------|-----------|--------|--------|--------|--------|--------|--------|
| **正常** | >30% | 全能力 | 全任务 | 全系统 | 全集成 | 全交付 | 全归档 |
| **节流** | 15-30% | 核心能力 | 核心任务 | 核心系统 | 有限集成 | 核心交付 | 延迟归档 |
| **暂停** | <15% | 等待指令 | 暂停 | 暂停 | 暂停 | 暂停 | 暂停 |

---

## 二、系统考虑（监控→判断→执行→恢复闭环）

### 2.1 三级调控规则

```yaml
token_throttle:
  level_1_normal:
    threshold: ">30%"
    action: "full_operation"
    available_lines: ["线1", "线2", "线3", "线4", "线5", "线6"]
    
  level_2_throttle:
    threshold: "15%-30%"
    action: "reduce_to_line2_only"
    available_lines: ["线2"]  # 仅保留优化复盘
    suspended: ["线1", "线3", "线4", "线5", "线6"]
    
  level_3_pause:
    threshold: "<15%"
    action: "full_pause_wait_for_instruction"
    available_lines: []
    all_suspended: true
    alert_user: true
```

---

## 三、迭代机制（每次Token检查自动调整）

---

## 四、Skill化（自动调控）

```python
def token_throttle_controller():
    """Token节流控制主函数"""
    token_level = get_current_token_level()
    
    if token_level > 30:
        resume_all_lines()
    elif 15 <= token_level <= 30:
        suspend_lines(["线1", "线3", "线4", "线5", "线6"])
        notify_user("Token进入节流模式，仅保留线2")
    else:
        suspend_all_lines()
        alert_user("Token低于15%，全部暂停，等待指令")
```

---

## 五、流程自动化（每15分钟检查）

```json
{
  "job": {
    "name": "token-throttle-check",
    "schedule": "*/15 * * * *"
  }
}
```

---

## 六、质量门控

- [x] **全局**: 三级×六层
- [x] **系统**: 监控→判断→执行→恢复
- [x] **迭代**: 自动调整
- [x] **Skill化**: 自动调控
- [x] **自动化**: 定时检查

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*