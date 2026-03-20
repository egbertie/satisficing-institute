#!/usr/bin/env python3
"""
Seven-Standard Auditor
7标准自动检验系统
"""

import sys
import os
import re
import json
from datetime import datetime

# 7标准定义
STANDARDS = {
    "S1": {
        "name": "全局考虑 (Global Coverage)",
        "weight": 0.15,
        "threshold": 0.60,
        "checks": [
            "覆盖全部工作维度",
            "外部集成考虑",
            "边界情况处理",
            "环境适配"
        ]
    },
    "S2": {
        "name": "系统考虑 (System Closure)",
        "weight": 0.15,
        "threshold": 0.50,
        "checks": [
            "输入→处理→输出→反馈闭环",
            "故障处理机制",
            "边界定义清晰"
        ]
    },
    "S3": {
        "name": "迭代机制 (Iteration)",
        "weight": 0.15,
        "threshold": 0.50,
        "checks": [
            "Plan-Do-Check-Act循环",
            "反馈收集机制",
            "优化触发条件"
        ]
    },
    "S4": {
        "name": "Skill化 (Standardization)",
        "weight": 0.15,
        "threshold": 0.80,
        "checks": [
            "SKILL.md格式规范",
            "可安装可调用",
            "标准化接口"
        ]
    },
    "S5": {
        "name": "自动化 (Automation)",
        "weight": 0.15,
        "threshold": 0.50,
        "checks": [
            "自动检验能力",
            "Cron监控",
            "自动报告"
        ]
    },
    "S6": {
        "name": "认知谦逊 (Humility)",
        "weight": 0.15,
        "threshold": 0.50,
        "checks": [
            "标注来源",
            "标注置信度",
            "承认局限"
        ]
    },
    "S7": {
        "name": "对抗验证 (Advocacy)",
        "weight": 0.10,
        "threshold": 0.30,
        "checks": [
            "反方观点",
            "失效场景",
            "替代方案"
        ]
    }
}

OVERALL_THRESHOLD = 0.70

def check_s1_global(content):
    """检查S1全局考虑"""
    score = 0
    evidence = []
    
    # 检查是否提及多个维度
    dimensions = ["人", "事", "物", "环境", "外部", "边界"]
    found_dims = [d for d in dimensions if d in content]
    if len(found_dims) >= 3:
        score += 0.4
        evidence.append(f"覆盖维度: {', '.join(found_dims)}")
    elif len(found_dims) >= 1:
        score += 0.2
        evidence.append(f"覆盖维度: {', '.join(found_dims)}")
    
    # 检查外部集成
    if any(kw in content for kw in ["外部", "集成", "API", "同步", "第三方"]):
        score += 0.3
        evidence.append("提及外部集成")
    
    # 检查边界处理
    if any(kw in content for kw in ["边界", "异常", "错误处理", "容错", "降级"]):
        score += 0.3
        evidence.append("提及边界处理")
    
    return min(score, 1.0), evidence

def check_s2_system(content):
    """检查S2系统闭环"""
    score = 0
    evidence = []
    
    # 检查闭环关键词
    if any(kw in content for kw in ["闭环", "反馈", "输入", "输出", "PDCA"]):
        score += 0.4
        evidence.append("提及闭环/反馈")
    
    # 检查故障处理
    if any(kw in content for kw in ["故障", "错误", "异常", "恢复", "回滚"]):
        score += 0.3
        evidence.append("提及故障处理")
    
    # 检查边界定义
    if any(kw in content for kw in ["范围", "边界", "适用", "不适用"]):
        score += 0.3
        evidence.append("提及边界定义")
    
    return min(score, 1.0), evidence

def check_s3_iteration(content):
    """检查S3迭代机制"""
    score = 0
    evidence = []
    
    # 检查迭代关键词
    if any(kw in content for kw in ["迭代", "优化", "改进", "PDCA", "复盘", "review"]):
        score += 0.4
        evidence.append("提及迭代机制")
    
    # 检查反馈收集
    if any(kw in content for kw in ["反馈", "收集", "评估", "度量"]):
        score += 0.3
        evidence.append("提及反馈收集")
    
    # 检查触发条件
    if any(kw in content for kw in ["触发", "条件", "阈值", "阈值"]):
        score += 0.3
        evidence.append("提及触发条件")
    
    return min(score, 1.0), evidence

def check_s4_skill(content, file_path):
    """检查S4 Skill化"""
    score = 0
    evidence = []
    
    # 检查SKILL.md格式
    if "SKILL.md" in file_path or "skill" in file_path.lower():
        score += 0.3
        evidence.append("文件名为SKILL.md格式")
    
    # 检查标准结构
    required_sections = ["Purpose", "Commands"]
    found_sections = [s for s in required_sections if s in content]
    score += len(found_sections) * 0.2
    evidence.append(f"包含章节: {', '.join(found_sections)}")
    
    # 检查标准化接口
    if any(kw in content for kw in ["Command", "Usage", "接口", "API"]):
        score += 0.3
        evidence.append("提及标准化接口")
    
    return min(score, 1.0), evidence

def check_s5_automation(content, file_dir):
    """检查S5自动化"""
    score = 0
    evidence = []
    
    # 检查脚本存在
    scripts_dir = os.path.join(file_dir, "scripts")
    if os.path.exists(scripts_dir) and os.listdir(scripts_dir):
        score += 0.4
        evidence.append("scripts目录存在且非空")
    
    # 检查cron配置
    cron_file = os.path.join(file_dir, "cron.json")
    if os.path.exists(cron_file):
        score += 0.3
        evidence.append("cron.json存在")
    
    # 检查自动报告
    if any(kw in content for kw in ["自动", "报告", "Report", "定时"]):
        score += 0.3
        evidence.append("提及自动报告")
    
    return min(score, 1.0), evidence

