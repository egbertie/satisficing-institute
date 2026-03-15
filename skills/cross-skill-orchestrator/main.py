#!/usr/bin/env python3
"""
跨Skill协调器 (Cross Skill Orchestrator)
功能：协调多个Skill的顺序/并行执行
优化：最小执行时间、最大资源利用、依赖自动处理
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor


class ExecutionMode(Enum):
    SEQUENTIAL = "顺序执行"
    PARALLEL = "并行执行"
    MIXED = "混合执行"


@dataclass
class SkillTask:
    """Skill任务定义"""
    skill_name: str
    parameters: Dict
    dependencies: List[str]  # 依赖的其他任务ID
    task_id: str
    estimated_time: float  # 预估执行时间(秒)
    priority: int = 1


@dataclass
class ExecutionResult:
    """执行结果"""
    task_id: str
    skill_name: str
    status: str  # success/failed/pending
    result: Any
    start_time: str
    end_time: str
    duration: float
    error_message: str = ""


@dataclass
class OrchestrationPlan:
    """协调计划"""
    plan_id: str
    execution_mode: ExecutionMode
    execution_order: List[List[str]]  # 分层执行计划
    estimated_total_time: float
    resource_plan: Dict
    risk_analysis: List[str]


@dataclass
class OrchestrationResult:
    """协调执行结果"""
    plan_id: str
    status: str
    results: List[ExecutionResult]
    summary: Dict
    execution_log: List[str]


class CrossSkillOrchestrator:
    """跨Skill协调器"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.execution_history = []
    
    def _detect_dependencies(self, tasks: List[SkillTask]) -> Dict[str, List[str]]:
        """检测任务间依赖关系"""
        dependency_graph = {}
        task_ids = {t.task_id for t in tasks}
        
        for task in tasks:
            # 检查显式依赖
            deps = [d for d in task.dependencies if d in task_ids]
            
            # 检查隐式依赖（参数引用）
            for param_value in task.parameters.values():
                if isinstance(param_value, str) and param_value.startswith("${"):
                    ref_task = param_value[2:-1].split(".")[0]
                    if ref_task in task_ids and ref_task not in deps:
                        deps.append(ref_task)
            
            dependency_graph[task.task_id] = deps
        
        return dependency_graph
    
    def _topological_sort(self, tasks: List[SkillTask], 
                          dependency_graph: Dict) -> List[List[str]]:
        """拓扑排序，生成分层执行计划"""
        # 计算入度
        in_degree = {t.task_id: 0 for t in tasks}
        for task_id, deps in dependency_graph.items():
            in_degree[task_id] = len(deps)
        
        # 分层执行
        layers = []
        remaining = set(t.task_id for t in tasks)
        
        while remaining:
            # 找出当前可以执行的任务（入度为0）
            current_layer = [
                task_id for task_id in remaining 
                if in_degree[task_id] == 0
            ]
            
            if not current_layer:
                # 存在循环依赖
                raise ValueError("检测到循环依赖，无法生成执行计划")
            
            layers.append(current_layer)
            remaining -= set(current_layer)
            
            # 更新入度
            for task_id in current_layer:
                for other_id, deps in dependency_graph.items():
                    if task_id in deps:
                        in_degree[other_id] -= 1
        
        return layers
    
    def _determine_execution_mode(self, layers: List[List[str]], 
                                   tasks: List[SkillTask]) -> ExecutionMode:
        """确定执行模式"""
        total_tasks = len(tasks)
        max_parallel = max(len(layer) for layer in layers)
        
        if len(layers) == 1 and max_parallel > 1:
            return ExecutionMode.PARALLEL
        elif len(layers) == total_tasks:
            return ExecutionMode.SEQUENTIAL
        else:
            return ExecutionMode.MIXED
    
    def _estimate_execution_time(self, layers: List[List[str]], 
                                  task_map: Dict[str, SkillTask]) -> float:
        """预估总执行时间"""
        total_time = 0
        
        for layer in layers:
            # 每层取最慢的任务
            layer_time = max(
                task_map[task_id].estimated_time 
                for task_id in layer
            )
            total_time += layer_time
        
        # 加上协调开销
        return total_time + len(layers) * 0.5
    
    def create_plan(self, task_description: str, 
                    skills: List[Dict]) -> OrchestrationPlan:
        """创建协调执行计划"""
        
        plan_id = f"PLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 构建任务列表
        tasks = []
        for i, skill_def in enumerate(skills):
            task = SkillTask(
                skill_name=skill_def["name"],
                parameters=skill_def.get("parameters", {}),
                dependencies=skill_def.get("dependencies", []),
                task_id=f"T{i+1:03d}",
                estimated_time=skill_def.get("estimated_time", 2.0),
                priority=skill_def.get("priority", 1)
            )
            tasks.append(task)
        
        # 检测依赖
        dependency_graph = self._detect_dependencies(tasks)
        
        # 拓扑排序
        layers = self._topological_sort(tasks, dependency_graph)
        
        # 确定执行模式
        execution_mode = self._determine_execution_mode(layers, tasks)
        
        # 计算预估时间
        task_map = {t.task_id: t for t in tasks}
        estimated_time = self._estimate_execution_time(layers, task_map)
        
        # 资源规划
        max_concurrent = max(len(layer) for layer in layers)
        resource_plan = {
            "max_concurrent_tasks": max_concurrent,
            "total_tasks": len(tasks),
            "execution_layers": len(layers),
            "recommended_workers": min(max_concurrent, self.max_workers)
        }
        
        # 风险分析
        risks = []
        if len(layers) > 5:
            risks.append("执行链路较长，建议检查是否可以简化")
        if any(len(layer) > 3 for layer in layers):
            risks.append("存在高度并行任务，注意资源竞争")
        if not risks:
            risks.append("执行计划风险较低")
        
        return OrchestrationPlan(
            plan_id=plan_id,
            execution_mode=execution_mode,
            execution_order=layers,
            estimated_total_time=estimated_time,
            resource_plan=resource_plan,
            risk_analysis=risks
        )
    
    def _execute_skill_mock(self, task: SkillTask) -> ExecutionResult:
        """模拟执行Skill（实际环境中会调用真实Skill）"""
        import time
        import random
        
        start = datetime.now()
        time.sleep(0.1)  # 模拟执行时间
        
        # 模拟成功率95%
        success = random.random() > 0.05
        
        end = datetime.now()
        duration = (end - start).total_seconds()
        
        return ExecutionResult(
            task_id=task.task_id,
            skill_name=task.skill_name,
            status="success" if success else "failed",
            result={"data": f"{task.skill_name} execution result"} if success else None,
            start_time=start.isoformat(),
            end_time=end.isoformat(),
            duration=duration,
            error_message="" if success else "模拟执行失败"
        )
    
    def execute(self, plan: OrchestrationPlan, 
                tasks: List[SkillTask]) -> OrchestrationResult:
        """执行协调计划"""
        
        task_map = {t.task_id: t for t in tasks}
        results = []
        execution_log = []
        
        start_time = datetime.now()
        
        for layer_idx, layer in enumerate(plan.execution_order):
            execution_log.append(f"开始执行第{layer_idx + 1}层: {layer}")
            
            layer_tasks = [task_map[tid] for tid in layer]
            
            if len(layer) == 1:
                # 顺序执行
                for task in layer_tasks:
                    result = self._execute_skill_mock(task)
                    results.append(result)
                    execution_log.append(f"  {task.task_id}({task.skill_name}): {result.status}")
            else:
                # 并行执行
                with ThreadPoolExecutor(max_workers=len(layer)) as executor:
                    layer_results = list(executor.map(self._execute_skill_mock, layer_tasks))
                    results.extend(layer_results)
                    for task, res in zip(layer_tasks, layer_results):
                        execution_log.append(f"  {task.task_id}({task.skill_name}): {res.status}")
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # 统计
        success_count = sum(1 for r in results if r.status == "success")
        failed_count = len(results) - success_count
        
        summary = {
            "total_tasks": len(results),
            "success_count": success_count,
            "failed_count": failed_count,
            "success_rate": f"{success_count/len(results)*100:.1f}%",
            "total_duration": f"{total_duration:.2f}s",
            "estimated_time": f"{plan.estimated_total_time:.2f}s"
        }
        
        status = "completed" if failed_count == 0 else "partial_failed" if success_count > 0 else "failed"
        
        return OrchestrationResult(
            plan_id=plan.plan_id,
            status=status,
            results=results,
            summary=summary,
            execution_log=execution_log
        )
    
    def generate_plan_report(self, plan: OrchestrationPlan) -> str:
        """生成计划报告"""
        lines = [
            "=" * 70,
            "              跨Skill协调执行计划",
            "=" * 70,
            f"计划ID: {plan.plan_id}",
            f"执行模式: {plan.execution_mode.value}",
            f"预估总时间: {plan.estimated_total_time:.1f}秒",
            "",
            "【执行顺序】",
        ]
        
        for i, layer in enumerate(plan.execution_order, 1):
            parallel = "并行" if len(layer) > 1 else "顺序"
            lines.append(f"  第{i}层 ({parallel}): {' → '.join(layer)}")
        
        lines.extend([
            "",
            "【资源规划】",
            f"  总任务数: {plan.resource_plan['total_tasks']}",
            f"  执行层数: {plan.resource_plan['execution_layers']}",
            f"  最大并发: {plan.resource_plan['max_concurrent_tasks']}",
            f"  推荐工作线程: {plan.resource_plan['recommended_workers']}",
            "",
            "【风险分析】",
        ])
        
        for risk in plan.risk_analysis:
            lines.append(f"  ⚠️  {risk}")
        
        lines.extend([
            "",
            "=" * 70
        ])
        
        return "\n".join(lines)
    
    def generate_execution_report(self, result: OrchestrationResult) -> str:
        """生成执行报告"""
        lines = [
            "=" * 70,
            "              跨Skill协调执行报告",
            "=" * 70,
            f"计划ID: {result.plan_id}",
            f"执行状态: {result.status}",
            "",
            "【执行摘要】",
            f"  总任务: {result.summary['total_tasks']}",
            f"  成功: {result.summary['success_count']}",
            f"  失败: {result.summary['failed_count']}",
            f"  成功率: {result.summary['success_rate']}",
            f"  实际耗时: {result.summary['total_duration']}",
            f"  预估时间: {result.summary['estimated_time']}",
            "",
            "【执行日志】",
        ]
        
        for log in result.execution_log:
            lines.append(f"  {log}")
        
        lines.extend([
            "",
            "【详细结果】",
        ])
        
        for res in result.results:
            icon = "✅" if res.status == "success" else "❌"
            lines.append(f"  {icon} {res.task_id} | {res.skill_name} | {res.duration:.2f}s | {res.status}")
        
        lines.extend([
            "",
            "=" * 70
        ])
        
        return "\n".join(lines)


