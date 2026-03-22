#!/usr/bin/env python3
"""Brave Search 简单封装"""
import os
import requests
from typing import List, Dict

def search(query: str, count: int = 10) -> List[Dict]:
    """
    使用Brave Search API搜索
    
    Args:
        query: 搜索查询词
        count: 返回结果数量（默认10）
        
    Returns:
        搜索结果列表
    """
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        raise ValueError("BRAVE_API_KEY not set")
    
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "X-Subscription-Token": api_key,
        "Accept": "application/json"
    }
    params = {
        "q": query,
        "count": count
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    results = []
    
    for item in data.get("web", {}).get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("description", ""),
            "source": "brave"
        })
    
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: brave_search.py 'query'")
        sys.exit(1)
    
    query = sys.argv[1]
    try:
        results = search(query)
        for i, r in enumerate(results[:5], 1):
            print(f"{i}. {r['title']}")
            print(f"   {r['url']}")
            print(f"   {r['snippet'][:100]}...")
            print()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
