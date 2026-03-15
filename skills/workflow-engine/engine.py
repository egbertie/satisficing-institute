#!/usr/bin/env python3
"""
事务工作流引擎 - Skill链的可靠执行
开始 → 执行 → 提交/回滚 → 完成
"""

import json
import uuid
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field

class TransactionStatus(Enum):
    PENDING = "pending"      # 待执行
    RUNNING = "running"      # 执行中
    COMMITTED = "committed"  # 已提交
    ROLLED_BACK = "rolled_back"  # 已回滚
    FAILED = "failed"        # 失败

@dataclass
class StepResult:
    """步骤执行结果"""
    step_id: str
    status: str  # success, failed, skipped
    output: Any = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class WorkflowStep:
    """工作流步骤"""
    id: str
    name: str
    action: Callable
    rollback_action: Optional[Callable] = None
    depends_on: List[str] = field(default_factory=list)
    retry_count: int = 3
    timeout_seconds: int = 300


class TransactionalWorkflow:
    """事务化工作流引擎"""
    
    def __init__(self, name: str):
        self.name = name
        self.workflow_id = str(uuid.uuid4())[:8]
        self.steps: Dict[str, WorkflowStep] = {}
        self.execution_order: List[str] = []
        self.results: Dict[str, StepResult] = {}
        self.status = TransactionStatus.PENDING
        self.context: Dict = {}
        self.log: List[Dict] = []
    
    def add_step(self, step: WorkflowStep) -> 'TransactionalWorkflow':
        """添加步骤"""
        self.steps[step.id] = step
        self._recalculate_order()
        return self
    
    def _recalculate_order(self):
        """重新计算执行顺序（拓扑排序）"""
        # 简化版：按依赖关系排序
        ordered = []
        remaining = set(self.steps.keys())
        
        while remaining:
            # 找到没有未满足依赖的步骤
            ready = [
                step_id for step_id in remaining
                if all(dep in ordered for dep in self.steps[step_id].depends_on)
            ]
            
            if not ready:
                raise ValueError("循环依赖 detected")
            
            ordered.extend(ready)
            remaining -= set(ready)
        
        self.execution_order = ordered
    
    def execute(self, initial_context: Dict = None) -> Dict:
        """
        执行工作流
        
        Args:
            initial_context: 初始上下文
        
        Returns:
            执行结果报告
        """
        self.context = initial_context or {}
        self.status = TransactionStatus.RUNNING
        
        print(f"🚀 启动工作流: {self.name} [{self.workflow_id}]")
        print(f"   步骤数: {len(self.steps)}")
        print(f"   执行顺序: {' → '.join(self.execution_order)}")
        
        try:
            for step_id in self.execution_order:
                step = self.steps[step_id]
                
                print(f"\n  ▶️ 执行步骤: {step.name}")
                
                # 检查依赖是否成功
                if not self._check_dependencies(step):
                    print(f"     ⚠️ 依赖失败，跳过此步骤")
                    self.results[step_id] = StepResult(
                        step_id=step_id,
                        status="skipped",
                        error="Dependencies failed"
                    )
                    continue
                
                # 执行步骤
                result = self._execute_step(step)
                self.results[step_id] = result
                
                # 记录日志
                self._log_step(step, result)
                
                if result.status == "failed":
                    print(f"     ❌ 步骤失败: {result.error}")
                    
                    # 是否需要回滚？
                    if self._should_rollback():
                        print(f"\n  ⏮️ 启动回滚...")
                        self._rollback()
                        self.status = TransactionStatus.ROLLED_BACK
                        return self._generate_report()
                    else:
                        self.status = TransactionStatus.FAILED
                        return self._generate_report()
                else:
                    print(f"     ✅ 步骤成功 ({result.execution_time_ms}ms)")
                    # 更新上下文
                    if result.output:
                        self.context[f"{step_id}_output"] = result.output
            
            # 全部成功，提交事务
            print(f"\n✅ 工作流完成，提交事务")
            self.status = TransactionStatus.COMMITTED
            return self._generate_report()
            
        except Exception as e:
            print(f"\n❌ 工作流异常: {str(e)}")
            self._rollback()
            self.status = TransactionStatus.ROLLED_BACK
            return self._generate_report()
    
    def _check_dependencies(self, step: WorkflowStep) -> bool:
        """检查依赖是否都成功"""
        for dep_id in step.depends_on:
            if dep_id not in self.results:
                return False
            if self.results[dep_id].status != "success":
                return False
        return True
    
    def _execute_step(self, step: WorkflowStep) -> StepResult:
        """执行单个步骤"""
        import time
        
        start_time = time.time()
        last_error = None
        
        # 重试机制
        for attempt in range(step.retry_count):
            try:
                # 传入上下文
                output = step.action(self.context)
                
                execution_time = int((time.time() - start_time) * 1000)
                
                return StepResult(
                    step_id=step.id,
                    status="success",
                    output=output,
                    execution_time_ms=execution_time
                )
                
            except Exception as e:
                last_error = str(e)
                print(f"     ⚠️ 尝试 {attempt + 1}/{step.retry_count} 失败: {last_error}")
                if attempt < step.retry_count - 1:
                    import time
                    time.sleep(1)  # 重试前等待
        
        # 全部重试失败
        execution_time = int((time.time() - start_time) * 1000)
        
        return StepResult(
            step_id=step.id,
            status="failed",
            error=last_error,
            execution_time_ms=execution_time
        )
    
    def _should_rollback(self) -> bool:
        """判断是否需要回滚"""
        # 默认策略：任何步骤失败都回滚
        # 可以配置为只有关键步骤失败才回滚
        return True
    
    def _rollback(self):
        """回滚已执行的步骤"""
        print(f"  ⏮️ 回滚 {len(self.results)} 个步骤...")
        
        # 逆序回滚
        for step_id in reversed(list(self.results.keys())):
            step = self.steps.get(step_id)
            if step and step.rollback_action:
                print(f"     回滚: {step.name}")
                try:
                    step.rollback_action(self.context)
                except Exception as e:
                    print(f"     ⚠️ 回滚失败: {str(e)}")
    
    def _log_step(self, step: WorkflowStep, result: StepResult):
        """记录步骤日志"""
        self.log.append({
            "timestamp": result.timestamp,
            "step_id": step.id,
            "step_name": step.name,
            "status": result.status,
            "error": result.error,
            "execution_time_ms": result.execution_time_ms
        })
    
    def _generate_report(self) -> Dict:
        """生成执行报告"""
        success_count = sum(1 for r in self.results.values() if r.status == "success")
        failed_count = sum(1 for r in self.results.values() if r.status == "failed")
        skipped_count = sum(1 for r in self.results.values() if r.status == "skipped")
        
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.name,
            "status": self.status.value,
            "start_time": self.log[0]["timestamp"] if self.log else None,
            "end_time": datetime.now().isoformat(),
            "summary": {
                "total_steps": len(self.steps),
                "success": success_count,
                "failed": failed_count,
                "skipped": skipped_count
            },
            "results": {
                step_id: {
                    "status": result.status,
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms
                }
                for step_id, result in self.results.items()
            },
            "final_context": self.context,
            "execution_log": self.log
        }
    
    def get_execution_trace(self) -> str:
        """获取执行轨迹（用于调试和审计）"""
        trace = f"工作流: {self.name} [{self.workflow_id}]\n"
        trace += f"状态: {self.status.value}\n"
        trace += "执行轨迹:\n"
        
        for entry in self.log:
            status_icon = "✅" if entry["status"] == "success" else "❌" if entry["status"] == "failed" else "⏭️"
            trace += f"  {status_icon} {entry['step_name']}: {entry['status']} ({entry['execution_time_ms']}ms)\n"
            if entry.get("error"):
                trace += f"     错误: {entry['error']}\n"
        
        return trace


