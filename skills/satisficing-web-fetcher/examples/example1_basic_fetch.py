#!/usr/bin/env python3
"""
示例1: 基础HTTP抓取

场景：抓取静态页面、API端点
特点：轻量级、快速、低资源消耗
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fetcher import HTTPFetcher


def example_basic_fetch():
    """基础抓取示例"""
    print("=" * 50)
    print("示例1: 基础HTTP抓取")
    print("=" * 50)
    
    # 创建fetcher实例
    fetcher = HTTPFetcher(
        impersonate="chrome",  # 模拟Chrome浏览器
        stealth_headers=True,   # 使用stealth请求头
        rate_limit=1.0,         # 每秒1个请求
    )
    
    # 抓取页面
    url = "https://quotes.toscrape.com"
    print(f"\nFetching: {url}")
    
    result = fetcher.fetch(url)
    
    print(f"Success: {result.success}")
    print(f"Status: {result.status_code}")
    print(f"Content length: {len(result.html)} bytes")
    
    # 使用CSS选择器提取数据
    print("\n--- 提取名言 ---")
    quotes = result.css(".quote .text::text").getall()
    for i, quote in enumerate(quotes[:5], 1):
        print(f"{i}. {quote[:80]}...")
    
    # 提取作者
    print("\n--- 提取作者 ---")
    authors = result.css(".quote .author::text").getall()
    for i, author in enumerate(authors[:5], 1):
        print(f"{i}. {author}")


def example_api_fetch():
    """API抓取示例"""
    print("\n" + "=" * 50)
    print("示例: API抓取")
    print("=" * 50)
    
    fetcher = HTTPFetcher()
    
    # 示例：获取GitHub API信息
    url = "https://api.github.com"
    print(f"\nFetching API: {url}")
    
    result = fetcher.fetch(url)
    
    if result.success:
        # 解析JSON响应
        try:
            data = result.json()
            print(f"\nGitHub API Version: {data.get('current_user_url', 'N/A')}")
            print(f"Available endpoints:")
            for key in list(data.keys())[:5]:
                print(f"  - {key}")
        except:
            print("Failed to parse JSON")


def example_session():
    """会话保持示例"""
    print("\n" + "=" * 50)
    print("示例: 使用会话保持Cookie")
    print("=" * 50)
    
    # HTTPFetcher会自动处理会话
    fetcher = HTTPFetcher()
    
    # 第一次请求
    print("\n--- 第一次请求 ---")
    result1 = fetcher.fetch("https://httpbin.org/cookies/set?name=value")
    print(f"Status: {result1.status_code}")
    
    # 注意：urllib默认不支持Cookie保持
    # 实际项目中需要额外实现或使用requests.Session
    print("(注：HTTPFetcher使用urllib，如需完整会话支持请使用requests.Session)")


if __name__ == "__main__":
    try:
        example_basic_fetch()
        example_api_fetch()
        example_session()
    except Exception as e:
        print(f"Error: {e}")
