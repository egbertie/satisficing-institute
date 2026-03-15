#!/usr/bin/env python3
"""
意图识别增强器 (Intent Recognition Enhancer)
功能：精准识别用户真实意图
支持：简化指令映射、模糊意图澄清、多意图分解
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    TASK_CREATE = "创建任务"
    TASK_QUERY = "查询任务"
    TASK_UPDATE = "更新任务"
    INFO_REQUEST = "信息请求"
    ANALYSIS_REQUEST = "分析请求"
    DECISION_SUPPORT = "决策支持"
    GREETING = "问候"
    UNKNOWN = "未知"


@dataclass
class IntentMatch:
    """意图匹配结果"""
    primary_intent: str
    confidence: float
    secondary_intents: List[Dict]
    suggested_response: str
    clarification_needed: bool
    extracted_entities: Dict
    simplified_mapping: str


class IntentRecognitionEnhancer:
    """意图识别增强器"""
    
    # 意图模式库
    INTENT_PATTERNS = {
        IntentType.TASK_CREATE: [
            r'(?:创建?|新建?|添加?).{0,5}(?:任务|待办|todo|工作)',
            r'(?:帮我?|需要).{0,10}(?:做|完成|处理|安排)',
            r'(?:记得|别忘了).{0,10}(?:做|处理|跟进)',
            r'(?:安排|布置|分配).{0,5}(?:任务|工作)',
            r'(?:设置|定).{0,5}(?:提醒|闹钟|计划)'
        ],
        IntentType.TASK_QUERY: [
            r'(?:查看?|查询?|看).{0,5}(?:任务|待办|进度|状态)',
            r'(?:有什么|有哪些).{0,5}(?:任务|工作|待办)',
            r'(?:进度|状态|情况).{0,3}(?:如何|怎么样|是啥)',
            r'(?:完成了|做了).{0,3}(?:多少|什么|哪些)'
        ],
        IntentType.TASK_UPDATE: [
            r'(?:更新|修改|调整|改).{0,5}(?:任务|状态|进度)',
            r'(?:标记|设为|改成).{0,5}(?:完成|进行中|已取消)',
            r'(?:删除|移除|取消).{0,5}(?:任务|待办)',
            r'(?:延期|推迟|改期).{0,5}(?:任务|截止日期)'
        ],
        IntentType.INFO_REQUEST: [
            r'(?:查询|查找|搜索).{0,10}(?:信息|资料|数据)',
            r'(?:什么是|什么是|介绍一下).{0,10}',
            r'(?:如何|怎么|怎样).{0,10}(?:做|实现|操作)',
            r'(?:为什么|为何).{0,10}',
            r'(?:请|帮我).{0,5}(?:解释|说明|描述)'
        ],
        IntentType.ANALYSIS_REQUEST: [
            r'(?:分析|评估|评价).{0,10}',
            r'(?:统计|汇总|总结).{0,10}',
            r'(?:对比|比较|差异).{0,10}',
            r'(?:趋势|走向|预测).{0,10}',
            r'(?:原因|因素|为什么).{0,10}(?:分析|剖析)'
        ],
        IntentType.DECISION_SUPPORT: [
            r'(?:建议|推荐|意见).{0,10}',
            r'(?:怎么|如何).{0,5}(?:选择|决定|判断)',
            r'(?:应?该|是否).{0,5}(?:做|选择|采用)',
            r'(?:哪个|什么).{0,5}(?:更好|更合适|最优)',
            r'(?:决策|决定|判断).{0,5}(?:帮助|支持|建议)'
        ],
        IntentType.GREETING: [
            r'^(?:你好|您好|嗨|Hello|Hi|hey)',
            r'(?:早上好|下午好|晚上好)',
            r'(?:在吗|在不在)',
            r'^(?:哈喽|哈啰)'
        ]
    }
    
    # 实体提取模式
    ENTITY_PATTERNS = {
        "date": r'(?:\d{4}[-/年])?\d{1,2}[-/月]\d{1,2}[日号]?|\d{4}[-/]\d{1,2}[-/]\d{1,2}|今天|明天|后天|下周|本月',
        "time": r'\d{1,2}[点:：]\d{1,2}(?:分)?|\d{1,2}[:：]\d{2}|早上|下午|晚上',
        "priority": r'(?:P\d|高优|低优|紧急|重要|一般)',
        "person": r'(?:@|给|让|叫)([^\s,.，。]{2,8})(?:做|负责|处理)?',
        "task_name": r'(?:任务[是为叫]|做|处理|完成|跟进)([^,.，。]{2,30})(?:任务)?'
    }
    
    # 简化指令映射
    SIMPLIFIED_COMMANDS = {
        "查任务": "查看我的任务列表",
        "新任务": "创建新任务",
        "完成任务": "标记任务为完成",
        "分析报告": "生成分析报告",
        "帮决策": "提供决策建议",
        "问专家": "咨询专家意见",
        "存知识": "保存到知识库"
    }
    
    def __init__(self):
        self.clarification_history = []
    
    def _check_simplified_command(self, message: str) -> Optional[str]:
        """检查是否为简化指令"""
        msg_clean = message.strip().lower()
        for cmd, full_intent in self.SIMPLIFIED_COMMANDS.items():
            if cmd in msg_clean or msg_clean.startswith(cmd[:2]):
                return full_intent
        return None
    
    def _extract_entities(self, message: str) -> Dict:
        """提取实体"""
        entities = {}
        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches[0] if isinstance(matches[0], str) else matches[0][0]
        return entities
    
    def _calculate_intent_confidence(self, message: str, patterns: List[str]) -> float:
        """计算意图匹配置信度"""
        scores = []
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            scores.extend([10] * len(matches))
        
        # 额外加分项
        if len(message) < 10:  # 简短消息可能是指令
            scores.append(5)
        
        return min(100, sum(scores) + 30)  # 基础分30
    
    def _detect_multi_intent(self, message: str) -> List[Dict]:
        """检测多意图"""
        intents = []
        
        # 分句检测
        sentences = re.split(r'[,，.。;；]+', message)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 3:
                continue
            
            for intent_type, patterns in self.INTENT_PATTERNS.items():
                confidence = self._calculate_intent_confidence(sentence, patterns)
                if confidence > 40:
                    intents.append({
                        "intent": intent_type.value,
                        "confidence": confidence,
                        "segment": sentence
                    })
        
        # 去重并排序
        seen = set()
        unique_intents = []
        for intent in sorted(intents, key=lambda x: x["confidence"], reverse=True):
            if intent["intent"] not in seen:
                seen.add(intent["intent"])
                unique_intents.append(intent)
        
        return unique_intents[:3]  # 最多返回3个意图
    
    def _generate_suggested_response(self, primary_intent: IntentType, 
                                     confidence: float, entities: Dict) -> str:
        """生成建议响应"""
        if confidence < 50:
            return "我理解您可能需要帮助，但不确定具体需求。您可以更详细地描述一下吗？"
        
        responses = {
            IntentType.TASK_CREATE: f"我将为您创建任务{'：' + entities.get('task_name', '') if 'task_name' in entities else ''}。请确认任务详情。",
            IntentType.TASK_QUERY: "我来帮您查询任务状态和进度。",
            IntentType.TASK_UPDATE: f"我将更新{'日期为' + entities.get('date', '') if 'date' in entities else ''}的任务状态。",
            IntentType.INFO_REQUEST: "我来为您查找相关信息。",
            IntentType.ANALYSIS_REQUEST: "我将对相关数据进行分析。",
            IntentType.DECISION_SUPPORT: "我来为您提供决策分析和建议。",
            IntentType.GREETING: "您好！有什么可以帮助您的吗？",
            IntentType.UNKNOWN: "我不太确定您的需求，能否提供更多细节？"
        }
        
        return responses.get(primary_intent, "我来处理您的请求。")
    
    def recognize(self, message: str) -> IntentMatch:
        """识别用户意图"""
        
        # 检查简化指令
        simplified_mapping = self._check_simplified_command(message)
        
        # 提取实体
        entities = self._extract_entities(message)
        
        # 多意图检测
        multi_intents = self._detect_multi_intent(message)
        
        # 确定主意图
        if multi_intents:
            best_intent = multi_intents[0]
            primary_intent_type = None
            for intent_type in IntentType:
                if intent_type.value == best_intent["intent"]:
                    primary_intent_type = intent_type
                    break
            if not primary_intent_type:
                primary_intent_type = IntentType.UNKNOWN
            confidence = best_intent["confidence"]
        else:
            primary_intent_type = IntentType.UNKNOWN
            confidence = 0
        
        # 如果是简化指令，提高置信度
        if simplified_mapping:
            confidence = max(confidence, 85)
        
        # 确定是否需要澄清
        clarification_needed = confidence < 60 or len(multi_intents) > 1
        
        # 生成建议响应
        suggested_response = self._generate_suggested_response(
            primary_intent_type, confidence, entities
        )
        
        # 构建次级意图列表
        secondary_intents = multi_intents[1:] if len(multi_intents) > 1 else []
        
        return IntentMatch(
            primary_intent=primary_intent_type.value,
            confidence=round(confidence, 2),
            secondary_intents=secondary_intents,
            suggested_response=suggested_response,
            clarification_needed=clarification_needed,
            extracted_entities=entities,
            simplified_mapping=simplified_mapping or "无"
        )
    
    def clarify(self, message: str, context: List[str] = None) -> Dict:
        """澄清模糊意图"""
        clarifying_questions = []
        
        # 检测模糊点
        if len(message) < 5:
            clarifying_questions.append("您是想创建任务、查询信息还是其他操作？")
        
        if not re.search(r'(?:是什么|做什么|关于)', message):
            if "任务" in message and not re.search(r'(?:完成|状态|进度)', message):
                clarifying_questions.append("您是要创建新任务还是查看已有任务？")
        
        if not any(kw in message for kw in ["时间", "日期", "什么时候", "几点"]):
            if any(kw in message for kw in ["任务", "工作", "做"]):
                clarifying_questions.append("这个任务有截止时间吗？")
        
        if not clarifying_questions:
            clarifying_questions.append("能详细描述一下您的具体需求吗？")
        
        return {
            "original_message": message,
            "clarifying_questions": clarifying_questions,
            "possible_interpretations": [
                "创建或更新任务",
                "查询任务或信息",
                "请求分析或建议"
            ]
        }
    
    def batch_recognize(self, messages: List[str]) -> List[IntentMatch]:
        """批量识别"""
        return [self.recognize(msg) for msg in messages]
    
    def generate_report(self, match: IntentMatch, original_message: str) -> str:
        """生成识别报告"""
        lines = [
            "=" * 60,
            "           意图识别报告",
            "=" * 60,
            f"原始消息: {original_message}",
            "",
            "【识别结果】",
            f"  主要意图: {match.primary_intent}",
            f"  置信度: {match.confidence}%",
            "",
            "【提取实体】",
        ]
        
        if match.extracted_entities:
            for entity, value in match.extracted_entities.items():
                lines.append(f"  {entity}: {value}")
        else:
            lines.append("  未提取到实体")
        
        lines.extend([
            "",
            "【简化指令映射】",
            f"  {match.simplified_mapping}",
        ])
        
        if match.secondary_intents:
            lines.extend([
                "",
                "【次要意图】",
            ])
            for intent in match.secondary_intents:
                lines.append(f"  - {intent['intent']} (置信度: {intent['confidence']}%)")
        
        lines.extend([
            "",
            "【建议响应】",
            f"  {match.suggested_response}",
            "",
            f"【是否需要澄清】 {'是' if match.clarification_needed else '否'}",
            "=" * 60
        ])
        
        return "\n".join(lines)


def main():
    """主函数演示"""
    print("🎯 意图识别增强器 - 演示\n")
    
    # 初始化识别器
    enhancer = IntentRecognitionEnhancer()
    
    # 测试消息
    test_messages = [
        "帮我创建一个明天截止的高优先级任务",
        "查一下我现在的任务进度",
        "分析下我们团队这个月的绩效",
        "你好",
        "该",
        "帮我分析为什么最近用户流失率上升了，建议怎么处理",
        "？",
        "完成任务"
    ]
    
    print("📨 批量意图识别测试:\n")
    
    for msg in test_messages:
        print("-" * 60)
        print(f"输入: {msg}")
        result = enhancer.recognize(msg)
        
        if result.clarification_needed:
            clarification = enhancer.clarify(msg)
            print(f"🤔 需要澄清 - 可能意图: {', '.join([i['intent'] for i in result.secondary_intents[:2]]) if result.secondary_intents else '不明确'}")
            print(f"   建议追问: {clarification['clarifying_questions'][0]}")
        else:
            print(f"✅ 识别意图: {result.primary_intent} (置信度: {result.confidence}%)")
            print(f"   实体: {result.extracted_entities}")
            print(f"   建议响应: {result.suggested_response[:50]}...")
    
    # 详细报告示例
    print("\n\n" + "=" * 60)
    print("详细识别报告示例")
    print("=" * 60)
    complex_msg = "帮我分析下销售数据，然后创建一个下周的团队任务"
    result = enhancer.recognize(complex_msg)
    print(enhancer.generate_report(result, complex_msg))
    
    # JSON输出
    print("\n\n📋 JSON格式输出:")
    json_output = {
        "recognition_results": [
            {
                "message": msg,
                "intent": enhancer.recognize(msg).primary_intent,
                "confidence": enhancer.recognize(msg).confidence
            }
            for msg in test_messages[:4]
        ]
    }
    print(json.dumps(json_output, ensure_ascii=False, indent=2))
    
    return result


if __name__ == "__main__":
    main()
