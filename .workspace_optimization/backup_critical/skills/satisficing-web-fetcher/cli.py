#!/usr/bin/env python3
"""
Satisficing Web Fetcher - CLI

简化命令行接口，提供核心抓取功能。
"""

import sys
import json
import argparse
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from fetcher import HTTPFetcher, StealthyFetcher, AdaptiveParser, fetch
from security.audit_logger import AuditLogger, get_recent_audit
from security.domain_whitelist import DomainWhitelist


def cmd_fetch(args):
    """执行抓取命令"""
    url = args.url
    mode = args.mode
    
    print(f"Fetching: {url}")
    print(f"Mode: {mode}")
    
    try:
        if mode == "http":
            fetcher = HTTPFetcher()
        elif mode == "stealthy":
            fetcher = StealthyFetcher(
                headless=not args.no_headless,
                solve_cloudflare=args.solve_cloudflare
            )
        else:
            print(f"Error: Unknown mode '{mode}'", file=sys.stderr)
            return 1
        
        result = fetcher.fetch(url)
        
        if not result.success:
            print(f"Error: {result.error}", file=sys.stderr)
            return 1
        
        # 输出结果
        if args.css:
            # CSS选择器提取
            sel_result = result.css(args.css)
            if args.first:
                output = sel_result.get()
            else:
                output = sel_result.getall()
        elif args.xpath:
            # XPath选择器提取
            sel_result = result.xpath(args.xpath)
            if args.first:
                output = sel_result.get()
            else:
                output = sel_result.getall()
        elif args.extract == "text":
            output = result.text
        else:
            output = result.html
        
        # 格式化输出
        if args.json:
            print(json.dumps({
                "success": True,
                "url": result.url,
                "status_code": result.status_code,
                "content": output,
                "metadata": result.metadata,
            }, ensure_ascii=False, indent=2))
        else:
            if isinstance(output, list):
                for item in output:
                    print(item)
            else:
                print(output)
        
        return 0
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


def cmd_audit(args):
    """查看审计日志"""
    logger = AuditLogger()
    
    if args.stats:
        stats = logger.get_stats(days=args.days)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        entries = logger.query(limit=args.limit)
        for entry in entries:
            timestamp = entry.get("timestamp", 0)
            url = entry.get("url", "")
            success = entry.get("success", False)
            fetcher = entry.get("fetcher_type", "unknown")
            status = "✓" if success else "✗"
            print(f"[{status}] {fetcher} | {url}")
    
    return 0


def cmd_whitelist(args):
    """管理域名白名单"""
    whitelist = DomainWhitelist()
    
    if args.add:
        for domain in args.add:
            whitelist.add(domain)
            print(f"Added: {domain}")
    
    if args.remove:
        for domain in args.remove:
            whitelist.remove(domain)
            print(f"Removed: {domain}")
    
    if args.list or not (args.add or args.remove):
        domains = whitelist.list()
        if domains:
            print("Whitelisted domains:")
            for domain in domains:
                print(f"  - {domain}")
        else:
            print("No domains in whitelist (all allowed)")
    
    return 0


def cmd_test(args):
    """运行测试"""
    test_url = args.url or "https://example.com"
    
    print("=" * 50)
    print("Satisficing Web Fetcher - Self Test")
    print("=" * 50)
    
    # 测试1: HTTP基础抓取
    print("\n[Test 1] HTTP Basic Fetch")
    try:
        fetcher = HTTPFetcher()
        result = fetcher.fetch(test_url)
        print(f"  Success: {result.success}")
        print(f"  Status: {result.status_code}")
        print(f"  Content length: {len(result.html)}")
        print("  ✓ PASSED")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
    
    # 测试2: CSS选择器
    print("\n[Test 2] CSS Selector")
    try:
        result = fetcher.fetch(test_url)
        title = result.css("title::text").get()
        print(f"  Title: {title[:50]}..." if title else "  Title: (not found)")
        print("  ✓ PASSED")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
    
    # 测试3: 安全模块
    print("\n[Test 3] Security Modules")
    try:
        from security.content_filter import ContentFilter
        filter_ = ContentFilter()
        test_content = "Contact: user@example.com, Phone: 13800138000"
        masked = filter_.mask_pii(test_content)
        print(f"  Original: {test_content}")
        print(f"  Masked: {masked}")
        print("  ✓ PASSED")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
    
    # 测试4: 审计日志
    print("\n[Test 4] Audit Logger")
    try:
        logger = AuditLogger()
        stats = logger.get_stats(days=1)
        print(f"  Recent requests: {stats.get('total_requests', 0)}")
        print("  ✓ PASSED")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="satisficing-web-fetcher",
        description="安全、高效、受控的网页抓取工具"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # fetch 命令
    fetch_parser = subparsers.add_parser("fetch", help="抓取网页")
    fetch_parser.add_argument("url", help="目标URL")
    fetch_parser.add_argument("--mode", choices=["http", "stealthy"], default="http",
                            help="抓取模式 (默认: http)")
    fetch_parser.add_argument("--css", help="CSS选择器提取")
    fetch_parser.add_argument("--xpath", help="XPath选择器提取")
    fetch_parser.add_argument("--first", action="store_true", help="仅返回第一个匹配")
    fetch_parser.add_argument("--extract", choices=["html", "text"], default="html",
                            help="提取类型")
    fetch_parser.add_argument("--no-headless", action="store_true",
                            help="显示浏览器窗口 (stealthy模式)")
    fetch_parser.add_argument("--solve-cloudflare", action="store_true",
                            help="尝试绕过Cloudflare (stealthy模式)")
    fetch_parser.add_argument("--json", action="store_true", help="JSON格式输出")
    
    # audit 命令
    audit_parser = subparsers.add_parser("audit", help="查看审计日志")
    audit_parser.add_argument("--stats", action="store_true", help="显示统计信息")
    audit_parser.add_argument("--days", type=int, default=7, help="统计天数")
    audit_parser.add_argument("--limit", type=int, default=50, help="显示条数")
    
    # whitelist 命令
    whitelist_parser = subparsers.add_parser("whitelist", help="管理域名白名单")
    whitelist_parser.add_argument("--add", nargs="+", help="添加域名")
    whitelist_parser.add_argument("--remove", nargs="+", help="移除域名")
    whitelist_parser.add_argument("--list", action="store_true", help="列出域名")
    
    # test 命令
    test_parser = subparsers.add_parser("test", help="运行自检")
    test_parser.add_argument("--url", default="https://example.com", help="测试URL")
    
    args = parser.parse_args()
    
    if args.command == "fetch":
        return cmd_fetch(args)
    elif args.command == "audit":
        return cmd_audit(args)
    elif args.command == "whitelist":
        return cmd_whitelist(args)
    elif args.command == "test":
        return cmd_test(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
