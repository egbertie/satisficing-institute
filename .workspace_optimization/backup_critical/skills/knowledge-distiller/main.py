#!/usr/bin/env python3
"""
知识蒸馏沉淀器 (Knowledge Distiller)
功能：从对话中提取知识并沉淀到知识库
自动分类：方法论、案例、洞察、金句
"""

import json
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum


class KnowledgeCategory(Enum):
    METHODOLOGY = "方法论"  # 方法论、框架、流程
    CASE = "案例"  # 具体案例、实战经验
    INSIGHT = "洞察"  # 深度洞察、观点
    QUOTE = "金句"  # 精炼语句、名言
    TOOL = "工具"  # 工具、资源、模板
    FAQ = "问答"  # 常见问题与解答


@dataclass
class KnowledgeItem:
    """知识条目"""
    id: str
    category: KnowledgeCategory
    content: str
    source: str  # 来源对话/文件
    context: str  # 上下文
    tags: List[str]
    confidence: float  # 提取置信度
    extracted_at: str
    archived_path: str
    related_items: List[str] = None
    
    def __post_init__(self):
        if self.related_items is None:
            self.related_items = []


@dataclass
class ExtractionResult:
    """提取结果"""
    source: str
    total_items: int
    by_category: Dict[str, int]
    items: List[KnowledgeItem]
    archive_location: str
    processing_time: str


