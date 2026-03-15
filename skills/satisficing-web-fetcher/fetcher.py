#!/usr/bin/env python3
"""
Satisficing Web Fetcher - 满意解Web抓取器主模块

核心设计原则：
1. 安全第一：所有操作都有边界和审计
2. 渐进增强：从简单到复杂，按需升级
3. 透明可控：用户清楚知道发生了什么
"""

from __future__ import annotations

import json
import re
import time
import hashlib
import urllib.request
import urllib.parse
import ssl
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Union
from dataclasses import dataclass, field
from pathlib import Path

# 安全模块导入
import sys
sys.path.insert(0, str(Path(__file__).parent))
from security.audit_logger import AuditLogger
from security.domain_whitelist import DomainWhitelist
from security.content_filter import ContentFilter


@dataclass
class FetchResult:
    """统一的抓取结果封装"""
    success: bool
    url: str
    status_code: int
    html: str = ""
    text: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def css(self, selector: str, **kwargs) -> "SelectorResult":
        """CSS选择器查询"""
        return AdaptiveParser(self.html).css(selector, **kwargs)
    
    def xpath(self, selector: str, **kwargs) -> "SelectorResult":
        """XPath选择器查询"""
        return AdaptiveParser(self.html).xpath(selector, **kwargs)
    
    def json(self) -> Dict:
        """将结果解析为JSON"""
        return json.loads(self.text or self.html)


@dataclass
class SelectorResult:
    """选择器结果封装"""
    elements: List[Dict[str, Any]] = field(default_factory=list)
    _html: str = ""
    
    def get(self, default: Any = None) -> Any:
        """获取第一个结果"""
        if self.elements:
            return self.elements[0].get("text", default)
        return default
    
    def getall(self) -> List[Any]:
        """获取所有结果"""
        return [e.get("text", "") for e in self.elements]
    
    def __len__(self) -> int:
        return len(self.elements)
    
    def __getitem__(self, index: int) -> "SelectorResult":
        if index < len(self.elements):
            return SelectorResult([self.elements[index]], self._html)
        raise IndexError(f"Index {index} out of range")


