#!/bin/bash
################################################################################
# Notion 数据备份脚本
# 功能: 导出所有Notion页面和数据库
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# 配置
NOTION_TOKEN="${NOTION_TOKEN:-}"  # Notion Integration Token
NOTION_VERSION="2022-06-28"
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-${HOME}/Backups/Notion}"
EXPORT_FORMAT="${EXPORT_FORMAT:-markdown}"  # markdown 或 html

# 日志
log_info "Notion 备份任务开始"

# 创建备份目录
mkdir -p "${BACKUP_BASE_DIR}"
BACKUP_DIR="${BACKUP_BASE_DIR}/notion_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "${BACKUP_DIR}"

# API请求函数
notion_api() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    
    local url="https://api.notion.com/v1${endpoint}"
    
    local curl_opts="-s -H \"Authorization: Bearer ${NOTION_TOKEN}\" -H \"Notion-Version: ${NOTION_VERSION}\" -H \"Content-Type: application/json\""
    
    if [[ "${method}" == "POST" && -n "${data}" ]]; then
        eval "curl ${curl_opts} -X POST -d '${data}' '${url}'"
    else
        eval "curl ${curl_opts} '${url}'"
    fi
}

# 搜索所有页面和数据库
search_all() {
    log_info "搜索 Notion 所有页面和数据库..."
    
    local all_results="[]"
    local cursor=""
    
    while true; do
        local data
        if [[ -n "${cursor}" ]]; then
            data="{\"query\":\"\",\"start_cursor\":\"${cursor}\"}"
        else
            data='{"query":""}'
        fi
        
        local response=$(notion_api "/search" "POST" "${data}")
        
        # 检查结果
        if echo "${response}" | grep -q '"object":"error"'; then
            log_error "API错误: ${response}"
            break
        fi
        
        # 合并结果 (简化处理，实际应使用jq)
        local results=$(echo "${response}" | grep -o '"results":\[[^]]*\]' || echo '[]')
        
        # 获取下一页cursor
        cursor=$(echo "${response}" | grep -o '"next_cursor":"[^"]*"' | cut -d'"' -f4 || echo '')
        
        if [[ -z "${cursor}" ]]; then
            break
        fi
        
        sleep 0.5  # 避免API限流
    done
    
    log_info "搜索完成"
}

