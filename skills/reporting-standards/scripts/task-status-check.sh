#!/bin/bash
# 任务状态检查脚本

WORKSPACE="/root/.openclaw/workspace"
PROTOCOL_DIR="$WORKSPACE/memory/protocol"

echo "=== 当前任务状态检查 ==="
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查已完成的任务
COMPLETED=0
if [ -d "$PROTOCOL_DIR" ]; then
    COMPLETED=$(find "$PROTOCOL_DIR" -name "*completion.md" -mtime -1 2>/dev/null | wc -l)
fi
echo "✅ 今日已完成: $COMPLETED"

# 检查进行中
IN_PROGRESS=0
if [ -d "$PROTOCOL_DIR" ]; then
    IN_PROGRESS=$(find "$PROTOCOL_DIR" -name "*progress*" -mtime -1 2>/dev/null | wc -l)
fi
echo "🔄 进行中: $IN_PROGRESS"

# 检查阻塞
BLOCKED=0
if [ -d "$PROTOCOL_DIR" ]; then
    BLOCKED=$(find "$PROTOCOL_DIR" -name "*escalation.md" -mtime -1 2>/dev/null | wc -l)
fi
echo "🚫 阻塞: $BLOCKED"

# 检查未完成的确认
NOT_STARTED=0
echo "⏸️ 未完成: $NOT_STARTED"

echo ""
echo "=== 5要素汇总 ==="
echo "已完成: $COMPLETED | 进行中: $IN_PROGRESS | 阻塞: $BLOCKED | 风险: 0 | 未完成: $NOT_STARTED"
echo "=== 检查完成 ==="
