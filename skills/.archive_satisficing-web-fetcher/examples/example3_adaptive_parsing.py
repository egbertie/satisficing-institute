#!/usr/bin/env python3
"""
示例3: 自适应解析

场景：页面结构经常变化、需要长期维护的爬虫
特点：智能元素追踪、自动适应页面变化
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fetcher import HTTPFetcher, AdaptiveParser


def example_adaptive_parsing():
    """自适应解析示例"""
    print("=" * 50)
    print("示例3: 自适应解析")
    print("=" * 50)
    
    # 第一步：抓取页面并保存元素指纹
    print("\n--- 步骤1: 首次抓取并保存指纹 ---")
    
    fetcher = HTTPFetcher()
    url = "https://quotes.toscrape.com"
    
    result = fetcher.fetch(url)
    
    if not result.success:
        print(f"Failed to fetch: {result.error}")
        return
    
    # 使用自适应解析器
    parser = AdaptiveParser(result.html)
    
    # 抓取元素并自动保存指纹
    print("\n提取名言并保存指纹...")
    quotes = parser.css(".quote .text::text", auto_save=True)
    
    print(f"Found {len(quotes)} quotes")
    for i, quote in enumerate(quotes.getall()[:3], 1):
        print(f"  {i}. {quote[:60]}...")
    
    # 指纹已保存到 .element_fingerprints.json
    print("\n元素指纹已保存到 .element_fingerprints.json")
    
    # 第二步：模拟页面变化后重新抓取
    print("\n--- 步骤2: 页面变化后使用自适应模式 ---")
    print("(假设页面结构已改变，但内容相似)")
    
    # 重新抓取
    result2 = fetcher.fetch(url)
    parser2 = AdaptiveParser(result2.html)
    
    # 使用adaptive=True尝试找回元素
    # 即使选择器失效，也能基于指纹找到相似元素
    quotes_adaptive = parser2.css(".quote .text::text", adaptive=True)
    
    print(f"Adaptive mode found {len(quotes_adaptive)} quotes")
    for i, quote in enumerate(quotes_adaptive.getall()[:3], 1):
        print(f"  {i}. {quote[:60]}...")


def example_find_by_text():
    """基于文本内容查找"""
    print("\n" + "=" * 50)
    print("示例: 基于文本查找")
    print("=" * 50)
    
    fetcher = HTTPFetcher()
    result = fetcher.fetch("https://quotes.toscrape.com")
    
    parser = AdaptiveParser(result.html)
    
    # 查找包含特定文本的元素
    print("\n查找包含 'world' 的元素...")
    elements = parser.find_by_text("world")
    
    print(f"Found {len(elements)} elements")
    for elem in elements.getall()[:3]:
        print(f"  - {elem[:80]}...")


def example_xpath_selection():
    """XPath选择器示例"""
    print("\n" + "=" * 50)
    print("示例: XPath选择器")
    print("=" * 50)
    
    fetcher = HTTPFetcher()
    result = fetcher.fetch("https://quotes.toscrape.com")
    
    parser = AdaptiveParser(result.html)
    
    # 使用XPath
    print("\n使用XPath提取名言...")
    quotes = parser.xpath('//span[@class="text"]/text()')
    
    print(f"Found {len(quotes)} quotes with XPath")
    for i, quote in enumerate(quotes.getall()[:3], 1):
        print(f"  {i}. {quote[:60]}...")


def example_element_navigation():
    """元素导航示例"""
    print("\n" + "=" * 50)
    print("示例: 元素关系导航")
    print("=" * 50)
    
    html = """
    <html>
        <body>
            <div class="product">
                <h2>Product Name</h2>
                <span class="price">$99.99</span>
                <div class="description">
                    <p>This is a great product.</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    parser = AdaptiveParser(html)
    
    # 找到产品容器
    product = parser.css(".product")
    
    if len(product) > 0:
        print("\n产品信息:")
        # 提取各种信息
        # 注意：当前实现是简化版，完整实现应支持链式导航


if __name__ == "__main__":
    print("注意：本示例需要lxml库")
    print("安装命令: pip install lxml")
    print()
    
    try:
        example_adaptive_parsing()
        example_find_by_text()
        example_xpath_selection()
        example_element_navigation()
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请先安装lxml: pip install lxml")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
