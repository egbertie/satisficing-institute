#!/usr/bin/env python3
"""
信息清洗与去重器 V1.0
清洗、去重、标准化收集的信息

核心功能：
1. 文本清洗（去除噪音）
2. 内容去重（相似度检测）
3. 格式标准化
4. 质量评分
"""

import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
import string

@dataclass
class CleanedContent:
    """清洗后的内容"""
    original_text: str
    cleaned_text: str
    content_hash: str
    title: str = ""
    url: str = ""
    quality_score: float = 0.0  # 0-100
    issues: List[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.metadata is None:
            self.metadata = {}

class InfoCleaner:
    """
    信息清洗与去重器
    确保信息质量和唯一性
    """
    
    # 广告/噪音关键词
    AD_KEYWORDS = [
        "广告", "赞助", "推广", "AD", "Sponsored", "Advertisement",
        "点击这里", "立即购买", "限时优惠", "免费试用",
        "相关推荐", "猜你喜欢", "热门文章"
    ]
    
    # 低质量标记
    LOW_QUALITY_MARKERS = [
        "本文仅供参考", "免责声明", "版权声明",
        "转载请注明出处", "责任编辑", "免责声明"
    ]
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.dedup_db = self.workspace / "cache" / "dedup_hashes.json"
        self.dedup_db.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载已处理的hash
        self.processed_hashes = self._load_hash_db()
        
        # 统计
        self.stats = {
            "total_processed": 0,
            "cleaned": 0,
            "duplicates": 0,
            "low_quality": 0,
            "issues_found": 0
        }
    
    def _load_hash_db(self) -> Set[str]:
        """加载已处理的hash数据库"""
        if self.dedup_db.exists():
            with open(self.dedup_db, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        return set()
    
    def _save_hash_db(self):
        """保存hash数据库"""
        with open(self.dedup_db, 'w', encoding='utf-8') as f:
            json.dump(list(self.processed_hashes), f, ensure_ascii=False)
    
    def clean(self, 
              text: str,
              title: str = "",
              url: str = "",
              remove_ads: bool = True,
              normalize: bool = True,
              check_duplicate: bool = True) -> CleanedContent:
        """
        清洗单条内容
        
        Args:
            text: 原始文本
            title: 标题
            url: 来源URL
            remove_ads: 是否去除广告
            normalize: 是否标准化
            check_duplicate: 是否检查重复
        
        Returns:
            清洗后的内容对象
        """
        self.stats["total_processed"] += 1
        
        issues = []
        cleaned = text
        
        # 1. 基础清洗
        cleaned = self._basic_clean(cleaned)
        
        # 2. 去除广告和噪音
        if remove_ads:
            cleaned, ad_issues = self._remove_ads(cleaned)
            issues.extend(ad_issues)
        
        # 3. 标准化
        if normalize:
            cleaned = self._normalize(cleaned)
        
        # 4. 计算hash
        content_hash = self._compute_hash(cleaned)
        
        # 5. 检查重复
        is_duplicate = False
        if check_duplicate and content_hash in self.processed_hashes:
            is_duplicate = True
            self.stats["duplicates"] += 1
            issues.append("疑似重复内容")
        else:
            self.processed_hashes.add(content_hash)
        
        # 6. 质量评分
        quality_score, quality_issues = self._assess_quality(cleaned, title)
        issues.extend(quality_issues)
        
        if quality_score < 50:
            self.stats["low_quality"] += 1
        
        # 7. 保存hash
        self._save_hash_db()
        
        self.stats["cleaned"] += 1
        self.stats["issues_found"] += len(issues)
        
        return CleanedContent(
            original_text=text,
            cleaned_text=cleaned,
            content_hash=content_hash,
            title=title,
            url=url,
            quality_score=quality_score,
            issues=issues,
            metadata={
                "is_duplicate": is_duplicate,
                "original_length": len(text),
                "cleaned_length": len(cleaned),
                "compression_ratio": len(cleaned) / max(len(text), 1),
                "processed_at": datetime.now().isoformat()
            }
        )
    
    def batch_clean(self, 
                    contents: List[Dict],
                    remove_duplicates: bool = True) -> List[CleanedContent]:
        """
        批量清洗内容
        
        Args:
            contents: 内容列表，每项包含text/title/url
            remove_duplicates: 是否去除重复
        
        Returns:
            清洗后的内容列表
        """
        print(f"\n🧹 开始批量清洗 {len(contents)} 条内容...")
        
        results = []
        duplicates_removed = 0
        
        for i, item in enumerate(contents, 1):
            print(f"   处理 [{i}/{len(contents)}]...", end="\r")
            
            cleaned = self.clean(
                text=item.get("text", ""),
                title=item.get("title", ""),
                url=item.get("url", ""),
                check_duplicate=remove_duplicates
            )
            
            # 如果要去重且是重复内容，则跳过
            if remove_duplicates and "疑似重复内容" in cleaned.issues:
                duplicates_removed += 1
                continue
            
            results.append(cleaned)
        
        print(f"\n✅ 清洗完成: {len(results)} 条有效内容 (去除 {duplicates_removed} 条重复)")
        
        return results
    
    def _basic_clean(self, text: str) -> str:
        """基础清洗"""
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        # 去除特殊字符（保留基本标点）
        # text = re.sub(r'[^\w\s' + re.escape(string.punctuation) + ']', '', text)
        
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 去除URL（保留文本）
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 去除多余换行
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def _remove_ads(self, text: str) -> Tuple[str, List[str]]:
        """去除广告和噪音"""
        issues = []
        
        # 去除包含广告关键词的句子
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            is_ad = False
            
            for keyword in self.AD_KEYWORDS:
                if keyword in line_stripped:
                    is_ad = True
                    issues.append(f"检测到广告关键词: {keyword}")
                    break
            
            if not is_ad and len(line_stripped) > 10:  # 保留有一定长度的内容
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines), issues
    
    def _normalize(self, text: str) -> str:
        """标准化文本"""
        # 统一中英文标点
        text = text.replace('，', ',').replace('。', '.').replace('"', '"').replace('"', '"')
        text = text.replace('\'', ''\'').replace('\'', '\'').replace('：', ':').replace('；', ';')
        
        # 统一数字格式
        text = re.sub(r'(\d),(\d)', r'\1\2', text)  # 去除千分位逗号
        
        # 统一空格
        text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)  # 去除中文字间空格
        
        return text.strip()
    
    def _compute_hash(self, text: str) -> str:
        """计算内容hash（用于去重）"""
        # 使用 SimHash 或 MinHash 的简化版本
        # 这里使用简单的MD5
        normalized = re.sub(r'\s+', '', text.lower())[:1000]  # 取前1000字符
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _compute_similarity_hash(self, text: str) -> str:
        """计算相似度hash（SimHash简化版）"""
        # 分词（简化版：按字符）
        tokens = list(text.lower())
        
        # 计算每个token的hash
        hashes = [int(hashlib.md5(t.encode()).hexdigest(), 16) for t in tokens]
        
        # 合并
        simhash = 0
        for h in hashes:
            simhash ^= h
        
        return hex(simhash)[2:]
    
    def _assess_quality(self, text: str, title: str) -> Tuple[float, List[str]]:
        """评估内容质量"""
        issues = []
        score = 100.0
        
        # 长度检查
        if len(text) < 100:
            score -= 30
            issues.append("内容过短")
        elif len(text) > 10000:
            score -= 10
            issues.append("内容过长")
        
        # 信息密度
        sentences = text.split('。')
        avg_sentence_length = len(text) / max(len(sentences), 1)
        if avg_sentence_length < 10:
            score -= 20
            issues.append("句子过短，信息密度低")
        
        # 重复内容检查
        words = text.split()
        unique_words = set(words)
        if len(words) > 0 and len(unique_words) / len(words) < 0.5:
            score -= 20
            issues.append("重复内容较多")
        
        # 检查低质量标记
        for marker in self.LOW_QUALITY_MARKERS:
            if marker in text:
                score -= 5
                issues.append(f"包含低质量标记: {marker}")
        
        # 标题相关
        if title and title in text[:len(title)*2]:
            score += 5  # 标题在开头出现，加分
        
        return max(0, score), issues
    
    def find_duplicates(self, contents: List[str], threshold: float = 0.8) -> List[Tuple[int, int, float]]:
        """
        查找相似内容
        
        Args:
            contents: 内容列表
            threshold: 相似度阈值
        
        Returns:
            相似内容对 [(index1, index2, similarity), ...]
        """
        duplicates = []
        
        for i in range(len(contents)):
            for j in range(i+1, len(contents)):
                sim = self._calculate_similarity(contents[i], contents[j])
                if sim >= threshold:
                    duplicates.append((i, j, sim))
        
        return duplicates
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度（Jaccard简化版）"""
        # 分词（按字符）
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def export_cleaned(self, contents: List[CleanedContent], output_file: str):
        """导出清洗后的内容"""
        data = []
        for c in contents:
            data.append({
                "title": c.title,
                "url": c.url,
                "content": c.cleaned_text,
                "quality_score": c.quality_score,
                "content_hash": c.content_hash,
                "metadata": c.metadata
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已导出 {len(data)} 条清洗内容到: {output_file}")
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total_processed": self.stats["total_processed"],
            "cleaned": self.stats["cleaned"],
            "duplicates": self.stats["duplicates"],
            "low_quality": self.stats["low_quality"],
            "issues_found": self.stats["issues_found"],
            "unique_hashes": len(self.processed_hashes),
            "success_rate": f"{(self.stats['cleaned'] - self.stats['low_quality']) / max(self.stats['cleaned'], 1) * 100:.1f}%"
        }

# 使用示例
if __name__ == "__main__":
    cleaner = InfoCleaner()
    
    print("="*70)
    print("测试信息清洗")
    print("="*70)
    
    # 测试数据
    test_contents = [
        {
            "text": """
            这是一篇关于硬科技合伙人匹配的文章。本文仅供参考，转载请注明出处。
            
            广告：点击这里了解更多！限时优惠！
            
            合伙人匹配是硬科技创业的关键环节。
            "",
            "title": "硬科技合伙人匹配指南",
            "url": "https://example.com/article1"
        },
        {
            "text": "这是另一篇完全不同的文章，讨论AI技术在创业中的应用。",
            "title": "AI创业指南",
            "url": "https://example.com/article2"
        },
        {
            "text": """
            这是一篇关于硬科技合伙人匹配的文章。本文仅供参考。
            合伙人匹配是硬科技创业的关键环节。
            """,
            "title": "硬科技合伙人匹配指南（重复版）",
            "url": "https://example.com/article3"
        }
    ]
    
    # 批量清洗
    results = cleaner.batch_clean(test_contents)
    
    print(f"\n结果:")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r.title}")
        print(f"   质量评分: {r.quality_score:.1f}/100")
        print(f"   Hash: {r.content_hash[:16]}...")
        print(f"   问题: {', '.join(r.issues) if r.issues else '无'}")
        print(f"   内容长度: {r.metadata['cleaned_length']}")
    
    print(f"\n统计:")
    print(json.dumps(cleaner.get_stats(), indent=2, ensure_ascii=False))
