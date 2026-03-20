# 每日备份检查清单

> **文档版本**: V1.0  
> **创建日期**: 2026-03-10  
> **关联文档**: [DISASTER_RECOVERY_PLAN_V1.0.md](./DISASTER_RECOVERY_PLAN_V1.0.md)

---

## 目录

1. [每日检查流程概览](#每日检查流程概览)
2. [自动检查脚本](#自动检查脚本)
3. [手动检查清单](#手动检查清单)
4. [异常处理流程](#异常处理流程)
5. [检查记录模板](#检查记录模板)

---

## 每日检查流程概览

### 检查时间

| 时间 | 检查类型 | 执行者 |
|------|----------|--------|
| **02:00** | 自动备份 | 系统 |
| **09:00** | 每日检查 | 管理员/AI |
| **22:00** | 日终确认 | 管理员/AI |

### 检查范围

```
/root/.openclaw/
├── workspace/
│   ├── *.md              # 核心Markdown文档
│   ├── .env              # API密钥配置
│   ├── .config/          # 配置文件
│   ├── memory/           # 记忆文件
│   ├── skills/           # Skill文件
│   ├── .scripts/         # 脚本文件
│   └── docs/             # 文档目录
├── cron/
│   └── jobs.json         # 定时任务配置
└── openclaw.json         # 主配置文件
```

---

## 自动检查脚本

### 脚本位置

`/root/.openclaw/workspace/scripts/backup-manager.py`

### 每日自动检查 (02:00 执行)

```bash
#!/bin/bash
# /root/.openclaw/workspace/scripts/daily-check.sh

LOG_FILE="/backups/logs/daily-check-$(date +%Y-%m-%d).log"
BACKUP_DIR="/backups/daily/$(date +%Y-%m-%d)"
STATUS_FILE="/backups/status/latest.json"

# 创建日志目录
mkdir -p /backups/logs /backups/status

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始每日备份检查" | tee -a $LOG_FILE

# 1. 磁盘空间检查
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查磁盘空间..." | tee -a $LOG_FILE
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 警告: 磁盘使用率 ${DISK_USAGE}% > 80%" | tee -a $LOG_FILE
    ALERT_DISK=true
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 磁盘使用率: ${DISK_USAGE}%" | tee -a $LOG_FILE
fi

# 2. 备份目录检查
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查备份目录..." | tee -a $LOG_FILE
if [ -d "$BACKUP_DIR" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 备份目录存在: $BACKUP_DIR" | tee -a $LOG_FILE
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 错误: 备份目录不存在" | tee -a $LOG_FILE
    ALERT_BACKUP=true
fi

# 3. Git状态检查
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查Git状态..." | tee -a $LOG_FILE
cd /root/.openclaw/workspace
if git diff --quiet; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Git工作区干净" | tee -a $LOG_FILE
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 警告: Git有未提交更改" | tee -a $LOG_FILE
    git status --short | tee -a $LOG_FILE
fi

# 4. 关键文件存在性检查
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查关键文件..." | tee -a $LOG_FILE
KEY_FILES=(
    "/root/.openclaw/workspace/.env"
    "/root/.openclaw/workspace/MEMORY.md"
    "/root/.openclaw/workspace/AGENTS.md"
    "/root/.openclaw/workspace/SOUL.md"
    "/root/.openclaw/workspace/USER.md"
    "/root/.openclaw/openclaw.json"
    "/root/.openclaw/cron/jobs.json"
)

for file in "${KEY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $file" | tee -a $LOG_FILE
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 丢失: $file" | tee -a $LOG_FILE
        ALERT_FILES=true
    fi
done

# 5. 今日记忆文件检查
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查今日记忆文件..." | tee -a $LOG_FILE
TODAY_MEM="/root/.openclaw/workspace/memory/$(date +%Y-%m-%d).md"
if [ -f "$TODAY_MEM" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 今日记忆文件存在" | tee -a $LOG_FILE
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 今日记忆文件不存在（可能正常）" | tee -a $LOG_FILE
fi

# 6. 生成状态报告
STATUS="success"
if [ "$ALERT_DISK" = true ] || [ "$ALERT_BACKUP" = true ] || [ "$ALERT_FILES" = true ]; then
    STATUS="warning"
fi

cat > $STATUS_FILE << EOF
{
  "date": "$(date +%Y-%m-%d)",
  "time": "$(date '+%H:%M:%S')",
  "status": "$STATUS",
  "disk_usage": $DISK_USAGE,
  "checks": {
    "disk_space": $(if [ "$DISK_USAGE" -gt 80 ]; then echo "false"; else echo "true"; fi),
    "backup_dir": $(if [ "$ALERT_BACKUP" = true ]; then echo "false"; else echo "true"; fi),
    "key_files": $(if [ "$ALERT_FILES" = true ]; then echo "false"; else echo "true"; fi)
  },
  "log_file": "$LOG_FILE"
}
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查完成，状态: $STATUS" | tee -a $LOG_FILE
```

### 快速健康检查脚本

```bash
#!/bin/bash
# 快速健康检查 - 每日09:00执行

echo "=== 满意解研究所每日健康检查 ==="
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 系统资源
echo "📊 系统资源"
echo "------------"
# CPU
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
printf "CPU使用率: "
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo -e "${RED}${CPU_USAGE}% ⚠️${NC}"
else
    echo -e "${GREEN}${CPU_USAGE}% ✅${NC}"
fi

# 内存
MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
printf "内存使用率: "
if (( $(echo "$MEM_USAGE > 85" | bc -l) )); then
    echo -e "${RED}${MEM_USAGE}% ⚠️${NC}"
else
    echo -e "${GREEN}${MEM_USAGE}% ✅${NC}"
fi

# 磁盘
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
printf "磁盘使用率: "
if [ "$DISK_USAGE" -gt 80 ]; then
    echo -e "${RED}${DISK_USAGE}% ⚠️${NC}"
else
    echo -e "${GREEN}${DISK_USAGE}% ✅${NC}"
fi
echo ""

# 2. 备份状态
echo "💾 备份状态"
echo "------------"
LATEST_BACKUP=$(ls -td /backups/daily/*/ 2>/dev/null | head -1)
if [ -n "$LATEST_BACKUP" ]; then
    BACKUP_DATE=$(basename $LATEST_BACKUP)
    echo -e "最新备份: ${GREEN}$BACKUP_DATE ✅${NC}"
else
    echo -e "最新备份: ${RED}无 ⚠️${NC}"
fi
echo ""

# 3. 关键文件
echo "📄 关键文件"
echo "------------"
KEY_FILES=(
    ".env:API配置"
    "MEMORY.md:长期记忆"
    "AGENTS.md:代理指南"
    "SOUL.md:组织精神"
)
for item in "${KEY_FILES[@]}"; do
    IFS=':' read -r file desc <<< "$item"
    if [ -f "/root/.openclaw/workspace/$file" ]; then
        echo -e "$desc: ${GREEN}✅${NC}"
    else
        echo -e "$desc: ${RED}❌${NC}"
    fi
done
echo ""

# 4. 服务状态
echo "🔧 服务状态"
echo "------------"
# Gateway状态
if pgrep -f "openclaw.*gateway" > /dev/null; then
    echo -e "OpenClaw Gateway: ${GREEN}运行中 ✅${NC}"
else
    echo -e "OpenClaw Gateway: ${RED}未运行 ❌${NC}"
fi
echo ""

# 5. Git状态
echo "📦 Git状态"
echo "------------"
cd /root/.openclaw/workspace
if git diff --quiet; then
    echo -e "工作区: ${GREEN}干净 ✅${NC}"
else
    UNSTAGED=$(git status --short | wc -l)
    echo -e "工作区: ${YELLOW}$UNSTAGED 个未提交更改 ⚠️${NC}"
fi

echo ""
echo "=== 检查完成 ==="
```

---

## 手动检查清单

### 每日09:00检查清单

#### 基础检查

- [ ] **1. 查看备份状态**
  ```bash
  cat /backups/status/latest.json
  ```
  - 期望结果: `status` 为 `"success"` 或 `"warning"`
  - 异常处理: 查看日志文件，定位问题

- [ ] **2. 检查磁盘空间**
  ```bash
  df -h
  ```
  - 期望结果: `/` 使用率 < 80%
  - 异常处理: 运行清理脚本 `backup-manager.py cleanup`

- [ ] **3. 检查今日记忆文件**
  ```bash
  ls -la /root/.openclaw/workspace/memory/$(date +%Y-%m-%d).md
  ```
  - 期望结果: 文件存在
  - 异常处理: 手动创建或从前一日复制

#### 核心文件检查

- [ ] **4. 验证核心配置文件**
  - [ ] `.env` 文件存在且可读
  - [ ] `openclaw.json` 格式正确
  - [ ] `cron/jobs.json` 格式正确

- [ ] **5. 验证关键文档**
  - [ ] `AGENTS.md` - AI代理工作指南
  - [ ] `SOUL.md` - 组织精神核心
  - [ ] `USER.md` - 用户信息
  - [ ] `MEMORY.md` - 长期记忆
  - [ ] `ORGANIZATION.md` - 组织架构

- [ ] **6. 检查角色定义文件**
  ```bash
  ls /root/.openclaw/workspace/ROLE-*.md | wc -l
  ```
  - 期望结果: 18个角色文件
  - 异常处理: 从备份恢复丢失的角色文件

#### 服务检查

- [ ] **7. 检查定时任务**
  ```bash
  openclaw cron list
  ```
  - 期望结果: 12个任务均显示 `enabled: true`
  - 重点关注:
    - 每日安全检查 (2个)
    - 每日晨报生成
    - 每日站会召开
    - 里程碑检查

- [ ] **8. 检查Git同步状态**
  ```bash
  cd /root/.openclaw/workspace && git status
  ```
  - 期望结果: `working tree clean` 或有预期的未提交更改
  - 异常处理: 提交重要更改，清理临时文件

### 每日22:00检查清单

- [ ] **1. 确认今日备份完成**
  ```bash
  ls -la /backups/daily/$(date +%Y-%m-%d)/
  ```

- [ ] **2. 检查日志文件**
  ```bash
  cat /backups/logs/daily-check-$(date +%Y-%m-%d).log
  ```

- [ ] **3. 确认无异常警告**
  - 查看备份状态JSON
  - 确认所有检查项通过

---

## 异常处理流程

### 异常分级

| 级别 | 描述 | 响应时间 | 处理人 |
|------|------|----------|--------|
| 🔴 紧急 | 备份失败/数据丢失 | 立即 | 系统管理员 |
| 🟠 重要 | 磁盘空间不足/关键文件缺失 | 1小时内 | 备份管理员 |
| 🟡 一般 | 非关键文件异常/警告 | 4小时内 | 值班人员 |
| 🟢 提示 | 信息性通知 | 下次检查时 | 自动处理 |

### 常见异常及处理

#### 🔴 异常1: 备份失败

**症状**: 
- 备份状态显示 `failed`
- 备份目录不存在

**处理步骤**:
```bash
# 1. 检查日志
tail -100 /backups/logs/daily-check-$(date +%Y-%m-%d).log

# 2. 检查磁盘空间
df -h

# 3. 手动触发备份
python3 /root/.openclaw/workspace/scripts/backup-manager.py backup --type daily

# 4. 验证备份
python3 /root/.openclaw/workspace/scripts/backup-manager.py verify --date $(date +%Y-%m-%d)
```

#### 🟠 异常2: 磁盘空间不足

**症状**:
- 磁盘使用率 > 80%
- 备份失败或警告

**处理步骤**:
```bash
# 1. 查看磁盘使用详情
du -sh /backups/* | sort -hr | head -10

# 2. 清理旧备份（保留最近30天）
python3 /root/.openclaw/workspace/scripts/backup-manager.py cleanup --days 30

# 3. 清理日志文件
find /backups/logs -name "*.log" -mtime +30 -delete

# 4. 再次检查
df -h
```

#### 🟠 异常3: 关键文件丢失

**症状**:
- 检查显示关键文件 ❌
- 文件大小为0或不存在

**处理步骤**:
```bash
# 1. 确认文件确实丢失
ls -la /path/to/missing/file

# 2. 从最新备份恢复
LATEST_BACKUP=$(ls -td /backups/daily/*/ | head -1)
cp $LATEST_BACKUP/workspace-md/MISSING_FILE.md /root/.openclaw/workspace/

# 3. 验证恢复结果
ls -la /root/.openclaw/workspace/MISSING_FILE.md
```

#### 🟡 异常4: Git未提交更改

**症状**:
- `git status` 显示有未提交文件
- 工作区不干净

**处理步骤**:
```bash
cd /root/.openclaw/workspace

# 1. 查看更改内容
git diff

# 2. 添加重要文件
git add -A

# 3. 提交
git commit -m "$(date +%Y-%m-%d) 自动备份提交"

# 4. 推送（如配置了远程仓库）
git push origin main
```

#### 🟡 异常5: 定时任务异常

**症状**:
- `openclaw cron list` 显示任务 disabled
- 任务上次执行状态为 error

**处理步骤**:
```bash
# 1. 查看任务详情
openclaw cron list

# 2. 重新启用任务
openclaw cron enable <task-id>

# 3. 如有必要，从备份恢复 jobs.json
cp /backups/daily/$(date +%Y-%m-%d)/cron/jobs.json /root/.openclaw/cron/jobs.json

# 4. 重启gateway
openclaw gateway restart
```

### 升级流程

```
检测到异常
    ↓
判断是否可自动恢复
    ↓
是 → 执行自动修复脚本
    ↓
否 → 评估异常级别
         ↓
    🔴紧急/🟠重要 → 立即通知系统管理员
         ↓
    🟡一般 → 记录到问题清单，安排处理
         ↓
    处理完成 → 更新检查记录
         ↓
    验证修复结果
```

---

## 检查记录模板

### 每日检查记录

```markdown
# 每日备份检查记录

**日期**: 2026-03-10  
**检查人**: [AI/管理员名称]  
**检查时间**: 09:00

## 执行结果

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 备份状态 | ✅ 通过 | 状态: success |
| 磁盘空间 | ✅ 通过 | 使用率: 45% |
| 核心文件 | ✅ 通过 | 所有关键文件存在 |
| 记忆文件 | ✅ 通过 | 今日文件已创建 |
| Git状态 | ✅ 通过 | 工作区干净 |
| 定时任务 | ✅ 通过 | 12/12 正常运行 |

## 发现问题

- [ ] 无问题
- [x] 发现问题（描述如下）

**问题描述**: [如有]

**处理措施**: [如有]

**处理结果**: [已解决/待跟进]

## 备注

[其他需要记录的信息]

---
**下次检查**: 2026-03-10 22:00
```

### 周检查记录

```markdown
# 每周备份检查记录

**周期**: 2026-03-03 至 2026-03-10  
**检查人**: [管理员名称]  
**检查日期**: 2026-03-10

## 本周备份统计

| 日期 | 状态 | 大小 | 完整性 |
|------|------|------|--------|
| 03-04 | ✅ | 8.5MB | ✓ |
| 03-05 | ✅ | 8.7MB | ✓ |
| 03-06 | ✅ | 8.6MB | ✓ |
| 03-07 | ✅ | 8.8MB | ✓ |
| 03-08 | ✅ | 8.5MB | ✓ |
| 03-09 | ✅ | 8.9MB | ✓ |
| 03-10 | ✅ | 8.6MB | ✓ |

## 恢复演练

- [x] 已执行恢复演练
- [ ] 未执行恢复演练

**演练结果**: [通过/未通过]

**发现的问题**: [如有]

## 存储分析

- 本周新增备份: 60.6 MB
- 当前总备份量: 1.2 GB
- 预计剩余可用: 45天

## 优化建议

[记录本周发现的可优化点]

## 下周计划

- [ ] 继续每日监控
- [ ] 执行月度恢复演练
- [ ] 审查备份策略
```

---

## 附录

### 快速命令参考

```bash
# 查看最新备份状态
cat /backups/status/latest.json

# 查看今日检查日志
cat /backups/logs/daily-check-$(date +%Y-%m-%d).log

# 手动触发备份
python3 /root/.openclaw/workspace/scripts/backup-manager.py backup --type daily

# 验证备份完整性
python3 /root/.openclaw/workspace/scripts/backup-manager.py verify

# 清理旧备份
python3 /root/.openclaw/workspace/scripts/backup-manager.py cleanup --days 30

# 恢复最新备份
python3 /root/.openclaw/workspace/scripts/backup-manager.py restore --latest

# 查看备份历史
python3 /root/.openclaw/workspace/scripts/backup-manager.py list
```

### 相关文档链接

- [主灾备计划](./DISASTER_RECOVERY_PLAN_V1.0.md)
- [备份管理器脚本](../scripts/backup-manager.py)
- [定时任务配置](../../cron/jobs.json)

---

**文档结束**

> 每日检查清单由满意解研究所灾备重建项目组维护  
> 发现问题请及时记录并报告
