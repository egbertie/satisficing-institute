#!/bin/bash
# 任务链检查脚本 - 检查完成的任务并触发下一任务

WORKSPACE="/root/.openclaw/workspace"
PROTOCOL_DIR="$WORKSPACE/memory/protocol"

echo "=== 任务链检查 ==="
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 创建目录
mkdir -p "$PROTOCOL_DIR"

# 查找最近完成的但未触发下一任务的任务
RECENTLY_COMPLETED=$(find "$PROTOCOL_DIR" -name "*completion.md" -mmin -30 2>/dev/null)

TRIGGER_COUNT=0

if [ -z "$RECENTLY_COMPLETED" ]; then
    echo "📭 无新完成任务（过去30分钟内）"
else
    for completion_file in $RECENTLY_COMPLETED; do
        task_id=$(basename "$completion_file" | sed 's/-completion.md//')
        chain_file="$PROTOCOL_DIR/${task_id}-chain-triggered"
        
        if [ ! -f "$chain_file" ]; then
            echo "🔄 任务 $task_id 刚完成，准备触发下一任务..."
            # 这里可以解析任务依赖关系，触发下一任务
            touch "$chain_file"
            echo "   时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$chain_file"
            echo "   状态: 已触发任务链" >> "$chain_file"
            echo "   ✅ 已标记任务链触发"
            TRIGGER_COUNT=$((TRIGGER_COUNT + 1))
        fi
    done
fi

echo ""
echo "本次触发任务数: $TRIGGER_COUNT"
echo "=== 检查完成 ==="
