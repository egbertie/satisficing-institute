#!/bin/bash
# 成本统计脚本
# 使用方式: ./cost-stats.sh [daily|weekly|monthly]

PERIOD=$1
WORKSPACE="/root/.openclaw/workspace"
COST_DIR="$WORKSPACE/memory/cost"

mkdir -p "$COST_DIR"

if [ -z "$PERIOD" ] || [ "$PERIOD" == "daily" ]; then
    DATE=$(date +%Y%m%d)
    echo "=== 今日成本统计 ($DATE) ==="
    
    if [ -f "$COST_DIR/cost-log.jsonl" ]; then
        TODAY_LINES=$(grep "\"date\":\"$DATE\"" "$COST_DIR/cost-log.jsonl" 2>/dev/null)
        
        if [ -n "$TODAY_LINES" ]; then
            # 按模型统计
            echo ""
            echo "📊 按模型统计:"
            echo "$TODAY_LINES" | python3 -c "
import sys, json
from collections import defaultdict
models = defaultdict(lambda: {'count': 0, 'cost': 0})
for line in sys.stdin:
    try:
        d = json.loads(line)
        models[d['model']]['count'] += 1
        models[d['model']]['cost'] += d['cost']
    except: pass
for model, data in sorted(models.items(), key=lambda x: -x[1]['cost']):
    print(f'  {model}: {data[\"count\"]}次, ¥{data[\"cost\"]:.2f}')
" 2>/dev/null
            
            # 高成本调用
            echo ""
            echo "💰 高成本调用(≥¥20):"
            HIGH_COSTS=$(echo "$TODAY_LINES" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d = json.loads(line)
        if d.get('cost', 0) >= 20:
            print(json.dumps(d))
    except: pass
" 2>/dev/null)
            if [ -z "$HIGH_COSTS" ]; then
                echo "  无"
            else
                echo "$HIGH_COSTS" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d = json.loads(line)
        print(f\"  {d['time']}: {d['model']} ¥{d['cost']}\")
    except: pass
"
            fi
            
            # 非Kimi总计
            echo ""
            echo "📈 日限额使用:"
            NON_KIMI_TOTAL=$(echo "$TODAY_LINES" | grep -v -i "kimi" | python3 -c "
import sys, json
total = 0
for line in sys.stdin:
    try:
        d = json.loads(line)
        total += d.get('cost', 0)
    except: pass
print(total)
" 2>/dev/null || echo "0")
            LIMIT=50
            PCT=$(awk "BEGIN {printf \"%.1f\", ($NON_KIMI_TOTAL / $LIMIT) * 100}")
            echo "  非Kimi成本: ¥$NON_KIMI_TOTAL / ¥$LIMIT ($PCT%)"
        else
            echo "暂无今日成本记录"
        fi
    else
        echo "暂无成本记录"
    fi
    
elif [ "$PERIOD" == "weekly" ]; then
    WEEK_START=$(date -d "7 days ago" +%Y%m%d 2>/dev/null || date -v-7d +%Y%m%d 2>/dev/null || echo "$(($(date +%Y%m%d) - 7))")
    echo "=== 本周成本统计 (最近7天) ==="
    
    if [ -f "$COST_DIR/cost-log.jsonl" ]; then
        echo ""
        echo "📅 每日成本:"
        python3 << EOF 2>/dev/null
import json
from collections import defaultdict
daily = defaultdict(lambda: {'total': 0, 'non_kimi': 0})
with open('$COST_DIR/cost-log.jsonl') as f:
    for line in f:
        try:
            d = json.loads(line)
            if d['date'] >= '$WEEK_START':
                daily[d['date']]['total'] += d['cost']
                if 'kimi' not in d['model'].lower():
                    daily[d['date']]['non_kimi'] += d['cost']
        except: pass
for date in sorted(daily.keys()):
    data = daily[date]
    status = "🚨" if data['non_kimi'] > 50 else "⚠️" if data['non_kimi'] > 40 else "✅"
    print(f"  {date}: 总计¥{data['total']:.2f}, 非Kimi¥{data['non_kimi']:.2f} {status}")
EOF
    else
        echo "暂无成本记录"
    fi
    
else
    echo "使用方式: $0 [daily|weekly]"
    echo "  daily   - 今日统计"
    echo "  weekly  - 本周统计"
fi