class BaseFetcher(ABC):
    """抓取器基类"""
    
    def __init__(self, 
                 rate_limit: float = 1.0,
                 timeout: int = 30,
                 max_content_size: int = 10 * 1024 * 1024):
        """
        Args:
            rate_limit: 每秒最大请求数
            timeout: 请求超时时间(秒)
            max_content_size: 最大内容大小(字节)
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.max_content_size = max_content_size
        self._last_request_time: Optional[float] = None
        self._audit_logger = AuditLogger()
        self._whitelist = DomainWhitelist()
        self._content_filter = ContentFilter()
    
    def _check_rate_limit(self):
        """检查并执行速率限制"""
        if self._last_request_time:
            elapsed = time.time() - self._last_request_time
            if elapsed < 1.0 / self.rate_limit:
                sleep_time = (1.0 / self.rate_limit) - elapsed
                time.sleep(sleep_time)
        self._last_request_time = time.time()
    
    def _check_domain(self, url: str) -> bool:
        """检查域名是否在白名单中"""
        return self._whitelist.is_allowed(url)
    
    def _log_request(self, url: str, success: bool, error: Optional[str] = None):
        """记录请求审计日志"""
        self._audit_logger.log({
            "timestamp": time.time(),
            "url": url,
            "fetcher_type": self.__class__.__name__,
            "success": success,
            "error": error,
        })
    
    @abstractmethod
    def fetch(self, url: str, **kwargs) -> FetchResult:
        """执行抓取，子类必须实现"""
        pass


class HTTPFetcher(BaseFetcher):
    """
    基础HTTP抓取器
    
    适用场景：
    - 静态HTML页面
    - API端点
    - 简单的GET请求
    
    特点：
    - 轻量级，无浏览器开销
    - TLS指纹模拟
    - 自动重试机制
    """
    
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    
    def __init__(self, 
                 impersonate: str = "chrome",
                 stealth_headers: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self.impersonate = impersonate
        self.stealth_headers = stealth_headers
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE
    
    def fetch(self, url: str, 
              method: str = "GET",
              headers: Optional[Dict] = None,
              data: Optional[bytes] = None,
              **kwargs) -> FetchResult:
        """
        执行HTTP抓取
        
        Args:
            url: 目标URL
            method: HTTP方法
            headers: 自定义请求头
            data: POST数据
            
        Returns:
            FetchResult: 抓取结果
        """
        # 安全检查
        if not self._check_domain(url):
            error_msg = f"Domain not in whitelist: {url}"
            self._log_request(url, False, error_msg)
            return FetchResult(
                success=False,
                url=url,
                status_code=0,
                error=error_msg
            )
        
        # 速率限制
        self._check_rate_limit()
        
        try:
            # 构建请求
            req_headers = self.DEFAULT_HEADERS.copy() if self.stealth_headers else {}
            if headers:
                req_headers.update(headers)
            
            req = urllib.request.Request(
                url,
                data=data,
                headers=req_headers,
                method=method
            )
            
            # 执行请求
            with urllib.request.urlopen(
                req, 
                timeout=self.timeout,
                context=self._ssl_context
            ) as response:
                content = response.read()
                
                # 大小检查
                if len(content) > self.max_content_size:
                    raise ValueError(f"Content size exceeds limit: {len(content)} bytes")
                
                # 解码内容
                html = content.decode('utf-8', errors='ignore')
                
                # 内容过滤
                html = self._content_filter.filter(html)
                
                result = FetchResult(
                    success=True,
                    url=url,
                    status_code=response.status,
                    html=html,
                    text=self._extract_text(html),
                    headers=dict(response.headers),
                    metadata={
                        "content_length": len(content),
                        "impersonate": self.impersonate,
                    }
                )
                
                self._log_request(url, True)
                return result
                
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            self._log_request(url, False, error_msg)
            return FetchResult(
                success=False,
                url=url,
                status_code=0,
                error=error_msg
            )
    
    def _extract_text(self, html: str) -> str:
        """从HTML中提取纯文本"""
        # 简单的文本提取，移除script和style
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text


class StealthyFetcher(BaseFetcher):
    """
    反爬绕过抓取器
    
    适用场景：
    - Cloudflare保护的页面
    - 有反爬机制的站点
    - 需要浏览器指纹模拟的页面
    
    特点：
    - Playwright浏览器自动化
    - 指纹模拟
    - 内存限制和超时控制
    """
    
    def __init__(self,
                 headless: bool = True,
                 solve_cloudflare: bool = False,
                 network_idle: bool = False,
                 memory_limit_mb: int = 2048,
                 browser_timeout: int = 300,
                 **kwargs):
        super().__init__(**kwargs)
        self.headless = headless
        self.solve_cloudflare = solve_cloudflare
        self.network_idle = network_idle
        self.memory_limit_mb = memory_limit_mb
        self.browser_timeout = browser_timeout
        self._playwright = None
        self._browser = None
    
    def fetch(self, url: str, **kwargs) -> FetchResult:
        """
        执行Stealthy抓取
        
        Args:
            url: 目标URL
            
        Returns:
            FetchResult: 抓取结果
        """
        # 安全检查
        if not self._check_domain(url):
            error_msg = f"Domain not in whitelist: {url}"
            self._log_request(url, False, error_msg)
            return FetchResult(
                success=False,
                url=url,
                status_code=0,
                error=error_msg
            )
        
        # 速率限制
        self._check_rate_limit()
        
        try:
            # 延迟导入playwright，避免不必要的依赖加载
            from playwright.sync_api import sync_playwright
            from sandbox.memory_limiter import MemoryLimiter
            from sandbox.timeout_guard import TimeoutGuard
            
            with TimeoutGuard(self.browser_timeout):
                with MemoryLimiter(self.memory_limit_mb):
                    with sync_playwright() as p:
                        # 启动浏览器
                        browser = p.chromium.launch(
                            headless=self.headless,
                            args=[
                                "--no-sandbox",
                                "--disable-setuid-sandbox",
                                "--disable-dev-shm-usage",
                                "--disable-accelerated-2d-canvas",
                                "--disable-gpu",
                                "--window-size=1920,1080",
                            ]
                        )
                        
                        context = browser.new_context(
                            viewport={"width": 1920, "height": 1080},
                            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0",
                            locale="en-US",
                            timezone_id="America/New_York",
                        )
                        
                        # 添加stealth脚本
                        self._apply_stealth(context)
                        
                        page = context.new_page()
                        
                        # 导航到页面
                        page.goto(url, wait_until="networkidle" if self.network_idle else "load")
                        
                        # 处理Cloudflare（如果启用）
                        if self.solve_cloudflare:
                            self._handle_cloudflare(page)
                        
                        # 获取内容
                        html = page.content()
                        title = page.title()
                        
                        # 内容过滤
                        html = self._content_filter.filter(html)
                        
                        browser.close()
                        
                        result = FetchResult(
                            success=True,
                            url=url,
                            status_code=200,
                            html=html,
                            text=self._extract_text(html),
                            metadata={
                                "title": title,
                                "headless": self.headless,
                                "cloudflare_solved": self.solve_cloudflare,
                            }
                        )
                        
                        self._log_request(url, True)
                        return result
                        
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            self._log_request(url, False, error_msg)
            return FetchResult(
                success=False,
                url=url,
                status_code=0,
                error=error_msg
            )
    
    def _apply_stealth(self, context):
        """应用stealth脚本减少被检测概率"""
        # 基础stealth注入
        stealth_script = """
        () => {
            // 覆盖webdriver检测
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 覆盖plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // 覆盖languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // 覆盖chrome对象
            window.chrome = {
                runtime: {}
            };
        }
        """
        context.add_init_script(stealth_script)
    
    def _handle_cloudflare(self, page):
        """处理Cloudflare挑战"""
        import time
        # 简单等待策略，实际可能需要更复杂的处理
        time.sleep(3)
        # 检查是否还有挑战
        if page.locator("#challenge-running").count() > 0:
            time.sleep(5)
    
    def _extract_text(self, html: str) -> str:
        """从HTML中提取纯文本"""
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text


class AdaptiveParser:
    """
    自适应解析器
    
    基于页面结构智能追踪元素，即使页面布局变化也能定位。
    """
    
    def __init__(self, html: str):
        self.html = html
        self._element_cache: Dict[str, List[Dict]] = {}
        self._fingerprint_db_path = Path(__file__).parent / ".element_fingerprints.json"
        self._fingerprints = self._load_fingerprints()
    
    def css(self, selector: str, 
            adaptive: bool = False,
            auto_save: bool = False,
            **kwargs) -> SelectorResult:
        """
        CSS选择器查询
        
        Args:
            selector: CSS选择器
            adaptive: 启用自适应匹配
            auto_save: 自动保存元素指纹
            
        Returns:
            SelectorResult: 选择结果
        """
        try:
            # 延迟导入lxml
            from lxml import html as lh
            
            tree = lh.fromstring(self.html)
            elements = tree.cssselect(selector)
            
            results = []
            for elem in elements:
                result = {
                    "tag": elem.tag,
                    "text": elem.text_content().strip() if elem.text else "",
                    "html": lh.tostring(elem, encoding='unicode'),
                    "attrib": dict(elem.attrib),
                }
                results.append(result)
            
            # 自适应匹配
            if adaptive and not results and selector in self._fingerprints:
                results = self._adaptive_find(selector)
            
            # 保存指纹
            if auto_save and results:
                self._save_fingerprint(selector, results[0])
            
            return SelectorResult(results, self.html)
            
        except Exception as e:
            print(f"CSS parsing error: {e}", file=sys.stderr)
            return SelectorResult([], self.html)
    
    def xpath(self, selector: str, **kwargs) -> SelectorResult:
        """XPath选择器查询"""
        try:
            from lxml import html as lh
            
            tree = lh.fromstring(self.html)
            elements = tree.xpath(selector)
            
            results = []
            for elem in elements:
                if hasattr(elem, 'text_content'):
                    result = {
                        "tag": elem.tag if hasattr(elem, 'tag') else 'text',
                        "text": elem.text_content().strip() if hasattr(elem, 'text_content') else str(elem),
                        "html": lh.tostring(elem, encoding='unicode') if hasattr(elem, 'tag') else str(elem),
                        "attrib": dict(elem.attrib) if hasattr(elem, 'attrib') else {},
                    }
                    results.append(result)
            
            return SelectorResult(results, self.html)
            
        except Exception as e:
            print(f"XPath parsing error: {e}", file=sys.stderr)
            return SelectorResult([], self.html)
    
    def find_by_text(self, text: str, tag: Optional[str] = None) -> SelectorResult:
        """通过文本内容查找元素"""
        try:
            from lxml import html as lh
            
            tree = lh.fromstring(self.html)
            xpath = f"//*[contains(text(), '{text}')]"
            if tag:
                xpath = f"//{tag}[contains(text(), '{text}')]"
            
            elements = tree.xpath(xpath)
            
            results = []
            for elem in elements:
                result = {
                    "tag": elem.tag,
                    "text": elem.text_content().strip(),
                    "html": lh.tostring(elem, encoding='unicode'),
                    "attrib": dict(elem.attrib),
                }
                results.append(result)
            
            return SelectorResult(results, self.html)
            
        except Exception as e:
            print(f"Text search error: {e}", file=sys.stderr)
            return SelectorResult([], self.html)
    
    def _load_fingerprints(self) -> Dict:
        """加载元素指纹数据库"""
        if self._fingerprint_db_path.exists():
            try:
                with open(self._fingerprint_db_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_fingerprint(self, selector: str, element: Dict):
        """保存元素指纹"""
        fingerprint = {
            "tag": element.get("tag"),
            "text_hash": hashlib.md5(element.get("text", "").encode()).hexdigest()[:16],
            "attrib_keys": list(element.get("attrib", {}).keys()),
        }
        self._fingerprints[selector] = fingerprint
        
        try:
            with open(self._fingerprint_db_path, 'w') as f:
                json.dump(self._fingerprints, f, indent=2)
        except Exception as e:
            print(f"Failed to save fingerprint: {e}", file=sys.stderr)
    
    def _adaptive_find(self, selector: str) -> List[Dict]:
        """基于指纹自适应查找元素"""
        fingerprint = self._fingerprints.get(selector)
        if not fingerprint:
            return []
        
        # 简化的自适应逻辑：基于标签和属性查找
        try:
            from lxml import html as lh
            tree = lh.fromstring(self.html)
            
            tag = fingerprint.get("tag")
            if tag:
                elements = tree.findall(f".//{tag}")
                results = []
                for elem in elements:
                    result = {
                        "tag": elem.tag,
                        "text": elem.text_content().strip() if elem.text else "",
                        "html": lh.tostring(elem, encoding='unicode'),
                        "attrib": dict(elem.attrib),
                    }
                    results.append(result)
                return results
        except Exception as e:
            print(f"Adaptive find error: {e}", file=sys.stderr)
        
        return []


# 便捷函数

def fetch(url: str, mode: str = "http", **kwargs) -> FetchResult:
    """
    便捷抓取函数
    
    Args:
        url: 目标URL
        mode: 抓取模式 (http|stealthy|dynamic)
        **kwargs: 传递给具体fetcher的参数
    
    Returns:
        FetchResult: 抓取结果
    """
    if mode == "http":
        fetcher = HTTPFetcher(**kwargs)
    elif mode == "stealthy":
        fetcher = StealthyFetcher(**kwargs)
    else:
        raise ValueError(f"Unknown mode: {mode}")
    
    return fetcher.fetch(url)


if __name__ == "__main__":
    # 简单测试
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Fetching {url}...")
        result = fetch(url, mode="http")
        print(f"Success: {result.success}")
        print(f"Status: {result.status_code}")
        print(f"Text preview: {result.text[:500]}...")
