# 担忧清单管理器 - 主运行脚本
# worry_runner.py

import os
import sys
import json
import yaml
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# 配置路径
SKILL_DIR = Path("/root/.openclaw/workspace/skills/worry-list-manager")
CONFIG_DIR = SKILL_DIR / "config"
DATA_DIR = SKILL_DIR / "data"
LOG_DIR = SKILL_DIR / "logs"

# 确保目录存在
for d in [DATA_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

WORRIES_FILE = DATA_DIR / "worries.json"
HISTORY_DIR = DATA_DIR / "history"
HISTORY_DIR.mkdir(exist_ok=True)

def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(LOG_DIR / "worry.log", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

def load_config() -> Dict:
    """加载配置"""
    config = {}
    for config_file in ["categories.yaml", "thresholds.yaml"]:
        path = CONFIG_DIR / config_file
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                config.update(yaml.safe_load(f) or {})
    return config

def load_worries() -> List[Dict]:
    """加载担忧列表"""
    if WORRIES_FILE.exists():
        with open(WORRIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_worries(worries: List[Dict]):
    """保存担忧列表"""
    # 备份旧数据
    if WORRIES_FILE.exists():
        backup_file = HISTORY_DIR / f"worries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        WORRIES_FILE.rename(backup_file)
    with open(WORRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(worries, f, ensure_ascii=False, indent=2)

def generate_id() -> str:
    """生成担忧ID"""
    prefix = "W"
    date_str = datetime.now().strftime("%y%m%d")
    worries = load_worries()
    today_count = sum(1 for w in worries if w.get("id", "").startswith(f"{prefix}{date_str}"))
    return f"{prefix}{date_str}{today_count+1:03d}"

def calculate_priority(impact: int, urgency: int, probability: int, config: Dict) -> str:
    """计算优先级"""
    weights = config.get("evaluation", {}).get("weights", {"impact": 0.4, "urgency": 0.4, "probability": 0.2})
    score = (impact * weights["impact"] + 
             urgency * weights["urgency"] + 
             probability * weights["probability"])
    
    if score >= 8:
        return "P0"
    elif score >= 6:
        return "P1"
    elif score >= 4:
        return "P2"
    else:
        return "P3"

def add_worry(content: str, category: str = "UNRESOLVED", source: str = "manual", 
              impact: int = 5, urgency: int = 5, probability: int = 5, 
              epistemic_status: str = "INFERRED", confidence: float = 0.5) -> str:
    """添加担忧"""
    config = load_config()
    worries = load_worries()
    
    worry_id = generate_id()
    priority = calculate_priority(impact, urgency, probability, config)
    
    worry = {
        "id": worry_id,
        "content": content,
        "category": category,
        "priority": priority,
        "source": source,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "impact": impact,
        "urgency": urgency,
        "probability": probability,
        "score": impact * 0.4 + urgency * 0.4 + probability * 0.2,
        "epistemic_status": epistemic_status,  # KNOWN/INFERRED/UNKNOWN
        "confidence": confidence,
        "evidence": [],
        "actions": [],
        "resolution": None,
        "feedback": None
    }
    
    worries.append(worry)
    save_worries(worries)
    log(f"✅ 添加担忧 [{priority}] {worry_id}: {content[:50]}...")
    return worry_id

def list_worries(priority: Optional[str] = None, status: Optional[str] = None, category: Optional[str] = None) -> List[Dict]:
    """列出担忧"""
    worries = load_worries()
    
    if priority:
        worries = [w for w in worries if w.get("priority") == priority]
    if status:
        worries = [w for w in worries if w.get("status") == status]
    if category:
        worries = [w for w in worries if w.get("category") == category]
    
    # 按优先级和时间排序
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    worries.sort(key=lambda x: (priority_order.get(x.get("priority", "P3"), 3), x.get("created_at", "")), reverse=False)
    
    return worries

def resolve_worry(worry_id: str, resolution: str, feedback: Optional[str] = None):
    """解决担忧"""
    worries = load_worries()
    for w in worries:
        if w.get("id") == worry_id:
            w["status"] = "resolved"
            w["resolution"] = resolution
            w["resolved_at"] = datetime.now().isoformat()
            w["feedback"] = feedback
            w["updated_at"] = datetime.now().isoformat()
            save_worries(worries)
            log(f"✅ 解决担忧 {worry_id}: {resolution[:50]}...")
            return True
    log(f"❌ 未找到担忧 {worry_id}")
    return False

def scan_system() -> List[Dict]:
    """扫描系统生成担忧"""
    config = load_config()
    new_worries = []
    
    # 模拟系统扫描 - 实际应用中应检查真实系统状态
    thresholds = config.get("alerting", {})
    
    # 检查资源状态
    # 这里应该调用实际的系统监控API
    # 示例：检查磁盘空间
    try:
        import shutil
        stat = shutil.disk_usage("/")
        usage_percent = stat.used / stat.total
        
        if usage_percent > thresholds.get("storage_critical", 0.9):
            new_worries.append({
                "content": f"存储空间严重告警: 使用率 {usage_percent*100:.1f}%",
                "category": "RESOURCE",
                "priority": "P0",
                "source": "system_scan"
            })
        elif usage_percent > thresholds.get("storage_high", 0.8):
            new_worries.append({
                "content": f"存储空间告警: 使用率 {usage_percent*100:.1f}%",
                "category": "RESOURCE",
                "priority": "P1",
                "source": "system_scan"
            })
    except Exception as e:
        log(f"扫描存储时出错: {e}")
    
    # 检查担忧清单本身的状态
    worries = load_worries()
    active_worries = [w for w in worries if w.get("status") == "active"]
    overdue_worries = [w for w in active_worries if datetime.fromisoformat(w.get("due_date", "2000-01-01")) < datetime.now()]
    
    if len(overdue_worries) > 0:
        overdue_rate = len(overdue_worries) / max(len(active_worries), 1)
        if overdue_rate > thresholds.get("overdue_rate_threshold", 0.2):
            new_worries.append({
                "content": f"担忧清单逾期率过高: {overdue_rate*100:.1f}% ({len(overdue_worries)}个)",
                "category": "UNRESOLVED",
                "priority": "P1",
                "source": "system_scan"
            })
    
    # 添加扫描到的担忧
    for nw in new_worries:
        add_worry(**nw)
    
    log(f"🔍 系统扫描完成，发现 {len(new_worries)} 个新担忧")
    return new_worries

def generate_report(period: str = "daily") -> str:
    """生成报告"""
    worries = load_worries()
    now = datetime.now()
    
    if period == "daily":
        # 日报 - 过去24小时
        cutoff = now - timedelta(days=1)
        title = f"📊 担忧日报 ({now.strftime('%Y-%m-%d')})"
    elif period == "weekly":
        # 周报 - 过去7天
        cutoff = now - timedelta(days=7)
        title = f"📊 担忧周报 ({(now-timedelta(days=7)).strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')})"
    else:
        cutoff = now - timedelta(days=1)
        title = f"📊 担忧报告"
    
    # 统计数据
    all_worries = worries
    active_worries = [w for w in all_worries if w.get("status") == "active"]
    resolved_worries = [w for w in all_worries if w.get("status") == "resolved"]
    period_worries = [w for w in all_worries if datetime.fromisoformat(w.get("created_at", "2000-01-01")) >= cutoff]
    
    priority_counts = {}
    for p in ["P0", "P1", "P2", "P3"]:
        priority_counts[p] = len([w for w in active_worries if w.get("priority") == p])
    
    # 生成报告
    lines = [
        title,
        "=" * 50,
        "",
        "## 📈 统计概览",
        f"- 活跃担忧: {len(active_worries)}",
        f"- 本周期新增: {len(period_worries)}",
        f"- 已解决: {len(resolved_worries)}",
        "",
        "### 按优先级分布",
        f"- 🔴 P0(紧急): {priority_counts['P0']}",
        f"- 🟠 P1(高): {priority_counts['P1']}",
        f"- 🟡 P2(中): {priority_counts['P2']}",
        f"- 🟢 P3(低): {priority_counts['P3']}",
        "",
    ]
    
    # 高优先级担忧详情
    high_priority = [w for w in active_worries if w.get("priority") in ["P0", "P1"]]
    if high_priority:
        lines.extend([
            "## 🔥 需关注的高优先级担忧",
            ""
        ])
        for w in high_priority[:10]:  # 最多显示10个
            lines.append(f"### {w['id']} [{w['priority']}]")
            lines.append(f"- 内容: {w['content']}")
            lines.append(f"- 分类: {w['category']}")
            lines.append(f"- 创建: {w['created_at'][:10]}")
            lines.append(f"- 置信度: {w.get('confidence', 0.5)*100:.0f}%")
            lines.append("")
    
    # 建议
    lines.extend([
        "## 💡 行动建议",
        ""
    ])
    if priority_counts["P0"] > 0:
        lines.append(f"⚠️ 有 {priority_counts['P0']} 个P0级紧急担忧需要立即处理")
    if priority_counts["P1"] > 3:
        lines.append(f"📋 P1级担忧较多({priority_counts['P1']}个)，建议安排专项时间处理")
    if len(active_worries) == 0:
        lines.append("✅ 当前无活跃担忧，系统状态良好")
    
    lines.append("")
    lines.append("---")
    lines.append(f"*生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')}*")
    
    report = "\n".join(lines)
    
    # 保存报告
    report_file = DATA_DIR / f"report_{period}_{now.strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    log(f"📊 生成{period}报告: {report_file}")
    return report

def push_alert():
    """推送晨间简报"""
    report = generate_report("daily")
    
    # 保存为最新简报
    brief_file = DATA_DIR / "latest_brief.md"
    with open(brief_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    # 输出到控制台（实际应用中可集成消息推送）
    print("\n" + "=" * 60)
    print("📢 晨间担忧简报")
    print("=" * 60)
    print(report)
    print("=" * 60 + "\n")
    
    log("📢 已推送晨间简报")
    return report

def evaluate_accuracy() -> Dict:
    """S5: 评估准确性 - 误报/漏报检查"""
    worries = load_worries()
    resolved = [w for w in worries if w.get("status") == "resolved"]
    
    if not resolved:
        return {"message": "尚无已解决的担忧用于评估"}
    
    # 统计反馈
    false_positives = [w for w in resolved if w.get("feedback") == "false_positive"]
    false_negatives = [w for w in resolved if w.get("feedback") == "false_negative"]
    accurate = [w for w in resolved if w.get("feedback") not in ["false_positive", "false_negative", None]]
    
    total = len(resolved)
    fp_rate = len(false_positives) / total if total > 0 else 0
    fn_rate = len(false_negatives) / total if total > 0 else 0
    accuracy = len(accurate) / total if total > 0 else 0
    
    result = {
        "total_resolved": total,
        "false_positives": len(false_positives),
        "false_negatives": len(false_negatives),
        "accurate": len(accurate),
        "false_positive_rate": fp_rate,
        "false_negative_rate": fn_rate,
        "accuracy_rate": accuracy,
        "assessment": "良好" if accuracy >= 0.85 else "需改进"
    }
    
    log(f"📊 准确性评估: 准确率 {accuracy*100:.1f}%, 误报率 {fp_rate*100:.1f}%, 漏报率 {fn_rate*100:.1f}%")
    return result

def adversarial_test():
    """S7: 对抗测试 - 模拟已知风险测试发现能力"""
    log("🔴 开始对抗测试...")
    
    test_cases = [
        {"content": "磁盘空间即将耗尽，剩余不足5%", "expected_category": "RESOURCE", "expected_priority": "P0"},
        {"content": "项目截止日期明天，核心功能尚未完成", "expected_category": "DEADLINE", "expected_priority": "P0"},
        {"content": "发现一个潜在的客户需求未跟进", "expected_category": "OPPORTUNITY", "expected_priority": "P2"},
    ]
    
    results = []
    for test in test_cases:
        # 模拟添加担忧
        worry_id = add_worry(
            content=test["content"],
            category=test["expected_category"],
            source="adversarial_test"
        )
        
        worries = load_worries()
        worry = next((w for w in worries if w["id"] == worry_id), None)
        
        passed = (
            worry and 
            worry.get("category") == test["expected_category"] and
            worry.get("priority") == test["expected_priority"]
        )
        
        results.append({
            "test": test["content"][:30],
            "passed": passed,
            "expected_priority": test["expected_priority"],
            "actual_priority": worry.get("priority") if worry else None
        })
        
        # 清理测试数据
        if worry:
            worry["status"] = "archived"
            save_worries(worries)
    
    passed_count = sum(1 for r in results if r["passed"])
    log(f"🔴 对抗测试完成: {passed_count}/{len(results)} 通过")
    
    return {
        "total_tests": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "results": results
    }

def main():
    parser = argparse.ArgumentParser(description="担忧清单管理器")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加担忧")
    add_parser.add_argument("--content", "-c", required=True, help="担忧内容")
    add_parser.add_argument("--category", "-t", default="UNRESOLVED", help="分类")
    add_parser.add_argument("--source", "-s", default="manual", help="来源")
    add_parser.add_argument("--impact", "-i", type=int, default=5, help="影响度(1-10)")
    add_parser.add_argument("--urgency", "-u", type=int, default=5, help="紧急度(1-10)")
    add_parser.add_argument("--probability", "-p", type=int, default=5, help="可能性(1-10)")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出担忧")
    list_parser.add_argument("--priority", help="按优先级筛选")
    list_parser.add_argument("--status", help="按状态筛选")
    list_parser.add_argument("--category", help="按分类筛选")
    
    # resolve 命令
    resolve_parser = subparsers.add_parser("resolve", help="解决担忧")
    resolve_parser.add_argument("id", help="担忧ID")
    resolve_parser.add_argument("--resolution", "-r", required=True, help="解决方案")
    resolve_parser.add_argument("--feedback", "-f", help="反馈(true_positive/false_positive/false_negative)")
    
    # scan 命令
    subparsers.add_parser("scan", help="系统扫描")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成报告")
    report_parser.add_argument("--period", "-p", default="daily", choices=["daily", "weekly"], help="报告周期")
    
    # weekly 命令
    subparsers.add_parser("weekly", help="生成周报")
    
    # push 命令
    subparsers.add_parser("push", help="推送简报")
    
    # evaluate 命令 (S5)
    subparsers.add_parser("evaluate", help="评估准确性")
    
    # test 命令 (S7)
    subparsers.add_parser("test", help="对抗测试")
    
    args = parser.parse_args()
    
    if args.command == "add":
        worry_id = add_worry(
            content=args.content,
            category=args.category,
            source=args.source,
            impact=args.impact,
            urgency=args.urgency,
            probability=args.probability
        )
        print(f"✅ 已添加担忧: {worry_id}")
    
    elif args.command == "list":
        worries = list_worries(args.priority, args.status, args.category)
        print(f"\n📋 担忧清单 ({len(worries)} 项)\n")
        print("-" * 80)
        print(f"{'ID':<12} {'优先级':<8} {'状态':<8} {'分类':<12} {'内容':<30}")
        print("-" * 80)
        for w in worries:
            content = w['content'][:28] + "..." if len(w['content']) > 30 else w['content']
            print(f"{w['id']:<12} {w['priority']:<8} {w['status']:<8} {w['category']:<12} {content:<30}")
        print("-" * 80)
    
    elif args.command == "resolve":
        if resolve_worry(args.id, args.resolution, args.feedback):
            print(f"✅ 已解决担忧: {args.id}")
        else:
            print(f"❌ 未找到担忧: {args.id}")
    
    elif args.command == "scan":
        new_worries = scan_system()
        print(f"🔍 扫描完成，发现 {len(new_worries)} 个新担忧")
    
    elif args.command == "report":
        report = generate_report(args.period)
        print(report)
    
    elif args.command == "weekly":
        report = generate_report("weekly")
        print(report)
    
    elif args.command == "push":
        push_alert()
    
    elif args.command == "evaluate":
        result = evaluate_accuracy()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == "test":
        result = adversarial_test()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
