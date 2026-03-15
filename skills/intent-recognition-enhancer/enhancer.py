#!/usr/bin/env python3
"""
意图识别增强器 - Intent Recognition Enhancer

功能：精准识别用户真实意图
支持：简化指令映射、模糊意图澄清、多意图分解
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class IntentResult:
    """意图识别结果"""
    primary_intent: str
    confidence: float
    sub_intents: List[str]
    matched_keywords: List[str]
    suggested_response: str
    needs_clarification: bool
    clarification_question: Optional[str] = None


class IntentRecognitionEnhancer:
    """意图识别增强器"""
    
    # 简化指令映射表
    SIMPLIFIED_COMMANDS = {
        "启动第一性原则": {
            "intent": "first_principle_analysis",
            "action": "执行五步复盘+管理哲学联动思考+生成可执行Skill",
            "keywords": ["第一性原则", "启动", "复盘", "优化"]
        },
        "零空置": {
            "intent": "zero_idle_enforcement",
            "action": "运行zero-idle-enforcer，检查并补位资源空缺",
            "keywords": ["零空置", "补位", "资源", "空置"]
        },
        "自我评估": {
            "intent": "self_assessment",
            "action": "运行self-assessment-calibrator，校准时间预估",
            "keywords": ["自我评估", "校准", "评估", "时间"]
        },
        "信息防火墙": {
            "intent": "information_filtering",
            "action": "运行information-intelligence，智能搜索+质量甄别",
            "keywords": ["信息防火墙", "搜索", "甄别", "质量"]
        },
        "每日审计": {
            "intent": "daily_audit",
            "action": "运行daily-reminder-auditor，扫描重复提醒",
            "keywords": ["每日审计", "审计", "提醒", "检查"]
        },
        "深度复盘": {
            "intent": "deep_review",
            "action": "运行continuous-improvement-engine，执行深度复盘",
            "keywords": ["深度复盘", "复盘", "优化", "改进"]
        }
    }
    
    # 模糊意图模式
    FUZZY_PATTERNS = {
        "question": {
            "patterns": [r".*\?", r"如何.*", r"怎么.*", r"什么.*", r"为什么.*"],
            "intent": "seeking_information"
        },
        "command": {
            "patterns": [r".*做.*", r".*开始.*", r".*启动.*", r".*执行.*", r".*运行.*"],
            "intent": "requesting_action"
        },
        "confirmation": {
            "patterns": [r".*对吗.*", r".*是吧.*", r".*确认.*", r".*检查.*"],
            "intent": "seeking_confirmation"
        }
    }
    
    def recognize(self, message: str) -> IntentResult:
        """
        识别用户意图
        
        Args:
            message: 用户原始消息
            
        Returns:
            意图识别结果
        """
        message_lower = message.lower().strip()
        
        # 1. 检查简化指令
        for cmd, config in self.SIMPLIFIED_COMMANDS.items():
            if cmd.lower() in message_lower or any(kw in message_lower for kw in config["keywords"]):
                return IntentResult(
                    primary_intent=config["intent"],
                    confidence=0.95,
                    sub_intents=[],
                    matched_keywords=config["keywords"],
                    suggested_response=f"执行[{cmd}]: {config['action']}",
                    needs_clarification=False
                )
        
        # 2. 检查模糊意图模式
        for category, config in self.FUZZY_PATTERNS.items():
            for pattern in config["patterns"]:
                if re.match(pattern, message_lower):
                    return self._handle_fuzzy_intent(message, config["intent"])
        
        # 3. 通用意图识别（基于关键词）
        return self._general_intent_recognition(message)
    
    def _handle_fuzzy_intent(self, message: str, base_intent: str) -> IntentResult:
        """处理模糊意图"""
        # 提取可能的具体内容
        topics = self._extract_topics(message)
        
        return IntentResult(
            primary_intent=base_intent,
            confidence=0.7,
            sub_intents=topics,
            matched_keywords=topics,
            suggested_response=f"识别到{basic_intent}意图，建议确认具体需求",
            needs_clarification=True,
            clarification_question=f"您是想了解关于'{', '.join(topics[:2])}'的具体信息吗？"
        )
    
    def _general_intent_recognition(self, message: str) -> IntentResult:
        """通用意图识别"""
        message_lower = message.lower()
        
        # 主题关键词
        topics = self._extract_topics(message)
        
        # 判断意图类型
        if any(word in message_lower for word in ["做", "执行", "开始", "启动"]):
            intent = "action_request"
            confidence = 0.75
            suggestion = "执行相关操作"
        elif any(word in message_lower for word in ["查", "看", "检查", "确认"]):
            intent = "status_check"
            confidence = 0.75
            suggestion = "检查当前状态"
        elif any(word in message_lower for word in ["教", "讲", "解释", "说明"]):
            intent = "explanation_request"
            confidence = 0.7
            suggestion = "提供解释说明"
        else:
            intent = "general_conversation"
            confidence = 0.5
            suggestion = "继续对话"
        
        return IntentResult(
            primary_intent=intent,
            confidence=confidence,
            sub_intents=topics,
            matched_keywords=topics,
            suggested_response=suggestion,
            needs_clarification=confidence < 0.7
        )
    
    def _extract_topics(self, message: str) -> List[str]:
        """提取主题关键词"""
        common_topics = [
            "第一性原则", "满意解", "零空置", "六线并行", "五路图腾",
            "合伙人", "决策", "技能", "任务", "优化", "复盘",
            "信息", "搜索", "防火墙", "知识", "方法论"
        ]
        
        found = []
        for topic in common_topics:
            if topic in message:
                found.append(topic)
        
        return found[:3]  # 最多3个主题
    
    def decompose_multiple_intents(self, message: str) -> List[IntentResult]:
        """
        分解多意图消息
        
        Args:
            message: 可能包含多个意图的消息
            
        Returns:
            意图列表
        """
        # 按标点分割
        segments = re.split(r'[。；;！!]+', message)
        segments = [s.strip() for s in segments if s.strip()]
        
        results = []
        for segment in segments:
            if len(segment) > 5:  # 过滤太短的片段
                intent = self.recognize(segment)
                results.append(intent)
        
        return results
    
    def generate_intent_report(self, message: str, result: IntentResult) -> str:
        """生成意图识别报告"""
        lines = [
            "# 意图识别报告",
            "",
            f"**原始消息**: {message}",
            f"**识别时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 识别结果",
            "",
            f"**主意图**: {result.primary_intent}",
            f"**置信度**: {result.confidence*100:.0f}%",
            f"**子意图**: {', '.join(result.sub_intents) if result.sub_intents else '无'}",
            f"**匹配关键词**: {', '.join(result.matched_keywords)}",
            "",
            "## 建议响应",
            "",
            f"> {result.suggested_response}",
            ""
        ]
        
        if result.needs_clarification:
            lines.extend([
                "## 需要澄清",
                "",
                f"**澄清问题**: {result.clarification_question}",
                ""
            ])
        
        lines.extend([
            "---",
            "",
            "*简化指令自动映射，模糊意图智能澄清*"
        ])
        
        return "\n".join(lines)


def main():
    """主函数 - 演示"""
    print("=" * 60)
    print("意图识别增强器 v1.0")
    print("=" * 60)
    
    enhancer = IntentRecognitionEnhancer()
    
    # 测试消息
    test_messages = [
        "启动第一性原则优化信息搜索",
        "零空置检查一下",
        "帮我看看任务进度",
        "这个怎么做的？",
        "准备官宣文案，同时检查专家资料"
    ]
    
    for msg in test_messages:
        print(f"\n【输入】{msg}")
        result = enhancer.recognize(msg)
        print(f"【意图】{result.primary_intent} (置信度:{result.confidence:.0%})")
        print(f"【建议】{result.suggested_response}")
        if result.needs_clarification:
            print(f"【澄清】{result.clarification_question}")
    
    # 多意图分解示例
    print("\n" + "=" * 60)
    print("多意图分解示例：")
    print("=" * 60)
    multi_msg = "准备官宣文案。检查专家资料。优化搜索策略。"
    print(f"\n【输入】{multi_msg}")
    intents = enhancer.decompose_multiple_intents(multi_msg)
    print(f"【分解为{len(intents)}个意图】")
    for i, intent in enumerate(intents, 1):
        print(f"  {i}. {intent.primary_intent} - {intent.suggested_response}")


if __name__ == "__main__":
    main()
