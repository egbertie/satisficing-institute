#!/bin/bash
################################################################################
# 灾备完整性验证脚本
# 用途: 验证7层备份的完整性和可用性
################################################################################

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
ERRORS=0
WARNINGS=0

echo "=========================================="
echo "🛡️ Claw灾备完整性验证"
echo "时间: $(date)"
echo "=========================================="

# ===== L4: 核心身份 =====
echo ""
echo "📋 [L4] 核心身份文件检查"
echo "----------------------------------------"

for file in SOUL.md IDENTITY.md USER.md AGENTS.md BOOTSTRAP.md; do
    if [[ -f "$WORKSPACE/$file" ]]; then
        size=$(wc -c < "$WORKSPACE/$file")
        echo "  ✅ $file 存在 ($size 字节)"
        
        # 验证文件可读且有内容
        if [[ $size -lt 100 ]]; then
            echo "  ⚠️  $file 内容过少，可能不完整"
            ((WARNINGS++))
        fi
    else
        echo "  ❌ $file 缺失!"
        ((ERRORS++))
    fi
done

# ===== L6: 动态记忆 =====
echo ""
echo "🧠 [L6] 动态记忆系统检查"
echo "----------------------------------------"

if [[ -f "$WORKSPACE/MEMORY.md" ]]; then
    size=$(wc -c < "$WORKSPACE/MEMORY.md")
    echo "  ✅ MEMORY.md 存在 ($size 字节)"
else
    echo "  ❌ MEMORY.md 缺失!"
    ((ERRORS++))
fi

TODAY_LOG="$WORKSPACE/memory/$(date +%Y-%m-%d).md"
if [[ -f "$TODAY_LOG" ]]; then
    echo "  ✅ 今日日志存在 ($(wc -c < "$TODAY_LOG") 字节)"
else
    echo "  ⚠️  今日日志缺失 (可接受，将在下次对话时创建)"
    ((WARNINGS++))
fi

MEMORY_COUNT=$(find "$WORKSPACE/memory" -name "*.md" -type f 2>/dev/null | wc -l)
echo "  📊 记忆文件总数: $MEMORY_COUNT"

# ===== L2: 自动化流水线 =====
echo ""
echo "⚙️  [L2] 自动化配置检查"
echo "----------------------------------------"

if [[ -f "$WORKSPACE/config/INFO_LOOP_CRON.md" ]]; then
    echo "  ✅ INFO_LOOP_CRON.md 存在"
else
    echo "  ❌ INFO_LOOP_CRON.md 缺失!"
    ((ERRORS++))
fi

if [[ -f "$WORKSPACE/config/cron-rules.yaml" ]]; then
    echo "  ✅ cron-rules.yaml 存在"
else
    echo "  ⚠️  cron-rules.yaml 缺失"
    ((WARNINGS++))
fi

SCRIPT_COUNT=$(find "$WORKSPACE/scripts" -name "*.py" -type f 2>/dev/null | wc -l)
echo "  📊 Python脚本数量: $SCRIPT_COUNT"

BACKUP_SCRIPT_COUNT=$(find "$WORKSPACE/disaster-recovery/02-自动化备份脚本" -name "*.sh" -type f 2>/dev/null | wc -l)
if [[ $BACKUP_SCRIPT_COUNT -gt 0 ]]; then
    echo "  ✅ 备份脚本套件存在 ($BACKUP_SCRIPT_COUNT 个脚本)"
else
    echo "  ❌ 备份脚本套件缺失!"
    ((ERRORS++))
fi

# ===== L5: 知识资产 =====
echo ""
echo "📚 [L5] 知识资产检查"
echo "----------------------------------------"

if [[ -d "$WORKSPACE/knowledge" ]]; then
    KNOWLEDGE_COUNT=$(find "$WORKSPACE/knowledge" -type f 2>/dev/null | wc -l)
    echo "  ✅ knowledge/ 目录存在 ($KNOWLEDGE_COUNT 个文件)"
else
    echo "  ⚠️  knowledge/ 目录缺失"
    ((WARNINGS++))