# 常用工作流模板
class WorkflowTemplates:
    """预定义工作流模板"""
    
    @staticmethod
    def report_generation_workflow() -> TransactionalWorkflow:
        """报告生成工作流"""
        workflow = TransactionalWorkflow("报告生成")
        
        # 步骤1：搜索数据
        workflow.add_step(WorkflowStep(
            id="search",
            name="搜索数据",
            action=lambda ctx: {"data": "搜索到的数据"},
            rollback_action=lambda ctx: print("   清理搜索结果")
        ))
        
        # 步骤2：分析数据（依赖搜索）
        workflow.add_step(WorkflowStep(
            id="analyze",
            name="分析数据",
            action=lambda ctx: {"analysis": f"分析: {ctx.get('search_output', {})}"},
            depends_on=["search"],
            rollback_action=lambda ctx: print("   清理分析结果")
        ))
        
        # 步骤3：生成报告（依赖分析）
        workflow.add_step(WorkflowStep(
            id="generate",
            name="生成报告",
            action=lambda ctx: {"report": f"报告: {ctx.get('analyze_output', {})}"},
            depends_on=["analyze"],
            rollback_action=lambda ctx: print("   删除生成的报告")
        ))
        
        # 步骤4：发送报告（依赖生成）
        workflow.add_step(WorkflowStep(
            id="send",
            name="发送报告",
            action=lambda ctx: {"sent": True, "to": "user"},
            depends_on=["generate"]
            # 发送后不回滚，因为已经发出去了
        ))
        
        return workflow
    
    @staticmethod
    def expert_consultation_workflow() -> TransactionalWorkflow:
        """专家会诊工作流"""
        workflow = TransactionalWorkflow("专家会诊")
        
        # 步骤1：路由到专家
        workflow.add_step(WorkflowStep(
            id="route",
            name="路由到专家",
            action=lambda ctx: {"experts": ["lihonglei", "luohan"]}
        ))
        
        # 步骤2：并行征询意见
        workflow.add_step(WorkflowStep(
            id="consult",
            name="征询专家意见",
            action=lambda ctx: {"opinions": ["专家意见1", "专家意见2"]},
            depends_on=["route"]
        ))
        
        # 步骤3：冲突检测
        workflow.add_step(WorkflowStep(
            id="detect_conflict",
            name="检测冲突",
            action=lambda ctx: {"conflicts": []},
            depends_on=["consult"]
        ))
        
        # 步骤4：生成会诊报告
        workflow.add_step(WorkflowStep(
            id="report",
            name="生成会诊报告",
            action=lambda ctx: {"report": "会诊报告内容"},
            depends_on=["detect_conflict"]
        ))
        
        return workflow


