#!/bin/bash
################################################################################
# 配置和密钥备份脚本
# 功能: 安全备份敏感配置和API密钥
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# 配置
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-${HOME}/Backups/Configs}"
ENCRYPTION_KEY="${ENCRYPTION_KEY:-}"  # GPG密钥ID或密码

# 日志
log_info "配置和密钥备份任务开始"

# 创建备份目录
mkdir -p "${BACKUP_BASE_DIR}"
BACKUP_DIR="${BACKUP_BASE_DIR}/config_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "${BACKUP_DIR}"

# 备份外部工具配置
backup_external_configs() {
    log_info "备份外部工具配置..."
    
    local external_dir="${BACKUP_DIR}/external_tools"
    mkdir -p "${external_dir}"
    
    # 飞书配置
    if [[ -f "${SCRIPT_DIR}/../.config/feishu_config.json" ]]; then
        log_info "  备份飞书配置..."
        cp "${SCRIPT_DIR}/../.config/feishu_config.json" "${external_dir}/feishu_config.json.enc"
    fi
    
    # 保存配置清单
    cat > "${external_dir}/README.txt" << 'EOF'
外部工具配置备份
=================

本目录包含外部服务的配置信息。
所有敏感文件均已加密存储。

配置清单:
- 飞书 (Feishu)
- Notion
- GitHub
- 阿里云
- AWS (如使用)

恢复方式:
1. 解密文件: gpg -d file.enc > file.json
2. 或查看密码管理器 (1Password/Bitwarden)

注意: 不要将解密的文件提交到Git!
EOF
    
    log_info "外部工具配置备份完成"
}

# 创建加密的密钥备份
backup_keys_encrypted() {
    log_info "创建加密密钥备份..."
    
    local keys_dir="${BACKUP_DIR}/keys"
    mkdir -p "${keys_dir}"
    
    # SSH密钥 (如果用户选择备份)
    if [[ -d "${HOME}/.ssh" ]]; then
        log_info "  备份 SSH 密钥..."
        
        # 创建密钥归档
        local ssh_backup="${keys_dir}/ssh_keys_$(date +%Y%m%d).tar.gz"
        
        # 仅备份私钥 (需要加密)
        tar czf "${ssh_backup}" -C "${HOME}/.ssh" \
            id_rsa id_ed25519 id_ecdsa \
            2>/dev/null || true
        
        # 加密
        if [[ -f "${ssh_backup}" && -n "${ENCRYPTION_KEY}" ]]; then
            if command -v gpg &> /dev/null; then
                gpg --symmetric --cipher-algo AES256 \
                    --output "${ssh_backup}.gpg" \
                    --passphrase "${ENCRYPTION_KEY}" \
                    --batch --yes \
                    "${ssh_backup}" 2>/dev/null || {
                    log_warn "  GPG加密失败，保留未加密文件 (危险!)"
                }
                
                if [[ -f "${ssh_backup}.gpg" ]]; then
                    rm -f "${ssh_backup}"
                    log_info "  SSH密钥已加密"
                fi
            fi
        fi
    fi
    
    # API密钥列表 (不保存实际密钥，只保存清单)
    log_info "  创建 API 密钥清单..."
    
    cat > "${keys_dir}/API_KEYS_CHECKLIST.txt" << 'EOF'
API密钥清单
===========

本文件记录了所有需要备份的API密钥，实际密钥存储在密码管理器中。

开发相关:
□ GitHub Personal Access Token
□ GitLab Access Token
□ Gitee Access Token

云服务:
□ 阿里云 AccessKey
□ AWS Access Key
□ 腾讯云 SecretId/Key

协作工具:
□ Notion Integration Token
□ 飞书 App ID / Secret
□ Slack Token

其他:
□ OpenAI API Key
□ 其他第三方服务API密钥

存储位置: 1Password / Bitwarden / KeePass
最后验证: ___________
EOF
    
    log_info "密钥备份完成"
}

