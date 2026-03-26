#!/bin/bash
# 每日成本检查脚本
# 使用方式: ./daily-cost-check.sh [--quiet]

QUIET=$1
WORKSPACE="/root/.openclaw/workspace"
COST_DIR="$WORKSPACE/memory/cost"
DATE=$(date +%Y%m%d)

mkdir -p "$COST_DIR"

# 计算当日非Kimi模型总成本
NON_KIMI_TOTAL=0
DAILY_TOTAL=0

if [ -f "$COST_DIR/cost-log.jsonl" ]; then
    # 非Kimi成本
    NON_KIMI_LINES=$(grep "\"date\":\"$DATE\"" "$COST_DIR/cost-log.jsonl" | grep -v -i "kimi" 2>/dev/null)
    if [ -n "$NON_KIMI_LINES" ]; then
        NON_KIMI_TOTAL=$(echo "$NON_KIMI_LINES" | python3 -c "
import sys, json
total = 0
for line in sys.stdin:
    try:
        d = json.loads(line)
        total += d.get('cost', 0)
    except: pass
print(total)
" 2>/dev/null || echo "0")
    fi
    
    # 当日总成本
    DAILY_LINES=$(grep "\"date\":\"$DATE\"" "$COST_DIR/cost-log.jsonl" 2>/dev/null)
    if [ -n "$DAILY_LINES" ]; then
        DAILY_TOTAL=$(echo "$DAILY_LINES" | python3 -c "
import sys, json
total = 0
for line in sys.stdin:
    try:
        d = json.loads(line)
        total += d.get('cost', 0)
    except: pass
print(total)
" 2>/dev/null || echo "0")
    fi
fi

# 检查限额
LIMIT=50
if command -v bc >/dev/null; then
    REMAINING=$(echo "scale=2; $LIMIT - $NON_KIMI_TOTAL" | bc)
    PCT_USED=$(echo "scale=1; ($NON_KIMI_TOTAL / $LIMIT) * 100" | bc)
else
    REMAINING=$(awk "BEGIN {printf \"%.2f\", $LIMIT - $NON_KIMI_TOTAL}")
    PCT_USED=$(awk "BEGIN {printf \"%.1f\", ($NON_KIMI_TOTAL / $LIMIT) * 100}")
fi

# 更新状态文件
STATUS_FILE="$COST_DIR/daily-status.json"
cat > "$STATUS_FILE" << EOF
{
  "date": "$DATE",
  "non_kimi_total": $NON_KIMI_TOTAL,
  "daily_total": $DAILY_TOTAL,
  "limit": $LIMIT,
  "remaining": $REMAINING,
  "percentage_used": "${PCT_USED}%",
  "updated_at": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF

if [ "$QUIET" != "--quiet" ]; then
    echo "=== 今日成本状态 ==="
    cat "$STATUS_FILE" 2>/dev/null | python3 -m json.tool 2>/dev/null || cat "$STATUS_FILE"
    echo ""
    
    # 检查预警
    LIMIT_REACHED=$(awk "BEGIN {print ($NON_KIMI_TOTAL >= $LIMIT) ? 1 : 0}")
    WARNING_REACHED=$(awk "BEGIN {print ($NON_KIMI_TOTAL >= 40) ? 1 : 0}")
    
    if [ "$LIMIT_REACHED" == "1" ]; then
        echo "🚨 警告：日限额已超限！"
        echo "   非Kimi模型成本: ¥$NON_KIMI_TOTAL / ¥$LIMIT"
        echo "   建议：暂停使用非Kimi模型，明日再恢复"
    elif [ "$WARNING_REACHED" == "1" ]; then
        echo "⚠️ 预警：日限额即将用完"
        echo "   非Kimi模型成本: ¥$NON_KIMI_TOTAL / ¥$LIMIT"
        echo "   剩余额度: ¥$REMAINING"
    else
        echo "✅ 成本正常"
        echo "   非Kimi模型成本: ¥$NON_KIMI_TOTAL / ¥$LIMIT"
        echo "   剩余额度: ¥$REMAINING"
    fi
fi
