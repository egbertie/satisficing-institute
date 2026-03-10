#!/usr/bin/env python3
"""
信息收集统一工作流 V1.0
整合所有信息收集Skill，提供一站式信息收集能力

工作流程:
1. 搜索 → 2. 抓取 → 3. 清洗 → 4. 提取 → 5. 输出
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 导入各个Skill
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/smart-web-scraper')
sys.path.insert(0, '/root/.openclaw/workspace/skills/multi-source-search')
sys.path.insert(0, '/root/.openclaw/workspace/skills/info-cleaner')
sys.path.insert(0, '/root/.openclaw/workspace/skills/knowledge-extractor')

from smart_web_scraper import SmartWebScraper
from multi_source_search import MultiSourceSearch
from info_cleaner import InfoCleaner
from knowledge_extractor import KnowledgeExtractor

class InfoCollectionWorkflow:
    """
    信息收集统一工作流
    一站式信息收集、清洗、提取知识
    """
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.output_dir = self.workspace / "collected_info"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化各个Skill
        print("🚀 初始化信息收集工作流...")
        self.scraper = SmartWebScraper(workspace_path)
        self.searcher = MultiSourceSearch(workspace_path)
        self.cleaner = InfoCleaner(workspace_path)
        self.extractor = KnowledgeExtractor(workspace_path)
        print("✅ 所有Skill初始化完成\n")
        
        # 统计
        self.stats = {
            "workflows_completed": 0,
            "total_urls_processed": 0,
            "total_knowledge_extracted": 0
        }
    
    def collect_from_search(self,
                           query: str,
                           max_results: int = 10,
                           extract_knowledge: bool = True) -> Dict:
        """
        从搜索开始的信息收集工作流
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            extract_knowledge: 是否提取知识
        
        Returns:
            完整的信息收集结果
        """
        print("="*70)
        print(f"🎯 信息收集工作流启动")
        print(f"   查询: {query}")
        print("="*70)
        
        workflow_result = {
            "query": query,
            "started_at": datetime.now().isoformat(),
            "steps": {},
            "final_output": {}
        }
        
        # Step 1: 搜索
        print("\n📡 Step 1: 多源搜索...")
        search_result = self.searcher.search(query, max_results=max_results)
        workflow_result["steps"]["search"] = {
            "status": "success" if search_result["success"] else "failed",
            "results_count": len(search_result.get("results", [])),
            "sources_used": search_result.get("sources_used", [])
        }
        
        if not search_result["success"] or not search_result.get("results"):
            print("❌ 搜索失败或无结果")
            workflow_result["status"] = "failed"
            return workflow_result
        
        print(f"   ✅ 找到 {len(search_result['results'])} 条结果")
        
        # Step 2: 抓取网页内容
        print("\n🌐 Step 2: 抓取网页内容...")
        urls = [r["url"] for r in search_result["results"]]
        scraped_contents = []
        
        for i, url_info in enumerate(search_result["results"][:5], 1):  # 先处理前5个
            print(f"   抓取 [{i}/5]: {url_info['url'][:60]}...")
            
            try:
                scrape_result = self.scraper.scrape(url_info["url"])
                if scrape_result.get("success"):
                    scraped_contents.append({
                        "url": url_info["url"],
                        "title": scrape_result.get("title", ""),
                        "text": scrape_result.get("content", ""),
                        "source": url_info.get("source", "unknown"),
                        "credibility": url_info.get("credibility", "medium")
                    })
            except Exception as e:
                print(f"   ⚠️  抓取失败: {e}")
        
        workflow_result["steps"]["scrape"] = {
            "status": "success",
            "urls_attempted": len(urls[:5]),
            "urls_succeeded": len(scraped_contents)
        }
        print(f"   ✅ 成功抓取 {len(scraped_contents)} 个网页")
        
        # Step 3: 清洗内容
        print("\n🧹 Step 3: 清洗内容...")
        cleaned_contents = self.cleaner.batch_clean(scraped_contents)
        
        workflow_result["steps"]["clean"] = {
            "status": "success",
            "contents_cleaned": len(cleaned_contents),
            "avg_quality": sum(c.quality_score for c in cleaned_contents) / max(len(cleaned_contents), 1)
        }
        print(f"   ✅ 清洗完成，平均质量: {workflow_result['steps']['clean']['avg_quality']:.1f}/100")
        
        # Step 4: 提取知识
        if extract_knowledge and cleaned_contents:
            print("\n🧠 Step 4: 提取知识...")
            
            knowledge_list = []
            for content in cleaned_contents:
                knowledge = self.extractor.extract(
                    text=content.cleaned_text,
                    title=content.title
                )
                knowledge_list.append(knowledge)
            
            # 合并所有知识
            merged_knowledge = self._merge_knowledge(knowledge_list)
            
            workflow_result["steps"]["extract"] = {
                "status": "success",
                "entities_count": len(merged_knowledge.get("entities", [])),
                "relations_count": len(merged_knowledge.get("relations", [])),
                "events_count": len(merged_knowledge.get("events", [])),
                "keywords": merged_knowledge.get("keywords", [])[:10]
            }
            print(f"   ✅ 知识提取完成")
            print(f"      实体: {workflow_result['steps']['extract']['entities_count']} 个")
            print(f"      关系: {workflow_result['steps']['extract']['relations_count']} 个")
            print(f"      事件: {workflow_result['steps']['extract']['events_count']} 个")
            
            workflow_result["final_output"]["knowledge"] = merged_knowledge
        
        # Step 5: 保存结果
        print("\n💾 Step 5: 保存结果...")
        output_file = self._save_workflow_result(query, workflow_result, cleaned_contents)
        workflow_result["output_file"] = str(output_file)
        print(f"   ✅ 结果已保存: {output_file}")
        
        workflow_result["status"] = "success"
        workflow_result["completed_at"] = datetime.now().isoformat()
        
        self.stats["workflows_completed"] += 1
        self.stats["total_urls_processed"] += len(scraped_contents)
        
        print("\n" + "="*70)
        print("🎉 信息收集工作流完成！")
        print("="*70)
        
        return workflow_result
    
    def collect_from_urls(self,
                         urls: List[str],
                         extract_knowledge: bool = True) -> Dict:
        """
        从指定URL开始的信息收集工作流
        """
        print("="*70)
        print(f"🎯 URL批量收集工作流启动")
        print(f"   URL数量: {len(urls)}")
        print("="*70)
        
        workflow_result = {
            "urls": urls,
            "started_at": datetime.now().isoformat(),
            "steps": {}
        }
        
        # 抓取
        print("\n🌐 抓取网页内容...")
        scraped_contents = []
        for url in urls:
            result = self.scraper.scrape(url)
            if result.get("success"):
                scraped_contents.append({
                    "url": url,
                    "title": result.get("title", ""),
                    "text": result.get("content", "")
                })
        
        workflow_result["steps"]["scrape"] = {
            "urls_attempted": len(urls),
            "urls_succeeded": len(scraped_contents)
        }
        
        # 清洗
        print("\n🧹 清洗内容...")
        cleaned_contents = self.cleaner.batch_clean(scraped_contents)
        
        # 提取知识
        if extract_knowledge:
            print("\n🧠 提取知识...")
            knowledge_list = []
            for content in cleaned_contents:
                knowledge = self.extractor.extract(content.cleaned_text, content.title)
                knowledge_list.append(knowledge)
            
            merged_knowledge = self._merge_knowledge(knowledge_list)
            workflow_result["final_output"] = {"knowledge": merged_knowledge}
        
        workflow_result["status"] = "success"
        workflow_result["completed_at"] = datetime.now().isoformat()
        
        return workflow_result
    
    def _merge_knowledge(self, knowledge_list: List) -> Dict:
        """合并多个知识提取结果"""
        merged = {
            "entities": [],
            "relations": [],
            "events": [],
            "keywords": [],
            "topics": [],
            "summaries": []
        }
        
        seen_entities = set()
        seen_relations = set()
        
        for k in knowledge_list:
            # 合并实体（去重）
            for e in k.entities:
                key = f"{e['type']}:{e['text']}"
                if key not in seen_entities:
                    seen_entities.add(key)
                    merged["entities"].append(e)
            
            # 合并关系（去重）
            for r in k.relations:
                key = f"{r['subject']}:{r['predicate']}:{r['object']}"
                if key not in seen_relations:
                    seen_relations.add(key)
                    merged["relations"].append(r)
            
            # 合并事件
            merged["events"].extend(k.events)
            
            # 合并关键词
            merged["keywords"].extend(k.keywords)
            
            # 合并主题
            merged["topics"].extend(k.topics)
            
            # 合并摘要
            if k.summary:
                merged["summaries"].append(k.summary)
        
        # 关键词和主题去重排序
        merged["keywords"] = list(dict.fromkeys(merged["keywords"]))[:20]
        merged["topics"] = list(dict.fromkeys(merged["topics"]))
        
        # 生成总体摘要
        merged["summary"] = " ".join(merged["summaries"])[:500] if merged["summaries"] else ""
        
        return merged
    
    def _save_workflow_result(self, query: str, result: Dict, contents: List) -> Path:
        """保存工作流结果"""
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_slug = query[:30].replace(" ", "_").replace("/", "_")
        filename = f"{timestamp}_{query_slug}.json"
        
        output_file = self.output_dir / filename
        
        # 准备保存的数据
        save_data = {
            "workflow_result": result,
            "collected_contents": [
                {
                    "title": c.title,
                    "url": c.url,
                    "cleaned_text": c.cleaned_text[:2000],  # 限制长度
                    "quality_score": c.quality_score,
                    "content_hash": c.content_hash
                }
                for c in contents
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def generate_expert_report(self, workflow_result: Dict, expert_name: str = "") -> str:
        """
        生成专家可用的研究报告
        
        Args:
            workflow_result: 工作流结果
            expert_name: 专家名称
        
        Returns:
            Markdown格式的报告
        """
        knowledge = workflow_result.get("final_output", {}).get("knowledge", {})
        
        report = f"""# 信息收集研究报告

