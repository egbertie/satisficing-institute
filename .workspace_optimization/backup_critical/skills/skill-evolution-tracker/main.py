#!/usr/bin/env python3
"""
技能进化追踪器 (Skill Evolution Tracker)
功能：追踪每个Skill的使用频率和效果
指标：调用次数、成功率、用户满意度、迭代次数
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict


@dataclass
class SkillMetrics:
    """Skill指标数据"""
    skill_name: str
    version: str
    total_calls: int
    success_calls: int
    failed_calls: int
    avg_response_time: float  # 毫秒
    user_satisfaction: float  # 0-100
    last_used: str
    first_used: str
    iteration_count: int
    daily_stats: Dict[str, Dict]  # 按天统计


@dataclass
class SkillEvaluation:
    """Skill评估结果"""
    skill_name: str
    health_score: float  # 0-100 健康度
    usage_level: str  # 高/中/低/未使用
    quality_level: str  # 优秀/良好/一般/需改进
    trends: Dict[str, str]  # 趋势：上升/下降/稳定
    recommendations: List[str]
    evolution_status: str  # 成熟/成长/衰退/新建


@dataclass
class TrackingReport:
    """追踪报告"""
    scan_time: str
    total_skills: int
    active_skills: int
    evaluations: List[SkillEvaluation]
    summary: Dict


class SkillEvolutionTracker:
    """技能进化追踪器"""
    
    # 评估阈值
    USAGE_THRESHOLDS = {
        "high": 100,    # 高使用：100+次/月
        "medium": 20,   # 中使用：20-99次/月
        "low": 1        # 低使用：1-19次/月
    }
    
    QUALITY_THRESHOLDS = {
        "excellent": 90,
        "good": 75,
        "average": 60
    }
    
    def __init__(self, skills_dir: str = "./skills", data_file: str = "./skill_tracking_data.json"):
        self.skills_dir = Path(skills_dir)
        self.data_file = Path(data_file)
        self.tracking_data = self._load_tracking_data()
    
    def _load_tracking_data(self) -> Dict:
        """加载追踪数据"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"skills": {}, "logs": []}
    
    def _save_tracking_data(self):
        """保存追踪数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.tracking_data, f, ensure_ascii=False, indent=2)
    
    def _scan_skills_directory(self) -> List[Dict]:
        """扫描Skill目录"""
        skills = []
        if not self.skills_dir.exists():
            return skills
        
        for item in self.skills_dir.iterdir():
            if item.is_dir():
                skill_json = item / "skill.json"
                main_py = item / "main.py"
                
                if skill_json.exists() and main_py.exists():
                    try:
                        with open(skill_json, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        
                        skills.append({
                            "name": config.get("name", item.name),
                            "version": config.get("version", "1.0.0"),
                            "description": config.get("description", ""),
                            "path": str(item),
                            "updated_at": config.get("updated_at", "")
                        })
                    except:
                        skills.append({
                            "name": item.name,
                            "version": "1.0.0",
                            "description": "",
                            "path": str(item),
                            "updated_at": ""
                        })
        
        return skills
    
    def record_usage(self, skill_name: str, success: bool = True, 
                     response_time: float = 0, user_rating: int = None):
        """记录Skill使用"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if skill_name not in self.tracking_data["skills"]:
            self.tracking_data["skills"][skill_name] = {
                "total_calls": 0,
                "success_calls": 0,
                "failed_calls": 0,
                "response_times": [],
                "ratings": [],
                "first_used": today,
                "last_used": today,
                "daily_stats": {}
            }
        
        skill_data = self.tracking_data["skills"][skill_name]
        skill_data["total_calls"] += 1
        skill_data["last_used"] = today
        
        if success:
            skill_data["success_calls"] += 1
        else:
            skill_data["failed_calls"] += 1
        
        if response_time > 0:
            skill_data["response_times"].append(response_time)
            # 保留最近100个记录
            skill_data["response_times"] = skill_data["response_times"][-100:]
        
        if user_rating is not None:
            skill_data["ratings"].append(user_rating)
            skill_data["ratings"] = skill_data["ratings"][-50:]
        
        # 日统计
        if today not in skill_data["daily_stats"]:
            skill_data["daily_stats"][today] = {"calls": 0, "success": 0}
        skill_data["daily_stats"][today]["calls"] += 1
        if success:
            skill_data["daily_stats"][today]["success"] += 1
        
        self._save_tracking_data()
    
    def _calculate_metrics(self, skill_name: str, skill_config: Dict) -> SkillMetrics:
        """计算Skill指标"""
        data = self.tracking_data["skills"].get(skill_name, {
            "total_calls": 0,
            "success_calls": 0,
            "failed_calls": 0,
            "response_times": [],
            "ratings": [],
            "first_used": datetime.now().strftime("%Y-%m-%d"),
            "last_used": "-",
            "daily_stats": {}
        })
        
        avg_response_time = sum(data["response_times"]) / len(data["response_times"]) \
                          if data["response_times"] else 0
        
        user_satisfaction = sum(data["ratings"]) / len(data["ratings"]) * 20 \
                           if data["ratings"] else 75  # 默认75分
        
        # 计算迭代次数（基于版本号）
        version = skill_config.get("version", "1.0.0")
        iteration_count = int(version.split('.')[0]) * 10 + int(version.split('.')[1])
        
        return SkillMetrics(
            skill_name=skill_name,
            version=version,
            total_calls=data["total_calls"],
            success_calls=data["success_calls"],
            failed_calls=data["failed_calls"],
            avg_response_time=round(avg_response_time, 2),
            user_satisfaction=round(user_satisfaction, 2),
            last_used=data["last_used"],
            first_used=data["first_used"],
            iteration_count=iteration_count,
            daily_stats=data.get("daily_stats", {})
        )
    
    def _evaluate_skill(self, metrics: SkillMetrics) -> SkillEvaluation:
        """评估单个Skill"""
        
        # 计算成功率
        success_rate = (metrics.success_calls / metrics.total_calls * 100) \
                      if metrics.total_calls > 0 else 0
        
        # 使用等级
        monthly_calls = sum(1 for d in metrics.daily_stats.values() if d["calls"] > 0)
        if monthly_calls >= self.USAGE_THRESHOLDS["high"]:
            usage_level = "高"
        elif monthly_calls >= self.USAGE_THRESHOLDS["medium"]:
            usage_level = "中"
        elif monthly_calls >= self.USAGE_THRESHOLDS["low"]:
            usage_level = "低"
        else:
            usage_level = "未使用" if metrics.total_calls == 0 else "极低"
        
        # 质量等级
        quality_score = (success_rate * 0.4 + 
                        metrics.user_satisfaction * 0.4 + 
                        (100 - min(metrics.avg_response_time / 10, 50)) * 0.2)
        
        if quality_score >= self.QUALITY_THRESHOLDS["excellent"]:
            quality_level = "优秀"
        elif quality_score >= self.QUALITY_THRESHOLDS["good"]:
            quality_level = "良好"
        elif quality_score >= self.QUALITY_THRESHOLDS["average"]:
            quality_level = "一般"
        else:
            quality_level = "需改进"
        
        # 健康度
        health_score = quality_score
        if metrics.total_calls == 0:
            health_score = 0
        
        # 趋势分析
        trends = self._analyze_trends(metrics)
        
        # 进化状态
        if metrics.total_calls == 0:
            evolution_status = "新建"
        elif trends.get("usage", "稳定") == "下降" and metrics.total_calls > 50:
            evolution_status = "衰退"
        elif metrics.iteration_count >= 5 and quality_level in ["优秀", "良好"]:
            evolution_status = "成熟"
        else:
            evolution_status = "成长"
        
        # 生成建议
        recommendations = self._generate_recommendations(metrics, quality_level, usage_level)
        
        return SkillEvaluation(
            skill_name=metrics.skill_name,
            health_score=round(health_score, 2),
            usage_level=usage_level,
            quality_level=quality_level,
            trends=trends,
            recommendations=recommendations,
            evolution_status=evolution_status
        )
    
    def _analyze_trends(self, metrics: SkillMetrics) -> Dict[str, str]:
        """分析趋势"""
        trends = {}
        
        # 获取最近7天的数据
        dates = sorted(metrics.daily_stats.keys())[-7:]
        if len(dates) >= 3:
            recent_calls = [metrics.daily_stats[d]["calls"] for d in dates[-3:]]
            older_calls = [metrics.daily_stats[d]["calls"] for d in dates[:3]]
            
            recent_avg = sum(recent_calls) / len(recent_calls)
            older_avg = sum(older_calls) / len(older_calls)
            
            if recent_avg > older_avg * 1.2:
                trends["usage"] = "上升"
            elif recent_avg < older_avg * 0.8:
                trends["usage"] = "下降"
            else:
                trends["usage"] = "稳定"
        else:
            trends["usage"] = "数据不足"
        
        trends["quality"] = "稳定"  # 简化处理
        
        return trends
    
    def _generate_recommendations(self, metrics: SkillMetrics, quality_level: str, 
                                   usage_level: str) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if metrics.total_calls == 0:
            recommendations.append("🔴 该Skill从未被使用，需要检查是否已部署或推广")
            return recommendations
        
        if usage_level == "低":
            recommendations.append("🟡 使用频率较低，建议增加推广或检查需求匹配度")
        
        if quality_level == "需改进":
            recommendations.append("🔴 质量评分较低，需要优化实现逻辑")
        elif quality_level == "一般":
            recommendations.append("🟡 质量有提升空间，建议收集用户反馈")
        
        success_rate = (metrics.success_calls / metrics.total_calls * 100) \
                      if metrics.total_calls > 0 else 0
        if success_rate < 80:
            recommendations.append(f"🟡 成功率仅{success_rate:.1f}%，需要排查失败原因")
        
        if metrics.avg_response_time > 5000:
            recommendations.append(f"🟡 平均响应时间{metrics.avg_response_time:.0f}ms，建议优化性能")
        
        if metrics.user_satisfaction < 70:
            recommendations.append("🟡 用户满意度较低，建议增加用户调研")
        
        if not recommendations:
            recommendations.append("✅ 该Skill表现良好，继续保持")
        
        return recommendations
    
    def track(self, skill_name: str = None) -> TrackingReport:
        """追踪Skill进化状态"""
        scan_time = datetime.now().isoformat()
        
        # 扫描所有Skill
        all_skills = self._scan_skills_directory()
        
        # 如果指定了特定Skill
        if skill_name:
            all_skills = [s for s in all_skills if s["name"] == skill_name]
        
        evaluations = []
        for skill in all_skills:
            metrics = self._calculate_metrics(skill["name"], skill)
            evaluation = self._evaluate_skill(metrics)
            evaluations.append(evaluation)
        
        # 按健康度排序
        evaluations.sort(key=lambda x: x.health_score, reverse=True)
        
        # 统计摘要
        active_count = sum(1 for e in evaluations if e.usage_level in ["高", "中"])
        
        summary = {
            "excellent_count": sum(1 for e in evaluations if e.quality_level == "优秀"),
            "good_count": sum(1 for e in evaluations if e.quality_level == "良好"),
            "needs_improvement": sum(1 for e in evaluations if e.quality_level in ["一般", "需改进"]),
            "unused_count": sum(1 for e in evaluations if e.usage_level == "未使用"),
            "avg_health": sum(e.health_score for e in evaluations) / len(evaluations) if evaluations else 0
        }
        
        return TrackingReport(
            scan_time=scan_time,
            total_skills=len(all_skills),
            active_skills=active_count,
            evaluations=evaluations,
            summary=summary
        )
    
    def generate_report(self, report: TrackingReport) -> str:
        """生成追踪报告"""
        lines = [
            "=" * 70,
            "              Skill进化追踪报告",
            "=" * 70,
            f"扫描时间: {report.scan_time}",
            f"Skill总数: {report.total_skills}",
            f"活跃Skill: {report.active_skills}",
            "-" * 70,
            "\n统计摘要:",
            f"  优秀: {report.summary['excellent_count']}个",
            f"  良好: {report.summary['good_count']}个",
            f"  需改进: {report.summary['needs_improvement']}个",
            f"  未使用: {report.summary['unused_count']}个",
            f"  平均健康度: {report.summary['avg_health']:.1f}",
            "\n" + "-" * 70,
            "详细评估:"
        ]
        
        for i, eval in enumerate(report.evaluations, 1):
            status_icon = {
                "成熟": "🌳",
                "成长": "🌱",
                "衰退": "🍂",
                "新建": "🆕"
            }.get(eval.evolution_status, "📊")
            
            lines.append(f"\n{i}. {status_icon} {eval.skill_name}")
            lines.append(f"   健康度: {eval.health_score:.1f} | 使用: {eval.usage_level} | 质量: {eval.quality_level}")
            lines.append(f"   状态: {eval.evolution_status} | 趋势: 使用{eval.trends.get('usage', '-')}")
            if eval.recommendations:
                lines.append(f"   建议: {eval.recommendations[0]}")
        
        lines.extend([
            "",
            "=" * 70
        ])
        
        return "\n".join(lines)


