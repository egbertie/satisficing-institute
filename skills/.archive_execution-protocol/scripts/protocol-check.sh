#!/bin/bash
# 执行协议检查脚本
# 检查特定任务的协议执行情况

TASK_ID=$1
WORKSPACE="/root/.openclaw/workspace"
PROTOCOL_DIR="$WORKSPACE/memory/protocol"

mkdir -p "$PROTOCOL_DIR"

echo "=== 执行协议检查 ==="
echo "任务ID: ${TASK_ID:-'(未指定)'}"
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

if [ -z "$TASK_ID" ]; then
    echo "使用方式: $0 <task-id>"
    echo ""
    echo "今日协议记录:"
    ls -la "$PROTOCOL_DIR"/*"$(date +%Y%m%d)"* 2>/dev/null | head -20 || echo "  无记录"
    exit 0
fi

# 检查确认状态
if [ -f "$PROTOCOL_DIR/${TASK_ID}-confirmation.md" ]; then
    echo "✅ 任务已确认"
    echo "确认时间: $(stat -c %y "$PROTOCOL_DIR/${TASK_ID}-confirmation.md" | cut -d'.' -f1)"
else
    echo "⚠️ 任务未确认，需要输出确认清单"
fi

# 检查进度汇报
REPORT_COUNT=$(find "$PROTOCOL_DIR" -name "${TASK_ID}-progress-*.md" 2>/dev/null | wc -l)
echo "📊 进度汇报次数: $REPORT_COUNT"
if [ "$REPORT_COUNT" -gt 0 ]; then
    echo "最近汇报:"
    ls -la "$PROTOCOL_DIR/${TASK_ID}"-progress-*.md 2>/dev/null | tail -3 | awk '{print "  " $9}'
fi

# 检查完成状态
if [ -f "$PROTOCOL_DIR/${TASK_ID}-completion.md" ]; then
    echo "✅ 任务已完成"
    echo "完成时间: $(stat -c %y "$PROTOCOL_DIR/${TASK_ID}-completion.md" | cut -d'.' -f1)"
    
    # 检查任务链触发
    if [ -f "$PROTOCOL_DIR/${TASK_ID}-chain-triggered" ]; then
        echo "🔄 下一任务已触发"
    else
        echo "⏳ 等待触发下一任务..."
    fi
else
    echo "⏳ 任务进行中"
fi

# 检查是否有阻塞升级
if [ -f "$PROTOCOL_DIR/${TASK_ID}-escalation.md" ]; then
    echo "🚨 存在升级记录"
    echo "---"
    cat "$PROTOCOL_DIR/${TASK_ID}-escalation.md" | head -10
    echo "---"
else
    echo "✅ 无阻塞升级"
fi

echo ""
echo "=== 检查完成 ==="