**研究主题**: {workflow_result.get('query', 'N/A')}  
**收集时间**: {workflow_result.get('completed_at', 'N/A')}  
**执行专家**: {expert_name or 'AI助理'}

---

## 📊 执行摘要

{workflow_result.get('final_output', {}).get('knowledge', {}).get('summary', '暂无摘要')}

---

## 🔑 核心关键词

{', '.join(knowledge.get('keywords', [])[:15])}

---

## 👤 关键实体

### 人物
{self._format_entities(knowledge.get('entities', []), 'person')}

### 组织
{self._format_entities(knowledge.get('entities', []), 'organization')}

### 技术
{self._format_entities(knowledge.get('entities', []), 'technology')}

---

## 🔗 重要关系

{self._format_relations(knowledge.get('relations', [])[:10])}

---

## 📅 关键事件

{self._format_events(knowledge.get('events', [])[:5])}

---

## 📂 主题分类

{', '.join(knowledge.get('topics', []))}

---

## 📈 数据质量

- 搜索源: {', '.join(workflow_result.get('steps', {}).get('search', {}).get('sources_used', []))}
- 成功抓取: {workflow_result.get('steps', {}).get('scrape', {}).get('urls_succeeded', 0)} 个网页
- 内容质量: {workflow_result.get('steps', {}).get('clean', {}).get('avg_quality', 0):.1f}/100
- 实体数量: {len(knowledge.get('entities', []))}
- 关系数量: {len(knowledge.get('relations', []))}

