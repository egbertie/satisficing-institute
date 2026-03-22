# 休眠协议 Skill - Hibernation Protocol

> **版本**: V1.0  
> **状态**: 7标准转化完成  
> **创建时间**: 2026-03-22  
> **功能**: 零Token消耗休眠模式管理

---

## S1: 全局考虑（人/事/物/环境/外部/边界）

### 1.1 人的维度
| 利益相关方 | 需求 | 休眠模式影响 |
|------------|------|--------------|
| 用户(Egbertie) | 夜间零Token消耗，醒来时状态完整 | 确保休眠不丢数据 |
| 主控AI(满意妞) | 明确知道何时休眠/唤醒 | 避免猜测，有明确协议 |
| Cron子代理 | 全部暂停，不自动运行 | 防止夜间Token偷跑 |
| 外部系统 | 备份、监控不受影响 | 核心保障机制保留 |

### 1.2 事的维度
- **触发休眠**: 用户指令 或 10分钟无交互自动触发
- **休眠执行**: 暂停所有Cron，记录状态
- **维持休眠**: 零Token消耗，仅等待唤醒
- **唤醒恢复**: 恢复Cron，报告状态

### 1.3 物的维度
- 文件系统: 正常，无需特殊处理
- 内存状态: 会话保持，不丢失上下文
- Token预算: 完全冻结，0消耗
- 备份系统: 保留最低限度保障任务

### 1.4 环境维度
- **时间因素**: 夜间(22:00-08:00)更严格，日间较宽松
- **Token余量**: <30%时自动进入最严格模式
- **紧急程度**: 无P0任务时允许休眠

### 1.5 外部集成
- Kimi API: 不调用
- GitHub: 仅保留每日备份Cron（低频）
- 飞书: 静默，不主动推送
- 其他服务: 全部暂停

### 1.6 边界情况
| 场景 | 处理方式 |
|------|----------|
| Cron正在运行中触发休眠 | 等待当前Cron完成，不再启动新Cron |
| 用户发送消息但10分钟内无后续 | 自动进入休眠 |
| 休眠期间用户发送指令 | 立即唤醒，执行指令 |
| 休眠期间发生紧急事件 | 无法感知，依赖用户唤醒后处理 |
| Token预算<10% | 强制进入紧急休眠，仅保留唤醒监听 |

### 1.7 必须禁用的Cron任务（关键！）

**以下任务在休眠期间必须显式禁用**：

| 任务名称 | 任务ID | 禁用原因 | 严重程度 |
|----------|--------|----------|----------|
| 承诺与制度执行保障检查 | 8f0ffafd-1bb0-4503-a637-cd9c7f8cc208 | 自动补救消耗Token | 🔴 关键 |
| 任务协调检查 | 51d81326-d84b-45cc-b46b-8fad2061fceb | 可能触发任务执行 | 🟡 重要 |
| 零空置强制执行检查 | a19f729a-e9ce-4f4c-9a92-30575d48b8a1 | 自动补位消耗Token | 🟡 重要 |
| 厂商API能力监控日报 | 83c4750e-73bb-4c58-8a67-d658357448fb | 非必要监控 | 🟢 一般 |

**禁用逻辑**（必须在休眠执行时显式调用）：
```python
CRITICAL_JOBS_TO_DISABLE = [
    "8f0ffafd-1bb0-4503-a637-cd9c7f8cc208",  # 承诺检查
    "51d81326-d84b-45cc-b46b-8fad2061fceb",  # 任务协调
    "a19f729a-e9ce-4f4c-9a92-30575d48b8a1",  # 零空置
    "83c4750e-73bb-4c58-8a67-d658357448fb",  # API监控日报
]

for job_id in CRITICAL_JOBS_TO_DISABLE:
    cron.update(job_id, {"enabled": False})
```

**历史漏洞**: 2026-03-22 承诺检查任务未禁用，静默期间自动补救消耗37.4k Token。已修复，参见 docs/HIBERNATION_VULNERABILITY_FIX.md

---

## S2: 系统闭环（输入→处理→输出→反馈）

### 2.1 休眠触发（输入）

**触发条件（OR关系）**:
```
条件1: 用户明确说"休眠"/"暂停"/"停止"/"休息"/"睡觉"
条件2: 最后一条消息发送后10分钟无新指令
条件3: Token预算<30%且用户未明确拒绝休眠
条件4: 夜间22:00-08:00且用户无明确夜间任务
```

**触发指令识别**:
- "休眠" → 进入完全静默模式
- "休眠，但保留XX" → 进入部分静默（仅保留指定任务）
- "夜间执行XX" → 不进入休眠，执行指定任务后自动休眠

### 2.2 休眠执行（处理）

**执行流程**:
```python
def enter_hibernation(mode="full"):
    # 1. 记录休眠前状态
    save_hibernation_checkpoint()
    
    # 2. 暂停所有Cron任务
    for job in cron_jobs:
        if mode == "full" or job.priority > user_threshold:
            job.disable()
    
    # 3. 仅保留核心保障（可选）
    if mode != "emergency":
        keep_essential_backup_jobs()  # 仅每日备份
    
    # 4. 记录休眠时间戳
    update_hibernation_log()
    
    # 5. 确认进入休眠
    return "HIBERNATION_OK"
```