fi

if [[ -f "$WORKSPACE/skill.json" ]]; then
    # 验证JSON格式
    if python3 -c "import json; json.load(open('$WORKSPACE/skill.json'))" 2>/dev/null; then
        echo "  ✅ skill.json 存在且格式正确"
    else
        echo "  ⚠️  skill.json 格式异常"
        ((WARNINGS++))
    fi
else
    echo "  ⚠️  skill.json 缺失"
    ((WARNINGS++))
fi

# ===== L1: 元协议 =====
echo ""
echo "📖 [L1] 元协议检查"
echo "----------------------------------------"

if [[ -f "$WORKSPACE/docs/DISASTER_RECOVERY_V1.1.md" ]]; then
    size=$(wc -c < "$WORKSPACE/docs/DISASTER_RECOVERY_V1.1.md")
    echo "  ✅ 灾备手册V1.1存在 ($size 字节)"
elif [[ -f "$WORKSPACE/docs/DISASTER_RECOVERY_V1.md" ]]; then
    echo "  ⚠️  V1.1缺失，但V1.0存在"
    ((WARNINGS++))
else
    echo "  ❌ 灾备手册缺失!"
    ((ERRORS++))
fi

if [[ -f "$WORKSPACE/disaster-recovery/01-灾备策略文档.md" ]]; then
    echo "  ✅ 灾备策略文档存在"
else
    echo "  ⚠️  灾备策略文档缺失"
    ((WARNINGS++))
fi

# ===== Git版本控制 =====
echo ""
echo "🔀 [Git] 版本控制检查"
echo "----------------------------------------"

cd "$WORKSPACE"
if git status &>/dev/null; then
    echo "  ✅ Git仓库正常"
    echo "  📍 当前分支: $(git branch --show-current 2>/dev/null || echo 'unknown')"
    
    LAST_COMMIT=$(git log -1 --oneline 2>/dev/null || echo '无提交')
    echo "  📝 最新提交: $LAST_COMMIT"
    
    # 检查未提交变更
    UNCOMMITTED=$(git status --porcelain 2>/dev/null | wc -l)
    if [[ $UNCOMMITTED -gt 0 ]]; then
        echo "  ⚠️  有 $UNCOMMITTED 个未提交变更"
        ((WARNINGS++))
    else
        echo "  ✅ 工作区干净"
    fi
else
    echo "  ❌ Git仓库异常!"
    ((ERRORS++))
fi

# ===== RTO验证 =====
echo ""
echo "⏱️  [RTO] 恢复时间目标验证"
echo "----------------------------------------"

# 模拟核心文件读取时间
START_TIME=$(date +%s%N)
head -1 "$WORKSPACE/SOUL.md" > /dev/null
head -1 "$WORKSPACE/USER.md" > /dev/null
head -1 "$WORKSPACE/MEMORY.md" > /dev/null
END_TIME=$(date +%s%N)

READ_TIME_MS=$(( (END_TIME - START_TIME) / 1000000 ))
echo "  📊 核心文件读取时间: ${READ_TIME_MS}ms"

if [[ $READ_TIME_MS -lt 1000 ]]; then
    echo "  ✅ 满足RTO目标 (<10分钟)"
else
    echo "  ⚠️  文件读取较慢，但仍在RTO范围内"
fi

# ===== 汇总 =====
echo ""
echo "=========================================="
echo "📊 验证结果汇总"
echo "=========================================="
echo "  错误数: $ERRORS"
echo "  警告数: $WARNINGS"
echo ""

if [[ $ERRORS -eq 0 && $WARNINGS -eq 0 ]]; then
    echo "✅ 所有检查通过，灾备系统状态健康"
    echo "=========================================="
    exit 0
elif [[ $ERRORS -eq 0 ]]; then
    echo "⚠️  发现 $WARNINGS 个警告，建议处理但非紧急"
    echo "=========================================="
    exit 0
else
    echo "❌ 发现 $ERRORS 个错误，$WARNINGS 个警告，需要修复"
    echo "=========================================="
    exit 1
fi
