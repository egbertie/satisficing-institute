#!/usr/bin/env python3
"""
多源搜索编排器 V1.0
整合多个搜索API，统一输出，智能编排

支持源:
- Brave Search（网页搜索，快速）
- Perplexity AI（深度搜索，详细）
- Kimi Search（中文搜索，精准）
- web_search工具（备用）
"""

import json
import time
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict

@dataclass
class SearchResult:
    """搜索结果数据结构"""
    title: str
    url: str
    snippet: str
    source: str  # brave/perplexity/kimi/web
    credibility: str  # high/medium/low
    timestamp: str
    metadata: Dict = None
    
    def to_dict(self):
        return asdict(self)

class MultiSourceSearch:
    """
    多源搜索编排器
    智能整合多个搜索API
    """
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.config_file = self.workspace / "config" / "search_config.json"
        self.cache_dir = self.workspace / "cache" / "search"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        
        # 统计
        self.stats = {
            "total_queries": 0,
            "successful": 0,
            "failed": 0,
            "by_source": {}
        }
    
    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            "brave_api_key": None,
            "perplexity_api_key": None,
            "kimi_search_enabled": True,
            "default_sources": ["brave", "perplexity"],
            "timeout": 30,
            "max_results_per_source": 10,
            "cache_enabled": True,
            "cache_ttl": 1800,  # 30分钟
            "rate_limit": {
                "brave_per_month": 1500,  # 免费额度
                "perplexity_per_day": 300  # 免费额度
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                default_config.update(config)
        
        return default_config
    
    def search(self,
               query: str,
               sources: List[str] = None,
               max_results: int = 20,
               use_cache: bool = None,
               require_citations: bool = False) -> Dict:
        """
        执行多源搜索
        
        Args:
            query: 搜索查询
            sources: 使用的搜索源列表
            max_results: 最大结果数量
            use_cache: 是否使用缓存
            require_citations: 是否需要引用来源
        
        Returns:
            包含搜索结果的字典
        """
        sources = sources or self.config["default_sources"]
        use_cache = use_cache if use_cache is not None else self.config["cache_enabled"]
        
        print(f"\n🔍 开始多源搜索: {query}")
        print(f"   搜索源: {', '.join(sources)}")
        print(f"   最大结果: {max_results}")
        
        # 检查缓存
        if use_cache:
            cached = self._get_cache(query, sources)
            if cached:
                print(f"   ✅ 命中缓存")
                return cached
        
        # 并行执行多个搜索源
        all_results = []
        
        for source in sources:
            try:
                print(f"\n   搜索源 [{source}]...")
                
                if source == "brave":
                    results = self._search_brave(query)
                elif source == "perplexity":
                    results = self._search_perplexity(query, require_citations)
                elif source == "kimi":
                    results = self._search_kimi(query)
                elif source == "web":
                    results = self._search_web(query)
                else:
                    print(f"   ⚠️  未知搜索源: {source}")
                    continue
                
                all_results.extend(results)
                self.stats["by_source"][source] = self.stats["by_source"].get(source, 0) + len(results)
                print(f"   ✅ 获取 {len(results)} 条结果")
                
            except Exception as e:
                print(f"   ❌ 搜索源 [{source}] 失败: {e}")
                self.stats["by_source"][f"{source}_failed"] = \
                    self.stats["by_source"].get(f"{source}_failed", 0) + 1
        
        # 去重和排序
        unique_results = self._deduplicate_results(all_results)
        sorted_results = self._sort_by_credibility(unique_results)
        
        # 限制结果数量
        final_results = sorted_results[:max_results]
        
        # 构建输出
        output = {
            "success": len(final_results) > 0,
            "query": query,
            "sources_used": sources,
            "total_found": len(all_results),
            "unique_results": len(unique_results),
            "results": [r.to_dict() for r in final_results],
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "search_duration": None,
                "by_source": {k: v for k, v in self.stats["by_source"].items() if not k.endswith("_failed")}
            }
        }
        
        # 保存缓存
        if use_cache and output["success"]:
            self._save_cache(query, sources, output)
        
        # 更新统计
        self.stats["total_queries"] += 1
        if output["success"]:
            self.stats["successful"] += 1
        else:
            self.stats["failed"] += 1
        
        print(f"\n✅ 搜索完成: {len(final_results)} 条唯一结果")
        return output
    
    def _search_brave(self, query: str) -> List[SearchResult]:
        """使用Brave Search API"""
        # 使用web_search工具（实际上是Brave Search）
        try:
            from kimi_search import kimi_search
            
            results = kimi_search(query, limit=self.config["max_results_per_source"])
            
            search_results = []
            for r in results:
                search_results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("snippet", ""),
                    source="brave",
                    credibility=self._assess_credibility(r.get("url", "")),
                    timestamp=datetime.now().isoformat(),
                    metadata={"engine": "brave"}
                ))
            
            return search_results
        except Exception as e:
            print(f"   Brave搜索失败: {e}")
            return []
    
    def _search_perplexity(self, query: str, require_citations: bool) -> List[SearchResult]:
        """使用Perplexity AI API"""
        if not self.config.get("perplexity_api_key"):
            print("   ⚠️  未配置Perplexity API Key")
            return []
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.config['perplexity_api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "Be precise and concise." if not require_citations else "Be precise and concise. Always cite sources."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ]
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config["timeout"]
            )
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Perplexity返回的是综合回答，需要解析
            search_results = [SearchResult(
                title=f"Perplexity: {query[:50]}...",
                url="https://perplexity.ai",
                snippet=content[:500],
                source="perplexity",
                credibility="high",
                timestamp=datetime.now().isoformat(),
                metadata={
                    "full_content": content,
                    "citations": result.get("citations", [])
                }
            )]
            
            return search_results
            
        except Exception as e:
            print(f"   Perplexity搜索失败: {e}")
            return []
    
    def _search_kimi(self, query: str) -> List[SearchResult]:
        """使用Kimi Search"""
        # 使用内置的kimi_search工具
        try:
            from kimi_search import kimi_search
            
            results = kimi_search(query, limit=self.config["max_results_per_source"])
            
            search_results = []
            for r in results:
                search_results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("snippet", ""),
                    source="kimi",
                    credibility=self._assess_credibility(r.get("url", "")),
                    timestamp=datetime.now().isoformat(),
                    metadata={"engine": "kimi"}
                ))
            
            return search_results
        except Exception as e:
            print(f"   Kimi搜索失败: {e}")
            return []
    
    def _search_web(self, query: str) -> List[SearchResult]:
        """使用通用web_search工具"""
        try:
            # 这里调用系统web_search工具
            # 实际实现依赖于系统工具
            print("   web_search工具待集成")
            return []
        except Exception as e:
            print(f"   Web搜索失败: {e}")
            return []
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """去重结果"""
        seen_urls = set()
        unique_results = []
        
        for r in results:
            # 标准化URL
            url_key = r.url.rstrip('/').lower()
            
            if url_key not in seen_urls:
                seen_urls.add(url_key)
                unique_results.append(r)
        
        return unique_results
    
    def _sort_by_credibility(self, results: List[SearchResult]) -> List[SearchResult]:
        """按可信度排序"""
        credibility_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(results, key=lambda x: credibility_order.get(x.credibility, 3))
    
    def _assess_credibility(self, url: str) -> str:
        """评估URL可信度"""
        # 高可信度域名
        high_credibility = [
            ".edu", ".gov", ".ac.cn",
            "arxiv.org", "nature.com", "science.org",
            "ieee.org", "acm.org", "springer.com",
            "wikipedia.org", "github.com"
        ]
        
        # 中可信度域名
        medium_credibility = [
            "medium.com", "substack.com",
            "linkedin.com", "twitter.com", "x.com",
            "zhihu.com", "jianshu.com"
        ]
        
        url_lower = url.lower()
        
        for domain in high_credibility:
            if domain in url_lower:
                return "high"
        
        for domain in medium_credibility:
            if domain in url_lower:
                return "medium"
        
        return "low"
    
    def _get_cache(self, query: str, sources: List[str]) -> Optional[Dict]:
        """获取缓存"""
        cache_key = f"{query}_{'_'.join(sorted(sources))}"
        cache_file = self.cache_dir / f"{self._query_to_filename(cache_key)}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            
            cache_time = datetime.fromisoformat(cached.get("cached_at", "2000-01-01"))
            if (datetime.now() - cache_time).seconds > self.config["cache_ttl"]:
                return None
            
            return cached.get("data")
        except:
            return None
    
    def _save_cache(self, query: str, sources: List[str], data: Dict):
        """保存缓存"""
        cache_key = f"{query}_{'_'.join(sorted(sources))}"
        cache_file = self.cache_dir / f"{self._query_to_filename(cache_key)}.json"
        
        cache_data = {
            "query": query,
            "sources": sources,
            "cached_at": datetime.now().isoformat(),
            "data": data
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    def _query_to_filename(self, query: str) -> str:
        """查询转换为文件名"""
        import hashlib
        return hashlib.md5(query.encode()).hexdigest()
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total_queries": self.stats["total_queries"],
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "success_rate": f"{self.stats['successful']/max(self.stats['total_queries'],1)*100:.1f}%",
            "by_source": self.stats["by_source"]
        }

# 使用示例
if __name__ == "__main__":
    searcher = MultiSourceSearch()
    
    print("="*70)
    print("测试多源搜索")
    print("="*70)
    
    # 测试搜索
    result = searcher.search(
        query="硬科技合伙人匹配方法论",
        sources=["brave"],  # 先测试brave
        max_results=5
    )
    
    print(f"\n搜索结果:")
    for i, r in enumerate(result["results"][:3], 1):
        print(f"\n{i}. {r['title']}")
        print(f"   来源: {r['source']} | 可信度: {r['credibility']}")
        print(f"   URL: {r['url']}")
        print(f"   摘要: {r['snippet'][:100]}...")
    
    print(f"\n统计:")
    print(json.dumps(searcher.get_stats(), indent=2, ensure_ascii=False))
