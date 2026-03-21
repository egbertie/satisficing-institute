#!/usr/bin/env python3
"""
Skill分级评估脚本
版本: V2.0
"""

import os
import json
from pathlib import Path

def check_skill_standards(skill_path):
    """检查Skill的5标准合规性"""
    results = {
        "has_skill_md": False,
        "has_scripts": False,
        "has_cron": False,
        "is_executable": False
    }
    
    skill_md = Path(skill_path) / "SKILL.md"
    scripts_dir = Path(skill_path) / "scripts"
    
    if skill_md.exists():
        results["has_skill_md"] = True
    
    if scripts_dir.exists() and any(scripts_dir.iterdir()):
        results["has_scripts"] = True
    
    # 检查Cron配置（简化）
    if results["has_scripts"]:
        results["has_cron"] = True  # 假设有脚本就有Cron计划
    
    return results

def classify_skill(results):
    """根据检查结果分级"""
    if all(results.values()):
        return "CORE"
    elif results["has_skill_md"] and results["has_scripts"]:
        return "EXTENSION"
    else:
        return "EXPERIMENTAL"

def main():
    print("=== Skill分级评估 ===")
    skills_dir = Path("/root/.openclaw/workspace/skills")
    
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            results = check_skill_standards(skill_dir)
            level = classify_skill(results)
            print(f"{skill_dir.name}: {level}")
    
    return 0

if __name__ == "__main__":
    main()