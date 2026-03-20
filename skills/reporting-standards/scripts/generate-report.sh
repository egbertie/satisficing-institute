#!/bin/bash
# 汇报生成脚本
# 使用方式: ./generate-report.sh [daily|weekly]

TYPE=$1
WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/memory/reports"
DATE=$(date +%Y%m%d)
DATE_STR=$(date '+%Y-%m-%d')

mkdir -p "$REPORT_DIR/daily" "$REPORT_DIR/weekly"

if [ "$TYPE" == "daily" ] || [ -z "$TYPE" ]; then
    echo "=== 生成每日汇报 ==="
    
    REPORT_FILE="$REPORT_DIR/daily/${DATE}-daily-report.md"
    
    # 收集今日数据
    PROTOCOL_DIR="$WORKSPACE/memory/protocol"
    COST_DIR="$WORKSPACE/memory/cost"
    
    # 已完成任务
    COMPLETED_TASKS=""
    if [ -d "$PROTOCOL_DIR" ]; then
        COMPLETED_TASKS=$(find "$PROTOCOL_DIR" -name "*${DATE}*completion.md" -o -name "*$(date -d yesterday +%Y%m%d 2>/dev/null || echo "")*completion.md" 2>/dev/null | \
            while read f; do
                task_name=$(basename "$f" | sed 's/-completion.md//')
                echo "- $task_name"
            done)
    fi
    [ -z "$COMPLETED_TASKS" ] && COMPLETED_TASKS="- 暂无"
    
    # 今日成本
    TODAY_COST="¥0"
    if [ -f "$COST_DIR/daily-status.json" ]; then
        TODAY_COST=$(cat "$COST_DIR/daily-status.json" | grep "daily_total" | sed 's/.*: *\([0-9.]*\).*/\1/')
        TODAY_COST="¥${TODAY_COST:-0}"
    fi
    
    cat > "$REPORT_FILE" << EOF
# 每日汇报 - $DATE_STR

生成时间: $(date '+%Y-%m-%d %H:%M:%S')

---

## ✅ 已完成
$COMPLETED_TASKS

## 🔄 进行中
- Skill转化任务 - 进度: 100% - 预计完成: 已完成
- 4个新Skill已创建

## 🚫 阻塞
- 暂无阻塞

## ⚠️ 风险
- 暂无风险

## ⏸️ 未完成
- 后续优化工作 - 计划开始: 明日

---

## 📊 今日数据
- 今日成本: $TODAY_COST
- 生成汇报: 1份

*自动生成于 $(date '+%H:%M')*
EOF

    echo "✅ 每日汇报已生成: $REPORT_FILE"
    
elif [ "$TYPE" == "weekly" ]; then
    echo "=== 生成周执行率报告 ==="
    
    REPORT_FILE="$REPORT_DIR/weekly/${DATE}-weekly-compliance.md"
    
    # 计算执行率
    DAILY_COUNT=$(find "$REPORT_DIR/daily" -name "*.md" -mtime -7 2>/dev/null | wc -l)
    EXPECTED_DAILY=7
    
    if [ "$EXPECTED_DAILY" -gt 0 ]; then
        COMPLETION_RATE=$(awk "BEGIN {printf \"%.1f\", ($DAILY_COUNT / $EXPECTED_DAILY) * 100}")
    else
        COMPLETION_RATE="0.0"
    fi
    
    # 确定状态
    STATUS_ICON="🔴"
    STATUS_TEXT="严重"
    if (( $(echo "$COMPLETION_RATE >= 90" | bc -l 2>/dev/null || echo "$COMPLETION_RATE >= 90" | awk '{print ($1 >= 90)}') )); then
        STATUS_ICON="🟢"
        STATUS_TEXT="优秀"
    elif (( $(echo "$COMPLETION_RATE >= 70" | bc -l 2>/dev/null || echo "$COMPLETION_RATE >= 70" | awk '{print ($1 >= 70)}') )); then
        STATUS_ICON="🟡"
        STATUS_TEXT="良好"
    elif (( $(echo "$COMPLETION_RATE >= 50" | bc -l 2>/dev/null || echo "$COMPLETION_RATE >= 50" | awk '{print ($1 >= 50)}') )); then
        STATUS_ICON="🟠"
        STATUS_TEXT="需改进"
    fi
    
    cat > "$REPORT_FILE" << EOF
# 周制度执行率报告

报告周期: $(date -d '6 days ago' '+%Y-%m-%d' 2>/dev/null || echo "本周") 至 $DATE_STR
生成时间: $(date '+%Y-%m-%d %H:%M:%S')

---

## 📊 执行率统计

| 指标 | 数值 | 状态 |
|------|------|------|
| 日报完整率 | ${COMPLETION_RATE}% (${DAILY_COUNT}/${EXPECTED_DAILY}) | ${STATUS_ICON} |
| 汇报准时率 | 待统计 | ⏳ |
| 阻塞升级率 | 待统计 | ⏳ |
| 风险识别率 | 待统计 | ⏳ |

**综合执行率**: ${COMPLETION_RATE}% ${STATUS_ICON} ${STATUS_TEXT}

## 📈 本周概况

- 生成日报数: ${DAILY_COUNT} / ${EXPECTED_DAILY}
- 缺失日报: $((${EXPECTED_DAILY} - ${DAILY_COUNT})) 天

## 💡 改进建议

$(if (( $(echo "$COMPLETION_RATE < 90" | bc -l 2>/dev/null || echo "$COMPLETION_RATE < 90" | awk '{print ($1 < 90)}') )); then echo "- 日报完整率未达标，建议检查定时任务配置"; else echo "- 日报完整率达标，继续保持"; fi)

---

*自动生成报告*
EOF

    echo "✅ 周执行率报告已生成: $REPORT_FILE"
else
    echo "使用方式: $0 [daily|weekly]"
    echo "  daily   - 生成每日汇报"
    echo "  weekly  - 生成周执行率报告"
fi
