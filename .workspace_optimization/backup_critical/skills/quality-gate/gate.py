#!/usr/bin/env python3
"""
质量门控机制 - 输出前的多重质量检查
自检 → 蓝军检查 → 交付确认
"""

import json
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class QualityLevel(Enum):
    DRAFT = "draft"        # 草稿，内部使用
    REVIEW = "review"      # 待审核，需检查
    APPROVED = "approved"  # 已审核，可交付
    PUBLISHED = "published" # 已发布，对外可见

class QualityGate:
    """质量门控中心"""
    
    def __init__(self, config_path=None):
        self.checkpoints = {
            "self_check": SelfCheckPoint(),
            "blue_team": BlueTeamCheckPoint(),
            "delivery": DeliveryCheckPoint()
        }
        self.quality_log = []
    
    def process(self, content, content_type, context=None):
        """
        处理内容通过质量门控
        
        Args:
            content: 待检查的内容
            content_type: 内容类型 (report/analysis/decision/document)
            context: 上下文信息
        
        Returns:
            质量检查报告
        """
        context = context or {}
        gate_report = {
            "timestamp": datetime.now().isoformat(),
            "content_type": content_type,
            "content_hash": self._hash_content(content),
            "checkpoints": {},
            "overall_status": "pending",
            "can_proceed": False
        }
        
        # 第一关：自检
        print("🔍 第一关：AI自检...")
        self_check = self.checkpoints["self_check"].check(content, content_type, context)
        gate_report["checkpoints"]["self_check"] = self_check
        
        if not self_check["passed"]:
            gate_report["overall_status"] = "failed_at_self_check"
            gate_report["can_proceed"] = False
            self._log_gate(gate_report)
            return gate_report
        
        # 第二关：蓝军检查
        print("🔍 第二关：蓝军检查...")
        blue_check = self.checkpoints["blue_team"].check(content, content_type, context)
        gate_report["checkpoints"]["blue_check"] = blue_check
        
        if blue_check["risk_level"] == "critical":
            gate_report["overall_status"] = "failed_at_blue_check"
            gate_report["can_proceed"] = False
            self._log_gate(gate_report)
            return gate_report
        
        # 第三关：交付确认（仅高风险内容）
        risk_score = self._calculate_risk(content_type, context)
        if risk_score >= 70:
            print("🔍 第三关：交付确认（高风险）...")
            delivery_check = self.checkpoints["delivery"].check(content, content_type, context)
            gate_report["checkpoints"]["delivery_check"] = delivery_check
            gate_report["can_proceed"] = delivery_check["confirmed"]
        else:
            gate_report["can_proceed"] = True
        
        gate_report["overall_status"] = "approved" if gate_report["can_proceed"] else "pending_confirmation"
        self._log_gate(gate_report)
        
        return gate_report
    
    def _hash_content(self, content):
        """生成内容哈希"""
        import hashlib
        return hashlib.md5(str(content).encode()).hexdigest()[:16]
    
    def _calculate_risk(self, content_type, context):
        """计算风险分数"""
        base_risk = {
            "report": 30,
            "analysis": 40,
            "decision": 80,
            "document": 20,
            "notification": 10
        }.get(content_type, 50)
        
        # 外部发送增加风险
        if context.get("external"):
            base_risk += 30
        
        # 涉及金额增加风险
        if context.get("financial"):
            base_risk += 20
        
        return min(base_risk, 100)
    
    def _log_gate(self, report):
        """记录门控日志"""
        self.quality_log.append(report)