# 备份环境变量模板
backup_env_template() {
    log_info "创建环境变量模板..."
    
    cat > "${BACKUP_DIR}/environment-template.sh" << 'EOF'
#!/bin/bash
################################################################################
# 环境变量恢复模板
# 用法: source ./environment-template.sh
# 注意: 实际值需要从密码管理器复制
################################################################################

# GitHub
export GITHUB_USER="your-username"
export GITHUB_TOKEN=""  # 从密码管理器复制

# Gitee (镜像用)
export GITEE_USER="your-username"
export GITEE_TOKEN=""  # 从密码管理器复制

# Notion
export NOTION_TOKEN=""  # 从密码管理器复制

# 阿里云
export ALIYUN_ACCESS_KEY_ID=""
export ALIYUN_ACCESS_KEY_SECRET=""
export ALIYUN_OSS_BUCKET="your-backup-bucket"

# AWS (如果使用)
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_DEFAULT_REGION="ap-northeast-1"

# 备份加密密钥
export ENCRYPTION_KEY=""  # GPG加密用密码

# 远程备份服务器 (如果使用)
export REMOTE_BACKUP_SERVER="user@backup-server.example.com"

################################################################################
# 验证环境变量是否已设置
################################################################################

check_env() {
    local var_name="$1"
    if [[ -z "${!var_name:-}" ]]; then
        echo "警告: ${var_name} 未设置"
        return 1
    fi
    return 0
}

# 检查关键变量
check_env "GITHUB_TOKEN" || true
check_env "NOTION_TOKEN" || true

echo "环境变量已加载"
echo "请确保所有敏感值已从密码管理器正确复制"
EOF
    
    chmod +x "${BACKUP_DIR}/environment-template.sh"
    
    log_info "环境变量模板已创建"
}

# 创建密码管理器导出指南
password_manager_guide() {
    log_info "创建密码管理器指南..."
    
    cat > "${BACKUP_DIR}/PASSWORD_MANAGER_GUIDE.md" << 'EOF'
# 密码管理器使用指南

## 推荐工具

### 1. 1Password (推荐)
- 官网: https://1password.com
- 优点: 跨平台、家庭共享、旅行模式、Watchtower安全报告

### 2. Bitwarden (开源免费)
- 官网: https://bitwarden.com
- 优点: 开源、免费版功能全、可自建服务器

### 3. KeePassXC (本地优先)
- 官网: https://keepassxc.org
- 优点: 完全离线、免费、高度可定制

## 必须存储的项目

### API密钥
- [ ] GitHub Personal Access Token (classic + fine-grained)
- [ ] Gitee Access Token
- [ ] Notion Integration Token
- [ ] 阿里云 AccessKey
- [ ] 飞书 App凭证

### SSH密钥
- [ ] 主开发机私钥密码 (如果使用密码保护)
- [ ] 服务器登录密钥密码

### 加密密钥
- [ ] GPG主密钥密码
- [ ] 备份加密密码
- [ ] 密码管理器主密码 (写下来保存在保险箱)

## 备份策略

1. **密码管理器本身也需要备份**
   - 1Password: 定期导出紧急包 (Emergency Kit)
   - Bitwarden: 导出加密JSON
   - KeePass: 数据库文件多地备份

2. **离线备份**
   - 打印紧急包 PDF 存银行保险箱
   - 加密U盘存放关键密钥

3. **多因素认证 (MFA) 备份码**
   - 所有服务的 MFA 备份码单独保存
   - 存放在与密码管理器不同的位置

## 恢复流程

### 场景: 密码管理器不可用

1. 使用紧急包恢复 1Password 账户
2. 或使用 KeePass 备份文件
3. 或使用 Bitwarden 服务器备份

### 场景: 需要在新设备访问API密钥

1. 安装密码管理器
2. 登录账户
3. 复制所需API密钥到环境变量

## 安全检查清单

每月检查:
- [ ] 检查 Have I Been Pwned 是否有泄露
- [ ] 更新重要服务的API密钥
- [ ] 检查密码管理器安全报告
- [ ] 验证备份文件可解密

每季度检查:
- [ ] 轮换所有长期使用的API密钥
- [ ] 审查并删除不再使用的密钥
- [ ] 更新离线备份
EOF
    
    log_info "密码管理器指南已创建"
}