def main():
    """主函数演示"""
    print("🎼 跨Skill协调器 - 演示\n")
    
    # 初始化协调器
    orchestrator = CrossSkillOrchestrator(max_workers=4)
    
    # 示例：复杂工作流 - 新产品上线准备
    task_description = "新产品上线准备：需要分析市场需求、评估风险、创建任务计划、协调资源"
    
    skills = [
        {
            "name": "market-analyzer",
            "parameters": {"product": "新产品A", "market": "华东区"},
            "estimated_time": 3.0,
            "dependencies": [],
            "priority": 1
        },
        {
            "name": "risk-assessor",
            "parameters": {"product": "新产品A", "context": "${T001}.result"},
            "estimated_time": 2.0,
            "dependencies": ["T001"],
            "priority": 2
        },
        {
            "name": "task-creator",
            "parameters": {"type": "project", "template": "product_launch"},
            "estimated_time": 1.5,
            "dependencies": [],
            "priority": 1
        },
        {
            "name": "resource-allocator",
            "parameters": {"project": "新产品上线", "requirements": "${T003}.tasks"},
            "estimated_time": 2.0,
            "dependencies": ["T003"],
            "priority": 3
        },
        {
            "name": "timeline-generator",
            "parameters": {
                "tasks": "${T003}.tasks",
                "resources": "${T004}.allocation"
            },
            "estimated_time": 1.0,
            "dependencies": ["T003", "T004"],
            "priority": 4
        }
    ]
    
    # 创建执行计划
    print("📋 创建工作流执行计划...")
    plan = orchestrator.create_plan(task_description, skills)
    print(orchestrator.generate_plan_report(plan))
    
    # 构建任务对象
    tasks = []
    for i, skill_def in enumerate(skills):
        tasks.append(SkillTask(
            skill_name=skill_def["name"],
            parameters=skill_def["parameters"],
            dependencies=skill_def.get("dependencies", []),
            task_id=f"T{i+1:03d}",
            estimated_time=skill_def.get("estimated_time", 2.0),
            priority=skill_def.get("priority", 1)
        ))
    
    # 执行计划
    print("\n🚀 开始执行协调计划...\n")
    result = orchestrator.execute(plan, tasks)
    print(orchestrator.generate_execution_report(result))
    
    # JSON输出
    print("\n\n📊 JSON格式输出:")
    json_output = {
        "plan": {
            "plan_id": plan.plan_id,
            "execution_mode": plan.execution_mode.value,
            "estimated_total_time": plan.estimated_total_time,
            "execution_order": plan.execution_order
        },
        "execution": {
            "status": result.status,
            "summary": result.summary,
            "results": [
                {
                    "task_id": r.task_id,
                    "skill_name": r.skill_name,
                    "status": r.status,
                    "duration": r.duration
                }
                for r in result.results
            ]
        }
    }
    print(json.dumps(json_output, ensure_ascii=False, indent=2))
    
    return result


if __name__ == "__main__":
    main()
