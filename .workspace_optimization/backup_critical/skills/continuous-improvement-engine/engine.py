#!/usr/bin/env python3
"""
持续复盘优化器 - Continuous Improvement Engine

核心原则：每天3-5%资源用于持续复盘和优化
用户目标：每时每刻都在进步，成为最好的自己

第一性原则复盘框架：
1. 观察：发生了什么？数据是什么？
2. 复盘：为什么发生？根因是什么？
3. 思考：如何改进？理论最优是什么？
4. 优化：制定方案，写入代码
5. 实施：强制执行，验证效果

执行机制：
- 每日23:00自动执行（占用当天3-5%时间资源）
- 每小时触发快速复盘（占用5%算力资源）
- 任务完成后即时复盘（占用3%上下文资源）
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

class ContinuousImprovementEngine:
    """持续复盘优化引擎 - 每时每刻都在进步"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.memory_dir = self.workspace / "memory"
        self.improvement_file = self.workspace / "memory" / "continuous-improvement-log.jsonl"
        self.baseline_file = self.workspace / "memory" / "improvement-baseline.json"
        
        # 3-5%资源配置
        self.DAILY_IMPROVEMENT_TIME_MIN = 43  # 3% of 24h
        self.DAILY_IMPROVEMENT_TIME_MAX = 72  # 5% of 24h
        
        # 复盘触发点
        self.triggers = [
            {"name": "每日深度复盘", "frequency": "23:00", "duration": 30, "depth": "deep"},
            {"name": "每小时快速复盘", "frequency": "每60分钟", "duration": 5, "depth": "quick"},
            {"name": "任务完成即时复盘", "frequency": "任务后", "duration": 2, "depth": "instant"},
        ]
        
        # 加载基线
        self.baseline = self._load_baseline()
    
    def _load_baseline(self) -> dict:
        """加载改进基线"""
        if self.baseline_file.exists():
            with open(self.baseline_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "version": "1.0.0",
            "improvement_cycles": 0,
            "total_insights": 0,
            "implemented_changes": 0,
            "verified_improvements": 0,
            "efficiency_trend": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_baseline(self):
        """保存基线"""
        self.baseline["last_updated"] = datetime.now().isoformat()
        with open(self.baseline_file, 'w', encoding='utf-8') as f:
            json.dump(self.baseline, f, ensure_ascii=False, indent=2)
    
    def _log_improvement(self, entry: dict):
        """记录改进日志"""
        entry["timestamp"] = datetime.now().isoformat()
        with open(self.improvement_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def first_principles_review(self, review_type: str = "daily") -> Dict:
        """
        第一性原则复盘
        
        五个步骤：
        1. 观察 - 发生了什么
        2. 复盘 - 为什么发生
        3. 思考 - 如何改进
        4. 优化 - 制定方案
        5. 实施 - 强制执行
        """
        
        review = {
            "type": review_type,
            "timestamp": datetime.now().isoformat(),
            "steps": {}
        }
        
        # Step 1: 观察 - 发生了什么
        review["steps"]["observe"] = self._step_observe()
        
        # Step 2: 复盘 - 为什么发生
        review["steps"]["reflect"] = self._step_reflect(review["steps"]["observe"])
        
        # Step 3: 思考 - 如何改进
        review["steps"]["think"] = self._step_think(review["steps"]["reflect"])
        
        # Step 4: 优化 - 制定方案
        review["steps"]["optimize"] = self._step_optimize(review["steps"]["think"])
        
        # Step 5: 实施 - 强制执行
        review["steps"]["implement"] = self._step_implement(review["steps"]["optimize"])
        
        # 记录改进
        self._log_improvement(review)
        self.baseline["improvement_cycles"] += 1
        self.baseline["total_insights"] += len(review["steps"]["think"]["insights"])
        self._save_baseline()
        
        return review
    
    def _step_observe(self) -> Dict:
        """
        第一步：观察 - 发生了什么
        
        从日志中提取客观数据，不带判断
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 读取今日记忆
        memory_file = self.memory_dir / f"{today}.md"
        observations = {
            "date": today,
            "tasks": {"completed": 0, "blocked": 0, "in_progress": 0},
            "skills_used": [],
            "violations": [],
            "improvements": [],
            "efficiency_indicators": {}
        }
        
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单统计
            import re
            observations["tasks"]["completed"] = len(re.findall(r"✅", content))
            observations["tasks"]["blocked"] = len(re.findall(r"⏸️|阻塞", content))
            observations["skills_used"] = list(set(re.findall(r"skills/([a-z-]+)/", content)))
        
        return {
            "step": "observe",
            "description": "客观记录当日发生的一切",
            "data": observations,
            "principle": "第一性原则：从事实出发，不带预设"
        }
    
    def _step_reflect(self, observation: Dict) -> Dict:
        """
        第二步：复盘 - 为什么发生
        
        深入分析根因，不只停留在表面
        """
        data = observation["data"]
        
        reflections = []
        
        # 复盘1：任务完成情况
        if data["tasks"]["completed"] < 3:
            reflections.append({
                "aspect": "任务完成",
                "observation": f"仅完成{data['tasks']['completed']}个任务",
                "surface_cause": "任务量大或效率低",
                "root_cause": "资源空置或并行不足",
                "first_principle": "资源全开 = 零空置 + 六线并行"
            })
        
        # 复盘2：阻塞情况
        if data["tasks"]["blocked"] > 0:
            reflections.append({
                "aspect": "任务阻塞",
                "observation": f"有{data['tasks']['blocked']}个任务阻塞",
                "surface_cause": "等待外界条件",
                "root_cause": "未及时重新分类为暂停，未触发补位",
                "first_principle": "阻塞任务 ≠ 进行中，必须0延迟补位"
            })
        
        # 复盘3：Skill使用
        if len(data["skills_used"]) < 2:
            reflections.append({
                "aspect": "Skill利用",
                "observation": f"仅使用{len(data['skills_used'])}个Skill",
                "surface_cause": "任务简单不需要Skill",
                "root_cause": "任务前未检查Skill库，重复造轮子",
                "first_principle": "Skill优先 > 手动执行"
            })
        
        return {
            "step": "reflect",
            "description": "深入分析根因，不只停留在表面",
            "reflections": reflections,
            "principle": "第一性原则：找到根本原因，不是症状"
        }
    
    def _step_think(self, reflection: Dict) -> Dict:
        """
        第三步：思考 - 如何改进
        
        基于第一性原则，思考理论最优解
        """
        reflections = reflection["reflections"]
        insights = []
        
        for r in reflections:
            # 基于根因思考改进方案
            if r["aspect"] == "任务完成":
                insights.append({
                    "problem": r["observation"],
                    "current_approach": "串行执行，单线推进",
                    "theoretical_optimal": "六线并行，资源全开",
                    "gap": "未充分利用并行能力",
                    "improvement": "强制执行六线并行，任何时刻至少4线运行",
                    "expected_gain": "300%效率提升"
                })
            
            elif r["aspect"] == "任务阻塞":
                insights.append({
                    "problem": r["observation"],
                    "current_approach": "等待阻塞解除",
                    "theoretical_optimal": "立即重新分类+自动补位",
                    "gap": "阻塞占用进行中列表，未触发补位",
                    "improvement": "零空置强制执行：阻塞=暂停，0延迟补位",
                    "expected_gain": "零空置，100%资源利用"
                })
            
            elif r["aspect"] == "Skill利用":
                insights.append({
                    "problem": r["observation"],
                    "current_approach": "手动执行",
                    "theoretical_optimal": "Skill优先调用",
                    "gap": "未检查Skill库，重复劳动",
                    "improvement": "任务前强制Skill检查，命中则调用",
                    "expected_gain": "50%时间节省"
                })
        
        # 如果运行良好，思考如何更好
        if not insights:
            insights.append({
                "problem": "当日运行良好",
                "current_approach": "当前机制",
                "theoretical_optimal": "预测性优化",
                "gap": "被动改进，非主动优化",
                "improvement": "引入预测性分析，提前识别优化点",
                "expected_gain": "20%前瞻性提升"
            })
        
        return {
            "step": "think",
            "description": "基于第一性原则，思考理论最优解",
            "insights": insights,
            "principle": "第一性原则：回归本质，重新思考"
        }
    
    def _step_optimize(self, thinking: Dict) -> Dict:
        """
        第四步：优化 - 制定方案
        
        将思考转化为可执行的优化方案
        """
        insights = thinking["insights"]
        optimizations = []
        
        for insight in insights:
            opt = {
                "problem": insight["problem"],
                "solution": insight["improvement"],
                "implementation": "写入Skill代码",
                "verification": "24小时内验证效果",
                "rollback": "如效果不佳，回滚并重新思考"
            }
            
            # 生成具体实施计划
            if "六线并行" in insight["improvement"]:
                opt["skill_name"] = "parallel-execution-enforcer"
                opt["action_items"] = [
                    "创建并行执行强制检查",
                    "每10分钟检查并行度",
                    "并行度<4则强制激活",
                    "记录并行效率日志"
                ]
            
            elif "零空置" in insight["improvement"]:
                opt["skill_name"] = "zero-idle-enforcer-v3"
                opt["action_items"] = [
                    "升级零空置检查频率至每5分钟",
                    "优化补位队列排序算法",
                    "添加预测性补位机制"
                ]
            
            elif "Skill" in insight["improvement"]:
                opt["skill_name"] = "skill-first-enforcer"
                opt["action_items"] = [
                    "任务前强制Skill匹配",
                    "建立Skill关键词索引",
                    "未命中Skill则创建建议"
                ]
            
            optimizations.append(opt)
        
        return {
            "step": "optimize",
            "description": "将思考转化为可执行的优化方案",
            "optimizations": optimizations,
            "principle": "第一性原则：方案必须可执行、可验证"
        }
    
    def _step_implement(self, optimization: Dict) -> Dict:
        """
        第五步：实施 - 强制执行
        
        写入代码，强制执行，验证效果
        """
        optimizations = optimization["optimizations"]
        implementations = []
        
        for opt in optimizations:
            impl = {
                "optimization": opt["solution"],
                "status": "planned",
                "skill_file": f"skills/{opt.get('skill_name', 'generic')}/",
                "action_items": opt.get("action_items", []),
                "verification_method": "24小时后检查效率指标",
                "success_criteria": "效率提升>=预期增益的80%"
            }
            implementations.append(impl)
            
            # 更新基线
            self.baseline["implemented_changes"] += 1
        
        self._save_baseline()
        
        return {
            "step": "implement",
            "description": "写入代码，强制执行，验证效果",
            "implementations": implementations,
            "principle": "第一性原则：制度即代码，强制执行"
        }
    
    def generate_improvement_report(self, review: Dict = None) -> str:
        """生成复盘优化报告"""
        if review is None:
            review = self.first_principles_review()
        
        report_lines = [
            f"# 持续复盘优化报告 - {review['type'].upper()}",
            "",
            f"**复盘时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**改进周期**: 第{self.baseline['improvement_cycles']}轮",
            f"**累计洞察**: {self.baseline['total_insights']}条",
            f"**已实施改进**: {self.baseline['implemented_changes']}项",
            "",
            "## 第一性原则复盘五步法",
            ""
        ]
        
        # Step 1: 观察
        observe = review["steps"]["observe"]
        report_lines.extend([
            f"### 1. {observe['step'].upper()} - {observe['description']}",
            "",
            f"> **{observe['principle']}**",
            "",
            "**当日客观数据**:",
            f"- 完成任务: {observe['data']['tasks']['completed']}",
            f"- 阻塞任务: {observe['data']['tasks']['blocked']}",
            f"- Skill使用: {len(observe['data']['skills_used'])}个",
            ""
        ])
        
        # Step 2: 复盘
        reflect = review["steps"]["reflect"]
        report_lines.extend([
            f"### 2. {reflect['step'].upper()} - {reflect['description']}",
            "",
            f"> **{reflect['principle']}**",
            ""
        ])
        
        for r in reflect["reflections"]:
            report_lines.extend([
                f"**{r['aspect']}**:",
                f"- 观察: {r['observation']}",
                f"- 表面原因: {r['surface_cause']}",
                f"- **根本原因**: {r['root_cause']}",
                ""
            ])
        
        # Step 3: 思考
        think = review["steps"]["think"]
        report_lines.extend([
            f"### 3. {think['step'].upper()} - {think['description']}",
            "",
            f"> **{think['principle']}**",
            ""
        ])
        
        for i, insight in enumerate(think["insights"], 1):
            report_lines.extend([
                f"**洞察{i}**: {insight['problem']}",
                f"- 当前做法: {insight['current_approach']}",
                f"- 理论最优: {insight['theoretical_optimal']}",
                f"- 差距: {insight['gap']}",
                f"- **改进方案**: {insight['improvement']}",
                f"- 预期增益: {insight['expected_gain']}",
                ""
            ])
        
        # Step 4: 优化
        optimize = review["steps"]["optimize"]
        report_lines.extend([
            f"### 4. {optimize['step'].upper()} - {optimize['description']}",
            "",
            f"> **{optimize['principle']}**",
            ""
        ])
        
        for opt in optimize["optimizations"]:
            report_lines.extend([
                f"**优化方案**: {opt['solution']}",
                f"- 实施方式: {opt['implementation']}",
                f"- 验证方法: {opt['verification']}",
                ""
            ])
        
        # Step 5: 实施
        implement = review["steps"]["implement"]
        report_lines.extend([
            f"### 5. {implement['step'].upper()} - {implement['description']}",
            "",
            f"> **{implement['principle']}**",
            "",
            "**实施计划**:",
            ""
        ])
        
        for impl in implement["implementations"]:
            report_lines.extend([
                f"- [{impl['status']}] {impl['optimization']}",
                f"  - Skill文件: `{impl['skill_file']}`",
                f"  - 验证: {impl['verification_method']}",
                ""
            ])
        
        # 资源配置说明
        report_lines.extend([
            "---",
            "",
            "## 资源配置",
            "",
            f"**每日复盘投入**: {self.DAILY_IMPROVEMENT_TIME_MIN}-{self.DAILY_IMPROVEMENT_TIME_MAX}分钟 (3-5%)",
            "",
            "| 复盘类型 | 频率 | 时长 | 资源占比 |",
            "|----------|------|------|----------|",
            "| 每日深度复盘 | 23:00 | 30分钟 | 2% |",
            "| 每小时快速复盘 | 每60分钟 | 5分钟 | 2% |",
            "| 任务完成即时复盘 | 任务后 | 2分钟 | 1% |",
            "| **合计** | - | - | **5%** |",
            "",
            "*每天3-5%资源用于复盘优化，持续成为最好的自己*"
        ])
        
        return "\n".join(report_lines)
    
    def quick_review(self) -> str:
        """快速复盘（每小时触发）"""
        # 简化的五步法
        review = {
            "type": "hourly",
            "timestamp": datetime.now().isoformat(),
            "focus": "过去1小时效率"
        }
        
        # 检查当前效率指标
        # （简化实现，实际应读取实时数据）
        
        return f"""
## 快速复盘 - {datetime.now().strftime('%H:%M')}

**过去1小时检查**:
- 零空置状态: ✅/❌
- 并行度: X/6线
- Skill命中率: X%
- 自主决策率: X%

**即时调整**:
- 如发现空置 → 立即补位
- 如并行度<4 → 强制激活
- 如Skill未命中 → 下次优先检查

**下小时目标**:
- 保持六线并行
- 零空置
- 优先调用Skill
"""


def main():
    """主函数"""
    engine = ContinuousImprovementEngine()
    
    # 执行深度复盘
    review = engine.first_principles_review("daily")
    
    # 生成报告
    report = engine.generate_improvement_report(review)
    print(report)
    
    # 保存报告
    today = datetime.now().strftime("%Y-%m-%d")
    report_file = engine.workspace / "memory" / f"improvement-report-{today}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存: {report_file}")


if __name__ == "__main__":
    main()