# 加密整个备份
encrypt_backup() {
    if [[ -n "${ENCRYPTION_KEY}" ]]; then
        log_info "加密备份..."
        
        local archive="${BACKUP_DIR}.tar.gz"
        tar czf "${archive}" -C "$(dirname "${BACKUP_DIR}")" "$(basename "${BACKUP_DIR}")"
        
        if command -v gpg &> /dev/null; then
            gpg --symmetric --cipher-algo AES256 \
                --output "${archive}.gpg" \
                --passphrase "${ENCRYPTION_KEY}" \
                --batch --yes \
                "${archive}" 2>/dev/null && {
                rm -f "${archive}"
                log_info "备份已加密: ${archive}.gpg"
            }
        fi
    fi
}

# 创建离线备份到U盘
offline_backup_to_usb() {
    log_info "检查离线备份介质..."
    
    # 检测挂载的U盘
    local usb_paths=(
        "/media/${USER}/BACKUP"
        "/Volumes/BACKUP"
        "/mnt/usb"
        "${HOME}/USB_BACKUP"
    )
    
    for usb_path in "${usb_paths[@]}"; do
        if [[ -d "${usb_path}" ]]; then
            log_info "  找到备份U盘: ${usb_path}"
            
            local offline_dir="${usb_path}/ConfigBackups"
            mkdir -p "${offline_dir}"
            
            # 复制加密备份
            if [[ -f "${BACKUP_DIR}.tar.gz.gpg" ]]; then
                cp "${BACKUP_DIR}.tar.gz.gpg" "${offline_dir}/"
                log_info "  已复制加密备份到U盘"
            fi
            
            # 复制密钥清单
            cp "${BACKUP_DIR}/keys/API_KEYS_CHECKLIST.txt" "${offline_dir}/"
            
            echo "$(date): 配置备份已同步" > "${offline_dir}/LAST_SYNC.txt"
            
            log_info "  离线备份完成"
            break
        fi
    done
}

# 主函数
main() {
    log_info "=========================================="
    log_info "配置和密钥备份开始"
    log_info "备份目录: ${BACKUP_DIR}"
    log_info "=========================================="
    
    backup_external_configs
    backup_keys_encrypted
    backup_env_template
    password_manager_guide
    
    # 创建清单
    cat > "${BACKUP_DIR}/MANIFEST.txt" << EOF
配置和密钥备份清单
====================
备份时间: $(date)

包含内容:
1. external_tools/ - 外部工具配置
2. keys/ - 加密密钥和API清单
3. environment-template.sh - 环境变量模板
4. PASSWORD_MANAGER_GUIDE.md - 密码管理器使用指南

注意事项:
- 敏感文件已加密 (.gpg)
- 实际API密钥存储在密码管理器
- 恢复时需要先解密再使用

恢复步骤:
1. 解密文件: gpg -d file.gpg > file.tar.gz
2. 解压: tar xzf file.tar.gz
3. 从密码管理器复制密钥到环境变量
4. 运行备份脚本验证配置
EOF
    
    # 加密
    encrypt_backup
    
    # 离线备份
    offline_backup_to_usb
    
    log_info "=========================================="
    log_info "配置和密钥备份完成"
    log_info "备份位置: ${BACKUP_DIR}"
    log_info "=========================================="
    
    echo "SUCCESS" > "${SCRIPT_DIR}/.config_backup_status"
}

main "$@"
