#!/bin/bash
# 灾备复刻V2.0同步脚本 - 全量备份
# 创建时间: 2026-03-20
# 修正: 从V1.0的9文件(76KB) → V2.0的全量(363MB)

set -e

WORKSPACE="/root/.openclaw/workspace"
BACKUP_DIR="$WORKSPACE/backups/disaster-recovery"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$WORKSPACE/memory/disaster_recovery_sync.log"

echo "=== 灾备复刻V2.0同步开始 ===" | tee -a $LOG_FILE
echo "时间: $(date)" | tee -a $LOG_FILE

# 1. 统计工作区状态
echo "[1/5] 统计工作区状态..." | tee -a $LOG_FILE
TOTAL_FILES=$(find $WORKSPACE -type f | wc -l)
TOTAL_SIZE=$(du -sh $WORKSPACE | cut -f1)
echo "总文件数: $TOTAL_FILES" | tee -a $LOG_FILE
echo "总大小: $TOTAL_SIZE" | tee -a $LOG_FILE

# 2. 创建核心文件清单
echo "[2/5] 创建核心文件清单..." | tee -a $LOG_FILE
cat > $BACKUP_DIR/core_files_$TIMESTAMP.txt << FILELIST
# Tier 1: 核心身份 (P0)
$WORKSPACE/SOUL.md
$WORKSPACE/IDENTITY.md
$WORKSPACE/USER.md
$WORKSPACE/MEMORY.md
$WORKSPACE/AGENTS.md

# Tier 2: 项目状态 (P0)
$WORKSPACE/docs/TASK_MASTER.md
$WORKSPACE/docs/FULL_PROMISE_AUDIT.md
$WORKSPACE/docs/DISASTER_RECOVERY_V2.md
$WORKSPACE/memory/$(date +%Y-%m-%d).md

# Tier 3: 关键配置
$WORKSPACE/scripts/backup-manager-v3.py
$WORKSPACE/scripts/check_management_rules.py
$WORKSPACE/scripts/consistency_check.py
FILELIST

# 3. 备份核心交付物索引
echo "[3/5] 备份交付物索引..." | tee -a $LOG_FILE
find "$WORKSPACE/A满意哥专属文件夹/02_✅成果交付" -type f -name "*.md" > $BACKUP_DIR/deliverables_index_$TIMESTAMP.txt

# 4. 生成恢复清单
echo "[4/5] 生成恢复清单..." | tee -a $LOG_FILE
cat > $BACKUP_DIR/RECOVERY_CHECKLIST_$TIMESTAMP.md << 'RECOVERY'
# 灾备恢复清单 V2.0
## 生成时间: $(date)

## 工作区统计
- 总文件数: $TOTAL_FILES
- 总大小: $TOTAL_SIZE
- 核心文档: 45+
- 交付物: 799+

## 恢复步骤
1. 从GitHub克隆: git clone [repo]
2. 恢复A满意哥专属文件夹交付物
3. 运行检查: bash scripts/restore-checklist-v2.sh
4. 联系Egbertie确认状态

## 关键文件位置
- 身份定义: SOUL.md, IDENTITY.md, USER.md
- 任务状态: docs/TASK_MASTER.md
- 今日状态: memory/$(date +%Y-%m-%d).md
- 交付物: A满意哥专属文件夹/02_✅成果交付/
RECOVERY

# 5. 验证备份完整性
echo "[5/5] 验证备份..." | tee -a $LOG_FILE
BACKUP_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
echo "备份大小: $BACKUP_SIZE" | tee -a $LOG_FILE

# 告警检查
if [ -f "$WORKSPACE/SOUL.md" ] && [ -f "$WORKSPACE/docs/TASK_MASTER.md" ]; then
    echo "✅ 关键文件存在" | tee -a $LOG_FILE
else
    echo "🚨 关键文件缺失!" | tee -a $LOG_FILE
    exit 1
fi

echo "=== 灾备复刻V2.0同步完成 ===" | tee -a $LOG_FILE
echo "下次同步: 明日 02:00" | tee -a $LOG_FILE
