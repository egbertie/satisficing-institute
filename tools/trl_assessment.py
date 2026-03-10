#!/usr/bin/env python3
"""
TRL 自评工具 - 技术成熟度等级评估
满意解研究所 · 硬科技合伙人匹配决策系统

基于 NASA/DoD TRL 1-9 级标准，针对硬科技创业场景优化
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TRLAssessment:
    """技术成熟度等级评估器"""
    
    # TRL 等级定义（符合 NASA/DoD/国标 GB/T 22900-2009）
    TRL_LEVELS = {
        1: {
            "name": "基本原理发现",
            "description": "观察到基础科学现象或提出理论假设，仅通过文献或实验验证其可行性",
            "indicators": ["理论研究完成", "核心算法/原理已验证", "可行性报告已出具"],
            "partner_need": "技术联合创始人、学术合伙人",
            "risk_level": "极高",
            "funding_stage": "种子轮/天使轮"
        },
        2: {
            "name": "技术方案形成",
            "description": "基于原理提出潜在应用概念，形成技术路线和概要设计",
            "indicators": ["技术路线已确定", "概要设计已完成", "应用场景已明确"],
            "partner_need": "CTO、系统架构师",
            "risk_level": "很高",
            "funding_stage": "天使轮"
        },
        3: {
            "name": "关键功能实验室验证",
            "description": "通过仿真或实验验证核心功能的可行性，关键部件性能测试通过",
            "indicators": ["关键功能已验证", "核心部件测试通过", "技术瓶颈已突破"],
            "partner_need": "工程合伙人、产品经理",
            "risk_level": "高",
            "funding_stage": "Pre-A轮"
        },
        4: {
            "name": "组件/实验板验证",
            "description": "实验室环境中集成关键组件并验证基本功能，低还原度原型",
            "indicators": ["实验板/样机已制作", "基本功能已验证", "组件集成测试通过"],
            "partner_need": "硬件合伙人、供应链专家",
            "risk_level": "中高",
            "funding_stage": "A轮"
        },
        5: {
            "name": "相关环境组件验证",
            "description": "在模拟或相关环境中验证组件级功能，接近实际使用条件",
            "indicators": ["相关环境测试通过", "性能指标基本达成", "可靠性初步验证"],
            "partner_need": "运营合伙人、市场验证专家",
            "risk_level": "中",
            "funding_stage": "A+轮"
        },
        6: {
            "name": "系统/子系统原型验证",
            "description": "在相关环境中进行系统或子系统级验证，高还原度原型",
            "indicators": ["系统原型已完成", "子系统集成验证通过", "性能达到设计要求"],
            "partner_need": "商业化合伙人、销售VP",
            "risk_level": "中低",
            "funding_stage": "B轮"
        },
        7: {
            "name": "操作环境原型演示",
            "description": "技术在实际操作环境中进行原型系统演示，真实场景验证",
            "indicators": ["现场演示成功", "真实环境测试通过", "用户初步反馈良好"],
            "partner_need": "大客户销售、行业专家",
            "risk_level": "低",
            "funding_stage": "B+轮/C轮"
        },
        8: {
            "name": "系统完成并通过测试",
            "description": "技术系统完成并通过全面测试，具备商业化条件",
            "indicators": ["系统定型完成", "全功能测试通过", "质量认证获得"],
            "partner_need": "规模化运营专家、财务合伙人",
            "risk_level": "很低",
            "funding_stage": "C轮/Pre-IPO"
        },
        9: {
            "name": "实际任务成功应用",
            "description": "技术系统在实际任务中成功应用，实现规模化商业化",
            "indicators": ["批量交付完成", "客户满意度高", "商业模式验证成功"],
            "partner_need": "战略合伙人、并购专家",
            "risk_level": "极低",
            "funding_stage": "IPO/并购"
        }
    }
    
    # 评估问卷（硬科技创业场景定制）
    QUESTIONS = [
        {
            "id": "q1",
            "category": "技术研发",
            "question": "您的核心技术目前处于什么阶段？",
            "options": [
                {"score": 1, "text": "仅完成理论研究/算法验证，尚无实物", "trl_hint": [1]},
                {"score": 2, "text": "已形成技术方案和概要设计", "trl_hint": [2]},
                {"score": 3, "text": "关键功能在实验室环境验证通过", "trl_hint": [3]},
                {"score": 4, "text": "实验板/功能样机已制作完成", "trl_hint": [4]},
                {"score": 5, "text": "在模拟环境/相关环境中验证通过", "trl_hint": [5]},
                {"score": 6, "text": "高还原度原型系统已集成验证", "trl_hint": [6]},
                {"score": 7, "text": "在实际操作环境中完成现场演示", "trl_hint": [7]},
                {"score": 8, "text": "产品定型完成并通过全功能测试", "trl_hint": [8]},
                {"score": 9, "text": "已实现批量生产和规模化应用", "trl_hint": [9]},
            ]
        },
        {
            "id": "q2",
            "category": "原型验证",
            "question": "您的产品原型验证程度如何？",
            "options": [
                {"score": 1, "text": "无实物原型，仅有仿真/理论模型", "trl_hint": [1,2]},
                {"score": 3, "text": "有功能单元验证件，未系统集成", "trl_hint": [3,4]},
                {"score": 5, "text": "系统集成原型完成，实验室验证通过", "trl_hint": [5,6]},
                {"score": 7, "text": "工程样机完成，现场环境测试通过", "trl_hint": [7,8]},
                {"score": 9, "text": "量产产品，已在市场规模化销售", "trl_hint": [9]},
            ]
        },
        {
            "id": "q3",
            "category": "测试环境",
            "question": "您的产品在哪些环境中完成了测试？",
            "options": [
                {"score": 1, "text": "仅理论分析/仿真验证", "trl_hint": [1,2]},
                {"score": 3, "text": "实验室理想环境", "trl_hint": [3,4]},
                {"score": 5, "text": "模拟/相关环境（接近真实条件）", "trl_hint": [5,6]},
                {"score": 7, "text": "实际操作环境（真实场景）", "trl_hint": [7,8]},
                {"score": 9, "text": "多样化实际应用场景，长期稳定运行", "trl_hint": [9]},
            ]
        },
        {
            "id": "q4",
            "category": "团队配置",
            "question": "您当前团队的技术-商业配比如何？",
            "options": [
                {"score": 2, "text": "纯技术团队，无商业化人员", "trl_hint": [1,2,3]},
                {"score": 4, "text": "技术为主，有兼职市场人员", "trl_hint": [4,5]},
                {"score": 6, "text": "技术+产品+市场，全职核心团队", "trl_hint": [6,7]},
                {"score": 8, "text": "完整团队，含供应链、销售、运营", "trl_hint": [8]},
                {"score": 9, "text": "规模化团队，各部门体系完善", "trl_hint": [9]},
            ]
        },
        {
            "id": "q5",
            "category": "客户验证",
            "question": "您的产品客户验证情况如何？",
            "options": [
                {"score": 1, "text": "无客户接触，仅有市场调研", "trl_hint": [1,2,3]},
                {"score": 3, "text": "有潜在客户意向/LOI", "trl_hint": [4,5]},
                {"score": 5, "text": "有试点客户，正在试用验证", "trl_hint": [6,7]},
                {"score": 7, "text": "有付费客户，完成商业验证", "trl_hint": [8]},
                {"score": 9, "text": "大量客户，复购率高，口碑良好", "trl_hint": [9]},
            ]
        },
        {
            "id": "q6",
            "category": "供应链",
            "question": "您的供应链和生产准备情况如何？",
            "options": [
                {"score": 2, "text": "无供应链规划，实验室自制", "trl_hint": [1,2,3,4]},
                {"score": 4, "text": "关键供应商已接触，有初步意向", "trl_hint": [5]},
                {"score": 6, "text": "核心供应链已确定，小批量可行", "trl_hint": [6,7]},
                {"score": 8, "text": "供应链体系完善，具备量产能力", "trl_hint": [8]},
                {"score": 9, "text": "规模化生产，成本控制优秀", "trl_hint": [9]},
            ]
        },
        {
            "id": "q7",
            "category": "知识产权",
            "question": "您的知识产权布局情况如何？",
            "options": [
                {"score": 2, "text": "无专利申请，技术秘密保护", "trl_hint": [1,2]},
                {"score": 4, "text": "核心专利已申请/受理中", "trl_hint": [3,4,5]},
                {"score": 6, "text": "核心专利已授权，有专利组合", "trl_hint": [6,7]},
                {"score": 8, "text": "完善专利布局，含国际专利", "trl_hint": [8]},
                {"score": 9, "text": "专利壁垒强大，行业标准制定者", "trl_hint": [9]},
            ]
        },
        {
            "id": "q8",
            "category": "资金需求",
            "question": "您当前的资金需求主要用于什么？",
            "options": [
                {"score": 2, "text": "技术研发/原理验证", "trl_hint": [1,2,3]},
                {"score": 4, "text": "原型开发/样机制作", "trl_hint": [4,5]},
                {"score": 6, "text": "产品定型/小规模试产", "trl_hint": [6,7]},
                {"score": 8, "text": "量产爬坡/市场推广", "trl_hint": [8]},
                {"score": 9, "text": "规模化扩张/并购整合", "trl_hint": [9]},
            ]
        }
    ]
    
    def __init__(self):
        self.responses = {}
        self.assessment_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def display_question(self, question: Dict) -> int:
        """显示单个问题并获取回答"""
        print(f"\n【{question['category']}】")
        print(f"Q: {question['question']}")
        print("-" * 50)
        
        for i, option in enumerate(question['options'], 1):
            print(f"  {i}. {option['text']}")
        
        while True:
            try:
                choice = input("\n请选择 (1-{}): ".format(len(question['options'])))
                idx = int(choice) - 1
                if 0 <= idx < len(question['options']):
                    return question['options'][idx]['score']
                else:
                    print("无效选择，请重试")
            except ValueError:
                print("请输入数字")
    
    def run_interactive(self) -> Dict:
        """运行交互式评估"""
        print("=" * 60)
        print("  TRL 技术成熟度自评工具")
        print("  满意解研究所 · 硬科技合伙人匹配系统")
        print("=" * 60)
        print("\n本评估基于 NASA/DoD TRL 1-9 级标准")
        print("针对硬科技创业场景优化")
        print("-" * 60)
        
        total_score = 0
        category_scores = {}
        
        for q in self.QUESTIONS:
            score = self.display_question(q)
            self.responses[q['id']] = {
                "question": q['question'],
                "score": score,
                "category": q['category']
            }
            total_score += score
            category_scores[q['category']] = category_scores.get(q['category'], 0) + score
        
        # 计算综合 TRL 等级
        avg_score = total_score / len(self.QUESTIONS)
        trl_level = self._calculate_trl_level(avg_score)
        
        result = {
            "assessment_date": self.assessment_date,
            "total_score": total_score,
            "max_possible": len(self.QUESTIONS) * 9,
            "average_score": round(avg_score, 2),
            "trl_level": trl_level,
            "category_scores": category_scores,
            "responses": self.responses,
            "trl_details": self.TRL_LEVELS[trl_level]
        }
        
        return result
    
    def _calculate_trl_level(self, avg_score: float) -> int:
        """根据平均分计算 TRL 等级"""
        if avg_score < 1.5:
            return 1
        elif avg_score < 2.5:
            return 2
        elif avg_score < 3.5:
            return 3
        elif avg_score < 4.5:
            return 4
        elif avg_score < 5.5:
            return 5
        elif avg_score < 6.5:
            return 6
        elif avg_score < 7.5:
            return 7
        elif avg_score < 8.5:
            return 8
        else:
            return 9
    
    def generate_report(self, result: Dict) -> str:
        """生成评估报告"""
        trl = result['trl_level']
        details = result['trl_details']
        
        report = f"""
{'='*60}
        TRL 技术成熟度评估报告
{'='*60}