---

*由信息收集工作流自动生成*  
*报告时间: {datetime.now().isoformat()}*
"""
        
        return report
    
    def _format_entities(self, entities: List[Dict], entity_type: str) -> str:
        """格式化实体列表"""
        filtered = [e for e in entities if e.get('type') == entity_type][:10]
        if not filtered:
            return "_暂无相关实体_"
        
        lines = []
        for e in filtered:
            lines.append(f"- **{e['text']}** (置信度: {e.get('confidence', 0):.2f})")
        
        return '\n'.join(lines)
    
    def _format_relations(self, relations: List[Dict]) -> str:
        """格式化关系列表"""
        if not relations:
            return "_暂无相关关系_"
        
        lines = []
        for r in relations:
            lines.append(f"- **{r['subject']}** → *{r['predicate']}* → **{r['object']}**")
        
        return '\n'.join(lines)
    
    def _format_events(self, events: List[Dict]) -> str:
        """格式化事件列表"""
        if not events:
            return "_暂无相关事件_"
        
        lines = []
        for e in events:
            lines.append(f"- **{e.get('date', '未知日期')}**: {e.get('description', 'N/A')[:80]}...")
        
        return '\n'.join(lines)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "workflows_completed": self.stats["workflows_completed"],
            "total_urls_processed": self.stats["total_urls_processed"],
            "scraper_stats": self.scraper.get_stats(),
            "searcher_stats": self.searcher.get_stats(),
            "cleaner_stats": self.cleaner.get_stats(),
            "extractor_stats": self.extractor.get_stats()
        }

# 使用示例
if __name__ == "__main__":
    print("="*70)
    print("信息收集工作流 - 测试运行")
    print("="*70)
    
    workflow = InfoCollectionWorkflow()
    
    # 测试搜索收集
    # result = workflow.collect_from_search("硬科技合伙人匹配", max_results=3)
    
    # 测试URL收集
    test_urls = [
        "https://example.com/article1",
        "https://example.com/article2"
    ]
    # result = workflow.collect_from_urls(test_urls)
    
    print("\n工作流初始化完成，可进行实际测试")
    print("\n使用方法:")
    print("  workflow.collect_from_search('查询主题')")
    print("  workflow.collect_from_urls(['url1', 'url2'])")
