#!/usr/bin/env python3
"""
内容过滤器

功能：
1. PII检测与脱敏
2. 敏感内容过滤
3. 内容大小限制

安全要求：
- 自动检测身份证号、手机号、银行卡
- 可选脱敏或拒绝
- 响应内容日志脱敏
"""

import re
import hashlib
from typing import List, Dict, Pattern, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SensitivityLevel(Enum):
    """敏感度级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SensitivePattern:
    """敏感信息模式"""
    name: str
    pattern: Pattern
    level: SensitivityLevel
    description: str


class ContentFilter:
    """内容过滤器"""
    
    # 预定义敏感信息模式
    DEFAULT_PATTERNS = [
        # 中国身份证号
        SensitivePattern(
            name="china_id_card",
            pattern=re.compile(r'\b\d{17}[\dXx]\b'),
            level=SensitivityLevel.CRITICAL,
            description="Chinese ID card number"
        ),
        # 中国手机号
        SensitivePattern(
            name="china_phone",
            pattern=re.compile(r'\b1[3-9]\d{9}\b'),
            level=SensitivityLevel.HIGH,
            description="Chinese mobile phone number"
        ),
        # 银行卡号（简单匹配，可能误报）
        SensitivePattern(
            name="bank_card",
            pattern=re.compile(r'\b\d{16,19}\b'),
            level=SensitivityLevel.HIGH,
            description="Possible bank card number"
        ),
        # 邮箱
        SensitivePattern(
            name="email",
            pattern=re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            level=SensitivityLevel.MEDIUM,
            description="Email address"
        ),
        # API Key（通用模式）
        SensitivePattern(
            name="api_key",
            pattern=re.compile(r'\b(api[_-]?key|apikey|token)\s*[:=]\s*["\']?[\w\-]{16,}["\']?\b', re.I),
            level=SensitivityLevel.HIGH,
            description="API Key or Token"
        ),
        # 密码字段
        SensitivePattern(
            name="password",
            pattern=re.compile(r'\b(password|passwd|pwd)\s*[:=]\s*["\'][^"\']+["\']\b', re.I),
            level=SensitivityLevel.CRITICAL,
            description="Password field"
        ),
    ]
    
    def __init__(self, 
                 patterns: Optional[List[SensitivePattern]] = None,
                 mask_char: str = "*",
                 max_content_length: int = 10 * 1024 * 1024):
        """
        Args:
            patterns: 敏感信息模式列表
            mask_char: 脱敏字符
            max_content_length: 最大内容长度
        """
        self.patterns = patterns or self.DEFAULT_PATTERNS.copy()
        self.mask_char = mask_char
        self.max_content_length = max_content_length
    
    def filter(self, content: str, auto_mask: bool = True) -> str:
        """
        过滤内容
        
        Args:
            content: 原始内容
            auto_mask: 是否自动脱敏
            
        Returns:
            str: 过滤后的内容
        """
        # 长度检查
        if len(content) > self.max_content_length:
            content = content[:self.max_content_length]
        
        # 敏感信息处理
        if auto_mask:
            content = self.mask_pii(content)
        
        return content
    
    def detect_pii(self, content: str) -> List[Dict]:
        """
        检测PII信息
        
        Args:
            content: 要检测的内容
            
        Returns:
            List[Dict]: 检测到的PII信息列表
        """
        findings = []
        
        for pattern in self.patterns:
            for match in pattern.pattern.finditer(content):
                findings.append({
                    "type": pattern.name,
                    "level": pattern.level.value,
                    "description": pattern.description,
                    "position": (match.start(), match.end()),
                    "value": match.group(),
                })
        
        return findings
    
    def mask_pii(self, content: str) -> str:
        """
        脱敏PII信息
        
        Args:
            content: 原始内容
            
        Returns:
            str: 脱敏后的内容
        """
        result = content
        
        for pattern in self.patterns:
            if pattern.level in (SensitivityLevel.HIGH, SensitivityLevel.CRITICAL):
                result = pattern.pattern.sub(
                    lambda m: self._mask_value(m.group()),
                    result
                )
        
        return result
    
    def check_safe(self, content: str, max_critical: int = 0) -> Tuple[bool, List[Dict]]:
        """
        检查内容是否安全
        
        Args:
            content: 要检查的内容
            max_critical: 允许的最大关键级别PII数量
            
        Returns:
            Tuple[bool, List[Dict]]: (是否安全, 检测到的PII列表)
        """
        findings = self.detect_pii(content)
        
        critical_count = sum(
            1 for f in findings 
            if f.get("level") == SensitivityLevel.CRITICAL.value
        )
        
        is_safe = critical_count <= max_critical
        return is_safe, findings
    
    def _mask_value(self, value: str) -> str:
        """脱敏单个值"""
        if len(value) <= 4:
            return self.mask_char * len(value)
        
        # 保留前2后2，中间脱敏
        return value[:2] + self.mask_char * (len(value) - 4) + value[-2:]
    
    def add_pattern(self, name: str, pattern: str, level: SensitivityLevel, description: str = ""):
        """添加自定义模式"""
        self.patterns.append(SensitivePattern(
            name=name,
            pattern=re.compile(pattern),
            level=level,
            description=description
        ))
    
    def remove_pattern(self, name: str):
        """移除模式"""
        self.patterns = [p for p in self.patterns if p.name != name]


# 便捷函数

def mask_sensitive(content: str) -> str:
    """便捷脱敏函数"""
    filter_ = ContentFilter()
    return filter_.mask_pii(content)


def contains_pii(content: str) -> bool:
    """检查是否包含PII"""
    filter_ = ContentFilter()
    findings = filter_.detect_pii(content)
    return len(findings) > 0