def check_s6_humility(content):
    """检查S6认知谦逊"""
    score = 0
    evidence = []
    
    # 检查认知标签
    tags = ["[KNOWN]", "[INFERRED]", "[UNKNOWN]", "置信度", "来源"]
    found_tags = [t for t in tags if t in content]
    if len(found_tags) >= 2:
        score += 0.5
        evidence.append(f"使用认知标签: {', '.join(found_tags)}")
    elif len(found_tags) >= 1:
        score += 0.3
        evidence.append(f"使用认知标签: {', '.join(found_tags)}")
    
    # 检查局限性承认
    if any(kw in content for kw in ["局限", "限制", "待验证", "未完成", "已知问题"]):
        score += 0.5
        evidence.append("承认局限性")
    
    return min(score, 1.0), evidence

def check_s7_advocacy(content):
    """检查S7对抗验证"""
    score = 0
    evidence = []
    
    # 检查反方观点
    if any(kw in content for kw in ["反方", "Devil", "反对", "质疑", "挑战"]):
        score += 0.4
        evidence.append("提及反方观点")
    
    # 检查失效场景
    if any(kw in content for kw in ["失效", "失败", "不适用", "风险", "问题"]):
        score += 0.3
        evidence.append("提及失效场景")
    
    # 检查替代方案
    if any(kw in content for kw in ["替代", "备选", "或者", "另一种"]):
        score += 0.3
        evidence.append("提及替代方案")
    
    return min(score, 1.0), evidence

def audit_file(file_path):
    """检验单个文件"""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    file_dir = os.path.dirname(file_path)
    
    # 执行7项检查
    results = {
        "S1": check_s1_global(content),
        "S2": check_s2_system(content),
        "S3": check_s3_iteration(content),
        "S4": check_s4_skill(content, file_path),
        "S5": check_s5_automation(content, file_dir),
        "S6": check_s6_humility(content),
        "S7": check_s7_advocacy(content)
    }
    
    # 计算加权总分
    total_score = 0
    for std_id, (score, _) in results.items():
        total_score += score * STANDARDS[std_id]["weight"]
    
    # 判断是否达标
    passed = total_score >= OVERALL_THRESHOLD
    
    return {
        "file": file_path,
        "total_score": round(total_score, 2),
        "passed": passed,
        "details": {std_id: {"score": round(score, 2), "threshold": STANDARDS[std_id]["threshold"], "evidence": evidence} 
                   for std_id, (score, evidence) in results.items()}
    }

def audit_directory(directory):
    """批量检验目录"""
    results = []
    
    for root, dirs, files in os.walk(directory):
        # 跳过backups目录
        if "backups" in root:
            continue
            
        for file in files:
            if file.endswith(".md") or file.endswith(".json"):
                file_path = os.path.join(root, file)
                result = audit_file(file_path)
                if result:
                    results.append(result)
    
    return results

def generate_report(results):
    """生成检验报告"""
    timestamp = datetime.now().isoformat()
    
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    pass_rate = passed_count / total_count if total_count > 0 else 0
    
    print("=" * 70)
    print(f"[7标准检验报告] 生成时间: {timestamp}")
    print("=" * 70)
    print(f"\n总体统计:")
    print(f"  检验文件数: {total_count}")
    print(f"  达标文件数: {passed_count}")
    print(f"  达标率: {pass_rate*100:.1f}%")
    print(f"  目标达标率: {OVERALL_THRESHOLD*100:.0f}%")
    
    print(f"\n详细结果:")
    for result in results:
        status = "✅" if result["passed"] else "❌"
        print(f"\n{status} {result['file']}")
        print(f"   综合得分: {result['total_score']*100:.1f}%")
        print(f"   各标准得分:")
        for std_id, detail in result["details"].items():
            std_name = STANDARDS[std_id]["name"]
            score_pct = detail["score"] * 100
            threshold_pct = detail["threshold"] * 100
            std_status = "✅" if detail["score"] >= detail["threshold"] else "❌"
            print(f"     {std_status} {std_id}: {score_pct:.0f}% (阈值: {threshold_pct:.0f}%)")
    
    print("\n" + "=" * 70)
    
    return pass_rate

def audit_self():
    """7标准自我检验（元检验）"""
    print("[元检验] 检验7标准检验Skill自身...")
    
    skill_path = "/root/.openclaw/workspace/skills/seven-standard-auditor/SKILL.md"
    result = audit_file(skill_path)
    
    if result:
        print(f"\n7标准检验Skill自身得分: {result['total_score']*100:.1f}%")
        print(f"达标状态: {'✅ 通过' if result['passed'] else '❌ 未通过'}")
        
        # 特别输出元悖论信息
        s7_score = result["details"]["S7"]["score"]
        if s7_score == 0:
            print("\n[注意] S7对抗验证为0% - 7标准检验Skill自身缺少反方观点")
            print("      这是'标准悖论'的一部分")
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 auditor.py [audit|audit-all|report|self-audit] [path]")
        print("  audit [file]     - 检验单个文件")
        print("  audit-all [dir]  - 批量检验目录")
        print("  self-audit       - 7标准自我检验")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "audit":
        if len(sys.argv) < 3:
            print("请指定文件路径")
            sys.exit(1)
        result = audit_file(sys.argv[2])
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("文件不存在")
            sys.exit(1)
    
    elif command == "audit-all":
        directory = sys.argv[2] if len(sys.argv) > 2 else "/root/.openclaw/workspace"
        results = audit_directory(directory)
        generate_report(results)
    
    elif command == "self-audit":
        audit_self()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
