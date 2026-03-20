#!/bin/bash
# 每日协议统计脚本

WORKSPACE="/root/.openclaw/workspace"
PROTOCOL_DIR="$WORKSPACE/memory/protocol"
TODAY=$(date +%Y%m%d)
STATS_FILE="$PROTOCOL_DIR/stats-${TODAY}.json"

echo "=== 生成每日协议统计 ==="
echo "日期: $TODAY"

# 创建目录
mkdir -p "$PROTOCOL_DIR"

# 统计今日数据
CONFIRMED=$(find "$PROTOCOL_DIR" -name "*${TODAY}*-confirmation.md" 2>/dev/null | wc -l)
COMPLETED=$(find "$PROTOCOL_DIR" -name "*${TODAY}*-completion.md" 2>/dev/null | wc -l)
ESCALATED=$(find "$PROTOCOL_DIR" -name "*${TODAY}*-escalation.md" 2>/dev/null | wc -l)
PROGRESS_REPORTS=$(find "$PROTOCOL_DIR" -name "*${TODAY}*-progress-*.md" 2>/dev/null | wc -l)

# 计算执行率
if [ "$CONFIRMED" -gt 0 ]; then
    ADHERENCE_RATE=$(awk "BEGIN {printf \"%.1f\", ($COMPLETED / $CONFIRMED) * 100}")
else
    ADHERENCE_RATE="0.0"
fi

# 生成JSON统计
cat > "$STATS_FILE" << EOF
{
  "date": "$TODAY",
  "tasks_confirmed": $CONFIRMED,
  "tasks_completed": $COMPLETED,
  "tasks_escalated": $ESCALATED,
  "progress_reports": $PROGRESS_REPORTS,
  "protocol_adherence_rate": "${ADHERENCE_RATE}%",
  "generated_at": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF

echo ""
echo "📊 今日统计:"
cat "$STATS_FILE" | python3 -m json.tool 2>/dev/null || cat "$STATS_FILE"
echo ""
echo "💾 统计已保存到: $STATS_FILE"
echo "=== 统计完成 ==="
