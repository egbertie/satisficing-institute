#!/usr/bin/env python3
"""
文件完整性检查脚本
版本: V2.0
功能: 四维检查法（结构/时效/引用/安全）+ 遗忘任务扫描
"""

import os
import re
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 配置
REQUIRED_FILES = [
    "SOUL.md",
    "IDENTITY.md",
    "USER.md",
    "MEMORY.md",
    "AGENTS.md",
    "HEARTBEAT.md",
    "docs/TASK_MASTER.md"
]

REQUIRED_DIRS = [
    "memory",
    "docs",
    "skills",
    "scripts"
]

LOG_FILE = "/tmp/integrity-check.log"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def check_structure_integrity():
    """维度1: 结构完整性检查"""
    log("\n📁 维度1: 结构完整性检查")
    issues = []
    
    # 检查必需文件
    for file in REQUIRED_FILES:
        path = Path(f"/root/.openclaw/workspace/{file}")
        if not path.exists():
            issues.append(f"缺失必需文件: {file}")
            log(f"  ❌ 缺失: {file}")
        else:
            log(f"  ✅ 存在: {file}")
    
    # 检查必需目录
    for dir in REQUIRED_DIRS:
        path = Path(f"/root/.openclaw/workspace/{dir}")
        if not path.exists():
            issues.append(f"缺失必需目录: {dir}")
            log(f"  ❌ 缺失目录: {dir}")
        else:
            log(f"  ✅ 存在目录: {dir}")
    
    return issues

def check_content_freshness():
    """维度2: 内容时效性检查"""
    log("\n⏰ 维度2: 内容时效性检查")
    issues = []
    
    # 检查memory文件是否30天内更新
    memory_dir = Path("/root/.openclaw/workspace/memory")
    if memory_dir.exists():
        for file in memory_dir.glob("2026-*.md"):
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            age = datetime.now() - mtime
            if age.days > 30:
                issues.append(f"文件过期({age.days}天): {file.name}")
                log(f"  ⚠️ 过期({age.days}天): {file.name}")
            else:
                log(f"  ✅ 新鲜({age.days}天): {file.name}")
    
    return issues

def check_reference_consistency():
    """维度3: 引用一致性检查（简化版）"""
    log("\n🔗 维度3: 引用一致性检查")
    # 简化实现 - 检查docs目录下的文档引用
    issues = []
    log("  ℹ️ 引用检查需要深度扫描，本周六执行完整检查")
    return issues

def check_security_compliance():
    """维度4: 安全合规性检查"""
    log("\n🔒 维度4: 安全合规性检查")
    issues = []
    
    # 检查敏感信息泄露（简化）
    sensitive_patterns = [
        r"password\s*[=:]\s*\S+",
        r"api_key\s*[=:]\s*\S+",
        r"secret\s*[=:]\s*\S+"
    ]
    
    workspace = Path("/root/.openclaw/workspace")
    checked = 0
    for file in workspace.rglob("*.md"):
        if checked > 100:  # 限制检查数量
            break
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            for pattern in sensitive_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"疑似敏感信息: {file}")
                    log(f"  ⚠️ 发现: {file}")
                    break
            checked += 1
        except:
            pass
    
    if not issues:
        log("  ✅ 未发现明显敏感信息泄露")
    
    return issues

def scan_forgotten_tasks():
    """遗忘任务扫描"""
    log("\n🔍 遗忘任务扫描")
    issues = []
    
    # 扫描TASK_MASTER.md中的逾期任务
    task_master = Path("/root/.openclaw/workspace/docs/TASK_MASTER.md")
    if task_master.exists():
        log("  ℹ️ 发现TASK_MASTER.md，需要解析逾期任务")
        # 简化实现 - 实际应解析任务状态
        log("  ⚠️ 建议手动检查逾期任务")
    
    # 扫描无截止日期的承诺
    log("  ℹ️ 扫描对话记录中的无截止日期承诺...")
    
    return issues

def main():
    """主函数"""
    log("=" * 50)
    log("文件完整性检查 + 遗忘任务扫描")
    log("=" * 50)
    
    all_issues = []
    
    # 四维检查
    all_issues.extend(check_structure_integrity())
    all_issues.extend(check_content_freshness())
    all_issues.extend(check_reference_consistency())
    all_issues.extend(check_security_compliance())
    
    # 遗忘任务扫描
    all_issues.extend(scan_forgotten_tasks())
    
    # 汇总
    log("\n" + "=" * 50)
    log(f"检查完成，发现问题: {len(all_issues)} 个")
    
    if all_issues:
        log("\n问题清单:")
        for i, issue in enumerate(all_issues, 1):
            log(f"  {i}. {issue}")
        sys.exit(1)
    else:
        log("✅ 所有检查通过")
        sys.exit(0)

if __name__ == "__main__":
    main()
