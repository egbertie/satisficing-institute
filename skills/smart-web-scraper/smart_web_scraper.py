#!/usr/bin/env python3
"""
智能网页抓取器 V1.0
统一封装所有网页抓取能力

核心功能：
1. 支持Jina AI API（推荐）
2. 支持本地抓取（requests+beautifulsoup）
3. 内容智能提取
4. 批量抓取
5. 自动重试和容错
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

class SmartWebScraper:
    """
    智能网页抓取器
    统一封装多种网页抓取方式
    """
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.config_file = self.workspace / "config" / "web_scraper_config.json"
        self.cache_dir = self.workspace / "cache" / "web_scraper"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        
        # 统计
        self.stats = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "cached": 0
        }
    
    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            "jina_api_key": None,  # 从环境变量或配置文件读取
            "default_method": "jina",  # jina | local | hybrid
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 2,
            "cache_enabled": True,
            "cache_ttl": 3600,  # 缓存1小时
            "rate_limit": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                default_config.update(config)
        
        return default_config
    
    def scrape(self, 
               url: str,
               method: str = None,
               extract_content: bool = True,
               use_cache: bool = None,
               metadata_only: bool = False) -> Dict:
        """
        抓取单个网页
        
        Args:
            url: 目标URL
            method: 抓取方式 (jina/local/hybrid)
            extract_content: 是否提取正文内容
            use_cache: 是否使用缓存
            metadata_only: 仅获取元数据
        
        Returns:
            包含抓取结果的字典
        """
        method = method or self.config["default_method"]
        use_cache = use_cache if use_cache is not None else self.config["cache_enabled"]
        
        print(f"🌐 正在抓取: {url}")
        print(f"   方法: {method} | 缓存: {'是' if use_cache else '否'}")
        
        # 检查缓存
        if use_cache:
            cached = self._get_cache(url)
            if cached:
                print(f"   ✅ 命中缓存")
                self.stats["cached"] += 1
                return cached
        
        # 执行抓取
        result = None
        for attempt in range(self.config["max_retries"]):
            try:
                if method == "jina":
                    result = self._scrape_with_jina(url)
                elif method == "local":
                    result = self._scrape_with_local(url)
                elif method == "hybrid":
                    result = self._scrape_hybrid(url)
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                if result and result.get("success"):
                    break
                    
            except Exception as e:
                print(f"   ⚠️  尝试 {attempt+1} 失败: {e}")
                if attempt < self.config["max_retries"] - 1:
                    time.sleep(self.config["retry_delay"])
        
        # 保存缓存
        if result and result.get("success") and use_cache:
            self._save_cache(url, result)
        
        # 更新统计
        self.stats["total_requests"] += 1
        if result and result.get("success"):
            self.stats["successful"] += 1
        else:
            self.stats["failed"] += 1
        
        return result or {"success": False, "error": "All retries failed"}
    
    def _scrape_with_jina(self, url: str) -> Dict:
        """使用Jina AI API抓取"""
        jina_url = f"https://r.jina.ai/http://{url}"
        
        headers = {}
        if self.config.get("jina_api_key"):
            headers["Authorization"] = f"Bearer {self.config['jina_api_key']}"
        
        response = requests.get(
            jina_url,
            headers=headers,
            timeout=self.config["timeout"]
        )
        response.raise_for_status()
        
        content = response.text
        
        # 解析Jina AI返回的内容
        lines = content.split('\n')
        title = lines[0] if lines else ""
        
        return {
            "success": True,
            "url": url,
            "title": title,
            "content": content,
            "method": "jina",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "source": "jina.ai",
                "content_length": len(content)
            }
        }
    
    def _scrape_with_local(self, url: str) -> Dict:
        """使用本地请求抓取"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(
            url,
            headers=headers,
            timeout=self.config["timeout"]
        )
        response.raise_for_status()
        
        html = response.text
        
        # 简单提取标题（实际应使用BeautifulSoup）
        title = ""
        if "<title>" in html:
            title = html.split("<title>")[1].split("</title>")[0]
        
        return {
            "success": True,
            "url": url,
            "title": title,
            "content": html,
            "method": "local",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "source": "local",
                "content_length": len(html),
                "status_code": response.status_code
            }
        }
    
    def _scrape_hybrid(self, url: str) -> Dict:
        """混合模式：先尝试Jina，失败用本地"""
        result = self._scrape_with_jina(url)
        if not result.get("success"):
            print(f"   Jina失败，切换到本地抓取...")
            result = self._scrape_with_local(url)
        return result
    
    def batch_scrape(self, 
                     urls: List[str],
                     method: str = None,
                     delay: float = 1.0) -> List[Dict]:
        """
        批量抓取多个网页
        
        Args:
            urls: URL列表
            method: 抓取方式
            delay: 请求间隔（秒）
        
        Returns:
            结果列表
        """
        print(f"\n🌐 开始批量抓取 {len(urls)} 个网页...")
        
        results = []
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}]")
            result = self.scrape(url, method=method)
            results.append(result)
            
            if i < len(urls):
                time.sleep(delay)
        
        # 统计
        success_count = sum(1 for r in results if r.get("success"))
        print(f"\n✅ 批量抓取完成: {success_count}/{len(urls)} 成功")
        
        return results
    
    def _get_cache(self, url: str) -> Optional[Dict]:
        """获取缓存"""
        cache_file = self.cache_dir / f"{self._url_to_filename(url)}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            
            # 检查缓存是否过期
            cache_time = datetime.fromisoformat(cached.get("cached_at", "2000-01-01"))
            if (datetime.now() - cache_time).seconds > self.config["cache_ttl"]:
                return None
            
            return cached.get("data")
        except:
            return None
    
    def _save_cache(self, url: str, data: Dict):
        """保存缓存"""
        cache_file = self.cache_dir / f"{self._url_to_filename(url)}.json"
        
        cache_data = {
            "url": url,
            "cached_at": datetime.now().isoformat(),
            "data": data
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    def _url_to_filename(self, url: str) -> str:
        """URL转换为文件名"""
        # 简化版：使用URL的hash
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_requests": self.stats["total_requests"],
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "cached": self.stats["cached"],
            "success_rate": f"{self.stats['successful']/max(self.stats['total_requests'],1)*100:.1f}%"
        }
    
    def export_to_markdown(self, result: Dict, output_file: str = None) -> str:
        """
        将抓取结果导出为Markdown
        
        Args:
            result: 抓取结果
            output_file: 输出文件路径（可选）
        
        Returns:
            Markdown字符串
        """
        if not result.get("success"):
            return f"# 抓取失败\n\nURL: {result.get('url')}\n\n错误: {result.get('error')}"
        
        md = f"""# {result['title']}

**来源**: {result['url']}  
**抓取时间**: {result['timestamp']}  
**方法**: {result['method']}

---

{result['content']}

---

*由智能网页抓取器生成*
"""
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md)
            print(f"✅ 已导出: {output_file}")
        
        return md

# 使用示例
if __name__ == "__main__":
    scraper = SmartWebScraper()
    
    # 单URL抓取
    print("="*70)
    print("测试单URL抓取")
    print("="*70)
    
    test_url = "https://example.com"
    result = scraper.scrape(test_url)
    
    print(f"\n结果:")
    print(f"  成功: {result.get('success')}")
    print(f"  标题: {result.get('title', 'N/A')}")
    print(f"  内容长度: {len(result.get('content', ''))}")
    
    # 统计
    print(f"\n统计:")
    stats = scraper.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
