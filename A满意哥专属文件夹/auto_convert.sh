#!/bin/bash
# A满意哥专属文件夹 - 自动格式转换脚本
# 用法: ./auto_convert.sh [文件夹路径]

TARGET_DIR="${1:-/root/.openclaw/workspace/A满意哥专属文件夹}"

echo "=== 自动格式转换系统 ==="
echo "目标文件夹: $TARGET_DIR"
echo ""

# 函数：转换 Markdown → Word/Excel/PDF
convert_markdown() {
    local file="$1"
    local dir=$(dirname "$file")
    local filename=$(basename "$file" .md)
    
    # 确保目录存在
    mkdir -p "${dir}/📄 源文件" "${dir}/📑 Word成品" 2>/dev/null
    
    # 移动源文件
    if [[ ! "$file" =~ "📄 源文件" ]]; then
        cp "$file" "${dir}/📄 源文件/" 2>/dev/null
        echo "  📄 源文件: ${filename}.md"
    fi
    
    # 转换为 Word
    if command -v pandoc >/dev/null 2>&1; then
        pandoc "$file" -o "${dir}/📑 Word成品/${filename}.docx" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "  ✅ Word: ${filename}.docx"
        else
            echo "  ⚠️  转换失败: ${filename}.md"
        fi
    else
        # 如果没有 pandoc，标记为待处理
        cp "$file" "${dir}/📑 Word成品/${filename}.md.txt"
        echo "  ⏳ 待转换: ${filename}.md (需安装 pandoc)"
    fi
}

# 函数：转换 Mermaid → 图片
convert_mermaid() {
    local file="$1"
    local dir=$(dirname "$file")
    local filename=$(basename "$file" .mmd)
    
    mkdir -p "${dir}/📈 图表源文件" "${dir}/🖼️ 可视化图片" 2>/dev/null
    
    # 移动源文件
    if [[ ! "$file" =~ "📈 图表源文件" ]]; then
        cp "$file" "${dir}/📈 图表源文件/" 2>/dev/null
        echo "  📈 图表源: ${filename}.mmd"
    fi
    
    # 尝试转换为 PNG (需要 mermaid-cli)
    if command -v mmdc >/dev/null 2>&1; then
        mmdc -i "$file" -o "${dir}/🖼️ 可视化图片/${filename}.png" 2>/dev/null
        echo "  ✅ PNG: ${filename}.png"
    else
        echo "  ⏳ 待转换: ${filename}.mmd (需安装 mermaid-cli)"
    fi
}

# 函数：转换 CSV → Excel
convert_csv() {
    local file="$1"
    local dir=$(dirname "$file")
    local filename=$(basename "$file" .csv)
    
    mkdir -p "${dir}/📊 Excel表格" 2>/dev/null
    
    # 使用已安装的 automate-excel
    if [ -f "/root/.openclaw/workspace/skills/automate-excel/excel.py" ]; then
        # 复制为 Excel 格式
        cp "$file" "${dir}/📊 Excel表格/${filename}.csv"
        echo "  📊 表格: ${filename}.csv (需手动转 Excel)"
    else
        cp "$file" "${dir}/📊 Excel表格/${filename}.csv"
        echo "  📊 表格: ${filename}.csv"
    fi
}

# 主流程
echo "【扫描 Markdown 文件】"
md_count=0
find "$TARGET_DIR" -name "*.md" -type f ! -path "*/📄 源文件/*" ! -path "*/📑 Word成品/*" 2>/dev/null | while read file; do
    convert_markdown "$file"
    ((md_count++))
done
echo ""

echo "【扫描 Mermaid 文件】"
find "$TARGET_DIR" -name "*.mmd" -type f ! -path "*/📈 图表源文件/*" ! -path "*/🖼️ 可视化图片/*" 2>/dev/null | while read file; do
    convert_mermaid "$file"
done
echo ""

echo "【扫描 CSV 文件】"
find "$TARGET_DIR" -name "*.csv" -type f ! -path "*/📊 Excel表格/*" 2>/dev/null | while read file; do
    convert_csv "$file"
done
echo ""

echo "=== 转换完成 ==="
echo "提示: 新文件放入文件夹后，运行此脚本即可自动转换"
