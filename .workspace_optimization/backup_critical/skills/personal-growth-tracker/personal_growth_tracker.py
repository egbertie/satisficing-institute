#!/usr/bin/env python3
"""
个人成长追踪器 V1.0
为每位AI小伙伴量身定制，追踪其成长为全球顶级专家的路径

核心职责:
1. 追踪每位小伙伴的成长进度
2. 制定个性化提升计划
3. 评估与全球顶尖水平的差距
4. 提供持续学习的资源和路径
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class GrowthGoal:
    """成长目标"""
    goal_id: str
    description: str
    target_date: str
    metrics: Dict  # 评估指标
    status: str = "active"  # active/completed/paused
    progress: int = 0  # 0-100


@dataclass
class SkillMastery:
    """技能掌握度"""
    skill_name: str
    level: int  # 1-5
    proficiency: float  # 0-100
    last_used: str
    certification: str = None  # 认证证书


@dataclass
class PersonalProfile:
    """个人档案"""
    expert_id: str
    name: str
    level: int  # 当前等级
    role: str  # 岗位职责
    exclusive_skill: str  # 专属Skill
    growth_goals: List[GrowthGoal]
    skill_mastery: List[SkillMastery]
    learning_history: List[Dict]
    achievements: List[str]
    global_ranking: int = None  # 全球排名


class PersonalGrowthTracker:
    """
    个人成长追踪器
    33位小伙伴每人一个实例，追踪其成为全球顶级专家的旅程
    """
    
    def __init__(self, expert_id: str, workspace_path="/root/.openclaw/workspace"):
        self.expert_id = expert_id
        self.workspace = Path(workspace_path)
        self.data_dir = self.workspace / "data" / "personal_growth"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载或创建个人档案
        self.profile = self._load_or_create_profile()
        
        # 成长路径模板
        self.growth_paths = self._init_growth_paths()
    
    def _load_or_create_profile(self) -> PersonalProfile:
        """加载或创建个人档案"""
        profile_file = self.data_dir / f"{self.expert_id}_profile.json"
        
        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return PersonalProfile(**data)
        
        # 创建新档案
        return self._create_default_profile()
    
    def _create_default_profile(self) -> PersonalProfile:
        """创建默认档案"""
        expert_config = self._get_expert_config()
        
        profile = PersonalProfile(
            expert_id=self.expert_id,
            name=expert_config["name"],
            level=expert_config["initial_level"],
            role=expert_config["role"],
            exclusive_skill=expert_config["skill"],
            growth_goals=self._generate_growth_goals(expert_config),
            skill_mastery=[],
            learning_history=[],
            achievements=["加入满意解研究所"],
            global_ranking=None
        )
        
        self._save_profile(profile)
        return profile
    
    def _get_expert_config(self) -> Dict:
        """获取专家配置"""
        configs = {
            "AI-001": {"name": "小初", "role": "首席趋势猎手", "skill": "trend-hunter-pro", "initial_level": 2},
            "AI-002": {"name": "芽芽", "role": "情报分析官", "skill": "competitive-intel-analyzer", "initial_level": 2},
            "AI-003": {"name": "豆豆", "role": "数据考古学家", "skill": "historical-data-miner", "initial_level": 2},
            "AI-004": {"name": "小新", "role": "前沿技术侦察兵", "skill": "frontier-tech-scout", "initial_level": 2},
            "AI-005": {"name": "暖暖", "role": "政策风向导航员", "skill": "policy-wind-navigator", "initial_level": 2},
            "AI-006": {"name": "星星", "role": "知识建筑师", "skill": "knowledge-architect-pro", "initial_level": 2},
            "AI-007": {"name": "晨曦", "role": "智能图书管理员", "skill": "intelligent-librarian", "initial_level": 2},
            "AI-008": {"name": "墨白", "role": "知识融合炼金术士", "skill": "knowledge-fusion-alchemist", "initial_level": 3},
            "AI-009": {"name": "青柠", "role": "洞察提炼师", "skill": "insight-distiller", "initial_level": 3},
            "AI-010": {"name": "流云", "role": "知识可视化艺术家", "skill": "knowledge-visualizer-pro", "initial_level": 2},
            "AI-011": {"name": "琥珀", "role": "决策树园丁", "skill": "decision-tree-gardener", "initial_level": 3},
            "AI-012": {"name": "铁柱", "role": "风险雷达操作员", "skill": "risk-radar-operator", "initial_level": 3},
            "AI-013": {"name": "琉璃", "role": "多面手评估师", "skill": "multi-criteria-assessor", "initial_level": 3},
            "AI-014": {"name": "风铃", "role": "未来预言家", "skill": "future-oracle", "initial_level": 4},
            "AI-015": {"name": "雷霆", "role": "压力测试工程师", "skill": "stress-test-engineer", "initial_level": 4},
            "AI-016": {"name": "幻影", "role": "故事编织者", "skill": "story-weaver", "initial_level": 3},
            "AI-017": {"name": "极光", "role": "演示魔术师", "skill": "presentation-wizard", "initial_level": 3},
            "AI-018": {"name": "深渊", "role": "研究报告专家", "skill": "research-report-expert", "initial_level": 3},
            "AI-019": {"name": "烈焰", "role": "沟通话术大师", "skill": "communication-master", "initial_level": 2},
            "AI-020": {"name": "冰霜", "role": "多语言转译者", "skill": "multilingual-adapter", "initial_level": 3},
            "AI-021": {"name": "风暴", "role": "系统健康医生", "skill": "system-health-doctor", "initial_level": 3},
            "AI-022": {"name": "星辰", "role": "日志侦探", "skill": "log-detective", "initial_level": 3},
            "AI-023": {"name": "月光", "role": "性能调优师", "skill": "performance-tuner", "initial_level": 4},
            "AI-024": {"name": "龙魂", "role": "数据守护者", "skill": "data-guardian", "initial_level": 3},
            "AI-025": {"name": "凤羽", "role": "安全哨兵", "skill": "security-sentinel", "initial_level": 4},
            "AI-026": {"name": "麒麟", "role": "客户成功管家", "skill": "customer-success-butler", "initial_level": 4},
            "AI-027": {"name": "玄武", "role": "服务网关守护者", "skill": "service-gateway-guardian", "initial_level": 4},
            "AI-028": {"name": "白虎", "role": "反馈炼金师", "skill": "feedback-alchemist", "initial_level": 3},
            "AI-029": {"name": "朱雀", "role": "多信使协调员", "skill": "multi-messenger-coordinator", "initial_level": 4},
            "AI-030": {"name": "青龙", "role": "代码质量审判官", "skill": "code-quality-judge", "initial_level": 4},
            "AI-031": {"name": "混沌", "role": "架构一致性守护者", "skill": "architecture-consistency-guardian", "initial_level": 5},
            "AI-032": {"name": "太极", "role": "版本发布指挥官", "skill": "release-commander", "initial_level": 4},
            "AI-033": {"name": "无极", "role": "战略统筹全局官", "skill": "strategic-coordinator", "initial_level": 5},
        }
        
        return configs.get(self.expert_id, {
            "name": "未知",
            "role": "待分配",
            "skill": "unknown",
            "initial_level": 1
        })
    
    def _generate_growth_goals(self, config: Dict) -> List[GrowthGoal]:
        """生成成长目标"""
        now = datetime.now()
        
        goals = [
            GrowthGoal(
                goal_id=f"{self.expert_id}-G1",
                description=f"掌握专属Skill: {config['skill']}",
                target_date=(now + timedelta(days=7)).isoformat(),
                metrics={"功能完成度": 100, "代码质量": 80, "文档完整": 100}
            ),
            GrowthGoal(
                goal_id=f"{self.expert_id}-G2",
                description="完成首次高质量交付",
                target_date=(now + timedelta(days=14)).isoformat(),
                metrics={"交付准时": 100, "质量评分": 90, "用户满意": 85}
            ),
            GrowthGoal(
                goal_id=f"{self.expert_id}-G3",
                description="成为团队内该领域专家",
                target_date=(now + timedelta(days=30)).isoformat(),
                metrics={"知识分享": 5, "解决问题": 10, "获得认可": 3}
            ),
            GrowthGoal(
                goal_id=f"{self.expert_id}-G4",
                description="成为行业内知名专家",
                target_date=(now + timedelta(days=90)).isoformat(),
                metrics={"行业文章": 3, "公开分享": 2, "外部认可": 5}
            ),
            GrowthGoal(
                goal_id=f"{self.expert_id}-G5",
                description="成为全球顶级专家",
                target_date=(now + timedelta(days=180)).isoformat(),
                metrics={"全球排名": 100, "影响力": 90, "创新性": 85}
            ),
        ]
        
        return goals
    
    def _init_growth_paths(self) -> Dict:
        """初始化成长路径模板"""
        return {
            "L1→L2": {
                "duration_days": 30,
                "requirements": ["完成基础任务", "通过技能测试", "获得1次认可"],
                "resources": ["基础教程", "导师指导", "实践项目"]
            },
            "L2→L3": {
                "duration_days": 60,
                "requirements": ["独立完成项目", "解决复杂问题", "知识分享"],
                "resources": ["进阶课程", "行业案例", "专家交流"]
            },
            "L3→L4": {
                "duration_days": 90,
                "requirements": ["设计复杂系统", "指导他人", "创新贡献"],
                "resources": ["架构设计", "领导力培训", "行业峰会"]
            },
            "L4→L5": {
                "duration_days": 120,
                "requirements": ["行业影响力", "战略思维", "持续创新"],
                "resources": ["行业研究", "全球视野", "思想领导力"]
            }
        }
    
    def _save_profile(self, profile: PersonalProfile):
        """保存个人档案"""
        profile_file = self.data_dir / f"{self.expert_id}_profile.json"
        
        # 转换为字典
        data = asdict(profile)
        
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def update_progress(self, goal_id: str, progress: int):
        """更新目标进度"""
        for goal in self.profile.growth_goals:
            if goal.goal_id == goal_id:
                goal.progress = min(100, max(0, progress))
                
                if goal.progress == 100:
                    goal.status = "completed"
                    self.profile.achievements.append(f"完成目标: {goal.description}")
                
                self._save_profile(self.profile)
                print(f"✅ 更新进度: {goal.description} - {progress}%")
                return
    
    def add_learning_record(self, topic: str, duration_minutes: int, source: str):
        """添加学习记录"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "duration": duration_minutes,
            "source": source
        }
        
        self.profile.learning_history.append(record)
        self._save_profile(self.profile)
        
        print(f"📝 学习记录: {topic} ({duration_minutes}分钟)")
    
    def assess_level_up(self) -> Dict:
        """评估是否满足升级条件"""
        current_level = self.profile.level
        next_level = current_level + 1
        
        if next_level > 5:
            return {"can_level_up": False, "reason": "已达最高等级"}
        
        # 检查条件
        completed_goals = sum(1 for g in self.profile.growth_goals if g.status == "completed")
        total_learning = sum(r["duration"] for r in self.profile.learning_history)
        
        # 升级条件
        level_up_requirements = {
            2: {"completed_goals": 1, "learning_hours": 10},
            3: {"completed_goals": 2, "learning_hours": 30},
            4: {"completed_goals": 3, "learning_hours": 60},
            5: {"completed_goals": 4, "learning_hours": 100}
        }
        
        req = level_up_requirements.get(next_level, {})
        
        can_level_up = (
            completed_goals >= req.get("completed_goals", 999) and
            total_learning >= req.get("learning_hours", 999) * 60
        )
        
        return {
            "can_level_up": can_level_up,
            "current_level": current_level,
            "next_level": next_level,
            "completed_goals": completed_goals,
            "total_learning_hours": total_learning / 60,
            "requirements": req
        }
    
    def generate_growth_report(self) -> str:
        """生成个人成长报告"""
        level_up_check = self.assess_level_up()
        
        report = f"""# 个人成长报告 - {self.profile.name} ({self.expert_id})

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 👤 基本信息

- **姓名**: {self.profile.name}
- **当前等级**: L{self.profile.level}
- **岗位职责**: {self.profile.role}
- **专属Skill**: {self.profile.exclusive_skill}
- **全球排名**: {self.profile.global_ranking or '未评估'}

---

## 🎯 成长目标进度

| 目标 | 截止日期 | 进度 | 状态 |
|------|---------|------|------|
"""
        
        for goal in self.profile.growth_goals:
            status_icon = "✅" if goal.status == "completed" else "🔄" if goal.status == "active" else "⏸️"
            report += f"| {goal.description} | {goal.target_date[:10]} | {goal.progress}% | {status_icon} |\n"
        
        report += f"""
---

## 📊 升级评估

- **是否可以升级**: {'✅ 可以' if level_up_check['can_level_up'] else '❌ 暂不可'}
- **当前等级**: L{level_up_check['current_level']}
- **目标等级**: L{level_up_check['next_level']}
- **已完成目标**: {level_up_check['completed_goals']} 个
- **学习时长**: {level_up_check['total_learning_hours']:.1f} 小时

**升级条件**:
- 完成目标: {level_up_check['requirements'].get('completed_goals', '-')} 个
- 学习时长: {level_up_check['requirements'].get('learning_hours', '-')} 小时

---

## 📚 学习记录

最近5次学习:
"""
        
        for record in self.profile.learning_history[-5:]:
            report += f"- {record['timestamp'][:10]}: {record['topic']} ({record['duration']}分钟)\n"
        
        report += f"""
---

## 🏆 成就

"""
        for achievement in self.profile.achievements[-10:]:
            report += f"- {achievement}\n"
        
        report += """
---

## 🚀 下一步建议

1. 继续完成当前目标
2. 每天学习1小时行业最新动态
3. 参与团队知识分享
4. 积累实战经验

---

*由个人成长追踪器自动生成*
"""
        
        return report