class KnowledgeDistiller:
    """知识蒸馏沉淀器"""
    
    # 分类关键词模式
    CATEGORY_PATTERNS = {
        KnowledgeCategory.METHODOLOGY: [
            r'(?:方法|框架|模型|流程|步骤|方法论|体系|机制|原则|策略)',
            r'(?:\d+步|第一步|首先.*然后|流程.*：|框架.*：)',
            r'(?:建议|推荐|应该|需要|必须).{3,30}(?:方法|方式|流程)',
            r'(?:如何|怎么|怎样).{3,30}(?:做|处理|解决|实施)'
        ],
        KnowledgeCategory.CASE: [
            r'(?:案例|例子|实例|故事|经历|曾经|有一次|之前|之前.*做过)',
            r'(?:比如|例如|像.*一样|类似.*的情况)',
            r'(?:公司|团队|项目|客户|用户).{2,20}(?:做了|实施了|完成了|实现了)',
            r'(?:结果|效果|成果).{2,10}(?:是|为|达到|获得)'
        ],
        KnowledgeCategory.INSIGHT: [
            r'(?:本质|核心|关键|实质|底层|逻辑|道理|规律|趋势)',
            r'(?:其实|实际上|本质上|说到底|归根结底|换言之)',
            r'(?:我发现|我意识到|重要的是|值得注意的是)',
            r'(?:之所以.*是因为|一方面.*另一方面)',
            r'(?:对比|相较|不同于|相比于).{3,30}(?:在于|说明|体现)'
        ],
        KnowledgeCategory.QUOTE: [
            r'".{5,100}"',
            r'「.{5,100}」',
            r'".{5,100}"',
            r'(?:金句|名言|常说|记住|牢记).{2,20}(?:：|:)',
            r'(?:一句话|简而言之|总结为|概括说).{2,30}(?:：|:)'
        ],
        KnowledgeCategory.TOOL: [
            r'(?:工具|软件|平台|系统|模板|文档|表格|清单|checklist)',
            r'(?:推荐|使用|采用|借助|通过).{2,15}(?:工具|软件|平台)',
            r'(?:链接|网址|地址|下载|访问).{2,30}(?:：|:)',
            r'(?:GitHub|Notion|飞书|钉钉|Jira|Confluence|Figma)'
        ],
        KnowledgeCategory.FAQ: [
            r'(?:Q:|问：|问题是|疑问|困惑|不懂|请问)',
            r'(?:A:|答：|回答是|解答|回复|答案)',
            r'(?:常问|常见|FAQ|问题|疑惑).{2,20}(?:：|:)'
        ]
    }
    
    def __init__(self, output_dir: str = "./knowledge_base"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建分类子目录
        for category in KnowledgeCategory:
            (self.output_dir / category.value).mkdir(exist_ok=True)
    
    def _load_content(self, source: str) -> str:
        """加载内容"""
        path = Path(source)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                with open(path, 'r', encoding='gbk') as f:
                    return f.read()
        return source  # 如果不是文件路径，直接返回内容
    
    def _split_into_paragraphs(self, content: str) -> List[str]:
        """将内容分割成段落"""
        # 按多个换行符分割
        paragraphs = re.split(r'\n\s*\n', content)
        # 清理并过滤短段落
        return [p.strip() for p in paragraphs if len(p.strip()) > 30]
    
    def _classify_content(self, content: str) -> Tuple[KnowledgeCategory, float]:
        """对内容进行分类"""
        scores = {category: 0 for category in KnowledgeCategory}
        
        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                scores[category] += len(matches) * 10
        
        # 基于内容长度和结构的额外评分
        if len(content) > 200:
            scores[KnowledgeCategory.CASE] += 5
        if '：' in content or ':' in content:
            scores[KnowledgeCategory.METHODOLOGY] += 3
        
        # 找到最高分的分类
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]
        
        # 计算置信度
        total_score = sum(scores.values())
        confidence = min(100, (max_score / max(total_score, 1)) * 100)
        
        # 如果最高分和第二分差距不大，降低置信度
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) > 1 and sorted_scores[0] - sorted_scores[1] < 5:
            confidence *= 0.8
        
        return best_category, round(confidence, 2)
    
    def _extract_tags(self, content: str, category: KnowledgeCategory) -> List[str]:
        """提取标签"""
        tags = []
        
        # 通用主题词提取
        topic_patterns = [
            r'(?:关于|针对|涉及|围绕).{2,10}(?:方面|领域|问题|主题)',
            r'(?:管理|开发|设计|运营|产品|技术|市场|销售|团队|项目)',
            r'(?:策略|方案|计划|目标|指标|KPI|OKR)',
            r'(?:用户|客户|需求|体验|增长|转化|留存)',
            r'(?:AI|人工智能|机器学习|数据|算法|系统|平台)'
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, content)
            tags.extend(matches)
        
        # 根据分类添加特定标签
        category_tags = {
            KnowledgeCategory.METHODOLOGY: ["方法论", "流程", "框架"],
            KnowledgeCategory.CASE: ["案例", "实践", "经验"],
            KnowledgeCategory.INSIGHT: ["洞察", "观点", "深度"],
            KnowledgeCategory.QUOTE: ["金句", "总结", "精华"],
            KnowledgeCategory.TOOL: ["工具", "资源"],
            KnowledgeCategory.FAQ: ["FAQ", "问答", "常见问题"]
        }
        
        tags.append(category.value)
        tags.extend(category_tags.get(category, []))
        
        # 去重并限制数量
        return list(set(tags))[:8]
    
    def _generate_id(self, content: str) -> str:
        """生成唯一ID"""
        hash_input = content[:100] + datetime.now().isoformat()
        return hashlib.md5(hash_input.encode()).hexdigest()[:12].upper()
    
    def _save_item(self, item: KnowledgeItem) -> str:
        """保存知识条目到文件"""
        category_dir = self.output_dir / item.category.value
        filename = f"{item.id}_{item.category.value}.json"
        filepath = category_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(item), f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def distill(self, source: str) -> ExtractionResult:
        """从对话/文件中蒸馏知识"""
        start_time = datetime.now()
        
        # 加载内容
        content = self._load_content(source)
        
        # 分割成段落
        paragraphs = self._split_into_paragraphs(content)
        
        items = []
        for para in paragraphs:
            # 分类
            category, confidence = self._classify_content(para)
            
            # 提取标签
            tags = self._extract_tags(para, category)
            
            # 创建知识条目
            item = KnowledgeItem(
                id=self._generate_id(para),
                category=category,
                content=para[:500] if len(para) > 500 else para,  # 限制长度
                source=source if len(source) < 100 else source[:100],
                context="",  # 可以后续扩展提取更多上下文
                tags=tags,
                confidence=confidence,
                extracted_at=datetime.now().isoformat(),
                archived_path=""
            )
            
            # 保存
            item.archived_path = self._save_item(item)
            items.append(item)
        
        # 统计分类分布
        by_category = {}
        for item in items:
            cat = item.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
        
        end_time = datetime.now()
        processing_time = f"{(end_time - start_time).total_seconds():.2f}s"
        
        return ExtractionResult(
            source=source[:50],
            total_items=len(items),
            by_category=by_category,
            items=items,
            archive_location=str(self.output_dir),
            processing_time=processing_time
        )
    
    def search(self, query: str, category: KnowledgeCategory = None) -> List[KnowledgeItem]:
        """搜索知识库"""
        results = []
        
        categories = [category] if category else list(KnowledgeCategory)
        
        for cat in categories:
            category_dir = self.output_dir / cat.value
            if not category_dir.exists():
                continue
            
            for filepath in category_dir.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # 简单文本匹配
                        if query.lower() in data.get('content', '').lower() or \
                           any(query.lower() in tag.lower() for tag in data.get('tags', [])):
                            results.append(KnowledgeItem(
                                id=data['id'],
                                category=KnowledgeCategory(data['category']),
                                content=data['content'],
                                source=data['source'],
                                context=data.get('context', ''),
                                tags=data['tags'],
                                confidence=data['confidence'],
                                extracted_at=data['extracted_at'],
                                archived_path=data['archived_path'],
                                related_items=data.get('related_items', [])
                            ))
                except:
                    continue
        
        # 按置信度排序
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:20]  # 限制返回数量
    
    def generate_summary(self, result: ExtractionResult) -> str:
        """生成提取摘要报告"""
        lines = [
            "=" * 60,
            "           知识蒸馏沉淀报告",
            "=" * 60,
            f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"处理耗时: {result.processing_time}",
            f"来源: {result.source}",
            "-" * 60,
            f"\n提取统计:",
            f"  总条目数: {result.total_items}",
            "\n分类分布:"
        ]
        
        for category, count in sorted(result.by_category.items()):
            lines.append(f"  {category}: {count}条")
        
        lines.extend([
            "\n归档位置:",
            f"  {result.archive_location}",
            "\n提取内容预览:",
            "-" * 60
        ])
        
        for i, item in enumerate(result.items[:5], 1):
            lines.append(f"\n【{i}】[{item.category.value}] 置信度: {item.confidence}%")
            lines.append(f"  标签: {', '.join(item.tags[:4])}")
            content_preview = item.content[:150] + "..." if len(item.content) > 150 else item.content
            lines.append(f"  内容: {content_preview}")
        
        if len(result.items) > 5:
            lines.append(f"\n... 还有 {len(result.items) - 5} 条内容已归档")
        
        lines.extend([
            "",
            "=" * 60,
            "💡 知识已自动分类归档，可使用search()方法检索",
            "=" * 60
        ])
        
        return "\n".join(lines)


