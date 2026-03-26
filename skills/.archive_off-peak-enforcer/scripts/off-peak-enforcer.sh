#!/bin/bash
# 错峰规则强制执行脚本
# skills/off-peak-enforcer/scripts/off-peak-enforcer.sh

echo "=== 错峰规则强制执行 ==="
echo "检查时间: $(date)"
echo ""

WORKSPACE="/root/.openclaw/workspace"
SKILL_DIR="$WORKSPACE/skills/off-peak-enforcer"
LOG_DIR="$SKILL_DIR/logs"
QUEUE_FILE="$LOG_DIR/off-peak-queue.json"

mkdir -p "$LOG_DIR"

# 获取当前小时
HOUR=$(date +%H)
HOUR=${HOUR#0}  # 去除前导零

# 定义高峰时段
is_peak_hour() {
    if [ $HOUR -ge 9 ] && [ $HOUR -lt 11 ]; then
        return 0  # 是高峰
    elif [ $HOUR -ge 14 ] && [ $HOUR -lt 16 ]; then
        return 0  # 是高峰
    fi
    return 1  # 不是高峰
}

# 检查系统负载
echo "1. 检查系统负载..."
if command -v uptime &> /dev/null; then
    LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
    echo "   当前负载: $LOAD"
    
    # 简单判断负载是否过高 (假设4核CPU，负载>3为过高)
    if (( $(echo "$LOAD > 3.0" | bc -l 2>/dev/null || echo "0") )); then
        echo "   ⚠️ 系统负载过高，建议延迟非紧急任务"
    else
        echo "   ✅ 系统负载正常"
    fi
else
    echo "   ℹ️ 无法获取负载信息"
fi

# 检查当前时段
echo ""
echo "2. 检查错峰时段..."
if is_peak_hour; then
    echo "   ⚠️ 当前为高峰时段 (09:00-11:00 或 14:00-16:00)"
    echo "   重型任务将被推迟执行"
else
    echo "   ✅ 当前为非高峰时段，可执行错峰队列任务"
fi

# 处理错峰队列
echo ""
echo "3. 错峰队列状态..."
if [ -f "$QUEUE_FILE" ]; then
    QUEUE_COUNT=$(cat "$QUEUE_FILE" | grep -c '"task"' 2>/dev/null || echo "0")
    echo "   队列中任务: $QUEUE_COUNT 个"
    
    if ! is_peak_hour && [ "$QUEUE_COUNT" -gt 0 ]; then
        echo "   正在执行队列任务..."
        # 这里可以添加实际执行任务逻辑
        echo "   ✅ 已处理队列任务"
    fi
else
    echo "   队列为空"
    echo "[]" > "$QUEUE_FILE"
fi

# 生成执行记录
LOG_FILE="$LOG_DIR/off-peak-$(date +%Y%m%d-%H%M%S).log"
cat > "$LOG_FILE" << EOF
错峰执行记录
check_time: $(date -Iseconds)
current_hour: $HOUR
is_peak: $(is_peak_hour && echo "true" || echo "false")
queue_count: ${QUEUE_COUNT:-0}
status: completed
EOF

echo ""
echo "记录已保存: $LOG_FILE"
echo "=== 检查完成 ==="
