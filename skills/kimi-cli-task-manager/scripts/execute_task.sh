#!/bin/bash
# Kimi Task Executor
# Kimi任务执行脚本

set -e

TASK_ID="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASKS_DIR="$(dirname "$SCRIPT_DIR")/tasks"

if [ -z "$TASK_ID" ]; then
    echo "🤖 Kimi Task Executor"
    echo ""
    echo "Usage: $0 [task-id]"
    exit 1
fi

TASK_FILE="$TASKS_DIR/pending/${TASK_ID}.json"
if [ ! -f "$TASK_FILE" ]; then
    echo "❌ 任务不存在: $TASK_ID"
    exit 1
fi

# 读取任务配置
PROMPT=$(python3 -c "import json; print(json.load(open('$TASK_FILE')).get('prompt', ''))")
WORKDIR=$(python3 -c "import json; print(json.load(open('$TASK_FILE')).get('workdir', '/tmp'))")
TIMEOUT=$(python3 -c "import json; print(json.load(open('$TASK_FILE')).get('timeout', 300))")

echo "🚀 执行任务: $TASK_ID"
echo "工作目录: $WORKDIR"
echo "超时: ${TIMEOUT}秒"
echo ""

# 确保工作目录存在
mkdir -p "$WORKDIR"

# 移动任务到运行中
mv "$TASK_FILE" "$TASKS_DIR/running/"
TASK_FILE="$TASKS_DIR/running/${TASK_ID}.json"

# 更新状态
python3 -c "
import json
task = json.load(open('$TASK_FILE'))
task['status'] = 'running'
task['started_at'] = __import__('datetime').datetime.now().isoformat()
json.dump(task, open('$TASK_FILE', 'w'), indent=2)
"

# 执行Kimi命令
echo "📝 执行Kimi..."
echo ""

if ! command -v kimi &> /dev/null; then
    echo "❌ 错误: 未找到 Kimi CLI"
    mv "$TASK_FILE" "$TASKS_DIR/failed/"
    exit 1
fi

# 使用PTY模式执行
if timeout "$TIMEOUT" kimi --print -p "$PROMPT" 2>&1; then
    echo ""
    echo "✅ 任务完成"
    
    # 更新状态为完成
    python3 -c "
import json
task = json.load(open('$TASK_FILE'))
task['status'] = 'completed'
task['completed_at'] = __import__('datetime').datetime.now().isoformat()
json.dump(task, open('$TASK_FILE', 'w'), indent=2)
"
    mv "$TASK_FILE" "$TASKS_DIR/completed/"
else
    EXIT_CODE=$?
    echo ""
    
    if [ $EXIT_CODE -eq 124 ]; then
        echo "⏱️  任务超时"
        FAIL_REASON="timeout"
    elif grep -q "429" /tmp/kimi_output_$$.txt 2>/dev/null; then
        echo "⚠️  遇到速率限制(429)"
        FAIL_REASON="rate_limit"
    else
        echo "❌ 任务失败"
        FAIL_REASON="error"
    fi
    
    # 更新状态为失败
    python3 -c "
import json
task = json.load(open('$TASK_FILE'))
task['status'] = 'failed'
task['failed_at'] = __import__('datetime').datetime.now().isoformat()
task['fail_reason'] = '$FAIL_REASON'
task['exit_code'] = $EXIT_CODE
json.dump(task, open('$TASK_FILE', 'w'), indent=2)
"
    mv "$TASK_FILE" "$TASKS_DIR/failed/"
    exit 1
fi
