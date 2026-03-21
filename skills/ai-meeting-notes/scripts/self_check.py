#!/usr/bin/env python3
"""
self_check.py
准确性自检模块 - S5标准实现

功能：
- 完整性检查
- 置信度评分
- 质量报告生成
"""

import json
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CheckResult:
    """检查结果"""
    check_name: str
    passed: bool
    score: float
    weight: float
    message: str

class SelfCheckEngine:
    """自检引擎"""
    
    # 检查项定义: (名称, 权重, 检查函数)
    CHECK_ITEMS = {
        'title': ('会议主题提取', 0.15),
        'date': ('日期识别', 0.10),
        'attendees': ('参会人员识别', 0.15),
        'summary': ('摘要质量', 0.20),
        'action_items': ('行动项提取', 0.25),
        'owner': ('责任人关联', 0.10),
        'deadline': ('截止时间解析', 0.05)
    }
    
    def __init__(self):
        self.results: List[CheckResult] = []
    
    def run_full_check(self, result_data: Dict) -> Dict:
        """运行完整自检"""
        self.results = []
        
        # 逐项检查
        for key, (name, weight) in self.CHECK_ITEMS.items():
            check_method = getattr(self, f'_check_{key}', self._check_default)
            passed, score, message = check_method(result_data)
            
            self.results.append(CheckResult(
                check_name=name,
                passed=passed,
                score=score,
                weight=weight,
                message=message
            ))
        
        return self._generate_report()
    
    def _check_title(self, data: Dict) -> Tuple[bool, float, str]:
        """检查主题提取"""
        title = data.get('metadata', {}).get('title', '')
        if not title or title == '未命名会议':
            return False, 0.3, "未能提取有效主题，使用默认名称"
        if len(title) < 5:
            return True, 0.7, "主题过短，可能不够明确"
        return True, 0.95, "主题提取成功"
    
    def _check_date(self, data: Dict) -> Tuple[bool, float, str]:
        """检查日期识别"""
        date = data.get('metadata', {}).get('date', '')
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            return True, 1.0, f"日期格式标准: {date}"
        if re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', date):
            return True, 0.8, f"日期格式非标准: {date}"
        return False, 0.3, "日期识别失败，使用当前日期"
    
    def _check_attendees(self, data: Dict) -> Tuple[bool, float, str]:
        """检查参会人员"""
        attendees = data.get('metadata', {}).get('attendees', [])
        count = len(attendees)
        if count == 0:
            return False, 0.0, "未识别到参会人员"
        if count < 2:
            return True, 0.6, f"仅识别到1名参会人员: {attendees[0]}"
        if count >= 3:
            return True, 0.95, f"识别到{count}名参会人员"
        return True, 0.8, f"识别到{count}名参会人员"
    
    def _check_summary(self, data: Dict) -> Tuple[bool, float, str]:
        """检查摘要质量"""
        summary = data.get('summary', '')
        length = len(summary)
        if length < 10:
            return False, 0.3, "摘要过短，信息覆盖不足"
        if length < 30:
            return True, 0.6, "摘要较短，建议补充"
        if length > 100:
            return True, 0.95, "摘要详细，覆盖充分"
        return True, 0.85, "摘要质量良好"
    
    def _check_action_items(self, data: Dict) -> Tuple[bool, float, str]:
        """检查行动项"""
        items = data.get('action_items', [])
        count = len(items)
        if count == 0:
            return True, 0.5, "未提取到行动项（可能确实无任务）"
        if count > 20:
            return True, 0.7, f"提取到{count}项行动项，数量较多，可能有误判"
        return True, min(0.95, 0.5 + count * 0.1), f"提取到{count}项行动项"
    
    def _check_owner(self, data: Dict) -> Tuple[bool, float, str]:
        """检查责任人"""
        items = data.get('action_items', [])
        if not items:
            return True, 0.5, "无行动项，跳过责任人检查"
        
        unknown = sum(1 for item in items if item.get('owner') in ['@待确认', '@Team', ''])
        total = len(items)
        ratio = (total - unknown) / total
        
        if ratio >= 0.9:
            return True, 0.95, f"{total}项任务中{total-unknown}项有明确责任人"
        if ratio >= 0.7:
            return True, 0.75, f"{unknown}项任务责任人待确认"
        return False, ratio, f"{unknown}项任务缺少责任人，占比过高"
    
    def _check_deadline(self, data: Dict) -> Tuple[bool, float, str]:
        """检查截止时间"""
        items = data.get('action_items', [])
        if not items:
            return True, 0.5, "无行动项，跳过截止时间检查"
        
        absolute = sum(1 for item in items if item.get('deadline_type') == 'absolute')
        total = len(items)
        ratio = absolute / total
        
        if ratio >= 0.8:
            return True, 0.95, f"{absolute}/{total}项任务有明确截止时间"
        if ratio >= 0.5:
            return True, 0.75, f"{total-absolute}项任务截止时间待确认"
        return True, 0.6, f"多数任务缺少明确截止时间"
    
    def _check_default(self, data: Dict) -> Tuple[bool, float, str]:
        """默认检查"""
        return True, 0.5, "默认通过"
    
    def _generate_report(self) -> Dict:
        """生成检查报告"""
        total_score = sum(r.score * r.weight for r in self.results)
        total_weight = sum(r.weight for r in self.results)
        weighted_score = total_score / total_weight if total_weight > 0 else 0
        
        passed_count = sum(1 for r in self.results if r.passed)
        
        # 确定等级
        if weighted_score >= 0.9:
            grade = 'A'
            grade_desc = '优秀'
        elif weighted_score >= 0.8:
            grade = 'B'
            grade_desc = '良好'
        elif weighted_score >= 0.7:
            grade = 'C'
            grade_desc = '合格'
        elif weighted_score >= 0.6:
            grade = 'D'
            grade_desc = '待改进'
        else:
            grade = 'F'
            grade_desc = '不合格'
        
        return {
            'overall_score': round(weighted_score, 2),
            'grade': grade,
            'grade_description': grade_desc,
            'passed_checks': passed_count,
            'total_checks': len(self.results),
            'check_details': [
                {
                    'name': r.check_name,
                    'passed': r.passed,
                    'score': round(r.score, 2),
                    'weight': r.weight,
                    'message': r.message
                }
                for r in self.results
            ],
            'suggestions': self._generate_suggestions()
        }
    
    def _generate_suggestions(self) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        for result in self.results:
            if not result.passed or result.score < 0.7:
                if result.check_name == '会议主题提取':
                    suggestions.append("建议在会议记录开头明确标注会议主题")
                elif result.check_name == '日期识别':
                    suggestions.append("建议使用标准日期格式：YYYY-MM-DD")
                elif result.check_name == '参会人员识别':
                    suggestions.append("建议使用@姓名格式标注参会人员")
                elif result.check_name == '行动项提取':
                    suggestions.append("建议使用明确行动词（如'完成'、'提交'）")
                elif result.check_name == '责任人关联':
                    suggestions.append("建议明确每项任务的负责人")
                elif result.check_name == '截止时间解析':
                    suggestions.append("建议明确任务截止时间")
        
        return suggestions[:5]  # 最多5条建议

def format_check_report(report: Dict) -> str:
    """格式化检查报告为Markdown"""
    lines = [
        "## 🔍 准确性自检报告",
        "",
        f"**整体评分**: {report['overall_score']:.0%} ({report['grade']}-{report['grade_description']})",
        f"**通过项**: {report['passed_checks']}/{report['total_checks']}",
        "",
        "### 详细检查项",
        "",
        "| 检查项 | 状态 | 得分 | 权重 | 说明 |",
        "|--------|------|------|------|------|"
    ]
    
    for detail in report['check_details']:
        status = '✅' if detail['passed'] else '❌'
        lines.append(f"| {detail['name']} | {status} | {detail['score']:.0%} | {detail['weight']:.0%} | {detail['message']} |")
    
    if report['suggestions']:
        lines.extend([
            "",
            "### 💡 改进建议",
            ""
        ])
        for i, suggestion in enumerate(report['suggestions'], 1):
            lines.append(f"{i}. {suggestion}")
    
    return '\n'.join(lines)

# 命令行接口
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 self_check.py <result.json>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    engine = SelfCheckEngine()
    report = engine.run_full_check(data)
    
    print(format_check_report(report))
    print(f"\n最终评分: {report['overall_score']:.0%} - {report['grade_description']}")
