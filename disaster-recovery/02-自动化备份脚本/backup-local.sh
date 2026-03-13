#!/bin/bash
################################################################################
# 本地环境备份脚本
# 功能: 备份本地开发环境、配置文件和代码仓库
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# 配置
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-${HOME}/Backups/Local}"
HOME_DIR="${HOME}"

# 需要备份的目录 (根据实际环境修改)
declare -a BACKUP_DIRS=(
    "${HOME}/workspace"
    "${HOME}/projects"
    "${HOME}/Documents/Important"
)

# 需要备份的文件
declare -a BACKUP_FILES=(
    "${HOME}/.bashrc"
    "${HOME}/.zshrc"
    "${HOME}/.vimrc"
    "${HOME}/.gitconfig"
    "${HOME}/.ssh/config"
    "${HOME}/.aws/config"
    "${HOME}/.aws/credentials"
)

# 日志
log_info "本地环境备份任务开始"

# 创建备份目录
mkdir -p "${BACKUP_BASE_DIR}"
BACKUP_DIR="${BACKUP_BASE_DIR}/local_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "${BACKUP_DIR}"

# 备份目录
backup_directories() {
    log_info "备份重要目录..."
    
    local dirs_dir="${BACKUP_DIR}/directories"
    mkdir -p "${dirs_dir}"
    
    for dir in "${BACKUP_DIRS[@]}"; do
        if [[ -d "${dir}" ]]; then
            local base_name=$(basename "${dir}")
            log_info "  备份: ${dir}"
            
            # 排除不需要的文件
            tar czf "${dirs_dir}/${base_name}.tar.gz" \
                --exclude='.git' \
                --exclude='node_modules' \
                --exclude='__pycache__' \
                --exclude='*.pyc' \
                --exclude='.DS_Store' \
                --exclude='*.log' \
                -C "$(dirname "${dir}")" "$(basename "${dir}")" 2>/dev/null || {
                log_warn "  备份 ${dir} 失败"
            }
        else
            log_warn "  目录不存在: ${dir}"
        fi
    done
    
    log_info "目录备份完成"
}

# 备份配置文件
backup_config_files() {
    log_info "备份配置文件..."
    
    local configs_dir="${BACKUP_DIR}/configs"
    mkdir -p "${configs_dir}"
    
    for file in "${BACKUP_FILES[@]}"; do
        if [[ -f "${file}" ]]; then
            log_info "  备份: ${file}"
            cp "${file}" "${configs_dir}/" 2>/dev/null || log_warn "  复制失败: ${file}"
        else
            log_warn "  文件不存在: ${file}"
        fi
    done
    
    # 备份整个.ssh目录 (排除私钥)
    if [[ -d "${HOME}/.ssh" ]]; then
        log_info "  备份 SSH 配置 (排除私钥)..."
        mkdir -p "${configs_dir}/.ssh"
        
        # 复制配置文件
        cp "${HOME}/.ssh/config" "${configs_dir}/.ssh/" 2>/dev/null || true
        cp "${HOME}/.ssh/known_hosts" "${configs_dir}/.ssh/" 2>/dev/null || true
        cp "${HOME}/.ssh/authorized_keys" "${configs_dir}/.ssh/" 2>/dev/null || true
        
        # 复制公钥
        cp "${HOME}/.ssh/"*.pub "${configs_dir}/.ssh/" 2>/dev/null || true
    fi
    
    # 备份VSCode配置
    if [[ -d "${HOME}/.config/Code/User" ]]; then
        log_info "  备份 VSCode 配置..."
        mkdir -p "${configs_dir}/vscode"
        cp "${HOME}/.config/Code/User/settings.json" "${configs_dir}/vscode/" 2>/dev/null || true
        cp "${HOME}/.config/Code/User/keybindings.json" "${configs_dir}/vscode/" 2>/dev/null || true
    fi
    
    # macOS: 备份iTerm2配置
    if [[ -f "${HOME}/Library/Preferences/com.googlecode.iterm2.plist" ]]; then
        log_info "  备份 iTerm2 配置..."
        mkdir -p "${configs_dir}/iterm2"
        cp "${HOME}/Library/Preferences/com.googlecode.iterm2.plist" "${configs_dir}/iterm2/" 2>/dev/null || true
    fi
    
    log_info "配置文件备份完成"
}

