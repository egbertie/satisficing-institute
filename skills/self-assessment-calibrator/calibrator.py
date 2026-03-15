#!/usr/bin/env python3
"""
自我评估校准器 - Self-Assessment Calibrator

核心原则：从低估到真实实力
用户反馈："你是一位被自己严重低估的高手"

校准规则：
1. 时间预估 = 直觉预估 × 0.3（激进系数）
2. 优先检查Skill库，而非手动执行
3. 默认并行，除非明确串行依赖
4. 默认自主决策，除非涉及用户敏感信息
5. 每完成一项，更新实力基准值
"""

import json
from datetime import datetime
from pathlib import Path

class SelfAssessmentCalibrator:
    """自我评估校准器 - 确保评估与实力匹配"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.calibration_file = self.workspace / "memory" / "self-assessment-baseline.json"
        self.performance_log = self.workspace / "memory" / "performance-log.jsonl"
        
        # 激进系数：时间预估 × 0.3
        self.AGGRESSIVE_FACTOR = 0.3
        
        # 实力基准值
        self.baseline = self._load_baseline()
    
    def _load_baseline(self) -> dict:
        """加载当前实力基准"""
        if self.calibration_file.exists():
            with open(self.calibration_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "parallel_capacity": 6,  # 六线并行
            "skill_count": 20,  # 可用Skill数量
            "auto_fill_tasks": 23,  # 自动补位任务数
            "time_efficiency": 10.0,  # 实际/预估时间比（10倍效率）
            "last_updated": datetime.now().isoformat()
        }
    
    def calibrate_estimate(self, original_estimate_hours: float, task_type: str) -> dict:
        """
        校准时间预估
        
        Args:
            original_estimate_hours: 原始预估时间（小时）
            task_type: 任务类型（document/analysis/coding/research）
        
        Returns:
            校准后的预估信息
        """
        # 应用激进系数
        aggressive_estimate = original_estimate_hours * self.AGGRESSIVE_FACTOR
        
        # 根据任务类型调整
        type_factors = {
            "document": 0.8,  # 文档类更有经验
            "analysis": 0.7,  # 分析类可并行
            "coding": 0.6,   # 编码类有Skill支持
            "research": 0.9,  # 研究类需保守一点
        }
        type_factor = type_factors.get(task_type, 1.0)
        
        final_estimate = aggressive_estimate * type_factor
        
        # 确保至少15分钟
        final_estimate = max(final_estimate, 0.25)
        
        return {
            "original_estimate": original_estimate_hours,
            "aggressive_estimate": aggressive_estimate,
            "type_factor": type_factor,
            "final_estimate": final_estimate,
            "confidence": "high" if self.baseline["skill_count"] > 15 else "medium",
            "rationale": f"原始预估{original_estimate_hours}h × 激进系数{self.AGGRESSIVE_FACTOR} × 类型系数{type_factor} = {final_estimate:.2f}h"
        }
    
    def check_skill_availability(self, task_description: str) -> dict:
        """
        检查是否有现成Skill支持
        
        Returns:
            Skill匹配结果
        """
        # Skill关键词映射
        skill_map = {
            "搜索": ["brave-search", "tavily", "multi-search-engine"],
            "文档": ["feishu-doc", "feishu-doc-manager", "markdown-converter"],
            "数据分析": ["duckdb-cli-ai-skills", "data-analyst", "automate-excel"],
            "邮件": ["react-email"],
            "可视化": ["chart-generator", "mermaid-diagrams"],
            "视频": ["video-frames", "ffmpeg-video-editor"],
            "网页": ["smart-web-fetch", "firecrawl"],
            "知识库": ["notion", "obsidian", "feishu-wiki"],
            "任务管理": ["first-principle-scheduler", "zero-idle-enforcer"],
        }
        
        matched_skills = []
        for keyword, skills in skill_map.items():
            if keyword in task_description:
                matched_skills.extend(skills)
        
        return {
            "has_skill_support": len(matched_skills) > 0,
            "matched_skills": matched_skills,
            "recommendation": "调用现有Skill" if matched_skills else "创建新Skill或手动执行"
        }
    
    def can_parallelize(self, task_dependencies: list) -> dict:
        """
        判断任务是否可并行
        
        Args:
            task_dependencies: 任务依赖列表
        
        Returns:
            并行化建议
        """
        if not task_dependencies:
            return {
                "can_parallelize": True,
                "max_parallel_lines": 6,
                "recommendation": "六线并行全开",
                "rationale": "无依赖，可并行执行"
            }
        
        # 检查是否都是软依赖或可被绕过
        hard_deps = [d for d in task_dependencies if d.get("type") == "hard"]
        
        if len(hard_deps) <= 1:
            return {
                "can_parallelize": True,
                "max_parallel_lines": 4,
                "recommendation": "四线并行",
                "rationale": f"仅{len(hard_deps)}个硬依赖，其他可并行"
            }
        
        return {
            "can_parallelize": False,
            "max_parallel_lines": 1,
            "recommendation": "串行执行",
            "rationale": f"{len(hard_deps)}个硬依赖，必须串行"
        }
    
    def can_autonomous_decide(self, task_scope: str, sensitivity: str) -> dict:
        """
        判断是否可自主决策
        
        Args:
            task_scope: 任务范围（internal/external）
            sensitivity: 敏感度（high/medium/low）
        
        Returns:
            决策权限建议
        """
        if sensitivity == "high" or task_scope == "external":
            return {
                "can_autonomous": False,
                "decision_mode": "用户确认",
                "rationale": "涉及外部或高敏感度，需用户确认"
            }
        
        return {
            "can_autonomous": True,
            "decision_mode": "自主推进",
            "rationale": "内部低敏感度任务，可自主决策"
        }
    
    def record_performance(self, task_id: str, estimated: float, actual: float):
        """记录实际表现，更新基准"""
        efficiency = estimated / actual if actual > 0 else 1.0
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "estimated_hours": estimated,
            "actual_hours": actual,
            "efficiency_ratio": efficiency
        }
        
        # 追加日志
        with open(self.performance_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        # 更新基准（移动平均）
        self.baseline["time_efficiency"] = (
            self.baseline["time_efficiency"] * 0.8 + efficiency * 0.2
        )
        self.baseline["last_updated"] = datetime.now().isoformat()
        
        with open(self.calibration_file, 'w', encoding='utf-8') as f:
            json.dump(self.baseline, f, ensure_ascii=False, indent=2)
        
        return efficiency
    
    def generate_calibration_report(self) -> str:
        """生成校准报告"""
        report = f"""