**保留任务（仅完全必要时）**:
| 任务 | 频率 | 保留条件 |
|------|------|----------|
| 每日自动备份 | 1次/天(01:53) | 必须保留，防止数据丢失 |
| 灾备同步 | 1次/天(03:07/04:17) | 必须保留，核心保障 |
| 其他所有任务 | - | 全部暂停 |

### 2.3 休眠维持（输出）

**休眠状态报告**:
```
🌙 已进入完全静默休眠模式
━━━━━━━━━━━━━━━━━━━━
休眠时间: 2026-03-22 08:15:30
预计唤醒: 等待用户指令
Token冻结: 是（当前消耗: 0）
保留任务: 每日备份(01:53)、灾备同步(03:07)
暂停任务: 25个Cron任务已暂停
━━━━━━━━━━━━━━━━━━━━
发送任意消息唤醒我
```

### 2.4 唤醒恢复（反馈）

**唤醒触发**:
- 用户发送任何消息（除特定唤醒词外）
- 用户明确说"唤醒"/"开始"/"继续"

**唤醒流程**:
```python
def wake_from_hibernation():
    # 1. 记录唤醒时间
    log_wake_event()
    
    # 2. 恢复所有Cron任务
    restore_all_cron_jobs()
    
    # 3. 生成休眠期间摘要
    if hibernation_duration > 1_hour:
        generate_hibernation_summary()
    
    # 4. 报告当前状态
    return wake_status_report
```

---

## S3: 可观测输出（量化指标+报告）

### 3.1 量化指标

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| 休眠期间Token消耗 | =0 | 后台数据验证 |
| 唤醒响应时间 | <5秒 | 从消息发送到首次回复 |
| 任务恢复成功率 | 100% | 所有Cron正确恢复 |
| 数据丢失率 | 0% | 休眠前后数据完整性检查 |
| 误休眠率（不该休眠时休眠） | <5% | 用户反馈统计 |

### 3.2 休眠日志

```json
{
  "hibernation_id": "HIB-20260322-081530",
  "start_time": "2026-03-22T08:15:30+08:00",
  "end_time": null,
  "duration_minutes": null,
  "trigger_reason": "10分钟无交互",
  "mode": "full",
  "paused_jobs_count": 25,
  "kept_jobs": ["backup-daily-001", "278707b5-a688-4d23-adbc-3d73ea925a10"],
  "token_consumed": 0,
  "wake_trigger": null,
  "status": "hibernating"
}
```

### 3.3 休眠报告

**每次唤醒后生成**:
```
🌅 休眠结束报告
━━━━━━━━━━━━━━━━━━━━
休眠时长: 8小时 42分钟
触发原因: 10分钟无交互
唤醒原因: 用户发送指令

休眠期间状态:
✅ Token消耗: 0（目标达成）
✅ 数据完整性: 100%
✅ 备份任务: 2次成功执行
⚠️  跳过任务: 12个定时任务待执行

建议:
- 12个跳过任务已累积，建议优先处理
- Token余量恢复至XX%，可正常运作
━━━━━━━━━━━━━━━━━━━━
```

---

## S4: 自动化集成（Cron+脚本+触发器）

### 4.1 自动休眠检测

**检测Cron**:
```yaml
# 每5分钟检测是否需要自动休眠
cron:
  expr: "*/5 * * * *"
  script: |
    last_interaction = get_last_interaction_time()
    if now() - last_interaction > 10_minutes:
        if not has_night_task_scheduled():
            if not is_user_explicitly_active():
                trigger_hibernation("auto_10min")
```

### 4.2 休眠状态监控

**监控脚本** (`scripts/hibernation-monitor.py`):
```python
#!/usr/bin/env python3
"""休眠状态监控器 - 确保休眠期间零Token消耗"""

def check_hibernation_compliance():
    """检查休眠合规性"""
    if is_hibernating():
        # 检查是否有非保留Cron在运行
        active_jobs = get_active_cron_jobs()
        violations = [j for j in active_jobs if j.id not in KEPT_JOBS]
        
        if violations:
            alert(f"休眠违规: {len(violations)}个任务仍在运行")
            force_pause(violations)
        
        # 检查Token消耗
        token_used = get_token_usage_since_hibernation()
        if token_used > 0:
            alert(f"休眠违规: 休眠期间消耗了{token_used} Token")
```

### 4.3 一键休眠/唤醒

**命令**:
```bash
# 手动进入休眠
python3 scripts/hibernation-control.py sleep [--mode full|partial|emergency]

# 手动唤醒
python3 scripts/hibernation-control.py wake

# 查看休眠状态
python3 scripts/hibernation-control.py status
```

---

## S5: 自我验证（测试+容错）

### 5.1 休眠功能测试