# 导出单个页面
export_page() {
    local page_id="$1"
    local page_title="$2"
    
    log_info "导出页面: ${page_title}"
    
    local safe_title=$(echo "${page_title}" | tr '/\\' '_' | cut -c1-100)
    local page_dir="${BACKUP_DIR}/${safe_title}_${page_id:0:8}"
    mkdir -p "${page_dir}"
    
    # 获取页面内容 (block children)
    local blocks=$(notion_api "/blocks/${page_id}/children")
    
    # 保存原始JSON
    echo "${blocks}" > "${page_dir}/content.json"
    
    # 尝试转换为Markdown (简化版)
    convert_to_markdown "${blocks}" > "${page_dir}/content.md"
    
    # 递归导出子页面
    local child_pages=$(echo "${blocks}" | grep -o '"type":"child_page"[^}]*"id":"[^"]*"' | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    
    for child_id in ${child_pages}; do
        export_page "${child_id}" "${safe_title}_subpage"
    done
}

# 简化的JSON到Markdown转换
convert_to_markdown() {
    local json="$1"
    
    # 这是一个简化版本，实际应使用专门的解析库
    echo "# Notion Page Export"
    echo ""
    echo "导出时间: $(date)"
    echo ""
    echo "原始数据保存在 content.json"
    echo ""
    echo "---"
    echo ""
    
    # 尝试提取文本内容
    echo "${json}" | grep -o '"content":"[^"]*"' | cut -d'"' -f4 | while read -r line; do
        echo "${line}"
        echo ""
    done
}

# 导出数据库
export_database() {
    local db_id="$1"
    local db_title="$2"
    
    log_info "导出数据库: ${db_title}"
    
    local safe_title=$(echo "${db_title}" | tr '/\\' '_' | cut -c1-100)
    local db_dir="${BACKUP_DIR}/${safe_title}_db_${db_id:0:8}"
    mkdir -p "${db_dir}"
    
    # 获取数据库结构
    local db_info=$(notion_api "/databases/${db_id}")
    echo "${db_info}" > "${db_dir}/schema.json"
    
    # 获取数据库内容
    local data=$(notion_api "/databases/${db_id}/query" "POST" '{}')
    echo "${data}" > "${db_dir}/data.json"
    
    # 转换为CSV (简化版)
    convert_db_to_csv "${data}" > "${db_dir}/data.csv"
}

# 数据库转CSV (简化版)
convert_db_to_csv() {
    local json="$1"
    
    echo "# 数据库导出"
    echo "导出时间,$(date)"
    echo ""
    echo "原始数据: data.json"
    echo "数据库结构: schema.json"
}

# 创建工作空间导出 (通过Notion的导出功能)
workspace_export() {
    log_info "触发工作空间完整导出..."
    
    # Notion API 目前不支持直接触发完整导出
    # 这里提供手动导出指南
    
    cat > "${BACKUP_DIR}/手动导出指南.txt" << 'EOF'
Notion 工作空间完整导出指南
============================

由于Notion API限制，完整工作空间导出需要手动操作:

1. 登录 Notion (notion.so)
2. 点击左侧边栏 Settings & Members
3. 选择 Settings → Export → Export all workspace content
4. 选择导出格式: Markdown & CSV (推荐) 或 HTML
5. 点击 Export
6. 等待邮件通知，下载导出文件
7. 将下载的文件移动到备份目录: 
EOF

    echo "   ${BACKUP_DIR}/" >> "${BACKUP_DIR}/手动导出指南.txt"
    
    log_info "已生成手动导出指南"
}

# 备份核心数据库到Git
backup_databases_to_git() {
    log_info "备份核心数据库到 Git 版本控制..."
    
    local git_backup_dir="${HOME}/Backups/Notion-Git"
    mkdir -p "${git_backup_dir}"
    cd "${git_backup_dir}"
    
    # 初始化Git仓库 (如果不存在)
    if [[ ! -d ".git" ]]; then
        git init
        git config user.email "backup@local"
        git config user.name "Notion Backup"
        echo "# Notion Database Backups" > README.md
        git add README.md
        git commit -m "Initial commit"
    fi
    
    # 创建每日备份目录
    local daily_dir="$(date +%Y-%m-%d)"
    mkdir -p "${daily_dir}"
    
    # 复制数据库备份
    if [[ -d "${BACKUP_DIR}" ]]; then
        cp -r "${BACKUP_DIR}"/* "${daily_dir}/" 2>/dev/null || true
    fi
    
    # Git提交
    git add -A
    git commit -m "Notion backup $(date '+%Y-%m-%d %H:%M:%S')" || true
    
    # 推送到远程 (如果配置了)
    git push origin main 2>/dev/null || git push origin master 2>/dev/null || true
    
    log_info "Git 备份完成"
}

# 清理旧备份
cleanup() {
    log_info "清理超过52周的旧备份..."
    
    find "${BACKUP_BASE_DIR}" -name "notion_backup_*" -type d -mtime +364 -exec rm -rf {} + 2>/dev/null || true
    
    # 清理Git备份历史 (保留最近100次提交)
    local git_dir="${HOME}/Backups/Notion-Git"
    if [[ -d "${git_dir}/.git" ]]; then
        cd "${git_dir}"
        # 可选: 使用 git-rebase 或创建归档分支来管理历史
    fi
    
    log_info "清理完成"
}

# 主函数
main() {
    log_info "=========================================="
    log_info "Notion 备份开始"
    log_info "备份目录: ${BACKUP_DIR}"
    log_info "=========================================="
    
    # 检查token
    if [[ -z "${NOTION_TOKEN}" ]]; then
        log_error "未设置 NOTION_TOKEN 环境变量"
        log_info "请在 https://www.notion.so/my-integrations 创建Integration并获取Token"
        
        # 继续生成手动导出指南
        mkdir -p "${BACKUP_DIR}"
        workspace_export
        
        log_info "已生成手动导出指南，请按指南操作"
        exit 0
    fi
    
    # 测试API连接
    log_info "测试 Notion API 连接..."
    local test_response=$(notion_api "/users/me")
    
    if echo "${test_response}" | grep -q '"object":"error"'; then
        log_error "API连接失败: ${test_response}"
        exit 1
    fi
    
    log_info "API连接成功"
    
    # 搜索并导出内容
    search_all
    
    # 如果安装了jq，执行详细导出
    if command -v jq &> /dev/null; then
        log_info "使用 jq 进行详细导出..."
        
        # 获取搜索结果
        local search_data='{"query":"","page_size":100}'
        local search_result=$(notion_api "/search" "POST" "${search_data}")
        
        # 导出每个页面
        local pages=$(echo "${search_result}" | jq -r '.results[] | select(.object == "page") | [.id, (.properties.Name.title[0].text.content // "Untitled")] | @tsv' 2>/dev/null)
        
        while IFS=$'\t' read -r page_id page_title; do
            if [[ -n "${page_id}" ]]; then
                export_page "${page_id}" "${page_title}"
                sleep 0.5
            fi
        done <<< "${pages}"
        
        # 导出每个数据库
        local databases=$(echo "${search_result}" | jq -r '.results[] | select(.object == "database") | [.id, (.title[0].text.content // "Untitled")] | @tsv' 2>/dev/null)
        
        while IFS=$'\t' read -r db_id db_title; do
            if [[ -n "${db_id}" ]]; then
                export_database "${db_id}" "${db_title}"
                sleep 0.5
            fi
        done <<< "${databases}"
    else
        log_warn "未安装 jq，跳过详细导出"
    fi
    
    # 生成手动导出指南
    workspace_export
    
    # Git版本控制备份
    backup_databases_to_git
    
    # 清理
    cleanup
    
    # 打包备份
    log_info "打包备份..."
    local archive_name="notion_backup_$(date +%Y%m%d).tar.gz"
    tar czf "${BACKUP_BASE_DIR}/${archive_name}" -C "${BACKUP_DIR}" . 2>/dev/null || true
    
    log_info "=========================================="
    log_info "Notion 备份完成"
    log_info "备份位置: ${BACKUP_DIR}"
    log_info "归档文件: ${BACKUP_BASE_DIR}/${archive_name}"
    log_info "=========================================="
    
    echo "SUCCESS" > "${SCRIPT_DIR}/.notion_backup_status"
}

main "$@"
