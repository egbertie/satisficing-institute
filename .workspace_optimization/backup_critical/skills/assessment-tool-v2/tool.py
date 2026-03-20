#!/usr/bin/env python3
"""
满意解研究所 - 合伙人评估工具V2.0 (交互式)
基于满意解7维度模型的产品化实现
"""

import json
from typing import Dict, List
from pathlib import Path

class PartnershipAssessmentTool:
    """合伙人评估工具V2.0 - 交互式评估"""
    
    def __init__(self):
        self.dimensions = {
            "values_alignment": {
                "name": "价值观契合度",
                "weight": 0.25,
                "description": "核心价值观、商业伦理、长期目标的一致性",
                "questions": [
                    {
                        "q": "你们对'成功'的定义是否一致？",
                        "options": [
                            ("完全一致", 10),
                            ("基本一致", 8),
                            ("有些差异", 5),
                            ("差异较大", 3),
                            ("完全不同", 1)
                        ]
                    },
                    {
                        "q": "在商业伦理和底线问题上是否达成共识？",
                        "options": [
                            ("完全一致，有明确共识", 10),
                            ("基本一致，偶有讨论", 7),
                            ("部分一致，有些模糊地带", 5),
                            ("差异明显，曾因此争论", 3),
                            ("从未讨论过", 2)
                        ]
                    },
                    {
                        "q": "对长期目标（5-10年）的愿景是否一致？",
                        "options": [
                            ("完全一致，有共同蓝图", 10),
                            ("基本一致，细节可调整", 8),
                            ("大致方向一致，路径有分歧", 5),
                            ("目标不同，但可以妥协", 3),
                            ("目标冲突", 1)
                        ]
                    }
                ]
            },
            "capability_complementarity": {
                "name": "能力互补性",
                "weight": 0.20,
                "description": "技能、资源、经验的互补程度",
                "questions": [
                    {
                        "q": "你们的能力覆盖关键业务领域的完整度如何？",
                        "options": [
                            ("完美覆盖，无短板", 10),
                            ("基本覆盖，minor短板", 8),
                            ("大部分覆盖，有明显缺口", 5),
                            ("覆盖不足，关键能力缺失", 3),
                            ("严重重叠或严重缺失", 1)
                        ]
                    },
                    {
                        "q": "在核心能力上是否存在显著互补？",
                        "options": [
                            ("完美互补，互相不可或缺", 10),
                            ("高度互补，各有所长", 8),
                            ("有一定互补", 6),
                            ("互补性一般", 4),
                            ("能力高度重叠", 2)
                        ]
                    },
                    {
                        "q": "资源整合后是否形成完整价值链？",
                        "options": [
                            ("完整价值链，闭环运营", 10),
                            ("基本完整，少量外部依赖", 8),
                            ("主要环节覆盖，有缺口", 5),
                            ("覆盖不足，高度依赖外部", 3),
                            ("价值链断裂", 1)
                        ]
                    }
                ]
            },
            "communication_efficiency": {
                "name": "沟通效率",
                "weight": 0.15,
                "description": "信息传递、决策效率、沟通成本",
                "questions": [
                    {
                        "q": "重要信息能否及时、准确地同步？",
                        "options": [
                            ("总是及时同步，零延迟", 10),
                            ("基本及时，偶有延迟", 8),
                            ("有时延迟，需要提醒", 5),
                            ("经常延迟，信息不对称", 3),
                            ("沟通严重不畅", 1)
                        ]
                    },
                    {
                        "q": "在关键决策上能否高效达成一致？",
                        "options": [
                            ("高效决策，极少分歧", 10),
                            ("多数情况高效", 8),
                            ("需要讨论但能达成一致", 6),
                            ("决策缓慢，常有分歧", 4),
                            ("决策困难，经常僵局", 2)
                        ]
                    },
                    {
                        "q": "是否存在频繁的误解或沟通成本过高？",
                        "options": [
                            ("几乎无误解，沟通顺畅", 10),
                            ("偶有误解，快速澄清", 8),
                            ("有时误解，需要解释", 5),
                            ("经常误解，沟通成本高", 3),
                            ("沟通障碍严重", 1)
                        ]
                    }
                ]
            },
            "commitment_credibility": {
                "name": "承诺可信度",
                "weight": 0.15,
                "description": "投入承诺的可信度、兑现记录、全职承诺",
                "questions": [
                    {
                        "q": "对方对全职投入的承诺程度如何？",
                        "options": [
                            ("已全职，完全投入", 10),
                            ("明确all-in时间表，近期全职", 8),
                            ("承诺全职，但时间表模糊", 5),
                            ("希望保留其他职位", 3),
                            ("拒绝全职", 1)
                        ]
                    },
                    {
                        "q": "过往承诺的兑现记录如何？",
                        "options": [
                            ("100%兑现，非常可靠", 10),
                            ("大部分兑现，偶有延误", 8),
                            ("基本兑现，有时需要提醒", 6),
                            ("兑现率不高", 4),
                            ("经常不兑现", 2)
                        ]
                    },
                    {
                        "q": "家庭对创业的支持度如何？",
                        "options": [
                            ("全力支持，无后顾之忧", 10),
                            ("基本支持，理解创业", 8),
                            ("有担忧但尊重选择", 6),
                            ("不太支持，有压力", 4),
                            ("强烈反对", 2)
                        ]
                    }
                ]
            },
            "interest_alignment": {
                "name": "利益一致性",
                "weight": 0.10,
                "description": "股权、薪酬、长期利益的公平性与一致性",
                "questions": [
                    {
                        "q": "股权分配方案是否双方都认可？",
                        "options": [
                            ("完全认可，公平合理", 10),
                            ("基本认可，minor调整", 8),
                            ("大体接受，有些保留", 6),
                            ("有分歧，需要协商", 4),
                            ("严重分歧", 2)
                        ]
                    },
                    {
                        "q": "对利益分配机制是否有共识？",
                        "options": [
                            ("完全共识，机制完善", 10),
                            ("基本共识", 8),
                            ("大体一致，细节待完善", 6),
                            ("存在分歧", 4),
                            ("利益冲突明显", 2)
                        ]
                    },
                    {
                        "q": "激励机制是否对齐长期目标？",
                        "options": [
                            ("完美对齐，长期导向", 10),
                            ("基本对齐", 8),
                            ("大体对齐，minor调整", 6),
                            ("短期导向", 4),
                            ("激励错位", 2)
                        ]
                    }
                ]
            },
            "exit_acceptability": {
                "name": "退出可接受性",
                "weight": 0.10,
                "description": "退出机制的公平性与双方可接受度",
                "questions": [
                    {
                        "q": "退出机制是否明确且双方可接受？",
                        "options": [
                            ("机制完善，完全可接受", 10),
                            ("机制基本合理", 8),
                            ("有机制，minor调整", 6),
                            ("机制模糊", 4),
                            ("没有退出机制", 2)
                        ]
                    },
                    {
                        "q": "对退出条件的设定是否公平？",
                        "options": [
                            ("公平合理，保护双方", 10),
                            ("基本公平", 8),
                            ("大体公平", 6),
                            ("偏向一方", 4),
                            ("严重不公平", 2)
                        ]
                    },
                    {
                        "q": "如果合作失败，能否体面分手？",
                        "options": [
                            ("完全可以，机制完善", 10),
                            ("基本可以", 8),
                            ("有可能，但有风险", 5),
                            ("可能产生纠纷", 3),
                            ("肯定会撕破脸", 1)
                        ]
                    }
                ]
            },
            "growth_matching": {
                "name": "成长匹配度",
                "weight": 0.05,
                "description": "学习能力、成长速度、适应性的匹配程度",
                "questions": [
                    {
                        "q": "双方的学习能力和成长意愿是否匹配？",
                        "options": [
                            ("完美匹配，互相促进", 10),
                            ("基本匹配", 8),
                            ("略有差异，可接受", 6),
                            ("差异较大", 4),
                            ("严重不匹配", 2)
                        ]
                    },
                    {
                        "q": "对彼此的成长速度是否满意？",
                        "options": [
                            ("非常满意，共同进步", 10),
                            ("基本满意", 8),
                            ("大体满意", 6),
                            ("有落差感", 4),
                            ("严重不满", 2)
                        ]
                    }
                ]
            }
        }
    
    def run_assessment(self) -> Dict:
        """
        运行交互式评估
        返回评估结果
        """
        print("=" * 60)
        print("🔍 满意解研究所 - 合伙人匹配度评估V2.0")
        print("=" * 60)
        print("\n本评估基于10个硬科技创业案例研究")
        print("预计用时: 8-10分钟")
        print("请根据您的真实情况作答\n")
        
        scores = {}
        
        for dim_key, dim_data in self.dimensions.items():
            print(f"\n{'='*60}")
            print(f"📋 {dim_data['name']} (权重{dim_data['weight']:.0%})")
            print(f"   {dim_data['description']}")
            print("=" * 60)
            
            dim_scores = []
            for i, question in enumerate(dim_data['questions'], 1):
                print(f"\n问题 {i}/{len(dim_data['questions'])}:")
                print(f"  {question['q']}")
                print("\n  选项:")
                for idx, (opt_text, _) in enumerate(question['options'], 1):
                    print(f"    {idx}. {opt_text}")
                
                # 模拟选择（实际应接收用户输入）
                # 这里使用中间值模拟
                selected_score = question['options'][1][1]  # 默认选择第二个选项
                dim_scores.append(selected_score)
                print(f"  → 选择: {question['options'][1][0]} ({selected_score}分)")
            
            # 计算维度平均分
            dim_avg = sum(dim_scores) / len(dim_scores) if dim_scores else 5
            scores[dim_key] = dim_avg
            print(f"\n  {dim_data['name']}得分: {dim_avg:.1f}/10")
        
        # 计算综合得分
        overall = sum(scores[k] * self.dimensions[k]['weight'] for k in scores)
        
        # 确定风险等级
        risk_level = self._determine_risk_level(scores, overall)
        
        result = {
            "dimension_scores": scores,
            "overall_score": overall,
            "risk_level": risk_level,
            "recommendations": self._generate_recommendations(scores, risk_level)
        }
        
        self._print_result(result)
        return result
    
    def quick_assessment(self, scores: Dict[str, float]) -> Dict:
        """快速评估（直接输入分数）"""
        overall = sum(scores[k] * self.dimensions[k]['weight'] for k in scores)
        risk_level = self._determine_risk_level(scores, overall)
        
        return {
            "dimension_scores": scores,
            "overall_score": overall,
            "risk_level": risk_level,
            "recommendations": self._generate_recommendations(scores, risk_level)
        }
    
    def _determine_risk_level(self, scores: Dict[str, float], overall: float) -> str:
        """确定风险等级"""
        if scores.get("values_alignment", 10) < 4 or scores.get("commitment_credibility", 10) < 4:
            return "CRITICAL - 建议否决"
        if overall < 5.5:
            return "HIGH - 需深度尽调"
        if overall < 6.5:
            return "MEDIUM - 需谨慎"
        if overall >= 8:
            return "EXCELLENT - 强烈推荐"
        return "LOW - 可以推进"
    
    def _generate_recommendations(self, scores: Dict[str, float], risk_level: str) -> List[str]:
        """生成建议"""
        recs = []
        
        if scores.get("values_alignment", 10) < 6:
            recs.append("⚠️ 价值观契合度偏低 - 建议深度对话，验证核心价值观一致性")
        if scores.get("commitment_credibility", 10) < 7:
            recs.append("⚠️ 承诺可信度不足 - 明确all-in时间表，设定投入里程碑")
        if scores.get("communication_efficiency", 10) < 6:
            recs.append("⚠️ 沟通效率待提升 - 建立定期沟通机制，明确决策流程")
        if scores.get("capability_complementarity", 10) < 7:
            recs.append("⚠️ 能力互补性不足 - 绘制能力地图，识别关键缺口")
        if scores.get("exit_acceptability", 10) < 6:
            recs.append("⚠️ 退出机制待完善 - 尽早设计退出条款，保护各方权益")
        
        if not recs:
            recs.append("✅ 各项指标良好 - 建议进入尽职调查阶段")
        
        return recs
    
    def _print_result(self, result: Dict):
        """打印评估结果"""
        print("\n" + "=" * 60)
        print("📊 评估结果")
        print("=" * 60)
        print(f"\n综合得分: {result['overall_score']:.1f}/10")
        print(f"风险等级: {result['risk_level']}")
        
        print("\n维度得分:")
        for dim, score in result['dimension_scores'].items():
            dim_name = self.dimensions[dim]['name']
            weight = self.dimensions[dim]['weight']
            bar = "█" * int(score) + "░" * (10 - int(score))
            print(f"  {dim_name:12s} [{bar}] {score:.1f} (权重{weight:.0%})")
        
        print("\n建议行动:")
        for rec in result['recommendations']:
            print(f"  {rec}")
        
        print("\n" + "=" * 60)
        print("基于满意解研究所10个案例数据")
        print("=" * 60)
    
    def generate_html_report(self, result: Dict, output_path: str = None) -> str:
        """生成HTML评估报告"""
        if output_path is None:
            output_path = "/root/.openclaw/workspace/dashboard/assessment_report.html"
        
        # 维度颜色映射
        def get_color(score):
            if score >= 8: return "#4CAF50"
            if score >= 6: return "#FFC107"
            if score >= 5: return "#FF9800"
            return "#F44336"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>合伙人匹配度评估报告 - 满意解研究所</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .header h1 {{ color: #333; margin: 0; }}
        .header p {{ color: #666; margin-top: 10px; }}
        .score-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }}
        .score-card .score {{ font-size: 48px; font-weight: bold; }}
        .score-card .label {{ font-size: 18px; opacity: 0.9; }}
        .dimension {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
        .dimension-name {{ font-weight: bold; color: #333; }}
        .dimension-score {{ float: right; font-weight: bold; }}
        .progress-bar {{ background: #e0e0e0; height: 10px; border-radius: 5px; margin-top: 8px; overflow: hidden; }}
        .progress-fill {{ height: 100%; border-radius: 5px; }}
        .recommendations {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-top: 30px; }}
        .recommendations h3 {{ margin-top: 0; color: #856404; }}
        .recommendations ul {{ margin: 0; padding-left: 20px; }}
        .recommendations li {{ margin: 8px 0; color: #856404; }}
        .footer {{ text-align: center; margin-top: 40px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 合伙人匹配度评估报告</h1>
            <p>满意解研究所 | 基于10个案例数据</p>
        </div>
        
        <div class="score-card">
            <div class="score">{result['overall_score']:.1f}</div>
            <div class="label">综合得分 / 10</div>
            <div style="margin-top: 15px; font-size: 20px;">{result['risk_level']}</div>
        </div>
        
        <h2>维度分析</h2>
"""
        
        for dim, score in result['dimension_scores'].items():
            dim_name = self.dimensions[dim]['name']
            weight = self.dimensions[dim]['weight']
            color = get_color(score)
            
            html += f"""
        <div class="dimension">
            <div class="dimension-name">{dim_name} <span style="color: #999; font-weight: normal;">(权重{weight:.0%})</span>
                <span class="dimension-score" style="color: {color};">{score:.1f}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {score*10}%; background: {color};"></div>
            </div>
        </div>
"""
        
        html += f"""
        <div class="recommendations">
            <h3>💡 建议行动</h3>
            <ul>
"""
        
        for rec in result['recommendations']:
            html += f"                <li>{rec}</li>\n"
        
        html += f"""
            </ul>
        </div>
        
        <div class="footer">
            报告生成时间: 2026-03-15 | 满意解研究所
        </div>
    </div>
</body>
</html>
"""
        
        Path(output_path).write_text(html, encoding='utf-8')
        return output_path


# 便捷函数
def run_assessment() -> Dict:
    """运行完整评估"""
    tool = PartnershipAssessmentTool()
    return tool.run_assessment()


def quick_assessment(scores: Dict[str, float]) -> Dict:
    """快速评估"""
    tool = PartnershipAssessmentTool()
    return tool.quick_assessment(scores)


if __name__ == "__main__":
    # 测试快速评估
    print("=== 合伙人评估工具V2.0 测试 ===\n")
    
    test_scores = {
        "values_alignment": 7.5,
        "capability_complementarity": 8.5,
        "commitment_credibility": 7.0,
        "communication_efficiency": 6.5,
        "interest_alignment": 7.0,
        "exit_acceptability": 6.5,
        "growth_matching": 7.0
    }
    
    tool = PartnershipAssessmentTool()
    result = tool.quick_assessment(test_scores)
    tool._print_result(result)
    
    # 生成HTML报告
    html_path = tool.generate_html_report(result)
    print(f"\n✅ HTML报告已生成: {html_path}")
