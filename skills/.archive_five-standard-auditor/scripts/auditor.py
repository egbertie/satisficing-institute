#!/usr/bin/env python3
"""
Five-Standard Auditor - 5标准检验脚本
核心标准(S1-S5) + 增强指南(S6-S7)
"""

import sys
import re
import os
from datetime import datetime

# 5+2标准定义
STANDARDS = {
    # 核心标准 (必须达标)
    "S1": {
        "name": "全局考虑",
        "keywords": ["全局", "全覆盖", "全部工作区", "外部集成", "边界情况"],
        "threshold": 0.6,
        "weight": 0.20,
        "required": True
    },
    "S2": {
        "name": "系统考虑",
        "keywords": ["闭环", "输入→处理→输出", "故障处理", "边界定义"],
        "threshold": 0.5,
        "weight": 0.20,
        "required": True
    },
    "S3": {
        "name": "迭代机制",
        "keywords": ["PDCA", "迭代", "反馈收集", "优化触发", "版本历史"],
        "threshold": 0.5,
        "weight": 0.20,
        "required": True
    },
    "S4": {
        "name": "Skill化",
        "keywords": ["SKILL.md", "可安装", "可调用", "标准化接口"],
        "threshold": 0.8,
        "weight": 0.20,
        "required": True
    },
    "S5": {
        "name": "自动化",
        "keywords": ["自动", "cron", "定时", "监控", "脚本"],
        "threshold": 0.5,
        "weight": 0.20,
        "required": True
    },
    # 增强指南 (推荐但不强制)
    "S6": {
        "name": "认知谦逊",
        "keywords": ["标注来源", "置信度", "局限", "待验证"],
        "threshold": 0.5,
        "weight": 0.0,
        "required": False,
        "guide": True
    },
    "S7": {
        "name": "对抗验证",
        "keywords": ["反方观点", "失效场景", "替代方案", "缓解措施"],
        "threshold": 0.3,
        "weight": 0.0,
        "required": False,
        "guide": True
    }
}

# 达标线
PASS_THRESHOLD = 0.70

def check_standard(content, standard_id):
    """检查单个标准的达成率"""
    standard = STANDARDS[standard_id]
    keywords = standard["keywords"]
    
    matches = 0
    for kw in keywords:
        if re.search(kw, content, re.IGNORECASE):
            matches += 1
    
    score = matches / len(keywords) if keywords else 0
    return min(score, 1.0)

