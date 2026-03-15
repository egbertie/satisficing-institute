#!/usr/bin/env python3
"""
示例2: Stealthy抓取 - 反爬绕过

场景：Cloudflare保护页面、有反爬机制的站点
特点：浏览器自动化、指纹模拟、资源消耗较高
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fetcher import StealthyFetcher


def example_stealthy_fetch():
    """Stealthy抓取示例"""
    print("=" * 50)
    print("示例2: Stealthy抓取 - 反爬绕过")
    print("=" * 50)
    
    # 创建stealthy fetcher
    fetcher = StealthyFetcher(
        headless=True,           # 无头模式
        network_idle=True,       # 等待网络空闲
        memory_limit_mb=2048,    # 内存限制2GB
        browser_timeout=60,      # 浏览器超时60秒
    )
    
    # 抓取一个可能有保护的页面
    url = "https://example.com"
    print(f"\nFetching: {url}")
    print("Mode: Stealthy (Playwright + 指纹模拟)")
    
    result = fetcher.fetch(url)
    
    print(f"Success: {result.success}")
    if result.success:
        print(f"Title: {result.metadata.get('title', 'N/A')}")
        print(f"Content length: {len(result.html)} bytes")
        
        # 提取内容
        print("\n--- 页面内容预览 ---")
        print(result.text[:500])
    else:
        print(f"Error: {result.error}")


def example_cloudflare_bypass():
    """Cloudflare绕过示例"""
    print("\n" + "=" * 50)
    print("示例: Cloudflare绕过 (演示)")
    print("=" * 50)
    
    # 注意：实际绕过Cloudflare需要更复杂的处理
    # 这里仅演示接口
    
    fetcher = StealthyFetcher(
        headless=True,
        solve_cloudflare=True,  # 启用Cloudflare处理
    )
    
    # 这是一个Cloudflare演示页面
    url = "https://nopecha.com/demo/cloudflare"
    print(f"\nTarget: {url}")
    print("Note: 实际绕过需要额外的等待和检测逻辑")
    
    # 实际使用时需要确保合法授权
    print("(跳过实际请求，避免不必要的网络访问)")


def example_with_javascript():
    """处理JavaScript渲染的页面"""
    print("\n" + "=" * 50)
    print("示例: JavaScript渲染页面")
    print("=" * 50)
    
    fetcher = StealthyFetcher(
        headless=True,
        network_idle=True,  # 等待网络空闲，确保JS执行完成
    )
    
    # 现代Web应用通常需要JS渲染
    url = "https://example.com"
    print(f"\nFetching: {url}")
    
    result = fetcher.fetch(url)
    
    if result.success:
        print(f"Page loaded successfully")
        # 可以执行更复杂的选择器操作
        # 因为页面已经完全渲染


if __name__ == "__main__":
    print("注意：Stealthy模式需要Playwright和浏览器安装")
    print("安装命令: pip install playwright && playwright install chromium")
    print()
    
    try:
        example_stealthy_fetch()
        example_cloudflare_bypass()
        example_with_javascript()
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请先安装Playwright: pip install playwright")
    except Exception as e:
        print(f"Error: {e}")