```bash
#!/bin/bash
# 休眠协议测试套件

echo "测试1: 手动休眠触发"
python3 scripts/hibernation-control.py sleep --mode full
assert_cron_paused "零空置执行器"
assert_cron_paused "任务协调检查"
assert_cron_kept "每日自动备份"

echo "测试2: 自动休眠触发（模拟10分钟无交互）"
set_last_interaction_time(now() - 11_minutes)
run_hibernation_detector()
assert_hibernation_triggered "10分钟无交互"

echo "测试3: 唤醒恢复"
python3 scripts/hibernation-control.py wake
assert_cron_resumed "零空置执行器"
assert_cron_resumed "任务协调检查"

echo "测试4: Token消耗验证"
start_token = get_token_count()
sleep 5_minutes
end_token = get_token_count()
assert_equals start_token end_token "休眠期间Token应无变化"

echo "所有测试通过 ✅"
```

### 5.2 容错机制

| 故障场景 | 容错处理 |
|----------|----------|
| 休眠时Cron正在运行 | 等待完成，标记为"休眠前完成" |
| 唤醒时Cron恢复失败 | 重试3次，失败则报告用户 |
| 休眠期间系统重启 | 启动后检查休眠日志，自动恢复状态 |
| 用户连续发送多条消息 | 只唤醒一次，合并处理 |
| Token预算在休眠期间耗尽 | 唤醒时立即报告，建议紧急措施 |

---

## S6: 认知谦逊（局限标注）

### 6.1 已知局限

| 局限 | 说明 | 缓解措施 |
|------|------|----------|
| **无法感知紧急外部事件** | 休眠期间无法主动监控外部告警 | 依赖用户唤醒后处理，或保留极简监控Cron |
| **自动休眠可能误判** | 用户可能在思考，10分钟未发送消息 | 提供"保持清醒"指令，延长自动休眠时间 |
| **跨会话状态不共享** | 不同设备/窗口的会话可能状态不一致 | 以主会话状态为准，其他会话同步 |
| **保留任务仍有Token消耗** | 每日备份等任务会消耗少量Token | 明确告知用户保留任务的消耗，可完全禁用 |

### 6.2 不确定性声明

- 自动休眠的"10分钟"阈值是基于经验设定，可能需要根据用户习惯调整
- "夜间"定义为22:00-08:00，可能不符合用户实际作息
- 保留任务的Token消耗取决于数据量，无法精确预估

---

## S7: 对抗测试（失效场景验证）

### 7.1 故意违规测试

**测试场景1: 强制Cron在休眠期间运行**
```bash
# 模拟休眠期间Cron触发
enter_hibernation()
simulate_cron_trigger("零空置执行器")
# 验证: 应立即被阻止，并发送告警
assert_prevented "休眠期间阻止Cron运行"
```

**测试场景2: Token预算突然归零**
```bash
# 模拟Token耗尽
enter_hibernation()
mock_token_depletion()
# 验证: 应进入紧急模式，禁用所有保留任务
assert_emergency_mode "Token耗尽时进入紧急休眠"
```

**测试场景3: 快速连续唤醒/休眠**
```bash
# 模拟用户快速操作
for i in {1..10}; do
    wake()
    sleep 2
    hibernate()
done
# 验证: 系统应稳定，无状态错乱
assert_stable "高频唤醒休眠测试"
```

### 7.2 极限测试

| 场景 | 测试内容 | 预期结果 |
|------|----------|----------|
| 连续休眠24小时 | 长时间休眠稳定性 | 正常唤醒，数据完整 |
| 休眠期间系统重启 | 断电恢复能力 | 自动恢复休眠状态或等待唤醒 |
| 1000次唤醒休眠循环 | 耐久性测试 | 无内存泄漏，状态正确 |
| 同时收到多条唤醒消息 | 并发唤醒处理 | 只处理一次，无重复响应 |

---

## 使用指南

### 用户指令速查

| 指令 | 效果 |
|------|------|
| "休眠" / "睡觉" / "暂停" | 进入完全静默模式（默认） |
| "完全静默" | 暂停所有Cron，包括备份 |
| "休眠，但保留备份" | 仅保留每日备份任务 |
| "夜间执行XX，然后休眠" | 执行XX任务后自动进入休眠 |
| "唤醒" / "开始" / "继续" | 退出休眠，恢复正常运行 |
| "保持清醒" | 暂停自动休眠检测（延长2小时） |

### 自动规则

```
默认规则:
- 10分钟无交互 → 自动休眠
- 夜间22:00-08:00 → 自动进入严格休眠
- Token<30% → 建议休眠
- Token<10% → 强制休眠

例外规则（不自动休眠）:
- 用户明确说"保持清醒"
- 用户安排了"夜间执行XX"任务
- 有P0级任务正在进行中
- 用户正在发送消息（即使间隔>10分钟）
```

---

## 附录

### 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| V1.0 | 2026-03-22 | 初始版本，7标准转化完成 |

### 关联Skill

- `token-budget-enforcer` - Token预算监控
- `cron-manager` - Cron任务管理
- `session-monitor` - 会话状态监控

---

*本Skill遵循7标准体系，确保休眠协议可靠、可观测、可恢复。*