# 备份已安装的软件包列表
backup_package_lists() {
    log_info "备份软件包列表..."
    
    local packages_dir="${BACKUP_DIR}/packages"
    mkdir -p "${packages_dir}"
    
    # Homebrew (macOS)
    if command -v brew &> /dev/null; then
        log_info "  备份 Homebrew 包列表..."
        brew list > "${packages_dir}/brew-list.txt" 2>/dev/null || true
        brew cask list > "${packages_dir}/brew-cask-list.txt" 2>/dev/null || true
        brew bundle dump --file="${packages_dir}/Brewfile" --force 2>/dev/null || true
    fi
    
    # APT (Ubuntu/Debian)
    if command -v apt &> /dev/null; then
        log_info "  备份 APT 包列表..."
        dpkg --get-selections > "${packages_dir}/apt-selections.txt" 2>/dev/null || true
        apt list --installed > "${packages_dir}/apt-installed.txt" 2>/dev/null || true
    fi
    
    # NPM
    if command -v npm &> /dev/null; then
        log_info "  备份 NPM 全局包..."
        npm list -g --depth=0 > "${packages_dir}/npm-global.txt" 2>/dev/null || true
    fi
    
    # Python pip
    if command -v pip &> /dev/null; then
        log_info "  备份 pip 包列表..."
        pip list > "${packages_dir}/pip-list.txt" 2>/dev/null || true
        pip freeze > "${packages_dir}/requirements.txt" 2>/dev/null || true
    fi
    
    # VSCode 扩展
    if command -v code &> /dev/null; then
        log_info "  备份 VSCode 扩展..."
        code --list-extensions > "${packages_dir}/vscode-extensions.txt" 2>/dev/null || true
    fi
    
    log_info "软件包列表备份完成"
}

# 备份本地Git仓库列表
backup_git_repos() {
    log_info "扫描本地 Git 仓库..."
    
    local repos_file="${BACKUP_DIR}/git-repos.txt"
    echo "# 本地 Git 仓库列表" > "${repos_file}"
    echo "# 生成时间: $(date)" >> "${repos_file}"
    echo "" >> "${repos_file}"
    
    # 在常用目录下查找Git仓库
    for search_dir in "${HOME}/workspace" "${HOME}/projects" "${HOME}/code"; do
        if [[ -d "${search_dir}" ]]; then
            while IFS= read -r git_dir; do
                local repo_dir=$(dirname "${git_dir}")
                echo "${repo_dir}" >> "${repos_file}"
                
                # 保存远程URL
                local remotes=$(cd "${repo_dir}" && git remote -v 2>/dev/null | grep fetch | awk '{print $1, $2}')
                if [[ -n "${remotes}" ]]; then
                    echo "  远程: ${remotes}" >> "${repos_file}"
                fi
            done < <(find "${search_dir}" -name ".git" -type d 2>/dev/null)
        fi
    done
    
    local count=$(grep -c "^/" "${repos_file}" 2>/dev/null || echo "0")
    log_info "发现 ${count} 个Git仓库"
}

