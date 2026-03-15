#!/usr/bin/env python3
"""
跨Skill协调器 - Cross Skill Orchestrator

功能：协调多个Skill的顺序/并行执行
优化：最小执行时间、最大资源利用、依赖自动处理
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class SkillTask:
    """Skill任务"""
    skill_name: str
    command: str
    dependencies: List[str]
    estimated_duration: int  # 秒
    can_parallel: bool

@dataclass
class ExecutionPlan:
    """执行计划"""
    task_id: str
    stages: List[List[SkillTask]]  # 分阶段，同阶段可并行
    total_duration_estimate: int
    parallel_degree: int

@dataclass
class ExecutionResult:
    """执行结果"""
    task_id: str
    status: str  # success/partial/failed
    results: Dict[str, Any]
    duration_seconds: float
    errors: List[str]


class CrossSkillOrchestrator:
    """跨Skill协调器"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.skills_dir = self.workspace / "skills"
    
    def create_plan(self, task_description: str, skill_list: List[str]) -> ExecutionPlan:
        """
        创建执行计划
        
        Args:
            task_description: 任务描述
            skill_list: 涉及的Skill列表
            
        Returns:
            执行计划
        """
        # 分析Skill依赖关系
        tasks = []
        for skill_name in skill_list:
            task = self._analyze_skill(skill_name)
            if task:
                tasks.append(task)
        
        # 拓扑排序，确定执行顺序
        stages = self._topological_sort(tasks)
        
        # 计算预估时间
        total_duration = sum(
            max(t.estimated_duration for t in stage)
            for stage in stages
        )
        
        # 计算并行度
        parallel_degree = max(len(stage) for stage in stages)
        
        return ExecutionPlan(
            task_id=f"ORCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            stages=stages,
            total_duration_estimate=total_duration,
            parallel_degree=parallel_degree
        )
    
    def _analyze_skill(self, skill_name: str) -> Optional[SkillTask]:
        """分析Skill信息"""
        skill_dir = self.skills_dir / skill_name
        
        if not skill_dir.exists():
            return None
        
        # 读取skill.json
        config_file = skill_dir / "skill.json"
        config = {}
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 确定入口文件
        entry = config.get("entry", "main.py")
        
        return SkillTask(
            skill_name=skill_name,
            command=f"python3 {skill_dir / entry}",
            dependencies=config.get("dependencies", []),
            estimated_duration=config.get("estimated_duration_seconds", 60),
            can_parallel=config.get("can_parallel", True)
        )
    
    def _topological_sort(self, tasks: List[SkillTask]) -> List[List[SkillTask]]:
        """拓扑排序，返回分阶段的任务列表"""
        # 构建依赖图
        task_map = {t.skill_name: t for t in tasks}
        in_degree = {t.skill_name: 0 for t in tasks}
        
        for task in tasks:
            for dep in task.dependencies:
                if dep in task_map:
                    in_degree[task.skill_name] += 1
        
        # Kahn算法
        stages = []
        remaining = set(t.skill_name for t in tasks)
        
        while remaining:
            # 找到入度为0的任务
            current_stage = [
                task_map[name] for name in remaining
                if in_degree[name] == 0
            ]
            
            if not current_stage:
                # 有循环依赖，打破循环
                current_stage = [task_map[list(remaining)[0]]]
            
            stages.append(current_stage)
            
            # 更新入度
            for task in current_stage:
                remaining.remove(task.skill_name)
                for other in remaining:
                    if task.skill_name in task_map[other].dependencies:
                        in_degree[other] -= 1
        
        return stages
    
    def execute_plan(self, plan: ExecutionPlan) -> ExecutionResult:
        """
        执行计划
        
        Args:
            plan: 执行计划
            
        Returns:
            执行结果
        """
        start_time = datetime.now()
        all_results = {}
        errors = []
        
        for stage_num, stage in enumerate(plan.stages, 1):
            print(f"执行第{stage_num}阶段 ({len(stage)}个任务)...")
            
            if len(stage) == 1 or not all(t.can_parallel for t in stage):
                # 串行执行
                for task in stage:
                    result = self._execute_single_task(task)
                    all_results[task.skill_name] = result
                    if not result["success"]:
                        errors.append(f"{task.skill_name}: {result.get('error', '未知错误')}")
            else:
                # 并行执行
                with ThreadPoolExecutor(max_workers=len(stage)) as executor:
                    futures = {
                        executor.submit(self._execute_single_task, task): task
                        for task in stage
                    }
                    
                    for future in as_completed(futures):
                        task = futures[future]
                        try:
                            result = future.result()
                            all_results[task.skill_name] = result
                            if not result["success"]:
                                errors.append(f"{task.skill_name}: {result.get('error', '未知错误')}")
                        except Exception as e:
                            errors.append(f"{task.skill_name}: {str(e)}")
                            all_results[task.skill_name] = {"success": False, "error": str(e)}
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # 确定状态
        if not errors:
            status = "success"
        elif len(errors) < len(all_results):
            status = "partial"
        else:
            status = "failed"
        
        return ExecutionResult(
            task_id=plan.task_id,
            status=status,
            results=all_results,
            duration_seconds=duration,
            errors=errors
        )
    
    def _execute_single_task(self, task: SkillTask) -> Dict:
        """执行单个任务"""
        try:
            result = subprocess.run(
                task.command.split(),
                capture_output=True,
                text=True,
                timeout=task.estimated_duration * 2,
                cwd=str(self.skills_dir / task.skill_name)
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:500],  # 限制长度
                "stderr": result.stderr[:500] if result.stderr else "",
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "执行超时"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_plan_report(self, plan: ExecutionPlan) -> str:
        """生成计划报告"""
        lines = [
            f"# 跨Skill执行计划",
            "",
            f"**计划ID**: {plan.task_id}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**预估总时长**: {plan.total_duration_estimate}秒",
            f"**最大并行度**: {plan.parallel_degree}",
            f"**执行阶段数**: {len(plan.stages)}",
            "",
            "## 执行流程",
            ""
        ]
        
        for i, stage in enumerate(plan.stages, 1):
            lines.append(f"### 阶段{i}")
            lines.append(f"并行任务: {len(stage)}个")
            for task in stage:
                parallel_mark = "【可并行】" if task.can_parallel else "【需串行】"
                lines.append(f"- {task.skill_name} {parallel_mark} (预估{task.estimated_duration}秒)")
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "*自动优化执行顺序，最大化并行效率*"
        ])
        
        return "\n".join(lines)
    
    def generate_execution_report(self, result: ExecutionResult) -> str:
        """生成执行报告"""
        lines = [
            f"# 跨Skill执行报告",
            "",
            f"**任务ID**: {result.task_id}",
            f"**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**执行状态**: {'✅ 成功' if result.status == 'success' else '⚠️ 部分成功' if result.status == 'partial' else '❌ 失败'}",
            f"**实际耗时**: {result.duration_seconds:.1f}秒",
            f"**执行任务数**: {len(result.results)}",
            "",
            "## 执行结果",
            ""
        ]
        
        for skill_name, skill_result in result.results.items():
            status = "✅" if skill_result.get("success") else "❌"
            lines.append(f"{status} **{skill_name}**")
        
        if result.errors:
            lines.extend([
                "",
                "## 错误信息",
                ""
            ])
            for error in result.errors:
                lines.append(f"- {error}")
        
        lines.extend([
            "",
            "---",
            "",
            "*多Skill协调执行，资源最优配置*"
        ])
        
        return "\n".join(lines)


def main():
    """主函数 - 演示"""
    print("=" * 60)
    print("跨Skill协调器 v1.0")
    print("=" * 60)
    
    orchestrator = CrossSkillOrchestrator()
    
    # 创建计划示例
    print("\n创建执行计划...")
    plan = orchestrator.create_plan(
        task_description="全面系统检查",
        skill_list=[
            "zero-idle-enforcer",
            "self-assessment-calibrator",
            "skill-evolution-tracker"
        ]
    )
    
    print(f"计划ID: {plan.task_id}")
    print(f"预估时长: {plan.total_duration_estimate}秒")
    print(f"执行阶段: {len(plan.stages)}")
    
    # 生成计划报告
    print("\n" + "=" * 60)
    print("执行计划详情：")
    print("=" * 60)
    report = orchestrator.generate_plan_report(plan)
    print(report)


if __name__ == "__main__":
    main()
