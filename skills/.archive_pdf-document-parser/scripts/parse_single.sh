#!/bin/bash
# PDF单文档解析脚本
# 用法: ./parse_single.sh <pdf_url> [output_dir]

set -e

PDF_URL="$1"
OUTPUT_DIR="${2:-./output}"
MINERU_TOKEN="${MINERU_TOKEN:-$(cat ~/.config/mineru/token 2>/dev/null || echo '')}"

if [ -z "$PDF_URL" ]; then
    echo "❌ 错误: 请提供PDF URL"
    echo "用法: $0 <pdf_url> [output_dir]"
    exit 1
fi

if [ -z "$MINERU_TOKEN" ]; then
    echo "❌ 错误: 未设置MINERU_TOKEN环境变量"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# 生成任务ID前缀
TASK_PREFIX="$(date +%Y%m%d_%H%M%S)"
echo "🚀 提交解析任务: $PDF_URL"

# 提交任务
RESPONSE=$(curl -s -X POST "https://mineru.net/api/v4/extract/task" \
    -H "Authorization: Bearer $MINERU_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"url\": \"$PDF_URL\",
        \"enable_formula\": true,
        \"enable_table\": true,
        \"layout_model\": \"doclayout_yolo\",
        \"language\": \"auto\"
    }")

TASK_ID=$(echo "$RESPONSE" | jq -r '.task_id // empty')
if [ -z "$TASK_ID" ] || [ "$TASK_ID" = "null" ]; then
    echo "❌ 提交失败: $RESPONSE"
    exit 1
fi

echo "✅ 任务创建成功: $TASK_ID"
echo "   任务ID已保存: $OUTPUT_DIR/${TASK_PREFIX}_task_id.txt"
echo "$TASK_ID" > "$OUTPUT_DIR/${TASK_PREFIX}_task_id.txt"

# 轮询结果
echo "⏳ 等待解析完成..."
MAX_RETRIES=60
RETRY=0

while [ $RETRY -lt $MAX_RETRIES ]; do
    sleep 10
    
    STATUS_RESP=$(curl -s "https://mineru.net/api/v4/extract/task/$TASK_ID" \
        -H "Authorization: Bearer $MINERU_TOKEN")
    
    STATUS=$(echo "$STATUS_RESP" | jq -r '.status // empty')
    echo "   状态检查 [$(($RETRY + 1))/$MAX_RETRIES]: $STATUS"
    
    if [ "$STATUS" = "done" ]; then
        DOWNLOAD_URL=$(echo "$STATUS_RESP" | jq -r '.result.zip_url // empty')
        if [ -n "$DOWNLOAD_URL" ] && [ "$DOWNLOAD_URL" != "null" ]; then
            echo "✅ 解析完成，下载结果..."
            curl -sL "$DOWNLOAD_URL" -o "$OUTPUT_DIR/${TASK_PREFIX}_result.zip"
            unzip -q "$OUTPUT_DIR/${TASK_PREFIX}_result.zip" -d "$OUTPUT_DIR/${TASK_PREFIX}_parsed"
            echo "✅ 结果已保存到: $OUTPUT_DIR/${TASK_PREFIX}_parsed/"
            exit 0
        fi
    elif [ "$STATUS" = "failed" ]; then
        echo "❌ 解析失败"
        exit 1
    fi
    
    RETRY=$((RETRY + 1))
done

echo "❌ 超时: 解析任务未完成"
exit 1
