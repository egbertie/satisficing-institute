#!/bin/bash
# 成本记录脚本
# 使用方式: ./record-cost.sh <model> <cost> [usage]

MODEL=$1
COST=$2
USAGE=${3:-"未记录"}
DATE=$(date +%Y%m%d)
TIME=$(date '+%Y-%m-%d %H:%M:%S')
WORKSPACE="/root/.openclaw/workspace"
COST_DIR="$WORKSPACE/memory/cost"

if [ -z "$MODEL" ] || [ -z "$COST" ]; then
    echo "使用方式: $0 <model> <cost> [usage]"
    echo "示例: $0 claude-opus 25 '复杂代码分析'"
    exit 1
fi

mkdir -p "$COST_DIR"

# 记录到JSONL日志
LOG_ENTRY="{\"time\":\"$TIME\",\"model\":\"$MODEL\",\"cost\":$COST,\"usage\":\"$USAGE\",\"date\":\"$DATE\"}"
echo "$LOG_ENTRY" >> "$COST_DIR/cost-log.jsonl"

echo "✅ 成本已记录: $MODEL = ¥$COST"

# 检查是否高成本(>¥20)
if (( $(echo "$COST >= 20" | bc -l 2>/dev/null || echo "$COST >= 20" | awk '{print ($1 >= 20)}') )); then
    echo "⚠️ 高成本调用(≥¥20)，已创建详细记录"
    mkdir -p "$COST_DIR/high-cost-records"
    HIGH_COST_FILE="$COST_DIR/high-cost-records/${DATE}-$(date +%H%M%S).md"
    cat > "$HIGH_COST_FILE" << EOF
# 高成本调用记录

- 时间: $TIME
- 模型: $MODEL
- 成本: ¥$COST
- 用途: $USAGE

## 成本效益分析
待补充...
EOF
    echo "📄 高成本记录: $HIGH_COST_FILE"
fi

# 更新当日累计
bash "$(dirname "$0")/daily-cost-check.sh" --quiet

echo "💰 成本记录完成"
