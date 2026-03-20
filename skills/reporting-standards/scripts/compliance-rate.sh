#!/bin/bash
# 制度执行率计算脚本

WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/memory/reports"

echo "=== 制度执行率统计 ==="
echo "统计时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 本周日报统计
DAILY_COUNT=0
if [ -d "$REPORT_DIR/daily" ]; then
    DAILY_COUNT=$(find "$REPORT_DIR/daily" -name "*.md" -mtime -7 2>/dev/null | wc -l)
fi

EXPECTED=7
RATE=$(awk "BEGIN {printf \"%.1f\", ($DAILY_COUNT / $EXPECTED) * 100}")

echo "📊 本周日报完成率: $RATE% ($DAILY_COUNT/$EXPECTED)"
echo ""

# 显示状态
if (( $(echo "$RATE >= 90" | bc -l 2>/dev/null || awk "BEGIN {exit !($RATE >= 90)}") )); then
    echo "🟢 状态: 优秀 (≥90%)"
elif (( $(echo "$RATE >= 70" | bc -l 2>/dev/null || awk "BEGIN {exit !($RATE >= 70)}") )); then
    echo "🟡 状态: 良好 (70-89%)"
elif (( $(echo "$RATE >= 50" | bc -l 2>/dev/null || awk "BEGIN {exit !($RATE >= 50)}") )); then
    echo "🟠 状态: 需改进 (50-69%)"
else
    echo "🔴 状态: 严重 (<50%)"
fi

echo ""
echo "=== 统计完成 ==="