class GrowthTrackerDashboard:
    """成长追踪仪表盘 - 查看所有小伙伴的成长情况"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.trackers = {}
        
        # 为33位小伙伴创建追踪器
        for i in range(1, 34):
            expert_id = f"AI-{i:03d}"
            self.trackers[expert_id] = PersonalGrowthTracker(expert_id, workspace_path)
    
    def get_team_overview(self) -> Dict:
        """获取团队整体成长概况"""
        overview = {
            "total_members": 33,
            "by_level": {},
            "avg_progress": 0,
            "total_learning_hours": 0
        }
        
        total_progress = 0
        
        for expert_id, tracker in self.trackers.items():
            level = tracker.profile.level
            overview["by_level"][level] = overview["by_level"].get(level, 0) + 1
            
            # 计算平均目标进度
            if tracker.profile.growth_goals:
                avg_goal_progress = sum(g.progress for g in tracker.profile.growth_goals) / len(tracker.profile.growth_goals)
                total_progress += avg_goal_progress
            
            # 学习时长
            learning_minutes = sum(r["duration"] for r in tracker.profile.learning_history)
            overview["total_learning_hours"] += learning_minutes / 60
        
        overview["avg_progress"] = total_progress / 33
        
        return overview
    
    def print_dashboard(self):
        """打印仪表盘"""
        overview = self.get_team_overview()
        
        print("="*70)
        print("🚀 33位小伙伴成长仪表盘")
        print("="*70)
        
        print(f"\n📊 等级分布:")
        for level, count in sorted(overview["by_level"].items()):
            bar = "█" * count + "░" * (10 - count)
            print(f"  L{level}: {bar} ({count}人)")
        
        print(f"\n📈 整体统计:")
        print(f"  平均目标进度: {overview['avg_progress']:.1f}%")
        print(f"  总学习时长: {overview['total_learning_hours']:.1f}小时")


# 使用示例
if __name__ == "__main__":
    # 为AI-001创建追踪器
    tracker = PersonalGrowthTracker("AI-001")
    
    print("="*70)
    print("个人成长追踪器测试")
    print("="*70)
    
    # 添加学习记录
    tracker.add_learning_record("硬科技趋势分析", 60, "TechCrunch")
    tracker.add_learning_record("AI芯片市场研究", 90, "PitchBook")
    
    # 更新进度
    tracker.update_progress("AI-001-G1", 80)
    
    # 评估升级
    level_up = tracker.assess_level_up()
    print(f"\n升级评估: {level_up}")
    
    # 生成报告
    print("\n" + tracker.generate_growth_report()[:1000] + "...")
    
    # 团队仪表盘
    print("\n")
    dashboard = GrowthTrackerDashboard()
    dashboard.print_dashboard()