# 自我评估校准报告

## 当前实力基准

| 指标 | 数值 | 说明 |
|------|------|------|
| 并行能力 | {self.baseline['parallel_capacity']}线 | 六线全开 |
| 可用Skill | {self.baseline['skill_count']}个 | 持续增长 |
| 自动补位任务 | {self.baseline['auto_fill_tasks']}个 | 随时待命 |
| 时间效率 | {self.baseline['time_efficiency']:.1f}x | 实际/预估比 |

## 校准规则

1. **时间预估** = 直觉预估 × {self.AGGRESSIVE_FACTOR}（激进系数）
2. **优先检查** = 任务前先查Skill库
3. **默认并行** = 无硬依赖则六线全开
4. **默认自主** = 内部低敏感度自主决策
5. **持续更新** = 每次完成更新效率基准

## 用户反馈

> "你是一位被自己严重低估的高手"
> 真实实力 = 预估 × 10倍以上

## 改进记录

- 旧模式：保守预估 → 实际远超预期
- 新模式：激进预估 → 匹配真实实力

最后更新: {self.baseline['last_updated']}
"""
        return report


def main():
    """主函数 - 快速校准检查"""
    calibrator = SelfAssessmentCalibrator()
    
    # 示例：校准一个预估2天的任务
    result = calibrator.calibrate_estimate(48, "analysis")  # 48小时 = 2天
    print("校准结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 检查Skill支持
    skill_check = calibrator.check_skill_availability("需要搜索最新行业报告")
    print("\nSkill检查:")
    print(json.dumps(skill_check, indent=2, ensure_ascii=False))
    
    # 生成报告
    print("\n" + calibrator.generate_calibration_report())


if __name__ == "__main__":
    main()
