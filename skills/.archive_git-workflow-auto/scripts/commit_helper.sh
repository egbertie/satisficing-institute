#!/bin/bash
# Git Commit Helper
# 提交信息规范化助手

TYPE="${1:-}"
MESSAGE="${2:-}"

# 提交类型说明
declare -A TYPE_DESCRIPTIONS=(
    ["feat"]="新功能"
    ["fix"]="修复"
    ["docs"]="文档"
    ["style"]="格式"
    ["refactor"]="重构"
    ["test"]="测试"
    ["chore"]="构建/工具"
)

show_help() {
    cat << EOF
Git Commit Helper - 规范化提交信息

Usage: $0 [type] [message]

Types:
  feat     新功能
  fix      修复
  docs     文档
  style    格式(不影响代码逻辑)
  refactor 重构
  test     测试
  chore    构建过程或辅助工具变动

Examples:
  $0 feat "add user authentication"
  $0 fix "resolve login timeout issue"
  $0 docs "update API documentation"

EOF
}

# 如果没有参数，显示帮助
if [ -z "$TYPE" ]; then
    show_help
    exit 0
fi

# 检查类型是否有效
if [ -z "${TYPE_DESCRIPTIONS[$TYPE]}" ]; then
    echo "❌ 错误: 未知的提交类型 '$TYPE'"
    echo ""
    show_help
    exit 1
fi

# 检查是否有提交信息
if [ -z "$MESSAGE" ]; then
    echo "❌ 错误: 请提供提交信息"
    echo "用法: $0 $TYPE 'your message'"
    exit 1
fi

# 检查是否在git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 错误: 当前目录不是Git仓库"
    exit 1
fi

# 检查工作区是否有更改
if git diff --quiet HEAD 2>/dev/null && git diff --cached --quiet HEAD 2>/dev/null; then
    echo "⚠️  警告: 工作区没有要提交的更改"
    git status
    exit 1
fi

# 构建提交信息
COMMIT_MSG="$TYPE: $MESSAGE"

echo "========================================"
echo "📝 准备提交"
echo "========================================"
echo "类型: $TYPE (${TYPE_DESCRIPTIONS[$TYPE]})"
echo "信息: $MESSAGE"
echo "完整: $COMMIT_MSG"
echo ""
echo "文件更改:"
git status -s
echo ""

# 执行提交
git commit -m "$COMMIT_MSG"

echo ""
echo "========================================"
echo "✅ 提交成功!"
echo "========================================"
