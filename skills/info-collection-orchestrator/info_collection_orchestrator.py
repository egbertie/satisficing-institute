#!/usr/bin/env python3
"""
信息收集与迭代编排器 V1.0
统一协调所有信息收集活动，确保持续迭代和更新

核心职责:
1. 统筹33位小伙伴的信息收集工作
2. 确保信息持续更新和迭代
3. 管理信息质量和可信度
4. 协调信息分发和使用
"""

import json
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class CollectionTask:
    """信息收集任务"""
    task_id: str
    name: str
    assignee: str  # AI小伙伴ID
    skill_name: str  # 使用的专属Skill
    sources: List[str]  # 信息源列表
    frequency: str  # real-time/hourly/daily/weekly
    output_format: str  # 输出格式
    last_run: str = None
    next_run: str = None
    status: str = "pending"  # pending/running/completed/failed


class InfoCollectionOrchestrator:
    """
    信息收集编排器
    总指挥33位小伙伴的信息收集工作
    """
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.config_dir = self.workspace / "config" / "info_collection"
        self.data_dir = self.workspace / "data" / "collected_info"
        self.log_dir = self.workspace / "logs" / "info_collection"
        
        for d in [self.config_dir, self.data_dir, self.log_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # 33位小伙伴的收集任务配置
        self.collection_tasks = self._init_collection_tasks()
        
        # 收集结果存储
        self.collection_db = self.data_dir / "collection_db.json"
        
        # 统计
        self.stats = {
            "total_collections": 0,
            "total_items_collected": 0,
            "last_24h_items": 0,
            "active_sources": 0
        }
    
    def _init_collection_tasks(self) -> List[CollectionTask]:
        """初始化33位小伙伴的收集任务"""
        tasks = [
            # 信息战略组 - 高频监控
            CollectionTask("T-001", "趋势监控", "AI-001", "trend-hunter-pro",
                          ["TechCrunch", "PitchBook", "ProductHunt"], "hourly", "trend_card"),
            CollectionTask("T-002", "竞争情报", "AI-002", "competitive-intel-analyzer",
                          ["LinkedIn", "工商信息", "新闻"], "daily", "intel_report"),
            CollectionTask("T-003", "历史数据", "AI-003", "historical-data-miner",
                          ["CB Insights", "Crunchbase", "招股书"], "weekly", "pattern_analysis"),
            CollectionTask("T-004", "前沿技术", "AI-004", "frontier-tech-scout",
                          ["arXiv", "Nature", "GitHub"], "daily", "tech_alert"),
            CollectionTask("T-005", "政策监控", "AI-005", "policy-wind-navigator",
                          ["国务院", "发改委", "地方政府"], "daily", "policy_brief"),
            
            # 知识工程组 - 中频更新
            CollectionTask("T-006", "知识图谱更新", "AI-006", "knowledge-architect-pro",
                          ["多源数据"], "daily", "kg_update"),
            CollectionTask("T-007", "文档整理", "AI-007", "intelligent-librarian",
                          ["内部文档", "外部资料"], "daily", "organized_docs"),
            CollectionTask("T-008", "知识融合", "AI-008", "knowledge-fusion-alchemist",
                          ["待融合数据"], "weekly", "fused_knowledge"),
            CollectionTask("T-009", "洞察提炼", "AI-009", "insight-distiller",
                          ["原始信息"], "daily", "insight_cards"),
            CollectionTask("T-010", "可视化更新", "AI-010", "knowledge-visualizer-pro",
                          ["结构化数据"], "weekly", "visual_assets"),
            
            # 决策科学组 - 按需触发
            CollectionTask("T-011", "决策模型更新", "AI-011", "decision-tree-gardener",
                          ["新案例数据"], "weekly", "model_update"),
            CollectionTask("T-012", "风险评估", "AI-012", "risk-radar-operator",
                          ["实时数据"], "daily", "risk_assessment"),
            CollectionTask("T-013", "方案评估", "AI-013", "multi-criteria-assessor",
                          ["决策需求"], "on_demand", "evaluation_report"),
            CollectionTask("T-014", "预测更新", "AI-014", "future-oracle",
                          ["历史+实时数据"], "weekly", "prediction_update"),
            CollectionTask("T-015", "压力测试", "AI-015", "stress-test-engineer",
                          ["场景数据"], "monthly", "stress_report"),
            
            # 内容生产组 - 按内容需求
            CollectionTask("T-016", "故事素材", "AI-016", "story-weaver",
                          ["案例数据"], "weekly", "story_materials"),
            CollectionTask("T-017", "演示更新", "AI-017", "presentation-wizard",
                          ["新内容"], "on_demand", "presentation"),
            CollectionTask("T-018", "研究报告", "AI-018", "research-report-expert",
                          ["研究数据"], "weekly", "research_report"),
            CollectionTask("T-019", "话术更新", "AI-019", "communication-master",
                          ["新场景"], "weekly", "scripts"),
            CollectionTask("T-020", "多语言内容", "AI-020", "multilingual-adapter",
                          ["中文内容"], "on_demand", "localized_content"),
            
            # 系统运营组 - 持续监控
            CollectionTask("T-021", "系统健康", "AI-021", "system-health-doctor",
                          ["系统指标"], "real-time", "health_metrics"),
            CollectionTask("T-022", "日志分析", "AI-022", "log-detective",
                          ["系统日志"], "hourly", "log_report"),
            CollectionTask("T-023", "性能监控", "AI-023", "performance-tuner",
                          ["性能数据"], "hourly", "performance_report"),
            CollectionTask("T-024", "数据备份", "AI-024", "data-guardian",
                          ["所有数据"], "daily", "backup_status"),
            CollectionTask("T-025", "安全监控", "AI-025", "security-sentinel",
                          ["安全日志"], "real-time", "security_alerts"),
            
            # 客户服务组 - 按客户活动
            CollectionTask("T-026", "客户跟踪", "AI-026", "customer-success-butler",
                          ["客户数据"], "daily", "customer_insights"),
            CollectionTask("T-027", "服务监控", "AI-027", "service-gateway-guardian",
                          ["服务指标"], "real-time", "service_metrics"),
            CollectionTask("T-028", "反馈收集", "AI-028", "feedback-alchemist",
                          ["多渠道反馈"], "daily", "feedback_analysis"),
            CollectionTask("T-029", "沟通统计", "AI-029", "multi-messenger-coordinator",
                          ["沟通数据"], "daily", "communication_stats"),
            
            # 架构统筹组 - 按需执行
            CollectionTask("T-030", "代码审查", "AI-030", "code-quality-judge",
                          ["代码库"], "on_commit", "quality_report"),
            CollectionTask("T-031", "架构检查", "AI-031", "architecture-consistency-guardian",
                          ["系统架构"], "weekly", "architecture_report"),
            CollectionTask("T-032", "版本管理", "AI-032", "release-commander",
                          ["版本数据"], "on_release", "release_notes"),
            CollectionTask("T-033", "全局统筹", "AI-033", "strategic-coordinator",
                          ["所有数据"], "daily", "strategic_dashboard"),
        ]
        
        return tasks
    
    def run_collection_cycle(self):
        """运行一轮信息收集"""
        print(f"\n{'='*70}")
        print(f"🔄 信息收集周期启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        # 检查哪些任务需要执行
        tasks_to_run = self._get_due_tasks()
        
        print(f"\n📋 本次需执行任务: {len(tasks_to_run)} 个")
        
        # 并行执行（简化版，实际应使用异步）
        for task in tasks_to_run:
            self._execute_task(task)
        
        # 更新统计
        self._update_stats()
        
        print(f"\n✅ 信息收集周期完成")
        print(f"   收集项目: {self.stats['last_24h_items']}")
        print(f"   活跃信源: {self.stats['active_sources']}")
    
    def _get_due_tasks(self) -> List[CollectionTask]:
        """获取到期的任务"""
        now = datetime.now()
        due_tasks = []
        
        for task in self.collection_tasks:
            if task.next_run is None:
                due_tasks.append(task)
                continue
            
            next_run = datetime.fromisoformat(task.next_run)
            if now >= next_run:
                due_tasks.append(task)
        
        return due_tasks
    
    def _execute_task(self, task: CollectionTask):
        """执行单个收集任务"""
        print(f"\n▶️ 执行任务 [{task.task_id}]: {task.name}")
        print(f"   负责人: {task.assignee} | Skill: {task.skill_name}")
        
        task.status = "running"
        task.last_run = datetime.now().isoformat()
        
        try:
            # 模拟执行（实际调用对应小伙伴的Skill）
            # result = self._call_skill(task.skill_name, task.sources)
            
            # 更新下次执行时间
            task.next_run = self._calculate_next_run(task.frequency)
            task.status = "completed"
            
            self.stats["total_collections"] += 1
            
            print(f"   ✅ 完成 - 下次执行: {task.next_run}")
            
        except Exception as e:
            task.status = "failed"
            print(f"   ❌ 失败: {e}")
    
    def _calculate_next_run(self, frequency: str) -> str:
        """计算下次执行时间"""
        now = datetime.now()
        
        if frequency == "real-time":
            next_run = now + timedelta(minutes=5)
        elif frequency == "hourly":
            next_run = now + timedelta(hours=1)
        elif frequency == "daily":
            next_run = now + timedelta(days=1)
        elif frequency == "weekly":
            next_run = now + timedelta(weeks=1)
        elif frequency == "monthly":
            next_run = now + timedelta(days=30)
        else:  # on_demand
            next_run = now + timedelta(days=7)  # 默认一周后检查
        
        return next_run.isoformat()
    
    def get_collection_status(self) -> Dict:
        """获取收集状态"""
        status = {
            "total_tasks": len(self.collection_tasks),
            "by_frequency": {},
            "by_status": {},
            "recent_activity": []
        }
        
        for task in self.collection_tasks:
            # 按频率统计
            freq = task.frequency
            status["by_frequency"][freq] = status["by_frequency"].get(freq, 0) + 1
            
            # 按状态统计
            st = task.status
            status["by_status"][st] = status["by_status"].get(st, 0) + 1
        
        return status
    
    def _update_stats(self):
        """更新统计"""
        # 计算过去24小时的收集量
        # 实际应从数据库统计
        self.stats["last_24h_items"] = self.stats.get("last_24h_items", 0) + 10
        self.stats["active_sources"] = len(set(
            source for task in self.collection_tasks for source in task.sources
        ))
    
    def generate_daily_report(self) -> str:
        """生成每日收集报告"""
        status = self.get_collection_status()
        
        report = f"""# 信息收集日报

**日期**: {datetime.now().strftime('%Y-%m-%d')}  
**生成时间**: {datetime.now().strftime('%H:%M:%S')}

---

## 📊 今日概况

- 总任务数: {status['total_tasks']}
- 实时监控: {status['by_frequency'].get('real-time', 0)} 个
- 每小时更新: {status['by_frequency'].get('hourly', 0)} 个
- 每日更新: {status['by_frequency'].get('daily', 0)} 个
- 每周更新: {status['by_frequency'].get('weekly', 0)} 个

---

## 👥 各组任务分布

| 组别 | 任务数 | 主要频率 |
|------|--------|---------|
| 信息战略组 | 5 | 实时监控 |
| 知识工程组 | 5 | 每日更新 |
| 决策科学组 | 5 | 按需执行 |
| 内容生产组 | 5 | 内容驱动 |
| 系统运营组 | 5 | 持续监控 |
| 客户服务组 | 4 | 客户驱动 |
| 架构统筹组 | 4 | 质量驱动 |

---

## ✅ 状态统计

- 待执行: {status['by_status'].get('pending', 0)}
- 执行中: {status['by_status'].get('running', 0)}
- 已完成: {status['by_status'].get('completed', 0)}
- 失败: {status['by_status'].get('failed', 0)}

---

## 📝 今日关键收集

（此处列出今日收集的重要信息摘要）

---

*由信息收集编排器自动生成*
"""
        
        return report


# 运行示例
if __name__ == "__main__":
    orchestrator = InfoCollectionOrchestrator()
    
    # 运行一轮收集
    orchestrator.run_collection_cycle()
    
    # 打印状态
    print("\n" + "="*70)
    print("收集状态:")
    status = orchestrator.get_collection_status()
    print(f"  总任务: {status['total_tasks']}")
    print(f"  按频率: {status['by_frequency']}")
    print(f"  按状态: {status['by_status']}")
