#!/bin/bash
# PDF批量解析脚本
# 用法: ./parse_batch.sh <urls_file> [output_dir]

set -e

URLS_FILE="$1"
OUTPUT_DIR="${2:-./batch_output}"
MAX_PARALLEL=3

if [ -z "$URLS_FILE" ] || [ ! -f "$URLS_FILE" ]; then
    echo "❌ 错误: 请提供有效的URL列表文件"
    echo "用法: $0 <urls_file> [output_dir]"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
QUEUE_FILE="$OUTPUT_DIR/.queue"
FAILED_FILE="$OUTPUT_DIR/.failed"

# 初始化队列
grep -v '^#' "$URLS_FILE" | grep -v '^$' > "$QUEUE_FILE"
TOTAL=$(wc -l < "$QUEUE_FILE")
echo "📋 批量解析启动: 共 $TOTAL 个文档"
echo "   输出目录: $OUTPUT_DIR"
echo "   并行度: $MAX_PARALLEL"
echo ""

# 处理队列
COUNTER=0
while IFS= read -r URL; do
    COUNTER=$((COUNTER + 1))
    echo "[$COUNTER/$TOTAL] 处理: $URL"
    
    # 创建子目录
    SUBDIR="$OUTPUT_DIR/doc_$(printf "%04d" $COUNTER)"
    mkdir -p "$SUBDIR"
    
    # 调用单文档解析
    if ! ./scripts/parse_single.sh "$URL" "$SUBDIR" 2>&1; then
        echo "$URL" >> "$FAILED_FILE"
        echo "   ⚠️  失败，已记录到失败列表"
    fi
    
    # 控制并行（简单串行，如需真正并行需用wait/background）
    sleep 2
done < "$QUEUE_FILE"

# 生成报告
echo ""
echo "✅ 批量解析完成"
echo "   成功: $(ls -d "$OUTPUT_DIR"/doc_*/parsed 2>/dev/null | wc -l) / $TOTAL"
if [ -f "$FAILED_FILE" ]; then
    echo "   失败: $(wc -l < "$FAILED_FILE")"
    echo "   失败列表: $FAILED_FILE"
fi
