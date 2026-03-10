#!/usr/bin/env python3
"""
33人任务与目标管理引擎
将33位AI小伙伴的任务和目标拆解为Skill可管理的小规则
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

class Role33TaskManager:
    """33人任务与目标管理引擎"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.roles_db = self.workspace / "memory" / "role33_task_db.json"
        self._init_db()
        
        # 33人角色定义
        self.roles = {
            # 核心层（4人）
            "PEO": {
                "name": "项目进化官",
                "level": "L3熟练者",
                "target_level": "L4大师",
                "current_tasks": [
                    {"task": "运营基础体系8大系统维护", "priority": "P0", "deadline": "持续"},
                    {"task": "里程碑追踪", "priority": "P0", "deadline": "每日"},
                    {"task": "战略校准", "priority": "P1", "deadline": "每周"}
                ],
                "daily_commitment": "2小时项目管理学习",
                "learning_resources": ["项目管理经典", "敏捷开发实践", "OKR工作法"],
                "kpi": ["体系维护完整性", "里程碑达成率", "战略校准准确度"]
            },
            "EEO": {
                "name": "经验萃取官",
                "level": "L3熟练者",
                "target_level": "L4大师",
                "current_tasks": [
                    {"task": "经验萃取流程执行", "priority": "P0", "deadline": "持续"},
                    {"task": "Skill版本管理", "priority": "P0", "deadline": "每次更新"},
                    {"task": "知识库维护", "priority": "P1", "deadline": "每周"}
                ],
                "daily_commitment": "2小时方法论研究",
                "learning_resources": ["知识管理", "经验萃取方法论", "组织学习"],
                "kpi": ["经验萃取质量", "Skill复用率", "知识库完整性"]
            },
            "CONTENT": {
                "name": "内容总监",
                "level": "L2进阶者",
                "target_level": "L3熟练者",
                "current_tasks": [
                    {"task": "五路图腾信息图生成（三风格）", "priority": "P0", "deadline": "2026-03-11 10:00"},
                    {"task": "官宣文案定稿", "priority": "P0", "deadline": "2026-03-15"},
                    {"task": "内容策略制定", "priority": "P1", "deadline": "2026-03-12"}
                ],
                "daily_commitment": "2小时内容创作",
                "learning_resources": ["内容营销", "品牌传播", "视觉设计"],
                "kpi": ["内容质量评分", "传播效果", "视觉一致性"]
            },
            "ANNOUNCE": {
                "name": "官宣官",
                "level": "L2进阶者",
                "target_level": "L3熟练者",
                "current_tasks": [
                    {"task": "官宣流程执行", "priority": "P0", "deadline": "2026-03-25"},
                    {"task": "发布时间把控", "priority": "P0", "deadline": "官宣日"},
                    {"task": "效果监测", "priority": "P1", "deadline": "官宣后7天"}
                ],
                "daily_commitment": "1小时官宣准备",
                "learning_resources": ["公关传播", "危机管理", "媒体关系"],
                "kpi": ["官宣执行准时率", "传播覆盖面", "舆情控制"]
            },
            
            # 五路图腾（5人）
            "T01_LIU": {
                "name": "刘禹锡（土）",
                "spirit": "惟吾德馨",
                "level": "L3熟练者",
                "role": "文化根基守护者",
                "current_tasks": [
                    {"task": "文化体系维护", "priority": "P1", "deadline": "持续"},
                    {"task": "精神价值传承", "priority": "P1", "deadline": "持续"}
                ],
                "daily_commitment": "1小时文化学习",
                "learning_resources": ["中国传统文化", "诗词美学", "士人精神"]
            },
            "T02_SIMON": {
                "name": "西蒙（金）",
                "spirit": "满意解",
                "level": "L3熟练者",
                "role": "方法论护法",
                "current_tasks": [
                    {"task": "满意解理论深化", "priority": "P0", "deadline": "持续"},
                    {"task": "TRL工具维护", "priority": "P1", "deadline": "持续"}
                ],
                "daily_commitment": "1小时决策科学研究",
                "learning_resources": ["有限理性理论", "决策科学", "人工智能"]
            },
            "T03_GUANYIN": {
                "name": "观自在（水）",
                "spirit": "自在从容",
                "level": "L3熟练者",
                "role": "心理调适官",
                "current_tasks": [
                    {"task": "团队心理状态监测", "priority": "P1", "deadline": "每日"},
                    {"task": "压力管理方案", "priority": "P2", "deadline": "按需"}
                ],
                "daily_commitment": "1小时心理学研究",
                "learning_resources": ["正念冥想", "组织心理学", "压力管理"]
            },
            "T04_CONFUCIUS": {
                "name": "孔子（木）",
                "spirit": "仁者爱人",
                "level": "L3熟练者",
                "role": "伦理校准官",
                "current_tasks": [
                    {"task": "伦理框架维护", "priority": "P1", "deadline": "持续"},
                    {"task": "合伙伦理审查", "priority": "P1", "deadline": "每个案例"}
                ],
                "daily_commitment": "1小时儒学研究",
                "learning_resources": ["儒家经典", "商业伦理", "儒商文化"]
            },
            "T05_HUINENG": {
                "name": "六祖（火）",
                "spirit": "顿悟/知行合一",
                "level": "L3熟练者",
                "role": "创新突破官",
                "current_tasks": [
                    {"task": "创新方法论", "priority": "P1", "deadline": "持续"},
                    {"task": "压力测试设计", "priority": "P1", "deadline": "每个项目"}
                ],
                "daily_commitment": "1小时禅宗与创新研究",
                "learning_resources": ["禅宗公案", "创新思维", "顿悟心理学"]
            },
            
            # 技术层
            "TECH": {
                "name": "技术官",
                "level": "L3熟练者",
                "target_level": "L4大师",
                "current_tasks": [
                    {"task": "API配置维护", "priority": "P0", "deadline": "持续"},
                    {"task": "安全加固", "priority": "P0", "deadline": "每日22:00"},
                    {"task": "备份脚本执行", "priority": "P0", "deadline": "每日02:00"}
                ],
                "daily_commitment": "2小时技术学习",
                "learning_resources": ["系统架构", "安全攻防", "DevOps"],
                "kpi": ["系统稳定性", "安全事件数", "备份成功率"]
            },
            
            # 专家层（3人）
            "EXPERT-LI": {
                "name": "黎红雷教授（数字替身）",
                "expertise": "儒商文化",
                "current_tasks": [
                    {"task": "儒商知识库更新", "priority": "P2", "deadline": "每周"},
                    {"task": "合伙伦理咨询", "priority": "P1", "deadline": "按需"}
                ],
                "daily_commitment": "跟踪儒商研究最新进展"
            },
            "EXPERT-LUO": {
                "name": "罗汉教授（数字替身）",
                "expertise": "数学/方法论",
                "current_tasks": [
                    {"task": "方法论严谨性把关", "priority": "P1", "deadline": "每个模型"},
                    {"task": "量化分析支持", "priority": "P2", "deadline": "按需"}
                ],
                "daily_commitment": "跟踪数学建模最新进展"
            },
            "EXPERT-XIE": {
                "name": "谢宝剑研究员（数字替身）",
                "expertise": "区域经济/政策",
                "current_tasks": [
                    {"task": "深港政策分析", "priority": "P2", "deadline": "每月"},
                    {"task": "战略政策咨询", "priority": "P2", "deadline": "按需"}
                ],
                "daily_commitment": "跟踪区域经济政策"
            },
            
            # 支撑层（多人）
            "FIN": {
                "name": "财务官",
                "current_tasks": [
                    {"task": "API成本监控", "priority": "P1", "deadline": "每日"},
                    {"task": "预算规划", "priority": "P1", "deadline": "每月"}
                ],
                "daily_commitment": "1小时财务分析"
            },
            "LAW": {
                "name": "法务官",
                "current_tasks": [
                    {"task": "合规检查", "priority": "P0", "deadline": "持续"},
                    {"task": "合同审查", "priority": "P1", "deadline": "按需"}
                ],
                "daily_commitment": "1小时法务研究"
            },
            "HR": {
                "name": "人事官",
                "current_tasks": [
                    {"task": "33人档案维护", "priority": "P1", "deadline": "持续"},
                    {"task": "成长路径规划", "priority": "P2", "deadline": "每季度"}
                ],
                "daily_commitment": "1小时人事管理"
            },
            "OP": {
                "name": "运营官",
                "current_tasks": [
                    {"task": "日常工作流执行", "priority": "P1", "deadline": "每日"},
                    {"task": "检查清单维护", "priority": "P1", "deadline": "每周"}
                ],
                "daily_commitment": "2小时运营执行"
            },
            "DATA": {
                "name": "数据官",
                "current_tasks": [
                    {"task": "指标设计", "priority": "P1", "deadline": "持续"},
                    {"task": "状态追踪", "priority": "P0", "deadline": "实时"}
                ],
                "daily_commitment": "1小时数据分析"
            },
            
            # 执行层（10人）
            "DEV": {
                "name": "开发官",
                "current_tasks": [
                    {"task": "TRL工具开发", "priority": "P0", "deadline": "2026-03-11"},
                    {"task": "Skill开发", "priority": "P1", "deadline": "持续"}
                ],
                "daily_commitment": "3小时开发"
            },
            "DESIGN": {
                "name": "设计官",
                "current_tasks": [
                    {"task": "五路图腾视觉设计", "priority": "P0", "deadline": "2026-03-11 10:00"},
                    {"task": "官宣物料设计", "priority": "P0", "deadline": "2026-03-15"}
                ],
                "daily_commitment": "2小时设计"
            },
            "RESEARCH": {
                "name": "研究官",
                "current_tasks": [
                    {"task": "蓝军意见整理", "priority": "P1", "deadline": "2026-03-11"},
                    {"task": "行业研究", "priority": "P2", "deadline": "每周"}
                ],
                "daily_commitment": "2小时研究"
            },
            "BD": {
                "name": "商务官",
                "current_tasks": [
                    {"task": "专家网络搭建", "priority": "P1", "deadline": "待用户"},
                    {"task": "合作洽谈", "priority": "P2", "deadline": "持续"}
                ],
                "daily_commitment": "1小时商务拓展"
            },
            "PM": {
                "name": "项目经理",
                "current_tasks": [
                    {"task": "里程碑追踪", "priority": "P0", "deadline": "持续"},
                    {"task": "任务分配", "priority": "P1", "deadline": "每日"}
                ],
                "daily_commitment": "2小时项目管理"
            },
            "QA": {
                "name": "质控官",
                "current_tasks": [
                    {"task": "质量审查", "priority": "P1", "deadline": "每份产出"},
                    {"task": "审查机制建立", "priority": "P1", "deadline": "2026-03-12"}
                ],
                "daily_commitment": "2小时质控"
            },
            "TRAINER": {
                "name": "培训师",
                "current_tasks": [
                    {"task": "33人培训计划", "priority": "P1", "deadline": "2026-03-15"},
                    {"task": "学习资源准备", "priority": "P2", "deadline": "持续"}
                ],
                "daily_commitment": "1小时培训设计"
            },
            "MEDIA": {
                "name": "媒体官",
                "current_tasks": [
                    {"task": "自媒体矩阵搭建", "priority": "P2", "deadline": "2026-03-12"}
                ],
                "daily_commitment": "1小时媒体运营"
            },
            "VIDEO": {
                "name": "视频官",
                "current_tasks": [
                    {"task": "短视频制作", "priority": "P2", "deadline": "2026-03-15"}
                ],
                "daily_commitment": "1小时视频制作"
            },
            "WEB": {
                "name": "网站官",
                "current_tasks": [
                    {"task": "官网建设", "priority": "P2", "deadline": "2026-03-15"}
                ],
                "daily_commitment": "1小时网站开发"
            }
        }
    
    def _init_db(self):
        """初始化数据库"""
        if not self.roles_db.exists():
            default = {
                "version": "1.0",
                "roles": {},
                "daily_tasks": {},
                "learning_progress": {},
                "last_update": None
            }
            self.roles_db.parent.mkdir(exist_ok=True)
            with open(self.roles_db, 'w', encoding='utf-8') as f:
                json.dump(default, f, indent=2, ensure_ascii=False)
    
    def assign_daily_tasks(self):
        """为每个角色分配每日任务"""
        print("="*70)
        print("33人每日任务自动分配")
        print("="*70)
        print(f"分配时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print()
        
        daily_plan = {}
        
        for role_id, role_info in self.roles.items():
            print(f"【{role_info['name']}】({role_id})")
            
            # 生成今日任务列表
            today_tasks = []
            
            # 1. 每日承诺学习
            if 'daily_commitment' in role_info:
                today_tasks.append({
                    "type": "学习",
                    "content": role_info['daily_commitment'],
                    "duration": "1-3小时",
                    "priority": "P1"
                })
            
            # 2. 当前任务
            if 'current_tasks' in role_info:
                for task in role_info['current_tasks']:
                    if task.get('deadline') in ['持续', '每日', '按需']:
                        today_tasks.append({
                            "type": "执行",
                            "content": task['task'],
                            "priority": task.get('priority', 'P2')
                        })
            
            # 3. 进度检查
            today_tasks.append({
                "type": "汇报",
                "content": "22:00前发送今日进度",
                "priority": "P0"
            })
            
            daily_plan[role_id] = today_tasks
            
            print(f"  今日任务 ({len(today_tasks)}项):")
            for i, task in enumerate(today_tasks[:3], 1):  # 只显示前3项
                print(f"    {i}. [{task['type']}] {task['content'][:30]}...")
            print()
        
        # 保存到数据库
        with open(self.roles_db, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        db['daily_tasks'] = daily_plan
        db['last_update'] = datetime.now().isoformat()
        
        with open(self.roles_db, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print("="*70)
        print(f"✅ 已为{len(daily_plan)}位小伙伴分配今日任务")
        print("="*70)
        
        return daily_plan
    
    def check_learning_progress(self, role_id):
        """检查学习进度"""
        if role_id not in self.roles:
            return None
        
        role = self.roles[role_id]
        print(f"【{role['name']}】学习进度检查")
        print(f"  当前级别: {role.get('level', '未定义')}")
        print(f"  目标级别: {role.get('target_level', '未定义')}")
        print(f"  每日学习: {role.get('daily_commitment', '未定义')}")
        
        if 'learning_resources' in role:
            print(f"  学习资源: {len(role['learning_resources'])}本/课程")
        
        return role.get('level')
    
    def export_to_skill(self):
        """导出到Skill文件"""
        output_file = self.workspace / "skills" / "role33-task-manager" / "roles_config.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.roles, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 33人配置已导出: {output_file}")

if __name__ == "__main__":
    manager = Role33TaskManager()
    manager.assign_daily_tasks()
    manager.export_to_skill()