评估时间: {result['assessment_date']}
综合得分: {result['average_score']}/9.0

{'─'*60}
【核心结论】TRL {trl} 级 - {details['name']}
{'─'*60}

{details['description']}

关键指标:
  ✓ {'✓ '.join(details['indicators'])}

风险等级: {details['risk_level']}
适配融资阶段: {details['funding_stage']}

{'─'*60}
【合伙人匹配建议】
{'─'*60}

当前最需要的合伙人角色:
  → {details['partner_need']}

基于 TRL {trl} 级的合伙人画像:
"""
        
        # 根据 TRL 级别生成具体建议
        partner_profiles = self._generate_partner_profiles(trl)
        for profile in partner_profiles:
            report += f"\n  ▪ {profile['role']}\n"
            report += f"    能力要求: {profile['skills']}\n"
            report += f"    股权建议: {profile['equity']}\n"
            report += f"    寻找渠道: {profile['channels']}"
        
        report += f"""

{'─'*60}
【维度得分分析】
{'─'*60}
"""
        for category, score in result['category_scores'].items():
            bar = "█" * int(score / 2) + "░" * (9 - int(score / 2))
            report += f"  {category:12s} [{bar}] {score}\n"
        
        report += f"""
{'─'*60}
【下一步行动建议】
{'─'*60}
"""
        
        actions = self._generate_action_items(trl)
        for i, action in enumerate(actions, 1):
            report += f"  {i}. {action}\n"
        
        report += f"""
{'='*60}
        满意解研究所 · 让技术找到对的人
{'='*60}
"""
        
        return report
    
    def _generate_partner_profiles(self, trl: int) -> List[Dict]:
        """根据 TRL 级别生成合伙人画像"""
        profiles = {
            1: [
                {"role": "技术联合创始人 (CTO)", "skills": "博士学位/顶级研究机构背景，核心技术领域专家", "equity": "20-40%（技术入股为主）", "channels": "学术会议、校友网络、研究院所"},
                {"role": "学术顾问", "skills": "行业知名教授，产学研经验丰富", "equity": "1-5% 顾问股", "channels": "导师推荐、学术合作"}
            ],
            2: [
                {"role": "工程合伙人 (VP Engineering)", "skills": "10年+工程经验，产品化经验丰富", "equity": "10-20%", "channels": "行业内推、技术社区"},
                {"role": "系统架构师", "skills": "复杂系统设计经验，技术视野宽广", "equity": "5-10%", "channels": "技术峰会、开源社区"}
            ],
            3: [
                {"role": "产品合伙人 (CPO)", "skills": "B2B/硬科技产品经验，技术背景强", "equity": "10-15%", "channels": "产品社群、行业展会"},
                {"role": "硬件合伙人", "skills": "供应链管理+硬件研发双重能力", "equity": "10-15%", "channels": "硬件孵化器、供应商网络"}
            ],
            4: [
                {"role": "供应链合伙人", "skills": "制造业资源深厚，成本控制能力", "equity": "5-15%", "channels": "产业带、行业协会"},
                {"role": "质量/测试专家", "skills": "ISO认证经验，可靠性工程背景", "equity": "3-8%", "channels": "质量管理协会、认证机构"}
            ],
            5: [
                {"role": "市场验证合伙人", "skills": "行业客户资源，试点项目推动能力", "equity": "5-12%", "channels": "行业峰会、客户推荐"},
                {"role": "应用工程师", "skills": "现场技术支持，客户需求转化", "equity": "3-8%", "channels": "行业展会、技术论坛"}
            ],
            6: [
                {"role": "商业化合伙人 (VP Sales)", "skills": "B2B销售经验，大客户开发能力", "equity": "8-15%", "channels": "销售社群、行业展会"},
                {"role": "客户成功负责人", "skills": "大客户服务经验，NPS优化", "equity": "3-8%", "channels": "客户成功社群、SaaS行业"}
            ],
            7: [
                {"role": "行业专家合伙人", "skills": "垂直行业深厚资源，标杆客户带动", "equity": "5-10%", "channels": "行业协会、标杆客户引荐"},
                {"role": "大客户经理", "skills": "复杂销售流程管理，高层关系", "equity": "3-8%", "channels": "行业活动、LinkedIn"}
            ],
            8: [
                {"role": "运营合伙人 (COO)", "skills": "规模化运营经验，流程体系建设", "equity": "5-10%", "channels": "运营社群、商学院"},
                {"role": "财务合伙人 (CFO)", "skills": "融资/IPO经验，财务管理", "equity": "3-8%", "channels": "投资机构、CFO俱乐部"}
            ],
            9: [
                {"role": "战略合伙人", "skills": "并购/IPO经验，行业资源整合", "equity": "3-8%", "channels": "投行、战略咨询公司"},
                {"role": "资本市场专家", "skills": "IPO/并购经验，投资者关系", "equity": "2-5%", "channels": "投行、律所"}
            ]
        }
        return profiles.get(trl, profiles[1])
    
    def _generate_action_items(self, trl: int) -> List[str]:
        """生成下一步行动建议"""
        actions = {
            1: [
                "完成核心技术的实验室验证，形成技术报告",
                "申请核心专利，建立知识产权壁垒",
                "参加学术会议，寻找技术联合创始人",
                "撰写商业计划书技术章节，明确应用场景"
            ],
            2: [
                "完成技术路线的详细设计，形成技术文档",
                "搭建核心团队，招募工程合伙人",
                "与潜在客户进行技术可行性沟通",
                "完成种子轮融资，支撑技术开发"
            ],
            3: [
                "制作功能原型，验证核心功能指标",
                "建立供应链初步联系，了解制造成本",
                "开展客户深度访谈，验证需求真实性",
                "申请天使轮融资，支撑原型开发"
            ],
            4: [
                "完成系统集成原型，进行内部测试",
                "建立核心供应商合作关系",
                "开展小范围客户试用，收集反馈",
                "完善产品文档和技术资料"
            ],
            5: [
                "在相关环境中完成系统验证测试",
                "制定可靠性测试计划并开始执行",
                "与3-5家潜在客户签署试点协议",
                "准备Pre-A轮融资材料"
            ],
            6: [
                "完成工程样机，进行现场演示",
                "建立完整供应链体系，确定代工厂",
                "获得首批付费客户，验证商业模式",
                "开展A轮融资，支撑量产准备"
            ],
            7: [
                "在实际客户现场完成部署验证",
                "建立客户成功案例，获取推荐信",
                "完成产品认证（如CCC、CE、FCC等）",
                "扩大销售团队，建立销售渠道"
            ],
            8: [
                "完成产品定型，启动规模量产",
                "建立售后服务体系",
                "拓展行业客户，建立标杆案例",
                "开展B轮融资，支撑市场扩张"
            ],
            9: [
                "优化生产成本，提升毛利率",
                "拓展国际市场，建立海外渠道",
                "探索并购机会，整合行业资源",
                "准备IPO或战略并购"
            ]
        }
        return actions.get(trl, actions[1])
    
    def save_result(self, result: Dict, filepath: str = None):
        """保存评估结果"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"trl_assessment_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 评估结果已保存: {filepath}")
        return filepath


def main():
    """主函数"""
    assessor = TRLAssessment()
    
    # 运行评估
    result = assessor.run_interactive()
    
    # 生成并显示报告
    report = assessor.generate_report(result)
    print(report)
    
    # 保存结果
    assessor.save_result(result)
    
    # 询问是否保存报告
    save_report = input("\n是否保存详细报告到文本文件? (y/n): ").lower()
    if save_report == 'y':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"trl_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ 报告已保存: {report_file}")


if __name__ == "__main__":
    main()
