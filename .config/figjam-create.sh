#!/bin/bash
# FigJam快速启动脚本

FIGMA_TOKEN="YOUR_TOKEN_HERE"

# 创建FigJam文件
create_figjam_file() {
    local file_name=$1
    local file_type=${2:-"jam"}
    
    curl -s -X POST \
        -H "X-Figma-Token: $FIGMA_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"$file_name\", \"type\": \"$file_type\"}" \
        https://api.figma.com/v1/files
}

# 添加矩形节点
add_rectangle() {
    local file_key=$1
    local x=$2
    local y=$3
    local width=$4
    local height=$5
    local text=$6
    
    curl -s -X POST \
        -H "X-Figma-Token: $FIGMA_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"nodes\": [{
                \"type\": \"RECTANGLE\",
                \"x\": $x,
                \"y\": $y,
                \"width\": $width,
                \"height\": $height,
                \"name\": \"$text\"
            }]
        }" \
        https://api.figma.com/v1/files/$file_key/nodes
}

# 创建组织架构图
create_org_chart() {
    echo "Creating organization chart..."
    
    # 创建文件
    response=$(create_figjam_file "满意解组织架构V2.2")
    file_key=$(echo $response | grep -o '"key":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    echo "File created: https://www.figma.com/file/$file_key"
    echo "Edit link: https://www.figma.com/jam/$file_key"
    
    # 添加决策层（指挥官）
    add_rectangle $file_key 400 50 150 60 "指挥官 Egbertie"
    
    # 添加文化层（五路图腾）
    add_rectangle $file_key 100 150 120 50 "LIU 刘禹锡"
    add_rectangle $file_key 250 150 120 50 "SIMON 西蒙"
    add_rectangle $file_key 400 150 120 50 "GUANYIN 观自在"
    add_rectangle $file_key 550 150 120 50 "CONFUCIUS 孔子"
    add_rectangle $file_key 700 150 120 50 "HUINENG 六祖"
    
    echo "Organization chart created!"
}

# 主执行
create_org_chart
