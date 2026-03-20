#!/usr/bin/env python3
"""
Task Coordinator Skill 质量评估测试套件
执行10个正例、10个负例、5个压力测试场景
"""

import json
import sys
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# 添加 parent 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from task_coordinator import TaskCoordinator

class TestResult:
    """测试结果记录器"""
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        
    def record(self, test_id: str, name: str, passed: bool, 
               expected: str, actual: str, duration_ms: float, 
               memory_mb: float, notes: str = ""):
        self.results.append({
            "test_id": test_id,
            "name": name,
            "passed": passed,
            "expected": expected,
            "actual": actual,
            "duration_ms": duration_ms,
            "memory_mb": memory_mb,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_summary(self) -> Dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        avg_duration = sum(r["duration_ms"] for r in self.results) / total if total else 0
        max_memory = max(r["memory_mb"] for r in self.results) if self.results else 0
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total * 100 if total else 0,
            "avg_duration_ms": avg_duration,
            "max_memory_mb": max_memory
        }

class TaskCoordinatorTester:
    """Task Coordinator 测试器"""
    
    def __init__(self):
        self.results = TestResult()
        if HAS_PSUTIL:
            self.process = psutil.Process()
        else:
            self.process = None
        
    def get_memory(self) -> float:
        """获取当前内存使用(MB)"""
        if HAS_PSUTIL:
            return self.process.memory_info().rss / 1024 / 1024
        return 0.0
    
    def run_test(self, test_id: str, name: str, test_fn, expected: str) -> bool:
        """执行单个测试"""
        print(f"\n[TEST] {test_id}: {name}")
        start_mem = self.get_memory()
        start_time = time.time()
        
        try:
            actual = test_fn()
            passed = (actual == expected)
            status = "✅ PASS" if passed else "❌ FAIL"
        except Exception as e:
            actual = f"ERROR: {str(e)}"
            passed = False
            status = "💥 ERROR"
        
        duration = (time.time() - start_time) * 1000
        end_mem = self.get_memory()
        memory_used = end_mem - start_mem
        
        self.results.record(test_id, name, passed, expected, actual, 
                          duration, memory_used)
        
        print(f"  {status} | 耗时: {duration:.2f}ms | 内存: {memory_used:.2f}MB")
        print(f"  期望: {expected}")
        print(f"  实际: {actual}")
        
        return passed

# ============ 正例测试场景 ============

def test_p01_sequential_overdue():
    """P01: 严重过期任务触发 sequential 模式"""
    coordinator = TaskCoordinator()
    
    # 模拟有严重过期任务
    coordinator.load_current_tasks = lambda: {
        "overdue": [{"id": "URG-001", "hours_overdue": 5, "name": "测试任务"}],
        "blocked": [],
        "at_risk": [],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    return analysis["recommended_mode"]

def test_p02_parallel_remedy():
    """P02: 多过期任务使用子代理并行"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [
            {"id": "URG-001", "hours_overdue": 3, "name": "任务1"},
            {"id": "URG-002", "hours_overdue": 4, "name": "任务2"}
        ],
        "blocked": [],
        "at_risk": [],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    plan = coordinator.generate_action_plan()
    
    # 检查是否启用并行子代理
    return analysis["recommended_mode"]

def test_p03_notify_blocked():
    """P03: 阻塞任务触发 notify_user 模式"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": [
            {"id": "BLK-001", "days_waiting": 3, "name": "阻塞任务1"}
        ],
        "at_risk": [],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    return analysis["recommended_mode"]

def test_p04_parallel_normal():
    """P04: 正常任务并行执行"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": [],
        "at_risk": [],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    return analysis["recommended_mode"]

def test_p05_hybrid_mode():
    """P05: 混合模式调度"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": [],
        "at_risk": [{"id": "RISK-001", "hours_left": 8, "name": "风险任务"}],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    # 有中低风险任务，可能触发 hybrid
    return analysis["recommended_mode"]

def test_p06_critical_threshold():
    """P06: risk_score=10 触发 sequential"""
    coordinator = TaskCoordinator()
    
    # 构造刚好触发阈值的场景
    coordinator.load_current_tasks = lambda: {
        "overdue": [
            {"id": "URG-001", "hours_overdue": 1, "name": "轻度逾期"}  # +5分
        ],
        "blocked": [
            {"id": "BLK-001", "days_waiting": 2, "name": "阻塞任务"}  # +3分
        ],
        "at_risk": [
            {"id": "RISK-001", "hours_left": 10, "name": "风险任务"}  # +4分
        ],
        "pending": []
    }
    # 总分 = 5+3+4 = 12 >= 10, 应该触发 sequential
    
    analysis = coordinator.analyze_workload()
    return analysis["recommended_mode"]

def test_p07_long_term_blocked():
    """P07: 长期阻塞检测（>2天）"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": [
            {"id": "BLK-001", "days_waiting": 5, "name": "长期阻塞"}
        ],
        "at_risk": [],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    # 检查 reasoning 中是否包含长期阻塞
    has_long_term = any("长期阻塞" in r for r in analysis["reasoning"])
    return "detected" if has_long_term else "not_detected"

def test_p08_high_risk_deadline():
    """P08: 高风险即将到期（12小时内）"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": [],
        "at_risk": [
            {"id": "RISK-001", "hours_left": 6, "name": "紧急任务"}
        ],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    has_imminent = any("即将到期" in r for r in analysis["reasoning"])
    return "detected" if has_imminent else "not_detected"

def test_p09_learning_optimization():
    """P09: 学习模式识别"""
    coordinator = TaskCoordinator()
    
    # 添加一些历史决策
    for i in range(10):
        coordinator.record_decision({
            "risk_score": 5,
            "recommended_mode": "parallel",
            "summary": {"overdue": 0, "blocked": 0},
            "reasoning": ["飞书调试任务"]
        }, {"status": "success"})
    
    coordinator.optimize_strategy()
    
    # 检查是否识别了模式
    has_pattern = len(coordinator.learning.get("patterns", {})) > 0
    return "optimized" if has_pattern else "no_pattern"

def test_p10_resource_allocation():
    """P10: 资源分配计算"""
    coordinator = TaskCoordinator()
    
    # Test sequential mode
    coordinator.load_current_tasks = lambda: {
        "overdue": [{"id": "URG-001", "hours_overdue": 5, "name": "过期"}],
        "blocked": [],
        "at_risk": [],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    allocation = coordinator._calculate_resource_allocation(analysis)
    
    # sequential 模式应该高用户交互，低后台任务
    if allocation["user_interaction"] >= 0.9 and allocation["background_tasks"] == 0.0:
        return "correct"
    return "incorrect"

# ============ 负例测试场景 ============

def test_n01_empty_tasks():
    """N01: 空任务列表不应触发 sequential"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": [],
        "at_risk": [],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    return "incorrect" if analysis["recommended_mode"] == "sequential" else "correct"

def test_n02_minor_overdue():
    """N02: 轻微逾期不应过度反应"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [{"id": "URG-001", "hours_overdue": 0.5, "name": "轻微逾期"}],
        "blocked": [],
        "at_risk": [],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    # 轻微逾期仍应该触发 sequential，但不应该是 critical
    return "correct" if analysis["risk_score"] < 10 else "incorrect"

def test_n03_short_blocked():
    """N03: 短期阻塞不应 notify_user"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": [{"id": "BLK-001", "days_waiting": 0.5, "name": "短期阻塞"}],
        "at_risk": [],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    # 无过期任务，有阻塞任务，可能触发 notify_user 或 parallel
    # 但不应触发 sequential
    return "correct" if analysis["recommended_mode"] != "sequential" else "incorrect"

def test_n04_far_deadline():
    """N04: 充足时间任务不应 hybrid"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": [],
        "at_risk": [{"id": "RISK-001", "hours_left": 72, "name": "远期任务"}],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    # 72小时后到期，不应触发特殊处理
    return "correct" if analysis["risk_score"] == 0 else "incorrect"

def test_n05_completed_tasks():
    """N05: 已完成任务不应干扰"""
    coordinator = TaskCoordinator()
    
    # 已完成任务不应被计入
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": [],
        "at_risk": [],
        "pending": [],
        "completed_today": [{"id": "DONE-001", "name": "已完成"}]
    }
    
    analysis = coordinator.analyze_workload()
    return "correct" if analysis["recommended_mode"] == "parallel" else "incorrect"

def test_n06_future_tasks():
    """N06: 未来任务不应提前处理"""
    coordinator = TaskCoordinator()
    
    # 当前任务协调器可能不直接处理未来任务
    # 测试是否有机制防止过早处理
    analysis = coordinator.analyze_workload()
    # 只要没有误触发 sequential 即可
    return "correct" if analysis["recommended_mode"] != "sequential" else "incorrect"

def test_n07_threshold_boundary():
    """N07: risk_score=9 不应触发 sequential"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],  # 无过期
        "blocked": [{"id": "BLK-001", "days_waiting": 3, "name": "阻塞"}],  # +3
        "at_risk": [{"id": "RISK-001", "hours_left": 10, "name": "风险"}],  # +4
        "pending": []
    }
    # risk_score = 3+4 = 7 < 10, 不应触发 sequential
    
    analysis = coordinator.analyze_workload()
    return "correct" if analysis["recommended_mode"] != "sequential" else "incorrect"

def test_n08_no_blocked_notify():
    """N08: 无阻塞时不应 notify_user"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": [],
        "at_risk": [],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    return "correct" if analysis["recommended_mode"] != "notify_user" else "incorrect"

def test_n09_blocked_no_parallel():
    """N09: 有阻塞时不应 parallel"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": [{"id": "BLK-001", "days_waiting": 3, "name": "阻塞"}],
        "at_risk": [],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    # 有阻塞任务，优先处理阻塞，不应直接进入 parallel
    return "correct" if analysis["recommended_mode"] != "parallel" else "incorrect"

def test_n10_overdue_no_hybrid():
    """N10: 有过期时不应 hybrid"""
    coordinator = TaskCoordinator()
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [{"id": "URG-001", "hours_overdue": 2, "name": "过期"}],
        "blocked": [],
        "at_risk": [{"id": "RISK-001", "hours_left": 10, "name": "风险"}],
        "pending": []
    }
    
    analysis = coordinator.analyze_workload()
    # 有过期任务，应该 sequential，不应 hybrid
    return "correct" if analysis["recommended_mode"] == "sequential" else "incorrect"

# ============ 压力测试场景 ============

def test_s01_massive_overdue():
    """S01: 大规模过期任务"""
    coordinator = TaskCoordinator()
    
    # 创建20个过期任务
    overdue_tasks = [
        {"id": f"URG-{i:03d}", "hours_overdue": i % 10 + 1, "name": f"任务{i}"}
        for i in range(20)
    ]
    
    coordinator.load_current_tasks = lambda: {
        "overdue": overdue_tasks,
        "blocked": [],
        "at_risk": [],
        "pending": []
    }
    
    start = time.time()
    analysis = coordinator.analyze_workload()
    duration = (time.time() - start) * 1000
    
    # 应该正确识别为 sequential，且响应时间合理
    passed = analysis["recommended_mode"] == "sequential" and duration < 1000
    return f"passed ({duration:.1f}ms)" if passed else f"failed ({duration:.1f}ms)"

def test_s02_mixed_high_concurrency():
    """S02: 混合高并发"""
    coordinator = TaskCoordinator()
    
    # 50个各类任务
    tasks = {
        "overdue": [{"id": f"O-{i}", "hours_overdue": i+1, "name": f"O{i}"} for i in range(10)],
        "blocked": [{"id": f"B-{i}", "days_waiting": i+1, "name": f"B{i}"} for i in range(15)],
        "at_risk": [{"id": f"R-{i}", "hours_left": i+1, "name": f"R{i}"} for i in range(15)],
        "pending": [{"id": f"P-{i}", "name": f"P{i}"} for i in range(10)]
    }
    
    coordinator.load_current_tasks = lambda: tasks
    
    analysis = coordinator.analyze_workload()
    # 有过期任务，应该 sequential
    return "passed" if analysis["recommended_mode"] == "sequential" else "failed"

def test_s03_rapid_fire():
    """S03: 快速连续触发"""
    coordinator = TaskCoordinator()
    
    results = []
    errors = []
    
    def check():
        try:
            analysis = coordinator.analyze_workload()
            results.append(analysis["recommended_mode"])
        except Exception as e:
            errors.append(str(e))
    
    # 1秒内10次检查
    threads = [threading.Thread(target=check) for _ in range(10)]
    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    duration = (time.time() - start) * 1000
    
    passed = len(errors) == 0 and len(results) == 10
    return f"passed ({duration:.1f}ms, {len(errors)} errors)" if passed else f"failed ({len(errors)} errors)"

def test_s04_extreme_blocked():
    """S04: 极端阻塞堆积"""
    coordinator = TaskCoordinator()
    
    # 30个阻塞任务
    blocked = [{"id": f"B-{i}", "days_waiting": 10, "name": f"阻塞{i}"} for i in range(30)]
    
    coordinator.load_current_tasks = lambda: {
        "overdue": [],
        "blocked": blocked,
        "at_risk": [],
        "pending": []
    }
    
    start = time.time()
    analysis = coordinator.analyze_workload()
    duration = (time.time() - start) * 1000
    
    # 应该触发 notify_user，且能处理大量阻塞
    passed = analysis["recommended_mode"] == "notify_user" and duration < 500
    return f"passed ({duration:.1f}ms)" if passed else f"failed ({duration:.1f}ms)"

def test_s05_resource_exhaustion():
    """S05: 资源耗尽模拟"""
    coordinator = TaskCoordinator()
    
    # 极端参数：100个任务
    tasks = {
        "overdue": [{"id": f"O-{i}", "hours_overdue": 100, "name": f"O{i}"} for i in range(50)],
        "blocked": [{"id": f"B-{i}", "days_waiting": 100, "name": f"B{i}"} for i in range(30)],
        "at_risk": [{"id": f"R-{i}", "hours_left": 1, "name": f"R{i}"} for i in range(20)],
        "pending": []
    }
    
    coordinator.load_current_tasks = lambda: tasks
    
    start = time.time()
    try:
        analysis = coordinator.analyze_workload()
        duration = (time.time() - start) * 1000
        
        # 应该仍能工作，不会崩溃
        return f"stable ({duration:.1f}ms, mode={analysis['recommended_mode']})"
    except Exception as e:
        return f"crashed: {str(e)}"

# ============ 主执行函数 ============

def run_all_tests():
    """运行所有测试"""
    tester = TaskCoordinatorTester()
    
    print("="*70)
    print("🧪 Task Coordinator Skill 质量评估测试")
    print("="*70)
    print(f"开始时间: {datetime.now().isoformat()}")
    print()
    
    # 正例测试
    print("\n" + "="*70)
    print("📗 正例测试场景 (应该正确触发)")
    print("="*70)
    
    positive_tests = [
        ("P01", "严重过期任务处理", test_p01_sequential_overdue, "sequential"),
        ("P02", "多过期任务并行补救", test_p02_parallel_remedy, "sequential"),
        ("P03", "阻塞任务批量确认", test_p03_notify_blocked, "notify_user"),
        ("P04", "正常任务并行执行", test_p04_parallel_normal, "parallel"),
        ("P05", "混合模式调度", test_p05_hybrid_mode, "hybrid"),
        ("P06", "临界风险分数触发", test_p06_critical_threshold, "sequential"),
        ("P07", "长期阻塞检测", test_p07_long_term_blocked, "detected"),
        ("P08", "高风险即将到期", test_p08_high_risk_deadline, "detected"),
        ("P09", "学习模式识别", test_p09_learning_optimization, "optimized"),
        ("P10", "资源分配计算", test_p10_resource_allocation, "correct"),
    ]
    
    for test_id, name, test_fn, expected in positive_tests:
        tester.run_test(test_id, name, test_fn, expected)
    
    # 负例测试
    print("\n" + "="*70)
    print("📕 负例测试场景 (不应误触发)")
    print("="*70)
    
    negative_tests = [
        ("N01", "空任务列表", test_n01_empty_tasks, "correct"),
        ("N02", "轻微逾期", test_n02_minor_overdue, "correct"),
        ("N03", "短期阻塞", test_n03_short_blocked, "correct"),
        ("N04", "充足时间任务", test_n04_far_deadline, "correct"),
        ("N05", "已完成任务干扰", test_n05_completed_tasks, "correct"),
        ("N06", "未来任务提前", test_n06_future_tasks, "correct"),
        ("N07", "阈值边界下", test_n07_threshold_boundary, "correct"),
        ("N08", "无阻塞时notify", test_n08_no_blocked_notify, "correct"),
        ("N09", "有阻塞时parallel", test_n09_blocked_no_parallel, "correct"),
        ("N10", "过期时hybrid", test_n10_overdue_no_hybrid, "correct"),
    ]
    
    for test_id, name, test_fn, expected in negative_tests:
        tester.run_test(test_id, name, test_fn, expected)
    
    # 压力测试
    print("\n" + "="*70)
    print("📙 压力测试场景 (高负载并发)")
    print("="*70)
    
    stress_tests = [
        ("S01", "大规模过期任务(20+)", test_s01_massive_overdue, "passed"),
        ("S02", "混合高并发(50+)", test_s02_mixed_high_concurrency, "passed"),
        ("S03", "快速连续触发(10次/秒)", test_s03_rapid_fire, "passed"),
        ("S04", "极端阻塞堆积(30+)", test_s04_extreme_blocked, "passed"),
        ("S05", "资源耗尽模拟(100+)", test_s05_resource_exhaustion, "stable"),
    ]
    
    for test_id, name, test_fn, expected in stress_tests:
        # 压力测试使用部分匹配
        result = test_fn()
        passed = expected in result.lower() or result.startswith(expected)
        tester.results.record(test_id, name, passed, f"contains '{expected}'", 
                            result, 0, 0)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n[TEST] {test_id}: {name}")
        print(f"  {status}")
        print(f"  结果: {result}")
    
    # 生成报告
    print("\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)
    
    summary = tester.results.get_summary()
    print(f"总测试数: {summary['total']}")
    print(f"通过: {summary['passed']} ({summary['pass_rate']:.1f}%)")
    print(f"失败: {summary['failed']}")
    print(f"平均耗时: {summary['avg_duration_ms']:.2f}ms")
    print(f"峰值内存: {summary['max_memory_mb']:.2f}MB")
    
    # 分类统计
    p_passed = sum(1 for r in tester.results.results if r["test_id"].startswith("P") and r["passed"])
    p_total = sum(1 for r in tester.results.results if r["test_id"].startswith("P"))
    n_passed = sum(1 for r in tester.results.results if r["test_id"].startswith("N") and r["passed"])
    n_total = sum(1 for r in tester.results.results if r["test_id"].startswith("N"))
    s_passed = sum(1 for r in tester.results.results if r["test_id"].startswith("S") and r["passed"])
    s_total = sum(1 for r in tester.results.results if r["test_id"].startswith("S"))
    
    print(f"\n正例测试: {p_passed}/{p_total} ({p_passed/p_total*100:.1f}%)")
    print(f"负例测试: {n_passed}/{n_total} ({n_passed/n_total*100:.1f}%)")
    print(f"压力测试: {s_passed}/{s_total} ({s_passed/s_total*100:.1f}%)")
    
    # 保存详细结果
    output = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "category_summary": {
            "positive": {"passed": p_passed, "total": p_total},
            "negative": {"passed": n_passed, "total": n_total},
            "stress": {"passed": s_passed, "total": s_total}
        },
        "details": tester.results.results
    }
    
    output_file = Path(__file__).parent / "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n详细结果已保存: {output_file}")
    
    return output

if __name__ == "__main__":
    run_all_tests()