def audit_file(file_path):
    """检验单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 无法读取: {file_path} - {e}")
        return None
    
    results = {}
    total_score = 0
    total_weight = 0
    all_required_pass = True
    
    for sid, std in STANDARDS.items():
        score = check_standard(content, sid)
        results[sid] = {
            "score": score,
            "threshold": std["threshold"],
            "passed": score >= std["threshold"],
            "is_guide": std.get("guide", False)
        }
        
        if std["required"]:
            total_score += score * std["weight"]
            total_weight += std["weight"]
            if not results[sid]["passed"]:
                all_required_pass = False
    
    overall = total_score / total_weight if total_weight > 0 else 0
    passed = overall >= PASS_THRESHOLD and all_required_pass
    
    return {
        "path": file_path,
        "overall": overall,
        "passed": passed,
        "details": results
    }

def print_result(result):
    """打印检验结果"""
    if not result:
        return
    
    status = "✅" if result["passed"] else "❌"
    print(f"{status} {result['path']}")
    print(f"   综合得分: {result['overall']:.1%} (达标线: {PASS_THRESHOLD:.0%})")
    print(f"   各标准得分:")
    
    for sid, detail in result["details"].items():
        std = STANDARDS[sid]
        icon = "✅" if detail["passed"] else "❌"
        guide_tag = "[指南]" if detail["is_guide"] else "[核心]"
        print(f"     {icon} {sid}({std['name']}): {detail['score']:.0%} {guide_tag}")
    print()

def audit_all(directory):
    """批量检验目录下所有SKILL.md"""
    results = []
    passed = 0
    failed = 0
    
    for root, dirs, files in os.walk(directory):
        # 跳过隐藏目录和archive
        dirs[:] = [d for d in dirs if not d.startswith('.') and 'archive' not in d.lower()]
        
        for file in files:
            if file == "SKILL.md":
                file_path = os.path.join(root, file)
                result = audit_file(file_path)
                if result:
                    print_result(result)
                    results.append(result)
                    if result["passed"]:
                        passed += 1
                    else:
                        failed += 1
    
    print("=" * 70)
    print(f"检验完成: 总计 {len(results)} 个Skill")
    print(f"  ✅ 达标: {passed} ({passed/len(results):.0%})" if results else "  ✅ 达标: 0")
    print(f"  ❌ 未达标: {failed}")
    
    # 核心5标准达成率统计
    core_passed = sum(1 for r in results if all(
        r["details"][sid]["passed"] for sid in ["S1","S2","S3","S4","S5"]
    ))
    print(f"  核心5标准全达标: {core_passed}")
    
    return results

def self_audit():
    """自我检验（元检验）"""
    print("=" * 70)
    print("5标准检验器 - 元检验")
    print("=" * 70)
    
    script_path = os.path.abspath(__file__)
    result = audit_file(script_path.replace('.py', '_self_check.md'))
    
    if not result:
        # 直接检验自己
        with open(script_path, 'r') as f:
            content = f.read()
        
        print("检验脚本自身结构...")
        # 简化的自我检查
        checks = {
            "S1(全局)": bool(re.search(r'(全局|覆盖|全部)', content)),
            "S2(系统)": bool(re.search(r'(闭环|输入.*输出)', content)),
            "S3(迭代)": bool(re.search(r'(迭代|版本|优化)', content)),
            "S4(Skill化)": os.path.exists(script_path.replace('scripts/auditor.py', 'SKILL.md')),
            "S5(自动化)": bool(re.search(r'(cron|自动|定时)', content))
        }
        
        all_pass = all(checks.values())
        print(f"自检结果: {'✅ 通过' if all_pass else '❌ 部分未通过'}")
        for item, passed in checks.items():
            print(f"  {'✅' if passed else '❌'} {item}")
    
    return 0

def enhanced_check():
    """增强标准检查（S6+S7）"""
    print("=" * 70)
    print("增强标准检查 - S6认知谦逊 + S7对抗验证")
    print("=" * 70)
    print("【指南性质】推荐但不强制")
    print()
    
    skills_dir = "/root/.openclaw/workspace/skills"
    for root, dirs, files in os.walk(skills_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 'archive' not in d.lower()]
        
        for file in files:
            if file == "SKILL.md":
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                
                s6_score = check_standard(content, "S6")
                s7_score = check_standard(content, "S7")
                
                if s6_score < 0.5 or s7_score < 0.3:
                    print(f"📋 {os.path.basename(root)}")
                    print(f"   S6认知谦逊: {s6_score:.0%} {'✅' if s6_score >= 0.5 else '○'}")
                    print(f"   S7对抗验证: {s7_score:.0%} {'✅' if s7_score >= 0.3 else '○'}")
                    print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 auditor.py [audit <file>|audit-all <dir>|self-audit|enhanced-check]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "audit":
        if len(sys.argv) < 3:
            print("Usage: python3 auditor.py audit <file_path>")
            sys.exit(1)
        result = audit_file(sys.argv[2])
        print_result(result)
    
    elif command == "audit-all":
        if len(sys.argv) < 3:
            print("Usage: python3 auditor.py audit-all <directory>")
            sys.exit(1)
        audit_all(sys.argv[2])
    
    elif command == "self-audit":
        self_audit()
    
    elif command == "enhanced-check":
        enhanced_check()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
