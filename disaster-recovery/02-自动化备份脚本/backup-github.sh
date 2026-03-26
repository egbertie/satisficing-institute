#!/bin/bash
################################################################################
# GitHub 仓库备份脚本
# 功能: 备份所有GitHub仓库到本地，并推送到镜像源
################################################################################

set -euo pipefail

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# GitHub配置 (需根据实际情况修改)
GITHUB_USER="${GITHUB_USER:-your-username}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"  # 从环境变量或配置文件读取
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-${HOME}/Backups/GitHub}"
MIRROR_GITEE="${MIRROR_GITEE:-true}"
MIRROR_GITLAB="${MIRROR_GITLAB:-false}"

# 镜像配置
GITEE_USER="${GITEE_USER:-}"
GITEE_TOKEN="${GITEE_TOKEN:-}"
GITLAB_USER="${GITLAB_USER:-}"
GITLAB_TOKEN="${GITLAB_TOKEN:-}"

# 日志
log_info "GitHub 备份任务开始"

# 创建备份目录
mkdir -p "${BACKUP_BASE_DIR}"
cd "${BACKUP_BASE_DIR}"

# 获取所有仓库列表
fetch_repos() {
    log_info "获取 GitHub 仓库列表..."
    
    local api_url="https://api.github.com/user/repos?per_page=100&type=all"
    local repos_file="/tmp/github_repos_$$.json"
    
    if [[ -n "${GITHUB_TOKEN}" ]]; then
        curl -s -H "Authorization: token ${GITHUB_TOKEN}" "${api_url}" > "${repos_file}"
    else
        curl -s "${api_url}?username=${GITHUB_USER}" > "${repos_file}"
    fi
    
    if [[ ! -s "${repos_file}" ]]; then
        log_error "无法获取仓库列表"
        return 1
    fi
    
    echo "${repos_file}"
}

# 克隆或更新单个仓库
backup_repo() {
    local repo_name="$1"
    local clone_url="$2"
    local private="$3"
    
    log_info "处理仓库: ${repo_name}"
    
    local repo_dir="${BACKUP_BASE_DIR}/${repo_name}"
    
    # 使用token认证 (如果是私有仓库)
    local auth_url="${clone_url}"
    if [[ "${private}" == "true" && -n "${GITHUB_TOKEN}" ]]; then
        auth_url="${clone_url/https:\/\//https:\/\/${GITHUB_TOKEN}@}"
    fi
    
    if [[ -d "${repo_dir}" ]]; then
        # 更新现有仓库
        log_info "  更新仓库..."
        cd "${repo_dir}"
        
        # 获取所有分支
        git fetch --all --prune || {
            log_warn "  获取更新失败，尝试重新克隆"
            cd "${BACKUP_BASE_DIR}"
            rm -rf "${repo_dir}"
            git clone --mirror "${auth_url}" "${repo_dir}"
        }
        
        # 更新镜像
        if [[ -f "config" ]] && grep -q "bare = true" config 2>/dev/null; then
            git remote update
        fi
    else
        # 克隆新仓库 (使用mirror模式保留所有信息)
        log_info "  克隆仓库..."
        git clone --mirror "${auth_url}" "${repo_dir}"
    fi
    
    # 打包备份
    cd "${BACKUP_BASE_DIR}"
    local backup_file="${repo_name}_$(date +%Y%m%d_%H%M%S).bundle"
    git bundle create "${backup_file}" --all -C "${repo_dir}" 2>/dev/null || {
        log_warn "  创建bundle失败，使用tar备份"
        tar czf "${repo_name}_$(date +%Y%m%d_%H%M%S).tar.gz" "${repo_name}"
    }
    
    # 推送到Gitee镜像
    if [[ "${MIRROR_GITEE}" == "true" && -n "${GITEE_TOKEN}" ]]; then
        mirror_to_gitee "${repo_name}" "${repo_dir}"
    fi
    
    # 推送到GitLab镜像
    if [[ "${MIRROR_GITLAB}" == "true" && -n "${GITLAB_TOKEN}" ]]; then
        mirror_to_gitlab "${repo_name}" "${repo_dir}"
    fi
}

# 镜像到Gitee
mirror_to_gitee() {
    local repo_name="$1"
    local repo_dir="$2"
    
    log_info "  推送到 Gitee 镜像..."
    
    local gitee_url="https://${GITEE_USER}:${GITEE_TOKEN}@gitee.com/${GITEE_USER}/${repo_name}.git"
    
    cd "${repo_dir}"
    
    # 检查是否已有gitee remote
    if git remote | grep -q "^gitee$"; then
        git remote set-url gitee "${gitee_url}"
    else
        git remote add gitee "${gitee_url}"
    fi
    
    # 尝试创建仓库 (如果不存在)
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${repo_name}\",\"private\":true}" \
        "https://gitee.com/api/v5/user/repos?access_token=${GITEE_TOKEN}" > /dev/null || true
    
    # 推送所有分支和标签
    git push gitee --all --force 2>/dev/null || log_warn "  推送到Gitee分支失败"
    git push gitee --tags --force 2>/dev/null || log_warn "  推送到Gitee标签失败"
}