class SelfCheckPoint:
    """自检关卡 - AI自我检查"""
    
    def check(self, content, content_type, context):
        """执行自检"""
        checks = {
            "completeness": self._check_completeness(content, content_type),
            "format": self._check_format(content, content_type),
            "logic": self._check_logic(content),
            "sources": self._check_sources(content)
        }
        
        all_passed = all(c["passed"] for c in checks.values())
        
        return {
            "checkpoint": "self_check",
            "passed": all_passed,
            "checks": checks,
            "suggestions": [c["suggestion"] for c in checks.values() if c.get("suggestion")]
        }
    
    def _check_completeness(self, content, content_type):
        """检查完整性"""
        templates = {
            "report": ["背景", "分析", "结论", "建议"],
            "analysis": ["数据", "方法", "发现", "局限"],
            "decision": ["背景", "选项", "评估", "决策", "风险"]
        }
        
        required = templates.get(content_type, [])
        content_str = str(content).lower()
        
        missing = []
        for item in required:
            if item not in content_str:
                missing.append(item)
        
        return {
            "name": "完整性检查",
            "passed": len(missing) == 0,
            "score": (len(required) - len(missing)) / len(required) if required else 1.0,
            "missing": missing,
            "suggestion": f"建议补充: {', '.join(missing)}" if missing else None
        }
    
    def _check_format(self, content, content_type):
        """检查格式规范"""
        issues = []
        
        # 检查标题层级
        if "# " not in str(content) and content_type in ["report", "analysis"]:
            issues.append("缺少一级标题")
        
        # 检查列表使用
        if "- " not in str(content) and len(str(content)) > 500:
            issues.append("建议使用列表提升可读性")
        
        return {
            "name": "格式规范检查",
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestion": f"格式问题: {'; '.join(issues)}" if issues else None
        }
    
    def _check_logic(self, content):
        """检查逻辑一致性"""
        # 简化版：检查明显的逻辑问题
        content_str = str(content)
        
        issues = []
        
        # 检查矛盾表述
        contradictions = [
            ("必然", "可能"),
            ("全部", "部分"),
            ("绝对", "相对")
        ]
        
        for strong, weak in contradictions:
            if strong in content_str and weak in content_str:
                # 简单检查是否在同一句
                sentences = content_str.split("。")
                for sent in sentences:
                    if strong in sent and weak in sent:
                        issues.append(f"潜在逻辑矛盾: '{strong}'与'{weak}'")
        
        return {
            "name": "逻辑一致性检查",
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestion": f"逻辑问题: {'; '.join(issues)}" if issues else None
        }
    
    def _check_sources(self, content):
        """检查数据来源"""
        content_str = str(content)
        
        # 检查是否有数据支撑
        has_data = any(kw in content_str for kw in ["数据", "统计", "调查显示", "根据"])
        has_source = any(kw in content_str for kw in ["来源", "引用", "参考"])
        
        if not has_data and len(content_str) > 300:
            return {
                "name": "数据来源检查",
                "passed": False,
                "suggestion": "建议添加数据支撑或来源说明"
            }
        
        return {
            "name": "数据来源检查",
            "passed": True
        }


