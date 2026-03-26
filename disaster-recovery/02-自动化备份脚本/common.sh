#!/bin/bash
################################################################################
# 通用函数库 - 被其他备份脚本引用
################################################################################

# 日志函数
LOG_DIR="${SCRIPT_DIR}/logs"
mkdir -p "${LOG_DIR}"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_file="${LOG_DIR}/backup-$(date +%Y%m%d).log"
    
    # 输出到控制台
    echo "[${timestamp}] [${level}] ${message}"
    
    # 追加到日志文件
    echo "[${timestamp}] [${level}] ${message}" >> "${log_file}"
}

log_info() { log "INFO" "$1"; }
log_warn() { log "WARN" "$1"; }
log_error() { log "ERROR" "$1"; }

# 检查命令是否存在
check_command() {
    local cmd="$1"
    if ! command -v "${cmd}" &> /dev/null; then
        log_error "未找到命令: ${cmd}"
        return 1
    fi
    return 0
}

# 检查环境变量
check_env_var() {
    local var_name="$1"
    if [[ -z "${!var_name:-}" ]]; then
        log_warn "环境变量未设置: ${var_name}"
        return 1
    fi
    return 0
}

# 创建目录 (如果不存在)
ensure_dir() {
    local dir="$1"
    if [[ ! -d "${dir}" ]]; then
        mkdir -p "${dir}"
        log_info "创建目录: ${dir}"
    fi
}

# 安全的文件复制 (带验证)
safe_copy() {
    local src="$1"
    local dst="$2"
    
    if [[ ! -f "${src}" ]]; then
        log_error "源文件不存在: ${src}"
        return 1
    fi
    
    cp "${src}" "${dst}" || {
        log_error "复制失败: ${src} -> ${dst}"
        return 1
    }
    
    # 验证
    if [[ -f "${dst}" ]]; then
        local src_sum=$(md5sum "${src}" 2>/dev/null | cut -d' ' -f1 || shasum "${src}" 2>/dev/null | cut -d' ' -f1)
        local dst_sum=$(md5sum "${dst}" 2>/dev/null | cut -d' ' -f1 || shasum "${dst}" 2>/dev/null | cut -d' ' -f1)
        
        if [[ "${src_sum}" == "${dst_sum}" ]]; then
            log_info "复制成功: $(basename "${src}")"
            return 0
        else
            log_error "校验失败: ${src}"
            return 1
        fi
    fi
    
    return 1
}

# 清理旧文件 (按时间)
cleanup_old() {
    local dir="$1"
    local days="$2"
    local pattern="${3:-*}"
    
    if [[ -d "${dir}" ]]; then
        find "${dir}" -name "${pattern}" -mtime +"${days}" -delete 2>/dev/null || {
            log_warn "清理旧文件失败: ${dir}"
        }
    fi
}

# 发送通知 (通用)
send_notification() {
    local title="$1"
    local message="$2"
    local status="${3:-info}"
    
    # 日志记录
    log_info "通知 [${status}]: ${title} - ${message}"
    
    # macOS 通知
    if command -v osascript &> /dev/null; then
        osascript -e "display notification \"${message}\" with title \"${title}\"" 2>/dev/null || true
    fi
    
    # Linux notify-send
    if command -v notify-send &> /dev/null; then
        notify-send "${title}" "${message}" 2>/dev/null || true
    fi
}

# 计算目录大小
get_dir_size() {
    local dir="$1"
    if [[ -d "${dir}" ]]; then
        du -sh "${dir}" 2>/dev/null | cut -f1
    else
        echo "N/A"
    fi
}

# 格式化时间间隔
format_duration() {
    local seconds="$1"
    local hours=$((seconds / 3600))
    local minutes=$(((seconds % 3600) / 60))
    local secs=$((seconds % 60))
    
    printf "%02d:%02d:%02d" ${hours} ${minutes} ${secs}
}

# 错误处理
handle_error() {
    local exit_code=$?
    local line_no=$1
    log_error "脚本在第 ${line_no} 行发生错误，退出码: ${exit_code}"
    exit "${exit_code}"
}

trap 'handle_error $LINENO' ERR