# 创建环境恢复脚本
create_restore_script() {
    log_info "创建环境恢复脚本..."
    
    cat > "${BACKUP_DIR}/restore.sh" << 'RESTORE_EOF'
#!/bin/bash
################################################################################
# 本地环境恢复脚本
# 用法: ./restore.sh [备份目录]
################################################################################

set -euo pipefail

BACKUP_DIR="${1:-$(dirname "$0")}"

echo "=========================================="
echo "本地环境恢复"
echo "备份目录: ${BACKUP_DIR}"
echo "=========================================="

# 恢复配置文件
echo "恢复配置文件..."
if [[ -d "${BACKUP_DIR}/configs" ]]; then
    for file in "${BACKUP_DIR}/configs"/*; do
        if [[ -f "${file}" ]]; then
            cp "${file}" "${HOME}/"
            echo "  已恢复: $(basename "${file}")"
        fi
    done
fi

# 恢复目录
echo "恢复目录..."
if [[ -d "${BACKUP_DIR}/directories" ]]; then
    for archive in "${BACKUP_DIR}/directories"/*.tar.gz; do
        if [[ -f "${archive}" ]]; then
            echo "  解压: $(basename "${archive}")"
            tar xzf "${archive}" -C "${HOME}/" 2>/dev/null || echo "    警告: 解压失败"
        fi
    done
fi

# 恢复软件包 (可选)
echo ""
echo "软件包恢复指南:"
echo "  - Homebrew: brew bundle --file=${BACKUP_DIR}/packages/Brewfile"
echo "  - APT: sudo dpkg --set-selections < ${BACKUP_DIR}/packages/apt-selections.txt"
echo "  - NPM: npm install -g < ${BACKUP_DIR}/packages/npm-global.txt"
echo "  - VSCode: cat ${BACKUP_DIR}/packages/vscode-extensions.txt | xargs -n 1 code --install-extension"

echo ""
echo "=========================================="
echo "恢复完成"
echo "=========================================="
RESTORE_EOF

    chmod +x "${BACKUP_DIR}/restore.sh"
    log_info "恢复脚本已创建: ${BACKUP_DIR}/restore.sh"
}

# 同步到云存储
sync_to_cloud() {
    log_info "同步到云存储..."
    
    # 阿里云OSS
    if command -v ossutil &> /dev/null; then
        log_info "  同步到阿里云 OSS..."
        ossutil cp -r "${BACKUP_DIR}" "oss://your-backup-bucket/local/" 2>/dev/null || {
            log_warn "  OSS同步失败"
        }
    fi
    
    # AWS S3
    if command -v aws &> /dev/null; then
        log_info "  同步到 AWS S3..."
        aws s3 sync "${BACKUP_DIR}" "s3://your-backup-bucket/local/" 2>/dev/null || {
            log_warn "  S3同步失败"
        }
    fi
    
    # Rsync到远程服务器
    if [[ -n "${REMOTE_BACKUP_SERVER:-}" ]]; then
        log_info "  同步到远程服务器..."
        rsync -avz --delete "${BACKUP_DIR}/" "${REMOTE_BACKUP_SERVER}:backups/local/" 2>/dev/null || {
            log_warn "  远程同步失败"
        }
    fi
    
    log_info "云存储同步完成"
}

# 清理旧备份
cleanup() {
    log_info "清理超过12周的旧备份..."
    
    find "${BACKUP_BASE_DIR}" -name "local_backup_*" -type d -mtime +84 -exec rm -rf {} + 2>/dev/null || true
    
    log_info "清理完成"
}

# 主函数
main() {
    log_info "=========================================="
    log_info "本地环境备份开始"
    log_info "备份目录: ${BACKUP_DIR}"
    log_info "=========================================="
    
    # 执行备份
    backup_directories
    backup_config_files
    backup_package_lists
    backup_git_repos
    create_restore_script
    
    # 创建备份清单
    cat > "${BACKUP_DIR}/MANIFEST.txt" << EOF
本地环境备份清单
================
备份时间: $(date)
备份目录: ${BACKUP_DIR}

包含内容:
1. directories/ - 重要工作目录
2. configs/ - 配置文件
3. packages/ - 软件包列表
4. git-repos.txt - Git仓库清单
5. restore.sh - 恢复脚本

恢复方法:
运行 ./restore.sh 或参考各目录内容手动恢复
EOF
    
    # 同步到云
    sync_to_cloud
    
    # 清理
    cleanup
    
    # 打包
    log_info "打包备份..."
    local archive_name="local_backup_$(date +%Y%m%d).tar.gz"
    tar czf "${BACKUP_BASE_DIR}/${archive_name}" -C "$(dirname "${BACKUP_DIR}")" "$(basename "${BACKUP_DIR}")" 2>/dev/null || true
    
    log_info "=========================================="
    log_info "本地环境备份完成"
    log_info "备份位置: ${BACKUP_DIR}"
    log_info "归档文件: ${BACKUP_BASE_DIR}/${archive_name}"
    log_info "=========================================="
    
    echo "SUCCESS" > "${SCRIPT_DIR}/.local_backup_status"
}

main "$@"