class BlueTeamCheckPoint:
    """蓝军检查关卡 - 批判性审查"""
    
    def check(self, content, content_type, context):
        """执行蓝军检查"""
        checks = {
            "assumptions": self._check_assumptions(content),
            "risks": self._check_risks(content, context),
            "biases": self._check_biases(content),
            "edge_cases": self._check_edge_cases(content)
        }
        
        # 计算风险等级
        risk_scores = [c["risk_score"] for c in checks.values()]
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        risk_level = "low"
        if avg_risk >= 80:
            risk_level = "critical"
        elif avg_risk >= 60:
            risk_level = "high"
        elif avg_risk >= 40:
            risk_level = "medium"
        
        return {
            "checkpoint": "blue_team",
            "risk_level": risk_level,
            "risk_score": avg_risk,
            "checks": checks,
            "red_flags": [c["issue"] for c in checks.values() if c.get("issue")]
        }
    
    def _check_assumptions(self, content):
        """检查隐含假设"""
        content_str = str(content)
        
        # 常见的隐含假设关键词
        assumption_keywords = ["显然", "众所周知", "默认", "当然"]
        found = [kw for kw in assumption_keywords if kw in content_str]
        
        risk_score = min(len(found) * 15, 50)
        
        return {
            "name": "隐含假设检查",
            "risk_score": risk_score,
            "issue": f"发现{len(found)}处未经验证的假设: {', '.join(found)}" if found else None
        }
    
    def _check_risks(self, content, context):
        """检查风险识别"""
        content_str = str(content).lower()
        
        # 检查是否讨论了风险
        risk_keywords = ["风险", "问题", "挑战", "局限", "不足"]
        has_risk_discussion = any(kw in content_str for kw in risk_keywords)
        
        # 高风险内容必须讨论风险
        is_high_risk = context.get("external") or context.get("financial")
        
        if is_high_risk and not has_risk_discussion:
            return {
                "name": "风险识别检查",
                "risk_score": 80,
                "issue": "高风险内容未讨论潜在风险和局限"
            }
        
        return {
            "name": "风险识别检查",
            "risk_score": 20 if has_risk_discussion else 50,
            "issue": None if has_risk_discussion else "建议补充风险分析"
        }
    
    def _check_biases(self, content):
        """检查认知偏差"""
        content_str = str(content)
        
        # 常见偏差信号
        bias_signals = {
            "确认偏差": ["正如我们所知", "显然证明", "完全符合"],
            "乐观偏差": ["肯定能", "必然成功", "绝对没问题"],
            "权威偏差": ["专家说", "权威认为", "众所周知"]
        }
        
        found_biases = []
        for bias_type, signals in bias_signals.items():
            if any(s in content_str for s in signals):
                found_biases.append(bias_type)
        
        risk_score = min(len(found_biases) * 20, 60)
        
        return {
            "name": "认知偏差检查",
            "risk_score": risk_score,
            "issue": f"可能存在偏差: {', '.join(found_biases)}" if found_biases else None
        }
    
    def _check_edge_cases(self, content):
        """检查边界情况"""
        content_str = str(content).lower()
        
        # 检查是否考虑了异常情况
        edge_keywords = ["如果", "假设", "例外", "特殊情况", "边界"]
        has_edge_consideration = any(kw in content_str for kw in edge_keywords)
        
        # 策略建议类内容应该有边界考虑
        is_strategy = "建议" in content_str or "应该" in content_str
        
        if is_strategy and not has_edge_consideration:
            return {
                "name": "边界情况检查",
                "risk_score": 50,
                "issue": "策略建议未考虑边界情况和例外"
            }
        
        return {
            "name": "边界情况检查",
            "risk_score": 20,
            "issue": None
        }


class DeliveryCheckPoint:
    """交付确认关卡 - 高风险内容的人工确认"""
    
    def check(self, content, content_type, context):
        """执行交付确认"""
        # 生成确认请求
        confirmation_request = {
            "checkpoint": "delivery",
            "requires_confirmation": True,
            "content_preview": str(content)[:500] + "..." if len(str(content)) > 500 else str(content),
            "risk_factors": self._identify_risk_factors(content, context),
            "confirmation_options": ["确认交付", "需要修改", "取消"],
            "confirmed": False,  # 等待用户确认
            "timestamp": datetime.now().isoformat()
        }
        
        return confirmation_request
    
    def _identify_risk_factors(self, content, context):
        """识别风险因素"""
        factors = []
        
        if context.get("external"):
            factors.append("对外发送")
        if context.get("financial"):
            factors.append("涉及财务")
        if context.get("irreversible"):
            factors.append("不可逆操作")
        if len(str(content)) > 1000:
            factors.append("内容较长，建议复核")
        
        return factors


# 便捷使用函数
def quality_check(content, content_type, context=None):
    """快速质量检查"""
    gate = QualityGate()
    return gate.process(content, content_type, context)


if __name__ == "__main__":
    # 测试
    test_content = """
# 测试报告

## 背景
这是一个测试报告。

## 分析
根据数据显示，情况良好。

## 结论
建议立即执行，必然成功。
"""
    
    print("=== 质量门控测试 ===\n")
    result = quality_check(test_content, "report", {"external": True})
    
    print(f"整体状态: {result['overall_status']}")
    print(f"是否可继续: {result['can_proceed']}")
    print(f"\n各关卡结果:")
    for cp, cp_result in result['checkpoints'].items():
        print(f"  {cp}: {cp_result}")
