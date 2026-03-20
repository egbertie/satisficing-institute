#!/usr/bin/env python3
"""
知识蒸馏沉淀器 - Knowledge Distiller

功能：从对话中提取知识并沉淀到知识库
自动分类：方法论、案例、洞察、金句
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class KnowledgeItem:
    """知识条目"""
    id: str
    category: str  # methodology/case/insight/quote
    content: str
    source: str
    timestamp: str
    tags: List[str]
    confidence: float


class KnowledgeDistiller:
    """知识蒸馏沉淀器"""
    
    CATEGORIES = {
        "methodology": "方法论 - 系统性方法、框架、流程",
        "case": "案例 - 具体实例、场景、应用",
        "insight": "洞察 - 深度见解、趋势、规律",
        "quote": "金句 - 精辟语句、核心理念"
    }
    
    # 分类关键词
    CATEGORY_KEYWORDS = {
        "methodology": ["方法", "框架", "流程", "步骤", "模型", "体系", "原则", "机制"],
        "case": ["案例", "实例", "场景", "比如", "例如", "实际", "实践", "应用"],
        "insight": ["洞察", "发现", "趋势", "规律", "本质", "关键", "核心", "底层"],
        "quote": ["金句", "名言", "核心", "本质", "第一性", "知行合一", "满意解"]
    }
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.knowledge_base_dir = self.workspace / "A满意哥专属文件夹" / "06_🧠方法论体系" / "知识蒸馏"
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.knowledge_base_dir / "knowledge-index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """加载知识索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"items": [], "version": "1.0.0"}
    
    def _save_index(self):
        """保存知识索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def distill(self, content: str, source: str = "conversation") -> List[KnowledgeItem]:
        """
        从内容中蒸馏知识
        
        Args:
            content: 原始内容
            source: 来源标识
            
        Returns:
            提取的知识条目列表
        """
        items = []
        
        # 按段落分割
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        for para in paragraphs:
            # 分类
            category = self._classify(para)
            
            # 提取标签
            tags = self._extract_tags(para)
            
            # 计算置信度
            confidence = self._calculate_confidence(para, category)
            
            # 只保留高置信度的知识
            if confidence >= 0.6:
                item = KnowledgeItem(
                    id=f"KN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(items):03d}",
                    category=category,
                    content=para[:500],  # 限制长度
                    source=source,
                    timestamp=datetime.now().isoformat(),
                    tags=tags,
                    confidence=round(confidence, 2)
                )
                items.append(item)
        
        # 保存到知识库
        self._save_items(items)
        
        return items
    
    def _classify(self, content: str) -> str:
        """分类内容"""
        scores = {cat: 0 for cat in self.CATEGORIES.keys()}
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content:
                    scores[category] += 1
        
        # 返回得分最高的类别
        max_category = max(scores, key=scores.get)
        return max_category if scores[max_category] > 0 else "insight"
    
    def _extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        # 基于关键词提取
        common_tags = [
            "满意解", "第一性原则", "知行合一", "零空置", "六线并行",
            "五路图腾", "儒商", "合伙人", "决策", "方法论", "辩证思维"
        ]
        
        tags = []
        for tag in common_tags:
            if tag in content:
                tags.append(tag)
        
        return tags[:5]  # 最多5个标签
    
    def _calculate_confidence(self, content: str, category: str) -> float:
        """计算置信度"""
        score = 0.5  # 基础分
        
        # 长度因素（太短或太长都不好）
        length = len(content)
        if 50 <= length <= 300:
            score += 0.2
        elif 30 <= length < 50 or 300 < length <= 500:
            score += 0.1
        
        # 关键词密度
        keyword_count = sum(1 for kw in self.CATEGORY_KEYWORDS[category] if kw in content)
        score += min(0.2, keyword_count * 0.05)
        
        # 结构化指标
        if any(marker in content for marker in ["：", "→", "=>", "1.", "-"]):
            score += 0.1
        
        return min(1.0, score)
    
    def _save_items(self, items: List[KnowledgeItem]):
        """保存知识条目"""
        # 按类别分类保存
        category_files = {}
        
        for item in items:
            if item.category not in category_files:
                category_files[item.category] = []
            category_files[item.category].append({
                "id": item.id,
                "content": item.content,
                "source": item.source,
                "timestamp": item.timestamp,
                "tags": item.tags,
                "confidence": item.confidence
            })
        
        # 追加到各类别文件
        for category, entries in category_files.items():
            file_path = self.knowledge_base_dir / f"{category}.jsonl"
            with open(file_path, 'a', encoding='utf-8') as f:
                for entry in entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        # 更新索引
        for item in items:
            self.index["items"].append({
                "id": item.id,
                "category": item.category,
                "preview": item.content[:100],
                "timestamp": item.timestamp
            })
        
        self._save_index()
    
    def search(self, query: str, category: str = None) -> List[Dict]:
        """搜索知识库"""
        results = []
        
        # 搜索索引
        for item in self.index["items"]:
            if category and item["category"] != category:
                continue
            
            if query.lower() in item["preview"].lower():
                results.append(item)
        
        return results[:10]  # 返回前10个
    
    def generate_distillation_report(self, items: List[KnowledgeItem]) -> str:
        """生成蒸馏报告"""
        lines = [
            "# 知识蒸馏报告",
            "",
            f"**蒸馏时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**提取条目数**: {len(items)}",
            "",
            "## 分类统计",
            ""
        ]
        
        # 统计各类别数量
        category_count = {}
        for item in items:
            category_count[item.category] = category_count.get(item.category, 0) + 1
        
        for cat, count in category_count.items():
            desc = self.CATEGORIES.get(cat, cat)
            lines.append(f"- **{desc}**: {count}条")
        
        lines.extend([
            "",
            "## 提取内容",
            ""
        ])
        
        for item in items:
            lines.extend([
                f"### {item.id} [{self.CATEGORIES.get(item.category, item.category)}]",
                f"**内容**: {item.content}",
                f"**标签**: {', '.join(item.tags)}",
                f"**置信度**: {item.confidence}",
                ""
            ])
        
        lines.extend([
            "---",
            "",
            "*知识已沉淀到方法论体系，可供后续复用*"
        ])
        
        return "\n".join(lines)


def main():
    """主函数 - 演示"""
    print("=" * 60)
    print("知识蒸馏沉淀器 v1.0")
    print("=" * 60)
    
    distiller = KnowledgeDistiller()
    
    # 示例内容
    content = """
启动第一性原则进行系统优化。我们要从本质出发，剥离所有假设。

零空置强制执行机制确保资源100%利用。六线并行随时激活：学习线、研究线、迭代线、替身线、游戏化线、优化线。

满意解不是最优解，而是在约束条件下的足够好的解。正如西蒙所说，人类理性是有限的。

辩证思维告诉我们：不能只防守不进攻，也不能只进攻不防守。要在矛盾中找到统一。

知行合一，持续精进。每天都要比昨天的自己更好一点。
    """
    
    print("\n开始蒸馏知识...")
    items = distiller.distill(content, source="演示对话")
    
    print(f"  提取知识条目: {len(items)}条")
    
    for item in items:
        print(f"  - [{item.category}] {item.content[:40]}... (置信度:{item.confidence})")
    
    # 生成报告
    print("\n" + "=" * 60)
    print("蒸馏报告：")
    print("=" * 60)
    report = distiller.generate_distillation_report(items)
    print(report)


if __name__ == "__main__":
    main()
