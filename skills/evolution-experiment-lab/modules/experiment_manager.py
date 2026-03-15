#!/usr/bin/env python3
"""
Evolution Experiment Lab - 进化实验实验室
支持隔离测试、小范围试点、数据驱动决策
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

class ExperimentStatus(Enum):
    DESIGN = "design"           # 设计阶段
    ISOLATION_TEST = "isolation"  # 隔离测试
    PILOT = "pilot"             # 小范围试点
    EVALUATION = "evaluation"   # 评估阶段
    PROMOTED = "promoted"       # 已推广
    ROLLED_BACK = "rolled_back" # 已回滚

class ExperimentManager:
    """实验管理器"""
    
    def __init__(self, 
                 workspace_path: str = '/root/.openclaw/workspace',
                 experiments_dir: str = 'experiments'):
        self.workspace = Path(workspace_path)
        self.experiments_dir = self.workspace / experiments_dir
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建模板目录
        self.template_dir = self.experiments_dir / '_template'
        self.template_dir.mkdir(exist_ok=True)
    
    def create_experiment(self, design: Dict[str, Any]) -> str:
        """创建新实验"""
        # 生成实验ID
        exp_id = self._generate_exp_id()
        exp_dir = self.experiments_dir / exp_id
        exp_dir.mkdir()
        
        # 创建实验结构
        (exp_dir / 'isolation-test').mkdir()
        (exp_dir / 'pilot').mkdir()
        
        # 保存设计文档
        design_data = {
            'experiment_id': exp_id,
            'created_at': datetime.now().isoformat(),
            'status': ExperimentStatus.DESIGN.value,
            **design
        }
        
        design_file = exp_dir / 'experiment-design.md'
        design_file.write_text(self._generate_design_doc(design_data))
        
        # 初始化结果文档
        results_file = exp_dir / 'results.md'
        results_file.write_text(f"# 实验结果: {exp_id}\n\n待填写...\n")
        
        print(f"实验已创建: {exp_id}")
        return exp_id
    
    def _generate_exp_id(self) -> str:
        """生成实验ID"""
        existing = [d.name for d in self.experiments_dir.iterdir() if d.is_dir()]
        numbers = [int(d.split('-')[1]) for d in existing if d.startswith('EXP-') and d.split('-')[1].isdigit()]
        next_num = max(numbers, default=0) + 1
        return f"EXP-{next_num:03d}"
    
    def _generate_design_doc(self, design: Dict) -> str:
        """生成设计文档"""
        return f"""# 实验设计: {design['experiment_id']}

## 基本信息
- 实验ID: {design['experiment_id']}
- 创建时间: {design['created_at']}
- 实验名称: {design.get('name', '未命名')}

## 实验目标
{design.get('goal', '待填写')}

## 成功指标
{design.get('metrics', '待填写')}

## 实验方案
{design.get('plan', '待填写')}

## 风险评估
{design.get('risks', '待填写')}

## 回滚计划
{design.get('rollback_plan', '待填写')}

---
*状态: {design['status']}*
"""
    
    def update_status(self, exp_id: str, status: ExperimentStatus, notes: str = ''):
        """更新实验状态"""
        exp_dir = self.experiments_dir / exp_id
        if not exp_dir.exists():
            raise ExperimentError(f"实验 {exp_id} 不存在")
        
        # 更新设计文档中的状态
        design_file = exp_dir / 'experiment-design.md'
        content = design_file.read_text()
        content = content.replace(
            f"*状态: {ExperimentStatus.DESIGN.value}*",
            f"*状态: {status.value}*"
        )
        design_file.write_text(content)
        
        # 记录状态变更
        log_file = exp_dir / 'status-log.txt'
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()}: {status.value} - {notes}\n")
        
        print(f"实验 {exp_id} 状态更新为: {status.value}")
    
    def evaluate_experiment(self, exp_id: str, result_data: Dict) -> Dict[str, Any]:
        """评估实验结果"""
        exp_dir = self.experiments_dir / exp_id
        
        # 生成评估报告
        evaluation = {
            'experiment_id': exp_id,
            'evaluated_at': datetime.now().isoformat(),
            'success_metrics': result_data.get('metrics', {}),
            'decision': result_data.get('decision', 'pending'),
            'reason': result_data.get('reason', ''),
            'next_steps': result_data.get('next_steps', [])
        }
        
        # 保存结果
        results_file = exp_dir / 'results.md'
        results_file.write_text(self._generate_results_doc(evaluation))
        
        return evaluation
    
    def _generate_results_doc(self, evaluation: Dict) -> str:
        """生成结果文档"""
        return f"""# 实验结果: {evaluation['experiment_id']}

## 执行摘要
- 评估时间: {evaluation['evaluated_at']}
- 决策: {evaluation['decision']}

## 指标对比
{json.dumps(evaluation['success_metrics'], indent=2)}

## 决策依据
{evaluation['reason']}

## 后续行动
{chr(10).join(f"- {step}" for step in evaluation['next_steps'])}

---
*实验完成*
"""
    
    def list_experiments(self, status: Optional[ExperimentStatus] = None) -> List[Dict[str, Any]]:
        """列出实验"""
        experiments = []
        
        for exp_dir in self.experiments_dir.iterdir():
            if not exp_dir.is_dir() or exp_dir.name == '_template':
                continue
            
            design_file = exp_dir / 'experiment-design.md'
            if design_file.exists():
                experiments.append({
                    'id': exp_dir.name,
                    'status': 'unknown',  # 简化
                    'created': datetime.fromtimestamp(exp_dir.stat().st_ctime).isoformat()
                })
        
        return experiments
    
    def generate_weekly_report(self) -> str:
        """生成周报"""
        experiments = self.list_experiments()
        
        lines = [
            "# 实验周报",
            f"生成时间: {datetime.now().isoformat()}",
            "",
            f"## 实验总览",
            f"- 总实验数: {len(experiments)}",
            "",
            "## 活跃实验",
        ]
        
        for exp in experiments:
            lines.append(f"- {exp['id']} ({exp['status']})")
        
        return "\n".join(lines)


class ExperimentError(Exception):
    """实验错误"""
    pass


def main():
    """命令行入口"""
    import sys
    
    manager = ExperimentManager()
    
    task = sys.argv[1] if len(sys.argv) > 1 else 'list'
    
    if task == 'create-experiment':
        # 示例设计
        design = {
            'name': '示例实验',
            'goal': '验证新功能',
            'metrics': '成功率 > 90%',
            'plan': '1. 隔离测试 2. 试点',
            'risks': '低风险',
            'rollback_plan': '一键回滚'
        }
        exp_id = manager.create_experiment(design)
        print(f"实验创建成功: {exp_id}")
        
    elif task == 'list':
        experiments = manager.list_experiments()
        print(f"共有 {len(experiments)} 个实验:")
        for exp in experiments:
            print(f"  - {exp['id']}: {exp['status']}")
    
    elif task == 'check-experiments':
        experiments = manager.list_experiments()
        print(f"检查完成。当前 {len(experiments)} 个实验")
    
    elif task == 'weekly-report':
        report = manager.generate_weekly_report()
        print(report)
    
    else:
        print(f"未知任务: {task}")
        sys.exit(1)


if __name__ == '__main__':
    main()
