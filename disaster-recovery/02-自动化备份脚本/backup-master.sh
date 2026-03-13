#!/bin/bash
################################################################################
# 灾备自动化备份脚本套件 - 主控脚本
# Disaster Recovery Automated Backup Scripts
#
# 版本: 1.0
# 日期: 2026-03-12
# 用途: 协调执行所有备份任务
################################################################################

set -euo pipefail

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
CONFIG_FILE="${SCRIPT_DIR}/backup.conf"
LOCK_FILE="/tmp/dr-backup.lock"

# 创建日志目录
mkdir -p "${LOG_DIR}"

# 日志函数
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_DIR}/backup-$(date +%Y%m%d).log"
}

log_info() { log "INFO" "$1"; }
log_warn() { log "WARN" "$1"; }
log_error() { log "ERROR" "$1"; }

# 检查锁文件
check_lock() {
    if [[ -f "${LOCK_FILE}" ]]; then
        local pid=$(cat "${LOCK_FILE}")
        if ps -p "${pid}" > /dev/null 2>&1; then
            log_error "另一个备份进程正在运行 (PID: ${pid})"
            exit 1
        else
            log_warn "发现陈旧的锁文件，已清除"
            rm -f "${LOCK_FILE}"
        fi
    fi
    echo $$ > "${LOCK_FILE}"
}

# 清理锁文件
cleanup() {
    rm -f "${LOCK_FILE}"
    log_info "备份任务完成，锁文件已清除"
}

trap cleanup EXIT

# 执行备份任务
run_backup() {
    local script_name="$1"
    local script_path="${SCRIPT_DIR}/${script_name}"
    
    log_info "开始执行: ${script_name}"
    
    if [[ -x "${script_path}" ]]; then
        if "${script_path}"; then
            log_info "✓ ${script_name} 执行成功"
            return 0
        else
            log_error "✗ ${script_name} 执行失败"
            return 1
        fi
    else
        log_error "✗ ${script_name} 不存在或没有执行权限"
        return 1
    fi
}

# 发送通知
send_notification() {
    local status="$1"
    local message="$2"
    
    # 这里可以集成飞书、邮件或其他通知渠道
    log_info "通知 [${status}]: ${message}"
    
    # 示例: 飞书通知 (需要配置 webhook)
    # curl -X POST -H "Content-Type: application/json" \
    #   -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"备份${status}: ${message}\"}}" \
    #   "${FEISHU_WEBHOOK_URL}" 2>/dev/null || true
}

# 主函数
main() {
    log_info "=========================================="
    log_info "灾备自动化备份任务开始"
    log_info "=========================================="
    
    check_lock
    
    local failed_tasks=()
    
    # 1. GitHub 仓库备份
    if ! run_backup "backup-github.sh"; then
        failed_tasks+=("GitHub备份")
    fi
    
    # 2. Notion 数据备份
    if ! run_backup "backup-notion.sh"; then
        failed_tasks+=("Notion备份")
    fi
    
    # 3. 本地环境备份
    if ! run_backup "backup-local.sh"; then
        failed_tasks+=("本地环境备份")
    fi
    
    # 4. 配置和密钥备份
    if ! run_backup "backup-configs.sh"; then
        failed_tasks+=("配置备份")
    fi
    
    # 汇总报告
    log_info "=========================================="
    if [[ ${#failed_tasks[@]} -eq 0 ]]; then
        log_info "✓ 所有备份任务成功完成"
        send_notification "成功" "所有备份任务已完成"
        exit 0
    else
        log_error "✗ 以下任务失败: ${failed_tasks[*]}"
        send_notification "失败" "失败任务: ${failed_tasks[*]}"
        exit 1
    fi
}

# 命令行参数处理
case "${1:-}" in
    --daily)
        # 每日完整备份
        export BACKUP_TYPE="daily"
        main
        ;;
    --weekly)
        # 每周深度备份
        export BACKUP_TYPE="weekly"
        main
        ;;
    --github)
        # 仅GitHub备份
        run_backup "backup-github.sh"
        ;;
    --notion)
        # 仅Notion备份
        run_backup "backup-notion.sh"
        ;;
    --local)
        # 仅本地备份
        run_backup "backup-local.sh"
        ;;
    --help|-h)
        cat << 'EOF'
用法: ./backup-master.sh [选项]

选项:
  --daily     执行每日完整备份 (默认)
  --weekly    执行每周深度备份
  --github    仅执行GitHub备份
  --notion    仅执行Notion备份
  --local     仅执行本地备份
  --help      显示此帮助信息

示例:
  ./backup-master.sh --daily    # 每日备份
  ./backup-master.sh --github     # 仅备份GitHub
EOF
        ;;
    *)
        # 默认执行每日备份
        export BACKUP_TYPE="daily"
        main
        ;;
esac
