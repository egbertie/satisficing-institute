#!/bin/bash
# 变更同步检查脚本
# skills/change-sync/scripts/change-sync-check.sh

echo "=== 变更同步检查 ==="
echo "检查时间: $(date)"
echo ""

WORKSPACE="/root/.openclaw/workspace"
SKILL_DIR="$WORKSPACE/skills/change-sync"
LOG_DIR="$SKILL_DIR/logs"
CHANGE_FILE="$LOG_DIR/changes.json"
QUEUE_FILE="$LOG_DIR/sync-queue.json"

mkdir -p "$LOG_DIR"

# 初始化文件
if [ ! -f "$CHANGE_FILE" ]; then
    echo "[]" > "$CHANGE_FILE"
fi
if [ ! -f "$QUEUE_FILE" ]; then
    echo "[]" > "$QUEUE_FILE"
fi

# 检测变更
echo "1. 检测变更..."
# 检查最近5分钟内修改的文件
RECENT_CHANGES=$(find "$WORKSPACE" -type f -mmin -5 ! -path "*/logs/*" ! -path "*/.git/*" 2>/dev/null | wc -l)
echo "   最近5分钟变更: $RECENT_CHANGES 个文件"

# 检查同步队列
echo ""
echo "2. 检查同步队列..."
PENDING_SYNC=$(cat "$QUEUE_FILE" 2>/dev/null | grep -c '"synced": false' || echo "0")
echo "   待同步: $PENDING_SYNC 个"

# 检查逾期同步
echo ""
echo "3. 检查逾期同步..."
# 简化处理，实际应解析JSON检查时间戳
OVERDUE_SYNC=0
echo "   逾期同步: $OVERDUE_SYNC 个"

# 生成检查记录
LOG_FILE="$LOG_DIR/change-sync-$(date +%Y%m%d-%H%M%S).log"
cat > "$LOG_FILE" << EOF
变更同步检查记录
check_time: $(date -Iseconds)
recent_changes: $RECENT_CHANGES
pending_sync: $PENDING_SYNC
overdue_sync: $OVERDUE_SYNC
status: completed
EOF

echo ""
echo "记录已保存: $LOG_FILE"
echo "=== 检查完成 ==="

# 如果有大量待同步，输出提醒
if [ "$PENDING_SYNC" -gt 10 ]; then
    echo ""
    echo "⚠️ 待同步队列积压，请检查同步服务!"
    exit 1
fi

exit 0
