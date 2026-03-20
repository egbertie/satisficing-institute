#!/usr/bin/env python3
"""
示例4: 安全功能演示

场景：生产环境使用、数据保护、审计合规
特点：审计日志、PII脱敏、域名白名单
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from security.audit_logger import AuditLogger, log_request
from security.domain_whitelist import DomainWhitelist, allow, is_allowed
from security.content_filter import ContentFilter, mask_sensitive, contains_pii


def example_audit_logging():
    """审计日志示例"""
    print("=" * 50)
    print("示例4: 安全功能 - 审计日志")
    print("=" * 50)
    
    logger = AuditLogger()
    
    # 记录一些示例请求
    print("\n--- 记录示例请求 ---")
    
    test_requests = [
        {"url": "https://example.com/page1", "success": True, "fetcher_type": "HTTPFetcher"},
        {"url": "https://example.com/page2", "success": True, "fetcher_type": "HTTPFetcher"},
        {"url": "https://blocked.com/secret", "success": False, "fetcher_type": "HTTPFetcher", 
         "error": "Domain not in whitelist"},
    ]
    
    for req in test_requests:
        logger.log(req)
        print(f"Logged: {req['url']} - {'✓' if req['success'] else '✗'}")
    
    # 查询最近日志
    print("\n--- 最近日志 ---")
    entries = logger.query(limit=5)
    for entry in entries:
        status = "✓" if entry.get("success") else "✗"
        print(f"  [{status}] {entry.get('url', 'N/A')}")
    
    # 统计信息
    print("\n--- 统计信息 ---")
    stats = logger.get_stats(days=1)
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Success rate: {stats['success_rate']}")


def example_domain_whitelist():
    """域名白名单示例"""
    print("\n" + "=" * 50)
    print("示例: 域名白名单")
    print("=" * 50)
    
    whitelist = DomainWhitelist()
    
    # 添加白名单
    print("\n--- 添加白名单 ---")
    domains = [
        "example.com",
        "*.github.com",
        "api.example.org",
    ]
    
    for domain in domains:
        whitelist.add(domain)
        print(f"  Added: {domain}")
    
    # 检查URL
    print("\n--- 检查URL访问权限 ---")
    test_urls = [
        "https://example.com/page",
        "https://sub.github.com/repo",
        "https://evil.com/hack",
        "https://api.example.org/data",
    ]
    
    for url in test_urls:
        allowed = whitelist.is_allowed(url)
        status = "✓ ALLOWED" if allowed else "✗ BLOCKED"
        print(f"  {status}: {url}")


def example_pii_filtering():
    """PII过滤示例"""
    print("\n" + "=" * 50)
    print("示例: PII检测与脱敏")
    print("=" * 50)
    
    # 测试内容
    test_contents = [
        "用户信息：姓名张三，手机号13800138000，邮箱zhangsan@example.com",
        "身份证号：110101199001011234",
        "API Key: api_key=sk_live_1234567890abcdef",
        "密码：password='secret123'",
    ]
    
    filter_ = ContentFilter()
    
    for content in test_contents:
        print(f"\n原始内容:")
        print(f"  {content}")
        
        # 检测PII
        findings = filter_.detect_pii(content)
        if findings:
            print(f"\n  检测到 {len(findings)} 个敏感信息:")
            for finding in findings:
                print(f"    - {finding['type']}: {finding['description']}")
        
        # 脱敏
        masked = filter_.mask_pii(content)
        print(f"\n  脱敏后:")
        print(f"    {masked}")


def example_safe_fetch():
    """安全抓取综合示例"""
    print("\n" + "=" * 50)
    print("示例: 安全抓取流程")
    print("=" * 50)
    
    from fetcher import HTTPFetcher
    
    # 配置白名单
    whitelist = DomainWhitelist()
    whitelist.add("example.com")
    whitelist.add("httpbin.org")
    
    # 创建fetcher
    fetcher = HTTPFetcher()
    fetcher._whitelist = whitelist  # 注入白名单
    
    # 安全抓取流程
    print("\n--- 安全抓取流程 ---")
    
    url = "https://example.com"
    print(f"1. 检查域名白名单: {url}")
    
    if not whitelist.is_allowed(url):
        print("   ✗ 域名不在白名单，拒绝访问")
        return
    print("   ✓ 域名允许访问")
    
    print(f"2. 执行抓取...")
    # result = fetcher.fetch(url)
    print("   (跳过实际请求)")
    
    print(f"3. 内容安全检查...")
    # 检查PII等
    print("   ✓ 内容安全")
    
    print(f"4. 记录审计日志...")
    log_request(url, success=True)
    print("   ✓ 已记录")


if __name__ == "__main__":
    try:
        example_audit_logging()
        example_domain_whitelist()
        example_pii_filtering()
        example_safe_fetch()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