# 便捷函数
def create_workflow(name: str) -> TransactionalWorkflow:
    """创建工作流"""
    return TransactionalWorkflow(name)


def run_report_workflow() -> Dict:
    """运行报告生成工作流"""
    workflow = WorkflowTemplates.report_generation_workflow()
    return workflow.execute()


if __name__ == "__main__":
    # 测试
    print("=== 事务工作流测试 ===\n")
    
    # 测试1：成功场景
    print("测试1: 正常报告生成")
    result = run_report_workflow()
    print(f"\n结果: {result['status']}")
    print(f"成功步骤: {result['summary']['success']}/{result['summary']['total_steps']}")
    
    # 测试2：失败回滚场景
    print("\n\n测试2: 带失败的工作流")
    workflow = TransactionalWorkflow("测试失败")
    
    workflow.add_step(WorkflowStep(
        id="step1",
        name="步骤1",
        action=lambda ctx: "步骤1成功",
        rollback_action=lambda ctx: print("   回滚步骤1")
    ))
    
    workflow.add_step(WorkflowStep(
        id="step2",
        name="步骤2（会失败）",
        action=lambda ctx: (_ for _ in ()).throw(Exception("模拟失败")),
        depends_on=["step1"],
        rollback_action=lambda ctx: print("   回滚步骤2")
    ))
    
    workflow.add_step(WorkflowStep(
        id="step3",
        name="步骤3",
        action=lambda ctx: "步骤3成功",
        depends_on=["step2"]
    ))
    
    result2 = workflow.execute()
    print(f"\n结果: {result2['status']}")
    print(f"执行轨迹:\n{workflow.get_execution_trace()}")