def main():
    """主函数演示"""
    print("📈 Skill进化追踪器 - 演示\n")
    
    # 初始化追踪器
    tracker = SkillEvolutionTracker(
        skills_dir="/root/.openclaw/workspace/skills",
        data_file="./skill_tracking_data.json"
    )
    
    # 模拟一些使用数据
    print("📝 模拟使用数据记录...")
    
    test_skills = [
        ("task-priority-intelligence", 50, 48, 85),
        ("knowledge-distiller", 30, 29, 90),
        ("intent-recognition-enhancer", 15, 14, 78),
        ("cross-skill-orchestrator", 5, 5, 82),
        ("skill-evolution-tracker", 0, 0, 0),  # 未使用
    ]
    
    for skill_name, calls, success, rating in test_skills:
        for _ in range(calls):
            tracker.record_usage(
                skill_name=skill_name,
                success=True if _ < success else False,
                response_time=1500 + (_ % 10) * 100,
                user_rating=rating // 20 if rating > 0 else None
            )
    
    print("✅ 模拟数据已记录\n")
    
    # 执行追踪
    print("🔍 开始扫描所有Skill...")
    report = tracker.track()
    
    # 生成并打印报告
    print(tracker.generate_report(report))
    
    # 追踪特定Skill
    print("\n\n" + "=" * 70)
    print("特定Skill追踪: task-priority-intelligence")
    print("=" * 70)
    specific_report = tracker.track("task-priority-intelligence")
    for eval in specific_report.evaluations:
        print(f"\nSkill: {eval.skill_name}")
        print(f"  健康度: {eval.health_score}")
        print(f"  使用等级: {eval.usage_level}")
        print(f"  质量等级: {eval.quality_level}")
        print(f"  进化状态: {eval.evolution_status}")
        print(f"  改进建议:")
        for rec in eval.recommendations:
            print(f"    - {rec}")
    
    # JSON输出
    print("\n\n📋 JSON格式输出:")
    json_output = {
        "summary": report.summary,
        "top_skills": [
            {
                "name": e.skill_name,
                "health": e.health_score,
                "usage": e.usage_level,
                "quality": e.quality_level
            }
            for e in report.evaluations[:3]
        ]
    }
    print(json.dumps(json_output, ensure_ascii=False, indent=2))
    
    return report


if __name__ == "__main__":
    main()
