#!/bin/bash
################################################################################
# 自动Git提交脚本 - 灾备关键组件
# 用途: 每2小时自动提交变更，防止数据丢失
################################################################################

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="/tmp/auto-git-commit.log"
LOCK_FILE="/tmp/auto-git-commit.lock"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查锁
if [[ -f "$LOCK_FILE" ]]; then
    pid=$(cat "$LOCK_FILE")
    if ps -p "$pid" > /dev/null 2>&1; then
        log "另一个自动提交进程正在运行，退出"
        exit 0
    fi
fi
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

cd "$WORKSPACE"

# 检查是否有变更
if [[ -z $(git status --porcelain) ]]; then
    log "工作区干净，无需提交"
    exit 0
fi

# 统计变更
changed_files=$(git status --short | wc -l)
insertions=$(git diff --cached --numstat 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
deletions=$(git diff --cached --numstat 2>/dev/null | awk '{sum+=$2} END {print sum+0}')

log "发现 $changed_files 个文件变更"

# 执行提交
git add -A
if git commit -m "AUTO: $(date +%Y%m%d-%H%M) 自动同步 - ${changed_files}文件"; then
    log "✅ 提交成功: ${changed_files}文件"
    
    # 尝试推送（可能失败，但不影响本地提交）
    if git push origin main 2>/dev/null; then
        log "✅ 推送成功"
    else
        log "⚠️ 推送失败（可能无网络或认证问题），变更已本地保存"
    fi
else
    log "❌ 提交失败"
    exit 1
fi
