#!/bin/bash
# GitHub CI Check - Main Monitoring Script
# CI状态检查主脚本

set -e

REPO="${1:-}"
PR_NUMBER="${2:-}"

if [ -z "$REPO" ]; then
    echo "🔍 GitHub CI Monitor"
    echo ""
    echo "Usage: $0 [owner/repo] [pr-number]"
    echo ""
    echo "Examples:"
    echo "  $0 myorg/myrepo           # 检查仓库整体状态"
    echo "  $0 myorg/myrepo 42        # 检查PR #42状态"
    exit 1
fi

echo "========================================"
echo "🔍 GitHub CI 状态检查"
echo "========================================"
echo "仓库: $REPO"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ 错误: 未找到 GitHub CLI (gh)"
    echo "请安装: https://cli.github.com/"
    exit 1
fi

# 检查登录状态
if ! gh auth status &> /dev/null; then
    echo "❌ 错误: 未登录GitHub"
    echo "请运行: gh auth login"
    exit 1
fi

# 如果指定了PR，检查PR状态
if [ -n "$PR_NUMBER" ]; then
    echo "📋 检查 PR #$PR_NUMBER"
    echo "-------------------"
    
    # 获取PR状态
    PR_DATA=$(gh pr view "$PR_NUMBER" --repo "$REPO" --json state,title,url,checks 2>/dev/null || echo '{}')
    
    if [ "$PR_DATA" = '{}' ]; then
        echo "❌ 无法获取PR #$PR_NUMBER 信息"
        exit 1
    fi
    
    echo "$PR_DATA" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"标题: {data.get('title', 'N/A')}\")
print(f\"状态: {data.get('state', 'N/A')}\")
print(f\"URL: {data.get('url', 'N/A')}\")
print()
checks = data.get('checks', [])
if checks:
    print('检查状态:')
    for check in checks:
        status = check.get('state', 'unknown')
        icon = '✅' if status == 'SUCCESS' else '❌' if status == 'FAILURE' else '⏳'
        print(f\"  {icon} {check.get('name', 'Unknown')}: {status}\")
else:
    print('检查: 无')
"
    echo ""
    
    # 获取CI检查详情
    echo "🔬 CI 检查详情:"
    echo "--------------"
    gh pr checks "$PR_NUMBER" --repo "$REPO" 2>/dev/null || echo "  无检查数据"
else
    # 检查仓库整体状态
    echo "🌿 最近工作流运行:"
    echo "----------------"
    gh run list --repo "$REPO" --limit 5 --json name,status,conclusion,event,createdAt 2>/dev/null | python3 -c "
import json, sys
runs = json.load(sys.stdin)
for run in runs:
    status = run.get('status', 'unknown')
    conclusion = run.get('conclusion', 'N/A')
    icon = '✅' if conclusion == 'success' else '❌' if conclusion == 'failure' else '⏳'
    print(f\"{icon} {run.get('name', 'Unknown')}\")
    print(f\"   状态: {status} | 结果: {conclusion}\")
    print(f\"   事件: {run.get('event', 'N/A')} | 时间: {run.get('createdAt', 'N/A')[:10]}\")
    print()
" || echo "  无法获取工作流数据"
    
    echo ""
    echo "📬 开放的PR:"
    echo "----------"
    gh pr list --repo "$REPO" --limit 5 --json number,title,author,state 2>/dev/null | python3 -c "
import json, sys
prs = json.load(sys.stdin)
if prs:
    for pr in prs:
        print(f\"  #{pr.get('number')} {pr.get('title', 'No title')} by {pr.get('author', {}).get('login', 'Unknown')}\")
else:
    print('  无开放的PR')
" || echo "  无法获取PR列表"
fi

echo ""
echo "========================================"
echo "✅ CI 检查完成"
echo "========================================"