# 镜像到GitLab
mirror_to_gitlab() {
    local repo_name="$1"
    local repo_dir="$2"
    
    log_info "  推送到 GitLab 镜像..."
    
    local gitlab_url="https://oauth2:${GITLAB_TOKEN}@gitlab.com/${GITLAB_USER}/${repo_name}.git"
    
    cd "${repo_dir}"
    
    if git remote | grep -q "^gitlab$"; then
        git remote set-url gitlab "${gitlab_url}"
    else
        git remote add gitlab "${gitlab_url}"
    fi
    
    git push gitlab --all --force 2>/dev/null || log_warn "  推送到GitLab分支失败"
    git push gitlab --tags --force 2>/dev/null || log_warn "  推送到GitLab标签失败"
}

# 导出Issues和PRs
export_issues() {
    log_info "导出 Issues 和 Pull Requests..."
    
    local repos_file="$1"
    local issues_dir="${BACKUP_BASE_DIR}/issues_$(date +%Y%m%d)"
    mkdir -p "${issues_dir}"
    
    # 解析JSON并导出每个仓库的Issues
    local repos=$(cat "${repos_file}" | grep -o '"full_name":"[^"]*"' | cut -d'"' -f4)
    
    for repo in ${repos}; do
        log_info "  导出 ${repo} 的 Issues..."
        
        local api_url="https://api.github.com/repos/${repo}/issues?state=all&per_page=100"
        local output_file="${issues_dir}/${repo//\//_}_issues.json"
        
        if [[ -n "${GITHUB_TOKEN}" ]]; then
            curl -s -H "Authorization: token ${GITHUB_TOKEN}" "${api_url}" > "${output_file}"
        else
            curl -s "${api_url}" > "${output_file}"
        fi
        
        sleep 1  # 避免触发API限流
    done
    
    log_info "Issues 导出完成: ${issues_dir}"
}

# 清理旧备份
cleanup_old_backups() {
    log_info "清理超过90天的旧备份..."
    
    find "${BACKUP_BASE_DIR}" -name "*.bundle" -mtime +90 -delete
    find "${BACKUP_BASE_DIR}" -name "*.tar.gz" -mtime +90 -delete
    find "${BACKUP_BASE_DIR}" -name "issues_*" -type d -mtime +90 -exec rm -rf {} + 2>/dev/null || true
    
    log_info "清理完成"
}

# 主函数
main() {
    log_info "=========================================="
    log_info "GitHub 备份开始"
    log_info "备份目录: ${BACKUP_BASE_DIR}"
    log_info "=========================================="
    
    # 检查依赖
    if ! command -v git &> /dev/null; then
        log_error "未找到 git 命令"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        log_error "未找到 curl 命令"
        exit 1
    fi
    
    # 获取仓库列表
    local repos_file=$(fetch_repos)
    
    if [[ ! -f "${repos_file}" ]]; then
        log_error "无法获取仓库列表"
        exit 1
    fi
    
    # 解析并备份每个仓库
    local count=0
    local failed=0
    
    # 使用jq解析JSON (如果可用)
    if command -v jq &> /dev/null; then
        while IFS= read -r repo; do
            local name=$(echo "${repo}" | jq -r '.name')
            local url=$(echo "${repo}" | jq -r '.clone_url')
            local private=$(echo "${repo}" | jq -r '.private')
            
            if backup_repo "${name}" "${url}" "${private}"; then
                ((count++))
            else
                ((failed++))
            fi
        done < <(cat "${repos_file}" | jq -c '.[]')
    else
        # 备用方案: 使用grep和sed解析
        log_warn "未安装 jq，使用备用解析方案"
        local repos=$(cat "${repos_file}" | grep -o '"clone_url":"[^"]*"' | cut -d'"' -f4)
        for url in ${repos}; do
            local name=$(basename "${url}" .git)
            if backup_repo "${name}" "${url}" "false"; then
                ((count++))
            else
                ((failed++))
            fi
        done
    fi
    
    # 导出Issues
    export_issues "${repos_file}"
    
    # 清理临时文件
    rm -f "${repos_file}"
    
    # 清理旧备份
    cleanup_old_backups
    
    # 生成报告
    log_info "=========================================="
    log_info "GitHub 备份完成"
    log_info "成功: ${count}, 失败: ${failed}"
    log_info "=========================================="
    
    # 创建状态文件供主脚本检查
    if [[ ${failed} -eq 0 ]]; then
        echo "SUCCESS" > "${SCRIPT_DIR}/.github_backup_status"
        exit 0
    else
        echo "FAILED: ${failed} repos" > "${SCRIPT_DIR}/.github_backup_status"
        exit 1
    fi
}

main "$@"
