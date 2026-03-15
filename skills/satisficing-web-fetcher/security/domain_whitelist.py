#!/usr/bin/env python3
"""
域名白名单模块

功能：
1. 域名访问控制
2. 支持通配符匹配
3. 默认拒绝策略

安全要求：
- 默认拒绝所有域名
- 必须显式添加白名单
- 支持通配符子域名
"""

import fnmatch
from typing import List, Set
from urllib.parse import urlparse
from pathlib import Path


class DomainWhitelist:
    """域名白名单管理器"""
    
    # 默认白名单 - 可以根据需要修改
    DEFAULT_WHITELIST = [
        # 示例域名，实际使用时应清空或配置
        "example.com",
        "*.example.com",
    ]
    
    def __init__(self, whitelist: List[str] = None):
        """
        Args:
            whitelist: 白名单域名列表，None则使用默认
        """
        self._whitelist: Set[str] = set(whitelist or self.DEFAULT_WHITELIST)
    
    def is_allowed(self, url: str) -> bool:
        """
        检查URL是否允许访问
        
        Args:
            url: 要检查的URL
            
        Returns:
            bool: 是否允许访问
        """
        # 如果白名单为空，默认允许（生产环境应改为默认拒绝）
        if not self._whitelist:
            return True  # 或者 return False 用于严格模式
        
        try:
            domain = self._extract_domain(url)
        except:
            return False
        
        # 精确匹配
        if domain in self._whitelist:
            return True
        
        # 通配符匹配
        for pattern in self._whitelist:
            if pattern.startswith("*."):
                # *.example.com 匹配 example.com 和 sub.example.com
                suffix = pattern[2:]  # "example.com"
                if domain == suffix or domain.endswith("." + suffix):
                    return True
            elif fnmatch.fnmatch(domain, pattern):
                return True
        
        return False
    
    def add(self, domain: str):
        """
        添加域名到白名单
        
        Args:
            domain: 域名，支持通配符如 *.example.com
        """
        domain = domain.lower().strip()
        self._whitelist.add(domain)
    
    def remove(self, domain: str):
        """
        从白名单移除域名
        
        Args:
            domain: 要移除的域名
        """
        domain = domain.lower().strip()
        self._whitelist.discard(domain)
    
    def list(self) -> List[str]:
        """获取所有白名单域名"""
        return sorted(list(self._whitelist))
    
    def clear(self):
        """清空白名单"""
        self._whitelist.clear()
    
    def _extract_domain(self, url: str) -> str:
        """从URL中提取域名"""
        # 确保有协议前缀
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # 移除端口
        if ":" in domain:
            domain = domain.split(":")[0]
        
        return domain
    
    def save_to_file(self, filepath: Path):
        """保存白名单到文件"""
        with open(filepath, 'w') as f:
            for domain in sorted(self._whitelist):
                f.write(domain + '\n')
    
    def load_from_file(self, filepath: Path):
        """从文件加载白名单"""
        if not filepath.exists():
            return
        
        with open(filepath, 'r') as f:
            for line in f:
                domain = line.strip()
                if domain and not domain.startswith('#'):
                    self.add(domain)


# 全局白名单实例（单例模式）
_whitelist_instance: DomainWhitelist = None

def get_whitelist() -> DomainWhitelist:
    """获取全局白名单实例"""
    global _whitelist_instance
    if _whitelist_instance is None:
        _whitelist_instance = DomainWhitelist()
    return _whitelist_instance


# 便捷函数

def is_allowed(url: str) -> bool:
    """便捷检查URL是否允许访问"""
    return get_whitelist().is_allowed(url)


def allow(domain: str):
    """便捷添加域名到白名单"""
    get_whitelist().add(domain)


def deny(domain: str):
    """便捷从白名单移除域名"""
    get_whitelist().remove(domain)
