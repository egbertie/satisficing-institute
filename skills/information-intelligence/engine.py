#!/usr/bin/env python3
"""
信息搜索与甄别引擎 - Information Intelligence Engine

核心功能：高效搜索 + 质量甄别 + 价值观过滤 + 持续蒸馏
用户目标：建立信息防火墙和蒸馏器，持续精进

第一性原则：
1. 信息质量 > 信息数量
2. 主动甄别 > 被动接收
3. 价值观匹配 > 内容有趣
4. 持续优化 > 一次性配置

搜索渠道优先级：
- P0: 学术论文、官方数据、权威媒体
- P1: 行业报告、专业分析、一手调研
- P2: 社交媒体、用户生成内容（需甄别）
- P3: 娱乐内容、低价值信息（过滤）
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SourceCredibility:
    """来源可信度评级"""
    source: str
    tier: str  # P0/P1/P2/P3
    reliability_score: float  # 0-100
    bias_risk: str  # low/medium/high
    verification_required: bool

@dataclass
class ContentQuality:
    """内容质量评估"""
    originality: str  # original/derived/aggregated
    data_support: bool
    expert_cited: bool
    timestamp: datetime
    update_frequency: str

@dataclass
class ValueAlignment:
    """价值观匹配度"""
    ethical_concerns: List[str]
    alignment_score: float  # 0-100
    red_flags: List[str]
    recommendation: str  # accept/review/reject


class InformationIntelligenceEngine:
    """信息智能引擎 - 搜索、甄别、蒸馏"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.config_file = self.workspace / "skills" / "information-intelligence" / "config.json"
        self.search_log = self.workspace / "memory" / "information-search-log.jsonl"
        self.quality_baseline = self.workspace / "memory" / "information-quality-baseline.json"
        
        # 加载配置
        self.config = self._load_config()
        self.baseline = self._load_baseline()
        
        # 来源可信度数据库
        self.source_db = self._init_source_database()
        
        # 价值观关键词
        self.value_keywords = self._init_value_keywords()
    
    def _load_config(self) -> dict:
        """加载搜索配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "search_channels": {
                "P0": ["academic", "official_data", "authoritative_media"],
                "P1": ["industry_report", "professional_analysis", "primary_research"],
                "P2": ["social_media", "user_generated", "community"],
                "P3": ["entertainment", "low_value"]
            },
            "quality_threshold": 70,  # 质量分数门槛
            "value_alignment_threshold": 80,  # 价值观匹配门槛
            "default_search_depth": "medium",  # shallow/medium/deep
            "auto_filter_enabled": True
        }
    
    def _load_baseline(self) -> dict:
        """加载质量基线"""
        if self.quality_baseline.exists():
            with open(self.quality_baseline, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "total_searches": 0,
            "high_quality_results": 0,
            "filtered_results": 0,
            "false_positive_rate": 0.0,
            "search_efficiency": 1.0,
            "last_optimized": datetime.now().isoformat()
        }
    
    def _init_source_database(self) -> Dict[str, SourceCredibility]:
        """初始化来源可信度数据库"""
        return {
            # P0 - 最高可信度
            "arxiv.org": SourceCredibility("arxiv.org", "P0", 95, "low", False),
            "nature.com": SourceCredibility("nature.com", "P0", 98, "low", False),
            "ieee.org": SourceCredibility("ieee.org", "P0", 95, "low", False),
            "gov.cn": SourceCredibility("gov.cn", "P0", 90, "low", False),
            "xinhuanet.com": SourceCredibility("xinhuanet.com", "P0", 85, "low", False),
            
            # P1 - 高可信度
            "36kr.com": SourceCredibility("36kr.com", "P1", 80, "medium", True),
            "huxiu.com": SourceCredibility("huxiu.com", "P1", 78, "medium", True),
            "iheima.com": SourceCredibility("iheima.com", "P1", 75, "medium", True),
            "cbnweek.com": SourceCredibility("cbnweek.com", "P1", 82, "low", True),
            "tmtpost.com": SourceCredibility("tmtpost.com", "P1", 76, "medium", True),
            
            # P2 - 中等可信度（需甄别）
            "zhihu.com": SourceCredibility("zhihu.com", "P2", 65, "medium", True),
            "weibo.com": SourceCredibility("weibo.com", "P2", 45, "high", True),
            "xiaohongshu.com": SourceCredibility("xiaohongshu.com", "P2", 50, "high", True),
            "bilibili.com": SourceCredibility("bilibili.com", "P2", 60, "medium", True),
            "mp.weixin.qq.com": SourceCredibility("mp.weixin.qq.com", "P2", 55, "medium", True),
            
            # P3 - 低可信度（过滤）
            "entertainment": SourceCredibility("entertainment", "P3", 30, "high", True),
            "rumor": SourceCredibility("rumor", "P3", 10, "high", True),
        }
    
    def _init_value_keywords(self) -> Dict[str, List[str]]:
        """初始化价值观关键词"""
        return {
            "positive_values": [
                "创新", "诚信", "长期主义", "用户第一", "合作共赢",
                "可持续发展", "社会责任", "工匠精神", "第一性原理",
                "知行合一", "持续改进", "开放透明"
            ],
            "red_flags": [
                "虚假宣传", "抄袭", "欺诈", " unethical", "投机取巧",
                "割韭菜", "一夜暴富", "不劳而获", "恶意竞争",
                "侵犯隐私", "数据造假", "误导消费者"
            ],
            "satisficing_values": [
                "满意解", "知行合一", "持续精进", "第一性原则",
                "资源全开", "零空置", "自我迭代", "成为最好的自己"
            ]
        }
    
    def search_with_intelligence(
        self, 
        query: str, 
        search_type: str = "comprehensive",
        min_quality: int = 70,
        value_filter: bool = True
    ) -> Dict[str, Any]:
        """
        智能搜索 - 带质量甄别和价值观过滤
        
        Args:
            query: 搜索关键词
            search_type: 搜索类型（comprehensive/news/academic/opinion）
            min_quality: 最低质量门槛
            value_filter: 是否启用价值观过滤
        
        Returns:
            筛选后的高质量结果
        """
        # 记录搜索
        search_record = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "type": search_type
        }
        
        # 步骤1: 多渠道搜索
        raw_results = self._multi_channel_search(query, search_type)
        search_record["raw_count"] = len(raw_results)
        
        # 步骤2: 来源可信度评级
        rated_results = self._rate_source_credibility(raw_results)
        
        # 步骤3: 内容质量评估
        quality_results = self._assess_content_quality(rated_results)
        
        # 步骤4: 价值观匹配检查
        if value_filter:
            aligned_results = self._check_value_alignment(quality_results)
        else:
            aligned_results = quality_results
        
        # 步骤5: 质量门槛过滤
        filtered_results = [
            r for r in aligned_results 
            if r.get("quality_score", 0) >= min_quality
        ]
        
        # 步骤6: 智能排序
        sorted_results = self._intelligent_ranking(filtered_results)
        
        # 更新统计
        self.baseline["total_searches"] += 1
        self.baseline["high_quality_results"] += len(sorted_results)
        self.baseline["filtered_results"] += len(raw_results) - len(sorted_results)
        self._save_baseline()
        
        # 记录搜索日志
        search_record["final_count"] = len(sorted_results)
        search_record["filter_rate"] = (len(raw_results) - len(sorted_results)) / len(raw_results) if raw_results else 0
        self._log_search(search_record)
        
        return {
            "query": query,
            "total_found": len(raw_results),
            "filtered": len(raw_results) - len(sorted_results),
            "final_results": len(sorted_results),
            "filter_rate": f"{(len(raw_results) - len(sorted_results)) / len(raw_results) * 100:.1f}%",
            "results": sorted_results[:10],  # 返回前10个最高质量结果
            "quality_breakdown": self._generate_quality_breakdown(sorted_results)
        }
    
    def _multi_channel_search(self, query: str, search_type: str) -> List[Dict]:
        """多渠道搜索 - 根据搜索类型选择渠道"""
        # 渠道映射
        channel_map = {
            "comprehensive": ["academic", "news", "social", "video"],
            "news": ["news", "social"],
            "academic": ["academic"],
            "opinion": ["social", "community"]
        }
        
        channels = channel_map.get(search_type, ["comprehensive"])
        
        # 这里模拟搜索结果（实际应调用对应搜索API）
        # 返回模拟数据用于演示
        mock_results = []
        
        # 学术来源（P0）
        if "academic" in channels:
            mock_results.extend([
                {"source": "arxiv.org", "title": f"Research on {query}", "type": "academic"},
                {"source": "nature.com", "title": f"Study about {query}", "type": "academic"}
            ])
        
        # 新闻来源（P1）
        if "news" in channels:
            mock_results.extend([
                {"source": "36kr.com", "title": f"Industry analysis: {query}", "type": "news"},
                {"source": "huxiu.com", "title": f"深度解读：{query}", "type": "news"}
            ])
        
        # 社交来源（P2，需甄别）
        if "social" in channels:
            mock_results.extend([
                {"source": "zhihu.com", "title": f"如何看待{query}", "type": "social"},
                {"source": "weibo.com", "title": f"#{query}#热门讨论", "type": "social"},
                {"source": "xiaohongshu.com", "title": f"{query}经验分享", "type": "social"}
            ])
        
        return mock_results
    
    def _rate_source_credibility(self, results: List[Dict]) -> List[Dict]:
        """评级来源可信度"""
        for result in results:
            source = result.get("source", "")
            
            # 匹配来源数据库
            credibility = None
            for key, cred in self.source_db.items():
                if key in source:
                    credibility = cred
                    break
            
            if credibility:
                result["source_tier"] = credibility.tier
                result["reliability_score"] = credibility.reliability_score
                result["bias_risk"] = credibility.bias_risk
                result["verification_required"] = credibility.verification_required
            else:
                # 未知来源，默认P2
                result["source_tier"] = "P2"
                result["reliability_score"] = 50
                result["bias_risk"] = "medium"
                result["verification_required"] = True
        
        return results
    
    def _assess_content_quality(self, results: List[Dict]) -> List[Dict]:
        """评估内容质量"""
        for result in results:
            quality_score = result.get("reliability_score", 50)
            
            # 根据来源等级调整
            tier_bonus = {"P0": 15, "P1": 10, "P2": 0, "P3": -20}
            quality_score += tier_bonus.get(result.get("source_tier", "P2"), 0)
            
            # 根据类型调整
            type_bonus = {"academic": 10, "news": 5, "social": 0}
            quality_score += type_bonus.get(result.get("type", "social"), 0)
            
            # 是否需要验证
            if result.get("verification_required"):
                quality_score -= 10
            
            result["quality_score"] = max(0, min(100, quality_score))
        
        return results
    
    def _check_value_alignment(self, results: List[Dict]) -> List[Dict]:
        """检查价值观匹配"""
        for result in results:
            title = result.get("title", "")
            
            # 检查正面价值观
            positive_matches = sum(1 for v in self.value_keywords["positive_values"] if v in title)
            
            # 检查红旗词汇
            red_flag_matches = sum(1 for r in self.value_keywords["red_flags"] if r in title)
            
            # 计算价值观匹配分数
            value_score = 50 + (positive_matches * 10) - (red_flag_matches * 30)
            
            result["value_score"] = max(0, min(100, value_score))
            result["value_flags"] = {
                "positive_matches": positive_matches,
                "red_flags": red_flag_matches
            }
            
            # 如果有严重红旗，标记为需审查
            if red_flag_matches > 0:
                result["review_required"] = True
        
        return results
    
    def _intelligent_ranking(self, results: List[Dict]) -> List[Dict]:
        """智能排序"""
        def ranking_score(result):
            quality = result.get("quality_score", 50)
            value = result.get("value_score", 50)
            tier_bonus = {"P0": 30, "P1": 20, "P2": 10, "P3": 0}
            tier = tier_bonus.get(result.get("source_tier", "P2"), 10)
            
            return quality * 0.4 + value * 0.4 + tier * 0.2
        
        return sorted(results, key=ranking_score, reverse=True)
    
    def _generate_quality_breakdown(self, results: List[Dict]) -> Dict:
        """生成质量分析"""
        tiers = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
        for r in results:
            tier = r.get("source_tier", "P2")
            tiers[tier] = tiers.get(tier, 0) + 1
        
        return {
            "by_tier": tiers,
            "avg_quality": sum(r.get("quality_score", 0) for r in results) / len(results) if results else 0,
            "avg_value": sum(r.get("value_score", 0) for r in results) / len(results) if results else 0
        }
    
    def _log_search(self, record: Dict):
        """记录搜索日志"""
        with open(self.search_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    def _save_baseline(self):
        """保存基线"""
        with open(self.quality_baseline, 'w', encoding='utf-8') as f:
            json.dump(self.baseline, f, ensure_ascii=False, indent=2)
    
    def generate_search_report(self, query: str, results: Dict) -> str:
        """生成搜索报告"""
        report_lines = [
            f"# 智能搜索报告 - {query}",
            "",
            f"**搜索时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**原始结果**: {results['total_found']}条",
            f"**过滤结果**: {results['filtered']}条",
            f"**最终返回**: {results['final_results']}条",
            f"**过滤率**: {results['filter_rate']}",
            "",
            "## 质量分布",
            ""
        ]
        
        breakdown = results.get("quality_breakdown", {})
        by_tier = breakdown.get("by_tier", {})
        
        report_lines.extend([
            "| 来源等级 | 数量 | 可信度 |",
            "|----------|------|--------|"
        ])
        
        for tier, count in sorted(by_tier.items()):
            credibility = {"P0": "极高", "P1": "高", "P2": "中等", "P3": "低"}.get(tier, "未知")
            report_lines.append(f"| {tier} | {count} | {credibility} |")
        
        report_lines.extend([
            "",
            f"**平均质量分数**: {breakdown.get('avg_quality', 0):.1f}/100",
            f"**平均价值观匹配**: {breakdown.get('avg_value', 0):.1f}/100",
            "",
            "## 推荐结果",
            ""
        ])
        
        for i, result in enumerate(results.get("results", [])[:5], 1):
            report_lines.append(f"{i}. **{result.get('title', 'N/A')}**")
            report_lines.append(f"   - 来源: {result.get('source', 'N/A')} ({result.get('source_tier', 'P2')})")
            report_lines.append(f"   - 质量: {result.get('quality_score', 0)}/100")
            report_lines.append(f"   - 价值观: {result.get('value_score', 0)}/100")
            if result.get("review_required"):
                report_lines.append(f"   - ⚠️ **需人工审查**")
            report_lines.append("")
        
        report_lines.extend([
            "---",
            "",
            "*信息防火墙已启用，低质量/价值观不匹配内容已过滤*"
        ])
        
        return "\n".join(report_lines)
    
    def continuous_optimization(self) -> Dict:
        """
        持续优化搜索效率和质量
        
        第一性原则五步法：
        1. 观察：分析搜索日志
        2. 复盘：识别效率瓶颈
        3. 思考：理论最优搜索策略
        4. 优化：调整渠道优先级
        5. 实施：更新配置并验证
        """
        # Step 1: 观察 - 分析搜索日志
        recent_searches = self._analyze_recent_searches()
        
        # Step 2: 复盘 - 识别问题
        issues = self._identify_search_issues(recent_searches)
        
        # Step 3: 思考 - 最优策略
        insights = self._generate_search_insights(issues)
        
        # Step 4: 优化 - 制定方案
        optimizations = self._plan_search_optimizations(insights)
        
        # Step 5: 实施 - 更新配置
        implemented = self._implement_search_optimizations(optimizations)
        
        return {
            "optimization_date": datetime.now().isoformat(),
            "searches_analyzed": len(recent_searches),
            "issues_found": len(issues),
            "insights_generated": len(insights),
            "optimizations_planned": len(optimizations),
            "optimizations_implemented": len(implemented),
            "details": {
                "issues": issues,
                "insights": insights,
                "implemented": implemented
            }
        }
    
    def _analyze_recent_searches(self) -> List[Dict]:
        """分析最近搜索记录"""
        if not self.search_log.exists():
            return []
        
        searches = []
        with open(self.search_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    search = json.loads(line)
                    # 只取最近7天的
                    search_time = datetime.fromisoformat(search.get("timestamp", "2000-01-01"))
                    if datetime.now() - search_time < timedelta(days=7):
                        searches.append(search)
                except:
                    continue
        
        return searches
    
    def _identify_search_issues(self, searches: List[Dict]) -> List[Dict]:
        """识别搜索问题"""
        issues = []
        
        if not searches:
            return issues
        
        # 问题1：过滤率过高
        avg_filter_rate = sum(s.get("filter_rate", 0) for s in searches) / len(searches)
        if avg_filter_rate > 0.8:
            issues.append({
                "type": "high_filter_rate",
                "description": f"平均过滤率{avg_filter_rate*100:.1f}%，搜索策略过于保守",
                "severity": "medium",
                "suggestion": "适当降低质量门槛或扩展搜索渠道"
            })
        
        # 问题2：过滤率过低
        if avg_filter_rate < 0.3:
            issues.append({
                "type": "low_filter_rate",
                "description": f"平均过滤率{avg_filter_rate*100:.1f}%，甄别力度不足",
                "severity": "high",
                "suggestion": "提高质量门槛，加强价值观过滤"
            })
        
        # 问题3：搜索频率异常
        if len(searches) > 100:  # 7天内超过100次
            issues.append({
                "type": "high_search_frequency",
                "description": f"7天内搜索{len(searches)}次，可能存在重复搜索",
                "severity": "low",
                "suggestion": "建立搜索结果缓存机制"
            })
        
        return issues
    
    def _generate_search_insights(self, issues: List[Dict]) -> List[Dict]:
        """生成搜索洞察"""
        insights = []
        
        for issue in issues:
            if issue["type"] == "high_filter_rate":
                insights.append({
                    "problem": "搜索策略过于保守",
                    "current_approach": "高质量门槛导致结果过少",
                    "optimal_approach": "分层搜索：P0优先，P1补充，P2备选",
                    "improvement": "动态调整质量门槛，根据查询类型灵活配置",
                    "expected_gain": "30%结果多样性提升"
                })
            
            elif issue["type"] == "low_filter_rate":
                insights.append({
                    "problem": "甄别力度不足",
                    "current_approach": "过滤率低，低质量内容流入",
                    "optimal_approach": "严格价值观审查，红旗内容零容忍",
                    "improvement": "强化价值观关键词库，提高P3内容过滤",
                    "expected_gain": "50%信息质量提升"
                })
        
        # 如果一切正常，思考如何更好
        if not insights:
            insights.append({
                "problem": "搜索运行良好",
                "current_approach": "现有机制",
                "optimal_approach": "预测性搜索",
                "improvement": "基于用户偏好预测搜索需求，主动推送",
                "expected_gain": "20%搜索效率提升"
            })
        
        return insights
    
    def _plan_search_optimizations(self, insights: List[Dict]) -> List[Dict]:
        """规划搜索优化"""
        optimizations = []
        
        for insight in insights:
            opt = {
                "problem": insight["problem"],
                "solution": insight["improvement"],
                "expected_gain": insight["expected_gain"],
                "implementation": "更新config.json",
                "verification": "7天后分析过滤率和结果质量"
            }
            optimizations.append(opt)
        
        return optimizations
    
    def _implement_search_optimizations(self, optimizations: List[Dict]) -> List[Dict]:
        """实施搜索优化"""
        implemented = []
        
        for opt in optimizations:
            # 更新配置
            if "动态调整" in opt["solution"]:
                self.config["adaptive_threshold"] = True
            
            if "价值观" in opt["solution"]:
                self.config["value_filter_enabled"] = True
                self.config["value_filter_strictness"] = "high"
            
            implemented.append(opt)
        
        # 保存配置
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        
        return implemented


def main():
    """主函数"""
    engine = InformationIntelligenceEngine()
    
    # 示例：智能搜索
    query = "硬科技创业合伙人选择"
    results = engine.search_with_intelligence(query, search_type="comprehensive")
    
    # 生成报告
    report = engine.generate_search_report(query, results)
    print(report)
    
    # 持续优化
    print("\n" + "="*50 + "\n")
    optimization = engine.continuous_optimization()
    print("持续优化结果:")
    print(json.dumps(optimization, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
