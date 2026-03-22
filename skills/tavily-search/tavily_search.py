#!/usr/bin/env python3
"""
Tavily Search 简单封装
"""
import os
import requests
from typing import List, Dict, Optional

def search(query: str, max_results: int = 10, search_depth: str = "basic") -> Dict:
    """
    使用Tavily Search API搜索
    
    Args:
        query: 搜索查询词
        max_results: 返回结果数量（默认10）
        search_depth: 搜索深度 basic|advanced
        
    Returns:
        搜索结果字典
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not set")
    
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    data = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": True if search_depth == "advanced" else False
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()
    
    return response.json()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: tavily_search.py 'query'")
        sys.exit(1)
    
    query = sys.argv[1]
    try:
        results = search(query)
        print(f"Query: {results.get('query', query)}")
        if 'answer' in results:
            print(f"\nAnswer: {results['answer'][:200]}...")
        print(f"\nResults:")
        for i, r in enumerate(results.get('results', [])[:5], 1):
            print(f"{i}. {r.get('title', 'No title')}")
            print(f"   {r.get('url', '')}")
            print()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
