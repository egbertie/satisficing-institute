#!/bin/bash
# Notion 批量同步脚本 - 使用 curl 直接调用 API

TOKEN="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"
API="https://api.notion.com/v1"
WORKSPACE="/root/.openclaw/workspace"
PARENT_ID="31fa8a0e-2bba-81fa-b98a-d61da835051e"  # 知识库页面ID

# 统计
TOTAL=0
SUCCESS=0
FAILED=0
SKIPPED=0
FAILED_FILES=""

echo "=========================================="
echo "📚 Notion 批量同步"
echo "=========================================="
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 查找所有文件
echo "1️⃣ 扫描文件..."
find "$WORKSPACE" -type f \( -name "*.md" -o -name "*.html" -o -name "*.py" -o -name "*.json" -o -name "*.txt" -o -name "*.js" -o -name "*.css" -o -name "*.yml" -o -name "*.yaml" \) ! -path "*/.git/*" ! -path "*/node_modules/*" > /tmp/all_files.txt
TOTAL=$(cat /tmp/all_files.txt | wc -l)
echo "   发现 $TOTAL 个文件"

# 获取已存在页面列表
echo ""
echo "2️⃣ 获取已存在页面..."
EXISTING=$(curl -s -X GET "$API/blocks/$PARENT_ID/children?page_size=100" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Notion-Version: 2022-06-28" | \
    python3 -c "import sys,json; d=json.load(sys.stdin); [print(r.get('child_page',{}).get('title','')) for r in d.get('results',[]) if r.get('type')=='child_page']" 2>/dev/null)

echo "   已存在页面数: $(echo "$EXISTING" | grep -v "^$" | wc -l)"
echo ""
echo "3️⃣ 开始同步..."
echo "------------------------------------------"

# 处理每个文件
COUNTER=0
while IFS= read -r file; do
    COUNTER=$((COUNTER + 1))
    filename=$(basename "$file")
    name=$(basename "$file" | sed 's/\.[^.]*$//')  # 去掉扩展名
    
    # 检查是否已存在
    if echo "$EXISTING" | grep -q "^${name}$" || echo "$EXISTING" | grep -q "^${filename}$"; then
        SKIPPED=$((SKIPPED + 1))
        echo "[$COUNTER/$TOTAL] ⏭️ $filename (已存在)"
        continue
    fi
    
    # 读取文件内容（限制大小）
    content=$(cat "$file" 2>/dev/null | head -c 50000 | sed 's/\\/\\\\/g; s/"/\\"/g; s/\t/ /g; s/$/\\n/' | tr -d '\n')
    
    if [ -z "$content" ]; then
        FAILED=$((FAILED + 1))
        FAILED_FILES="$FAILED_FILES\n  - $filename (空文件)"
        echo "[$COUNTER/$TOTAL] ❌ $filename (空文件)"
        continue
    fi
    
    # 截断标题
    title=$(echo "$name" | cut -c1-100)
    
    # 创建页面
    response=$(curl -s -X POST "$API/pages" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -H "Notion-Version: 2022-06-28" \
        -d "{
            \"parent\": {\"page_id\": \"$PARENT_ID\"},
            \"properties\": {
                \"title\": {
                    \"title\": [{\"text\": {\"content\": \"$title\"}}]
                }
            },
            \"children\": [{
                \"object\": \"block\",
                \"type\": \"paragraph\",
                \"paragraph\": {
                    \"rich_text\": [{\"type\": \"text\", \"text\": {\"content\": \"${content:0:1800}\"}}]
                }
            }]
        }" 2>/dev/null)
    
    if echo "$response" | grep -q '"id"'; then
        SUCCESS=$((SUCCESS + 1))
        echo "[$COUNTER/$TOTAL] ✅ $filename"
    else
        FAILED=$((FAILED + 1))
        error=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','Unknown'))" 2>/dev/null || echo "Unknown")
        FAILED_FILES="$FAILED_FILES\n  - $filename ($error)"
        echo "[$COUNTER/$TOTAL] ❌ $filename"
    fi
    
    # 速率限制 - 每3个文件等待1秒
    if [ $((COUNTER % 3)) -eq 0 ]; then
        sleep 1
    fi
    
    # 每50个文件显示进度
    if [ $((COUNTER % 50)) -eq 0 ]; then
        echo ""
        echo "💾 进度: 成功 $SUCCESS, 失败 $FAILED, 跳过 $SKIPPED"
        echo ""
    fi
done < /tmp/all_files.txt

echo ""
echo "=========================================="
echo "📊 同步完成报告"
echo "=========================================="
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "统计:"
echo "  • 总文件: $TOTAL"
echo "  • ✅ 成功: $SUCCESS"
echo "  • ❌ 失败: $FAILED"
echo "  • ⏭️ 跳过: $SKIPPED"
echo ""
echo "Notion链接: https://notion.so/${PARENT_ID//-/}"
echo ""

# 保存报告
REPORT_FILE="$WORKSPACE/NOTION_BATCH_SYNC_REPORT_$(date +%Y%m%d_%H%M%S).json"
cat > "$REPORT_FILE" << EOF
{
  "sync_time": "$(date -Iseconds)",
  "total_files": $TOTAL,
  "success": $SUCCESS,
  "failed": $FAILED,
  "skipped": $SKIPPED,
  "notion_url": "https://notion.so/${PARENT_ID//-/}"
}
EOF

echo "报告已保存: $REPORT_FILE"
