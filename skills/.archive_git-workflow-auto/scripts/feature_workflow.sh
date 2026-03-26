#!/bin/bash
# Git Feature Branch Workflow
# 特性分支工作流脚本

set -e

ACTION="${1:-help}"
FEATURE_NAME="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    cat << EOF
Git Feature Branch Workflow

Usage: $0 [action] [name]

Actions:
  start [name]     创建并切换到新的特性分支
  finish           完成特性开发（推送并提示创建PR）
  status           显示当前工作流状态

Examples:
  $0 start user-authentication    # 创建 feature/user-authentication 分支
  $0 finish                       # 推送并准备合并
EOF
}

# 检查是否在git仓库中
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "❌ 错误: 当前目录不是Git仓库"
        exit 1
    fi
}

# 检查工作区是否干净
check_clean_worktree() {
    if ! git diff --quiet HEAD 2>/dev/null || ! git diff --cached --quiet HEAD 2>/dev/null; then
        echo "⚠️  警告: 工作区有未提交的更改"
        git status -s
        read -p "是否继续? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 获取默认分支名
get_default_branch() {
    git remote show origin 2>/dev/null | grep "HEAD branch" | awk '{print $NF}' || echo "main"
}

# 创建特性分支
start_feature() {
    check_git_repo
    
    if [ -z "$FEATURE_NAME" ]; then
        echo "❌ 错误: 请提供特性名称"
        echo "用法: $0 start [feature-name]"
        exit 1
    fi
    
    check_clean_worktree
    
    DEFAULT_BRANCH=$(get_default_branch)
    BRANCH_NAME="feature/$FEATURE_NAME"
    
    echo "🌿 创建特性分支: $BRANCH_NAME"
    echo ""
    
    # 更新主分支
    echo "📥 更新 $DEFAULT_BRANCH..."
    git checkout "$DEFAULT_BRANCH" 2>/dev/null || git checkout main
    git pull origin "$DEFAULT_BRANCH" 2>/dev/null || git pull origin main
    
    # 创建分支
    echo "🌱 创建分支: $BRANCH_NAME"
    git checkout -b "$BRANCH_NAME"
    
    echo ""
    echo "========================================"
    echo "✅ 特性分支已创建!"
    echo "分支: $BRANCH_NAME"
    echo ""
    echo "开始开发:"
    echo "  1. 进行更改"
    echo "  2. git add ."
    echo "  3. git commit -m 'feat: your changes'"
    echo "  4. $0 finish"
    echo "========================================"
}

# 完成特性开发
finish_feature() {
    check_git_repo
    
    CURRENT_BRANCH=$(git branch --show-current)
    
    if [[ ! $CURRENT_BRANCH =~ ^feature/ ]]; then
        echo "❌ 错误: 当前不在特性分支上 (当前: $CURRENT_BRANCH)"
        exit 1
    fi
    
    check_clean_worktree
    
    DEFAULT_BRANCH=$(get_default_branch)
    
    echo "🏁 完成特性开发: $CURRENT_BRANCH"
    echo ""
    
    # 检查是否有提交
    COMMIT_COUNT=$(git rev-list --count HEAD ^"$DEFAULT_BRANCH" 2>/dev/null || echo "0")
    if [ "$COMMIT_COUNT" -eq 0 ]; then
        echo "⚠️  警告: 没有新的提交"
        read -p "是否继续推送? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "📤 推送 $COMMIT_COUNT 个提交到远程..."
    fi
    
    # 推送分支
    git push -u origin "$CURRENT_BRANCH"
    
    echo ""
    echo "========================================"
    echo "✅ 分支已推送!"
    echo ""
    echo "下一步:"
    echo "  1. 在GitHub/GitLab创建Pull Request"
    echo "  2. 代码审查"
    echo "  3. 合并到 $DEFAULT_BRANCH"
    echo "  4. 运行: ./cleanup.sh"
    echo "========================================"
}

# 显示状态
show_status() {
    check_git_repo
    
    CURRENT_BRANCH=$(git branch --show-current)
    DEFAULT_BRANCH=$(get_default_branch)
    
    echo "========================================"
    echo "📊 Git 工作流状态"
    echo "========================================"
    echo "当前分支: $CURRENT_BRANCH"
    echo "默认分支: $DEFAULT_BRANCH"
    echo ""
    
    # 检查工作区状态
    if git diff --quiet HEAD 2>/dev/null && git diff --cached --quiet HEAD 2>/dev/null; then
        echo "工作区: ✅ 干净"
    else
        echo "工作区: ⚠️  有未提交更改"
        git status -s
    fi
    
    # 检查与默认分支的差异
    AHEAD=$(git rev-list --count "$DEFAULT_BRANCH"..HEAD 2>/dev/null || echo "0")
    BEHIND=$(git rev-list --count HEAD.."$DEFAULT_BRANCH" 2>/dev/null || echo "0")
    
    echo ""
    echo "与 $DEFAULT_BRANCH 比较:"
    echo "  领先: $AHEAD 个提交"
    echo "  落后: $BEHIND 个提交"
    
    # 显示最近的提交
    echo ""
    echo "最近提交:"
    git log --oneline -5
    
    echo ""
    echo "========================================"
}

# 主逻辑
case "$ACTION" in
    start)
        start_feature
        ;;
    finish)
        finish_feature
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ 未知操作: $ACTION"
        show_help
        exit 1
        ;;
esac