def main():
    """主函数演示"""
    print("🧠 知识蒸馏沉淀器 - 演示\n")
    
    # 初始化沉淀器
    distiller = KnowledgeDistiller(output_dir="./knowledge_base")
    
    # 示例对话内容
    sample_dialogue = """
产品经理老王分享了他带领团队做用户增长的经验。

他说："增长的本质是创造价值，而不是获取流量。"

关于方法论，他分享了一个四步增长框架：
第一步：明确目标用户群体，建立用户画像
第二步：找到产品的核心价值点，设计增长实验
第三步：建立数据监控体系，追踪关键指标
第四步：根据数据反馈持续优化迭代

他还分享了一个真实的案例：之前他们团队负责的一款B端产品，通过优化onboarding流程，将新用户7日留存率从25%提升到了45%。具体做法是先梳理了用户首次使用时的关键痛点，然后重新设计了引导流程，最后通过A/B测试验证了效果。

他强调了一个关键洞察：很多团队做增长只看数量不看质量，这其实是本末倒置。真正的增长应该是高质量用户的有机增长，这需要产品本身有足够的价值。

他推荐了几个有用的工具：Google Analytics做数据分析，Mixpanel做用户行为追踪，Amplitude做产品分析。

最后他总结道："做对的事，而不是容易的事。"

有同事问：如何平衡短期增长和长期价值？
他回答说：短期增长应该服务于长期价值，任何损害用户体验的短期增长都是不可持续的。关键是要找到那个既能带来增长又不损害用户体验的甜蜜点。
"""
    
    print("📄 示例对话内容已加载\n")
    print("-" * 60)
    
    # 执行知识蒸馏
    print("\n🔄 开始知识提取...")
    result = distiller.distill(sample_dialogue)
    
    # 生成并打印报告
    report = distiller.generate_summary(result)
    print("\n" + report)
    
    # 演示搜索功能
    print("\n\n🔍 搜索演示: '增长'")
    search_results = distiller.search("增长")
    print(f"找到 {len(search_results)} 条相关知识:")
    for i, item in enumerate(search_results[:3], 1):
        print(f"\n  {i}. [{item.category.value}] {item.content[:80]}...")
    
    # 演示按分类搜索
    print("\n\n🔍 搜索演示: 分类='方法论'")
    method_results = distiller.search("", category=KnowledgeCategory.METHODOLOGY)
    print(f"找到 {len(method_results)} 条方法论类知识")
    
    # 输出JSON格式
    print("\n\n📋 JSON格式输出:")
    json_output = {
        "extraction_summary": {
            "total_items": result.total_items,
            "by_category": result.by_category,
            "processing_time": result.processing_time
        },
        "sample_items": [
            {
                "id": item.id,
                "category": item.category.value,
                "confidence": item.confidence,
                "tags": item.tags,
                "content_preview": item.content[:100]
            }
            for item in result.items[:3]
        ]
    }
    print(json.dumps(json_output, ensure_ascii=False, indent=2))
    
    return result


if __name__ == "__main__":
    main()
