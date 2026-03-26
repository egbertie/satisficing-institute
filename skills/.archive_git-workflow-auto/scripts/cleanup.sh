#!/bin/bash
# Git Cleanup Script
# Git清理脚本 - 删除已合并分支、清理旧stash

set -e

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    echo "🔍 DRY RUN 模式 - 不会执行实际删除"
    echo ""
fi

echo "========================================"
echo "🧹 Git 清理工具"
echo "========================================"
echo ""

# 检查git仓库
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 错误: 当前目录不是Git仓库"
    exit 1
fi

DEFAULT_BRANCH=$(git remote show origin 2>/dev/null | grep "HEAD branch" | awk '{print $NF}' || echo "main")
CURRENT_BRANCH=$(git branch --show-current)

echo "默认分支: $DEFAULT_BRANCH"
echo "当前分支: $CURRENT_BRANCH"
echo ""

# 1. 删除已合并的本地分支
echo "📋 已合并的本地分支:"
echo "-------------------"
MERGED_BRANCHES=$(git branch --merged "$DEFAULT_BRANCH" | grep -v "^\*" | grep -v "$DEFAULT_BRANCH" || true)

if [ -z "$MERGED_BRANCHES" ]; then
    echo "  (无)"
else
    echo "$MERGED_BRANCHES" | while read -r branch; do
        branch=$(echo "$branch" | xargs)
        if [ -n "$branch" ]; then
            echo "  🗑️  $branch"
            if [ "$DRY_RUN" = false ]; then
                git branch -d "$branch" 2>/dev/null && echo "     ✅ 已删除" || echo "     ❌ 删除失败"
            fi
        fi
    done
fi
echo ""

# 2. 删除已合并的远程分支
echo "🌐 已合并的远程分支:"
echo "-------------------"
git fetch --prune 2>/dev/null || true

REMOTE_BRANCHES=$(git branch -r --merged "$DEFAULT_BRANCH" | grep -v "HEAD" | grep -v "$DEFAULT_BRANCH" || true)
if [ -z "$REMOTE_BRANCHES" ]; then
    echo "  (无)"
else
    echo "$REMOTE_BRANCHES" | while read -r branch; do
        branch=$(echo "$branch" | xargs)
        if [ -n "$branch" ]; then
            echo "  🗑️  $branch"
            # 注意: 通常不自动删除远程分支，仅显示
        fi
    done
fi
echo ""

# 3. 清理旧的stash
echo "📦 Stash 列表:"
echo "-------------"
STASH_COUNT=$(git stash list | wc -l)
if [ "$STASH_COUNT" -eq 0 ]; then
    echo "  (无)"
else
    git stash list | head -5
    if [ "$STASH_COUNT" -gt 5 ]; then
        echo "  ... 还有 $((STASH_COUNT - 5)) 个"
    fi
    
    if [ "$STASH_COUNT" -gt 10 ] && [ "$DRY_RUN" = false ]; then
        echo ""
        read -p "是否清理最旧的 $((STASH_COUNT - 5)) 个stash? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            for i in $(seq 0 $((STASH_COUNT - 6))); do
                git stash drop "stash@{0}" 2>/dev/null || true
            done
            echo "  ✅ 已清理旧stash"
        fi
    fi
fi
echo ""

# 4. 清理无效的远程引用
echo "🔄 远程引用清理:"
echo "---------------"
if [ "$DRY_RUN" = false ]; then
    git remote prune origin 2>/dev/null && echo "  ✅ 已清理无效引用" || echo "  ℹ️  无无效引用"
else
    echo "  🔍 将执行: git remote prune origin"
fi
echo ""

# 5. 垃圾回收
echo "♻️  垃圾回收:"
echo "-----------"
if [ "$DRY_RUN" = false ]; then
    git gc --auto 2>/dev/null && echo "  ✅ 已完成" || echo "  ℹ️  无需回收"
else
    echo "  🔍 将执行: git gc --auto"
fi

echo ""
echo "========================================"
if [ "$DRY_RUN" = true ]; then
    echo "🔍 DRY RUN 完成 - 未执行实际更改"
    echo "运行时不加 --dry-run 以执行清理"
else
    echo "✅ 清理完成!"
fi
echo "========================================"
