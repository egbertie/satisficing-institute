#!/bin/bash
# GitHub Workflow Monitor
# 工作流监控脚本

set -e

REPO="${1:-}"
FAILED_ONLY=false

# 解析参数
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --failed-only)
            FAILED_ONLY=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$REPO" ]; then
    echo "🔍 GitHub Workflow Monitor"
    echo ""
    echo "Usage: $0 [owner/repo] [--failed-only]"
    echo ""
    echo "Options:"
    echo "  --failed-only    仅显示失败的工作流"
    exit 1
fi

echo "========================================"
echo "🔍 工作流监控: $REPO"
echo "========================================"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
if [ "$FAILED_ONLY" = true ]; then
    echo "模式: 仅显示失败"
fi
echo ""

# 检查gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ 错误: 未找到 GitHub CLI (gh)"
    exit 1
fi

# 获取工作流列表
LIMIT=10
if [ "$FAILED_ONLY" = true ]; then
    # 获取失败的工作流
    RUNS=$(gh run list --repo "$REPO" --limit 50 --json databaseId,name,status,conclusion,headBranch,createdAt 2>/dev/null | python3 -c "
import json, sys
runs = json.load(sys.stdin)
failed = [r for r in runs if r.get('conclusion') == 'failure']
print(json.dumps(failed[:10]))
")
else
    RUNS=$(gh run list --repo "$REPO" --limit "$LIMIT" --json databaseId,name,status,conclusion,headBranch,createdAt 2>/dev/null)
fi

echo "$RUNS" | python3 -c "
import json, sys
runs = json.load(sys.stdin)
if not runs:
    print('未发现工作流运行')
    sys.exit(0)

for run in runs:
    run_id = run.get('databaseId', 'N/A')
    name = run.get('name', 'Unknown')
    status = run.get('status', 'unknown')
    conclusion = run.get('conclusion', 'N/A')
    branch = run.get('headBranch', 'N/A')
    created = run.get('createdAt', 'N/A')[:16]
    
    if conclusion == 'success':
        icon = '✅'
    elif conclusion == 'failure':
        icon = '❌'
    elif conclusion == 'cancelled':
        icon = '🚫'
    else:
        icon = '⏳'
    
    print(f'{icon} {name}')
    print(f'   ID: {run_id} | 分支: {branch}')
    print(f'   状态: {status} | 结果: {conclusion}')
    print(f'   时间: {created}')
    print()
"

# 如果有失败的工作流，显示日志
FAILED_COUNT=$(echo "$RUNS" | python3 -c "
import json, sys
runs = json.load(sys.stdin)
count = sum(1 for r in runs if r.get('conclusion') == 'failure')
print(count)
")

if [ "$FAILED_COUNT" -gt 0 ]; then
    echo ""
    echo "⚠️  发现 $FAILED_COUNT 个失败的工作流"
    echo ""
    echo "查看失败的日志:"
    
    # 获取第一个失败的run ID
    FIRST_FAILED=$(echo "$RUNS" | python3 -c "
import json, sys
runs = json.load(sys.stdin)
for r in runs:
    if r.get('conclusion') == 'failure':
        print(r.get('databaseId'))
        break
")
    
    if [ -n "$FIRST_FAILED" ]; then
        echo "  gh run view $FIRST_FAILED --repo $REPO --log-failed"
        echo ""
        echo "最近的失败日志摘要:"
        gh run view "$FIRST_FAILED" --repo "$REPO" --log-failed 2>/dev/null | head -30 || echo "  (无法获取日志)"
    fi
fi

echo ""
echo "========================================"
echo "✅ 工作流监控完成"
echo "========================================"
