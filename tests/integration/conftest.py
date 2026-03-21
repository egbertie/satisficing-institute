"""
L4 集成测试框架 - conftest.py
提供共享的测试固件和工具函数
"""

import pytest
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class SkillTestContext:
    """技能测试上下文"""
    skill_name: str
    skill_path: Path
    config: Dict[str, Any]
    test_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "skill_path": str(self.skill_path),
            "config": self.config,
            "test_data": self.test_data
        }


@dataclass
class IntegrationTestResult:
    """集成测试结果"""
    scenario_name: str
    success: bool
    duration_ms: float
    skills_involved: List[str]
    error_message: Optional[str] = None
    artifacts: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "skills_involved": self.skills_involved,
            "error_message": self.error_message,
            "artifacts": self.artifacts or {}
        }


@pytest.fixture
def skills_dir():
    """返回技能目录路径"""
    return SKILLS_DIR


@pytest.fixture
def project_root():
    """返回项目根目录路径"""
    return PROJECT_ROOT


@pytest.fixture
def skill_paths():
    """返回关键技能的目录路径"""
    return {
        "zero_idle_enforcer": SKILLS_DIR / "zero-idle-enforcer",
        "token_budget_enforcer": SKILLS_DIR / "token-budget-enforcer",
        "blue_sentinel": SKILLS_DIR / "blue-sentinel",
        "quality_assurance": SKILLS_DIR / "quality-assurance",
        "honesty_tagging": SKILLS_DIR / "honesty-tagging-protocol",
        "role_federation": SKILLS_DIR / "role-federation",
    }


@pytest.fixture
def mock_task_data():
    """提供模拟任务数据"""
    return {
        "task_id": f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "task_type": "integration_test",
        "priority": "P1",
        "created_at": datetime.now().isoformat(),
        "metadata": {
            "test_suite": "L4_integration",
            "test_scenario": "skill_interaction"
        }
    }


@pytest.fixture
def mock_budget_data():
    """提供模拟预算数据"""
    return {
        "total_budget": 100000,
        "strategic_reserve": 30000,
        "operational_budget": 50000,
        "innovation_fund": 20000,
        "consumed_today": 15000,
        "remaining_percentage": 85.0
    }


@pytest.fixture
def mock_idle_context():
    """提供模拟空闲检测上下文"""
    return {
        "user_last_active": (datetime.now() - timedelta(hours=3)).isoformat(),
        "inactive_duration_hours": 3.0,
        "token_remaining_percentage": 65.0,
        "fill_tasks_pending": [
            {"id": "LEARN-001", "type": "learning"},
            {"id": "OPT-001", "type": "optimization"}
        ]
    }


@pytest.fixture
def mock_quality_output():
    """提供模拟质量检查输出"""
    return {
        "content": "这是一个重要的决策建议",
        "confidence_level": "medium",
        "requires_cross_validation": True,
        "source_reliability": "high",
        "logic_soundness": "good"
    }


@pytest.fixture
def mock_honesty_tags():
    """提供模拟诚实性标注"""
    return {
        "statements": [
            {
                "text": "市场规模达1000亿",
                "tag": "KNOWN",
                "confidence": 95,
                "source": "工信部2025年报",
                "timestamp": "2026-01"
            },
            {
                "text": "预计增长率25%",
                "tag": "INFERRED",
                "confidence": 75,
                "reasoning": "基于Q1-Q3趋势推断",
                "timestamp": "2026-03"
            }
        ]
    }


@pytest.fixture
def mock_role_assignment():
    """提供模拟角色分配数据"""
    return {
        "task_id": "TASK-001",
        "assigned_role": "Specialist",
        "backup_roles": ["Auditor"],
        "confidence": 0.85,
        "estimated_duration": 3600
    }


class SkillIntegrationTester:
    """技能集成测试助手类"""
    
    def __init__(self):
        self.results: List[IntegrationTestResult] = []
        self.test_start_time = datetime.now()
    
    def record_result(self, result: IntegrationTestResult):
        """记录测试结果"""
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "duration_seconds": (datetime.now() - self.test_start_time).total_seconds(),
            "results": [r.to_dict() for r in self.results]
        }
    
    def export_report(self, output_path: Path):
        """导出测试报告"""
        summary = self.get_summary()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        return output_path


@pytest.fixture
def integration_tester():
    """提供集成测试助手实例"""
    return SkillIntegrationTester()


@pytest.fixture
def skill_exists_checker(skill_paths):
    """检查技能是否存在的工具"""
    def checker(skill_name: str) -> bool:
        path = skill_paths.get(skill_name)
        if path is None:
            return False
        return path.exists()
    return checker


def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "skill_integration: 标记技能集成测试"
    )
    config.addinivalue_line(
        "markers", "scenario1: 资源紧张时的补位决策测试"
    )
    config.addinivalue_line(
        "markers", "scenario2: 错误检测后质量检查测试"
    )
    config.addinivalue_line(
        "markers", "scenario3: 多角色下的诚实标注测试"
    )
    config.addinivalue_line(
        "markers", "scenario4: 完整任务流程测试"
    )
    config.addinivalue_line(
        "markers", "scenario5: 灾备恢复流程测试"
    )
    config.addinivalue_line(
        "markers", "scenario6: Token预算与质量保证联动测试"
    )
    config.addinivalue_line(
        "markers", "scenario7: 角色联邦与诚实标注联动测试"
    )
    config.addinivalue_line(
        "markers", "scenario8: 全系统综合压力测试"
    )
