#!/usr/bin/env python3
"""
知识提取引擎 V1.0
从文本中提取结构化知识

核心功能：
1. 实体识别（人名/机构/地点/时间）
2. 关系抽取
3. 事件提取
4. 关键词提取
5. 主题分类
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from collections import Counter

@dataclass
class ExtractedKnowledge:
    """提取的知识结构"""
    entities: List[Dict] = field(default_factory=list)
    relations: List[Dict] = field(default_factory=list)
    events: List[Dict] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    summary: str = ""
    metadata: Dict = field(default_factory=dict)

class KnowledgeExtractor:
    """
    知识提取引擎
    将非结构化文本转换为结构化知识
    """
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        
        # 实体类型词典
        self.entity_patterns = {
            "person": [
                r'[\u4e00-\u9fff]{2,4}(?:教授|博士|先生|女士|总|CEO|CTO|创始人)',
                r'[A-Z][a-z]+ [A-Z][a-z]+',
            ],
            "organization": [
                r'[^，。；：]+?(?:公司|集团|研究院|大学|学院|实验室|基金|协会|联盟)',
                r'[A-Z][A-Za-z]+ (?:Inc|Corp|Ltd|LLC|University|Institute)',
            ],
            "location": [
                r'[^，。]+?(?:市|省|自治区|特别行政区|区|县|镇)',
                r'北京|上海|广州|深圳|杭州|苏州|成都|武汉|西安|南京',
            ],
            "technology": [
                r'[^，。]+?(?:芯片|AI|人工智能|区块链|物联网|云计算|大数据|5G|新能源|生物医药)',
                r'(?:Machine Learning|Deep Learning|Blockchain|IoT|Cloud Computing)',
            ],
            "time": [
                r'\d{4}年(?:\d{1,2}月)?(?:\d{1,2}日)?',
                r'\d{4}-\d{2}-\d{2}',
                r'(?:20|19)\d{2}',
            ],
            "money": [
                r'\d+(?:\.\d+)?(?:万|亿|千万|百万)?(?:元|美元|人民币|USD|RMB)',
                r'\$\d+(?:\.\d+)?(?:[KMB]?)',
            ]
        }
        
        # 停用词
        self.stopwords = {
            "的", "了", "和", "是", "在", "有", "我", "都", "个", "与", "也",
            "对", "为", "能", "很", "可以", "就", "不", "会", "要", "没有",
            "我们", "这", "上", "他", "而", "及", "与", "或", "但", "the",
            "is", "and", "of", "to", "in", "that", "have", "it", "for"
        }
        
        # 统计
        self.stats = {
            "total_processed": 0,
            "entities_extracted": 0,
            "relations_extracted": 0,
            "events_extracted": 0,
            "keywords_extracted": 0
        }
    
    def extract(self, 
                text: str,
                title: str = "",
                extract_entities: bool = True,
                extract_relations: bool = True,
                extract_events: bool = True,
                extract_keywords: bool = True) -> ExtractedKnowledge:
        """
        从文本中提取知识
        
        Args:
            text: 输入文本
            title: 标题
            extract_entities: 是否提取实体
            extract_relations: 是否提取关系
            extract_events: 是否提取事件
            extract_keywords: 是否提取关键词
        
        Returns:
            提取的知识结构
        """
        self.stats["total_processed"] += 1
        
        knowledge = ExtractedKnowledge()
        
        # 1. 提取实体
        if extract_entities:
            knowledge.entities = self._extract_entities(text)
            self.stats["entities_extracted"] += len(knowledge.entities)
        
        # 2. 提取关系
        if extract_relations and knowledge.entities:
            knowledge.relations = self._extract_relations(text, knowledge.entities)
            self.stats["relations_extracted"] += len(knowledge.relations)
        
        # 3. 提取事件
        if extract_events:
            knowledge.events = self._extract_events(text)
            self.stats["events_extracted"] += len(knowledge.events)
        
        # 4. 提取关键词
        if extract_keywords:
            knowledge.keywords = self._extract_keywords(text)
            knowledge.topics = self._classify_topics(text, knowledge.keywords)
            self.stats["keywords_extracted"] += len(knowledge.keywords)
        
        # 5. 生成摘要
        knowledge.summary = self._generate_summary(text, knowledge.keywords)
        
        # 6. 元数据
        knowledge.metadata = {
            "source_title": title,
            "text_length": len(text),
            "processed_at": datetime.now().isoformat(),
            "extraction_quality": self._assess_extraction_quality(knowledge)
        }
        
        return knowledge
    
    def batch_extract(self, contents: List[Dict]) -> List[ExtractedKnowledge]:
        """
        批量提取知识
        
        Args:
            contents: 内容列表，每项包含text/title
        
        Returns:
            知识列表
        """
        print(f"\n🧠 开始批量知识提取: {len(contents)} 条内容")
        
        results = []
        for i, item in enumerate(contents, 1):
            print(f"   提取 [{i}/{len(contents)}]...", end="\r")
            
            knowledge = self.extract(
                text=item.get("text", ""),
                title=item.get("title", "")
            )
            results.append(knowledge)
        
        print(f"\n✅ 知识提取完成")
        return results
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """提取实体"""
        entities = []
        seen = set()
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entity_text = match.group(0).strip()
                    
                    # 去重
                    key = f"{entity_type}:{entity_text}"
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    # 过滤过短的实体
                    if len(entity_text) < 2:
                        continue
                    
                    entities.append({
                        "text": entity_text,
                        "type": entity_type,
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": self._calculate_entity_confidence(entity_text, entity_type)
                    })
        
        # 按置信度排序
        entities.sort(key=lambda x: x["confidence"], reverse=True)
        
        return entities[:50]  # 限制数量
    
    def _extract_relations(self, text: str, entities: List[Dict]) -> List[Dict]:
        """提取实体间关系"""
        relations = []
        
        # 关系模式
        relation_patterns = [
            (r'(\w+)(?:是|担任|成为|出任)(?:了)?(\w+)', "is_a"),
            (r'(\w+)(?:投资|融资|收购|合并)(?:了)?(\w+)', "investment"),
            (r'(\w+)(?:与|和|同)(\w+)(?:合作|联合|携手)', "collaboration"),
            (r'(\w+)(?:创立|创办|创建|成立)(?:了)?(\w+)', "founder_of"),
            (r'(\w+)(?:加入|加盟|进入)(?:了)?(\w+)', "joined"),
        ]
        
        # 简化版：基于实体共现
        for i, e1 in enumerate(entities):
            for e2 in entities[i+1:]:
                # 检查两个实体是否在相近位置
                if abs(e1["start"] - e2["start"]) < 200:  # 200字符内
                    # 检查中间文本是否有关系词
                    start = min(e1["end"], e2["end"])
                    end = max(e1["start"], e2["start"])
                    middle_text = text[start:end]
                    
                    relation_type = "related"
                    for pattern, rel_type in relation_patterns:
                        if re.search(pattern, middle_text):
                            relation_type = rel_type
                            break
                    
                    relations.append({
                        "subject": e1["text"],
                        "subject_type": e1["type"],
                        "predicate": relation_type,
                        "object": e2["text"],
                        "object_type": e2["type"],
                        "context": middle_text[:100]
                    })
        
        return relations[:30]
    
    def _extract_events(self, text: str) -> List[Dict]:
        """提取事件"""
        events = []
        
        # 事件模式
        event_patterns = [
            (r'(\d{4}年(?:\d{1,2}月)?(?:\d{1,2}日)?)[^，。]{0,30}(?:发布|发布|推出|上线|成立|获得|完成)', "milestone"),
            (r'(\d{4}年(?:\d{1,2}月)?(?:\d{1,2}日)?)[^，。]{0,30}(?:融资|投资|收购|合并)', "funding"),
            (r'(\d{4}年(?:\d{1,2}月)?(?:\d{1,2}日)?)[^，。]{0,30}(?:任命|加入|离职)', "personnel"),
            (r'(\d{4}年(?:\d{1,2}月)?(?:\d{1,2}日)?)[^，。]{0,30}(?:合作|签约|达成)', "partnership"),
        ]
        
        for pattern, event_type in event_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                events.append({
                    "date": match.group(1),
                    "type": event_type,
                    "description": match.group(0),
                    "entities": self._extract_entities(match.group(0))
                })
        
        return events[:20]
    
    def _extract_keywords(self, text: str, top_k: int = 20) -> List[str]:
        """提取关键词"""
        # 分词（简化版：按字符和词组）
        # 实际应用中应使用jieba等分词工具
        
        # 提取2-4字词组
        words = []
        for length in [2, 3, 4]:
            for i in range(len(text) - length + 1):
                word = text[i:i+length]
                # 过滤条件
                if any(c in self.stopwords for c in word):
                    continue
                if re.search(r'[\d\s]', word):
                    continue
                words.append(word)
        
        # 统计词频
        word_counts = Counter(words)
        
        # 返回高频词
        keywords = [word for word, count in word_counts.most_common(top_k * 2)]
        
        # 过滤重复（子串）
        filtered = []
        for kw in keywords:
            if not any(kw != other and kw in other for other in keywords):
                filtered.append(kw)
        
        return filtered[:top_k]
    
    def _classify_topics(self, text: str, keywords: List[str]) -> List[str]:
        """主题分类"""
        topics = []
        
        # 主题词典
        topic_keywords = {
            "硬科技": ["芯片", "半导体", "人工智能", "AI", "区块链", "物联网", "5G"],
            "生物医药": ["生物医药", "创新药", "医疗器械", "基因", "细胞", "诊断"],
            "新能源": ["新能源", "电池", "储能", "光伏", "风电", "氢能"],
            "智能制造": ["智能制造", "机器人", "自动化", "工业互联网", "传感器"],
            "创业投资": ["融资", "投资", "VC", "PE", "估值", "IPO", "独角兽"],
            "合伙人": ["合伙人", "联合创始人", "团队", "股权", "期权", "激励"],
        }
        
        text_lower = text.lower()
        
        for topic, keywords_list in topic_keywords.items():
            score = sum(1 for kw in keywords_list if kw in text_lower)
            if score >= 2:  # 至少匹配2个关键词
                topics.append(topic)
        
        return topics
    
    def _generate_summary(self, text: str, keywords: List[str], max_length: int = 300) -> str:
        """生成摘要"""
        # 简单摘要：取开头 + 包含关键词的句子
        sentences = re.split(r'[。！？]', text)
        
        summary_parts = []
        
        # 取前两句
        for sent in sentences[:2]:
            if len(sent) > 10:
                summary_parts.append(sent.strip())
        
        # 找包含关键词的句子
        for sent in sentences:
            if any(kw in sent for kw in keywords[:5]):
                if sent not in summary_parts and len(sent) > 10:
                    summary_parts.append(sent.strip())
                    if len(".".join(summary_parts)) > max_length:
                        break
        
        summary = "。".join(summary_parts)
        return summary[:max_length] + "..." if len(summary) > max_length else summary
    
    def _calculate_entity_confidence(self, text: str, entity_type: str) -> float:
        """计算实体置信度"""
        confidence = 0.5
        
        # 长度因素
        if 3 <= len(text) <= 10:
            confidence += 0.2
        
        # 类型特定规则
        if entity_type == "person":
            if any(suffix in text for suffix in ["教授", "博士", "CEO", "创始人"]):
                confidence += 0.2
        elif entity_type == "organization":
            if any(suffix in text for suffix in ["公司", "集团", "研究院", "大学"]):
                confidence += 0.2
        
        return min(1.0, confidence)
    
    def _assess_extraction_quality(self, knowledge: ExtractedKnowledge) -> str:
        """评估提取质量"""
        scores = []
        
        if knowledge.entities:
            scores.append(min(len(knowledge.entities) / 10, 1.0))
        if knowledge.keywords:
            scores.append(min(len(knowledge.keywords) / 10, 1.0))
        if knowledge.relations:
            scores.append(min(len(knowledge.relations) / 5, 1.0))
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score >= 0.7:
            return "high"
        elif avg_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def export_knowledge(self, knowledge_list: List[ExtractedKnowledge], output_file: str):
        """导出知识"""
        data = []
        for k in knowledge_list:
            data.append({
                "summary": k.summary,
                "entities": k.entities,
                "relations": k.relations,
                "events": k.events,
                "keywords": k.keywords,
                "topics": k.topics,
                "metadata": k.metadata
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已导出 {len(data)} 条知识到: {output_file}")
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total_processed": self.stats["total_processed"],
            "entities_extracted": self.stats["entities_extracted"],
            "relations_extracted": self.stats["relations_extracted"],
            "events_extracted": self.stats["events_extracted"],
            "keywords_extracted": self.stats["keywords_extracted"],
            "avg_entities_per_doc": self.stats["entities_extracted"] / max(self.stats["total_processed"], 1),
            "avg_keywords_per_doc": self.stats["keywords_extracted"] / max(self.stats["total_processed"], 1)
        }

# 使用示例
if __name__ == "__main__":
    extractor = KnowledgeExtractor()
    
    print("="*70)
    print("测试知识提取")
    print("="*70)
    
    # 测试文本
    test_text = """
    2024年3月15日，知名AI芯片公司深鉴科技宣布完成5亿元B轮融资，
    由红杉资本领投，高瓴资本跟投。深鉴科技创始人兼CEO姚颂表示，
    本轮融资将用于新一代AI芯片的研发和市场拓展。
    
    深鉴科技成立于2016年，是一家专注于深度学习处理器研发的硬科技企业。
    公司核心团队来自清华大学，在AI芯片领域拥有深厚的技术积累。
    
    此前，深鉴科技已与华为、阿里等科技巨头达成合作，
    其AI芯片产品已在智慧城市、自动驾驶等领域实现商用。
    """
    
    # 提取知识
    knowledge = extractor.extract(test_text, title="深鉴科技完成B轮融资")
    
    print(f"\n提取结果:")
    print(f"\n📌 摘要: {knowledge.summary}")
    
    print(f"\n👤 实体 ({len(knowledge.entities)}个):")
    for e in knowledge.entities[:5]:
        print(f"   - {e['text']} ({e['type']}, 置信度:{e['confidence']:.2f})")
    
    print(f"\n🔗 关系 ({len(knowledge.relations)}个):")
    for r in knowledge.relations[:3]:
        print(f"   - {r['subject']} --{r['predicate']}--> {r['object']}")
    
    print(f"\n📅 事件 ({len(knowledge.events)}个):")
    for e in knowledge.events:
        print(f"   - {e['date']}: {e['description'][:50]}...")
    
    print(f"\n🔑 关键词: {', '.join(knowledge.keywords[:10])}")
    print(f"\n📂 主题: {', '.join(knowledge.topics)}")
    
    print(f"\n统计:")
    print(json.dumps(extractor.get_stats(), indent=2, ensure_ascii=False))
