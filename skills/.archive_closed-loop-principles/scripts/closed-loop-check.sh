#!/bin/bash
# 闭环三原则检查脚本
# skills/closed-loop-principles/scripts/closed-loop-check.sh

echo "=== 闭环三原则检查 ==="
echo "检查时间: $(date)"
echo ""

WORKSPACE="/root/.openclaw/workspace"
SKILL_DIR="$WORKSPACE/skills/closed-loop-principles"
LOG_DIR="$SKILL_DIR/logs"

mkdir -p "$LOG_DIR"

# 检查待确认事项
echo "1. 检查待确认事项..."
PENDING_CONFIRM=$(find "$WORKSPACE" -name "*.md" -mtime -1 -exec grep -l "待确认\|pending" {} \; 2>/dev/null | wc -l)
echo "   发现 $PENDING_CONFIRM 个待确认事项"

# 检查待落实事项
echo "2. 检查待落实事项..."
PENDING_IMPL=$(find "$WORKSPACE" -name "*.md" -mtime -3 -exec grep -l "待落实\|in_progress\|进行中" {} \; 2>/dev/null | wc -l)
echo "   发现 $PENDING_IMPL 个待落实事项"

# 检查待反馈事项
echo "3. 检查待反馈事项..."
PENDING_FEEDBACK=$(find "$WORKSPACE" -name "*.md" -mtime -7 -exec grep -l "待反馈\|等待反馈\|pending_feedback" {} \; 2>/dev/null | wc -l)
echo "   发现 $PENDING_FEEDBACK 个待反馈事项"

# 生成检查记录
LOG_FILE="$LOG_DIR/closed-loop-check-$(date +%Y%m%d-%H%M%S).log"
cat > "$LOG_FILE" << EOF
闭环检查记录
check_time: $(date -Iseconds)
pending_confirmations: $PENDING_CONFIRM
pending_implementations: $PENDING_IMPL
pending_feedbacks: $PENDING_FEEDBACK
status: completed
EOF

echo ""
echo "记录已保存: $LOG_FILE"
echo "=== 检查完成 ==="

# 如果有待闭环事项，输出提醒
TOTAL=$((PENDING_CONFIRM + PENDING_IMPL + PENDING_FEEDBACK))
if [ $TOTAL -gt 0 ]; then
    echo ""
    echo "⚠️ 发现 $TOTAL 个待闭环事项，请关注!"
    exit 1
fi

exit 0
