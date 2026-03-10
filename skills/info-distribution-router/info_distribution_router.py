#!/usr/bin/env python3
"""
信息分发路由器 V1.0
管理信息在33位小伙伴之间的高效流通和使用

核心职责:
1. 信息分级和权限控制
2. 智能路由到需要的人
3. 确保信息及时到达
4. 追踪信息使用效果
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

class InfoLevel(Enum):
    """信息分级"""
    PUBLIC = "C"      # 公开信息，可外部分享
    INTERNAL = "B"    # 内部信息，全员可见
    SENSITIVE = "A"   # 敏感信息，L3及以上可见
    STRATEGIC = "S"   # 战略信息，L4-L5可见


@dataclass
class InfoItem:
    """信息项"""
    item_id: str
    title: str
    content: str
    source: str
    credibility: str
    level: InfoLevel
    topics: List[str]
    related_experts: List[str]  # 相关的AI小伙伴ID
    created_at: str
    expires_at: str = None  # 信息过期时间


@dataclass
class RouteRule:
    """路由规则"""
    rule_id: str
    name: str
    condition: Dict  # 触发条件
    target_groups: List[str]  # 目标组
    delivery_method: str  # 推送方式
    priority: int  # 优先级


class InfoDistributionRouter:
    """
    信息分发路由器
    确保信息在33位小伙伴之间高效流通
    """
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.data_dir = self.workspace / "data" / "info_distribution"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 33位小伙伴的权限配置
        self.access_matrix = self._init_access_matrix()
        
        # 路由规则
        self.route_rules = self._init_route_rules()
        
        # 分发记录
        self.distribution_log = []
    
    def _init_access_matrix(self) -> Dict:
        """初始化访问权限矩阵"""
        return {
            # 信息战略组 - 最高信息敏感度
            "AI-001": {"level": "L2", "access": ["C", "B", "A"], "topics": ["趋势", "技术", "市场"]},
            "AI-002": {"level": "L2", "access": ["C", "B", "A"], "topics": ["竞争", "情报", "分析"]},
            "AI-003": {"level": "L2", "access": ["C", "B", "A"], "topics": ["数据", "历史", "模式"]},
            "AI-004": {"level": "L2", "access": ["C", "B", "A"], "topics": ["技术", "前沿", "研发"]},
            "AI-005": {"level": "L2", "access": ["C", "B", "A"], "topics": ["政策", "法规", "政府"]},
            
            # 知识工程组
            "AI-006": {"level": "L2", "access": ["C", "B", "A"], "topics": ["知识", "图谱", "实体"]},
            "AI-007": {"level": "L2", "access": ["C", "B", "A"], "topics": ["检索", "文档", "组织"]},
            "AI-008": {"level": "L3", "access": ["C", "B", "A"], "topics": ["融合", "对齐", "整合"]},
            "AI-009": {"level": "L2", "access": ["C", "B", "A"], "topics": ["洞察", "提炼", "摘要"]},
            "AI-010": {"level": "L2", "access": ["C", "B"], "topics": ["可视化", "图表", "展示"]},
            
            # 决策科学组 - 高权限
            "AI-011": {"level": "L3", "access": ["C", "B", "A", "S"], "topics": ["决策", "分析", "模型"]},
            "AI-012": {"level": "L3", "access": ["C", "B", "A", "S"], "topics": ["风险", "评估", "预警"]},
            "AI-013": {"level": "L3", "access": ["C", "B", "A", "S"], "topics": ["评估", "对比", "排序"]},
            "AI-014": {"level": "L4", "access": ["C", "B", "A", "S"], "topics": ["预测", "趋势", "未来"]},
            "AI-015": {"level": "L4", "access": ["C", "B", "A", "S"], "topics": ["压力测试", "极端场景"]},
            
            # 内容生产组
            "AI-016": {"level": "L3", "access": ["C", "B", "A"], "topics": ["故事", "叙事", "内容"]},
            "AI-017": {"level": "L3", "access": ["C", "B"], "topics": ["演示", "PPT", "视觉"]},
            "AI-018": {"level": "L3", "access": ["C", "B", "A"], "topics": ["报告", "研究", "分析"]},
            "AI-019": {"level": "L2", "access": ["C", "B"], "topics": ["沟通", "话术", "对话"]},
            "AI-020": {"level": "L3", "access": ["C", "B", "A"], "topics": ["翻译", "本地化", "多语言"]},
            
            # 系统运营组
            "AI-021": {"level": "L3", "access": ["C", "B", "A", "S"], "topics": ["系统", "监控", "运维"]},
            "AI-022": {"level": "L3", "access": ["C", "B", "A"], "topics": ["日志", "分析", "排查"]},
            "AI-023": {"level": "L4", "access": ["C", "B", "A", "S"], "topics": ["性能", "优化", "调优"]},
            "AI-024": {"level": "L3", "access": ["C", "B", "A", "S"], "topics": ["备份", "数据", "安全"]},
            "AI-025": {"level": "L4", "access": ["C", "B", "A", "S"], "topics": ["安全", "审计", "合规"]},
            
            # 客户服务组
            "AI-026": {"level": "L4", "access": ["C", "B", "A"], "topics": ["客户", "服务", "成功"]},
            "AI-027": {"level": "L4", "access": ["C", "B", "A", "S"], "topics": ["服务", "网关", "API"]},
            "AI-028": {"level": "L3", "access": ["C", "B"], "topics": ["反馈", "分析", "改进"]},
            "AI-029": {"level": "L4", "access": ["C", "B", "A"], "topics": ["沟通", "渠道", "协调"]},
            
            # 架构统筹组 - 最高权限
            "AI-030": {"level": "L4", "access": ["C", "B", "A", "S"], "topics": ["代码", "质量", "审查"]},
            "AI-031": {"level": "L5", "access": ["C", "B", "A", "S"], "topics": ["架构", "设计", "标准"]},
            "AI-032": {"level": "L4", "access": ["C", "B", "A", "S"], "topics": ["版本", "发布", "管理"]},
            "AI-033": {"level": "L5", "access": ["C", "B", "A", "S"], "topics": ["战略", "统筹", "全局"]},
        }
    
    def _init_route_rules(self) -> List[RouteRule]:
        """初始化路由规则"""
        return [
            # 实时紧急推送
            RouteRule("R-001", "战略级紧急推送",
                     {"level": "S", "priority": "urgent"},
                     ["架构统筹组", "决策科学组"],
                     "immediate", 1),
            
            # 日常信息汇总
            RouteRule("R-002", "每日信息汇总",
                     {"frequency": "daily"},
                     ["全体成员"],
                     "daily_digest", 3),
            
            # 主题相关推送
            RouteRule("R-003", "趋势相关推送",
                     {"topics": ["趋势", "技术"]},
                     ["信息战略组", "决策科学组"],
                     "push", 2),
            
            RouteRule("R-004", "客户相关推送",
                     {"topics": ["客户", "反馈"]},
                     ["客户服务组", "内容生产组"],
                     "push", 2),
            
            # 个性化推荐
            RouteRule("R-005", "个性化信息推荐",
                     {"method": "recommendation"},
                     ["基于个人兴趣"],
                     "recommendation", 4),
        ]
    
    def route_info(self, info_item: InfoItem) -> Dict:
        """
        路由信息到目标用户
        
        Args:
            info_item: 信息项
        
        Returns:
            路由结果
        """
        print(f"\n📨 路由信息: {info_item.title}")
        print(f"   级别: {info_item.level.value} | 主题: {info_item.topics}")
        
        # 确定目标接收者
        targets = self._determine_targets(info_item)
        
        # 过滤权限
        authorized_targets = self._filter_by_permission(targets, info_item.level)
        
        # 选择分发方式
        delivery_method = self._select_delivery_method(info_item)
        
        # 执行分发
        distribution_result = self._distribute(info_item, authorized_targets, delivery_method)
        
        # 记录日志
        self._log_distribution(info_item, distribution_result)
        
        return distribution_result
    
    def _determine_targets(self, info_item: InfoItem) -> List[str]:
        """确定目标接收者"""
        targets = []
        
        # 基于主题匹配
        for expert_id, config in self.access_matrix.items():
            if any(topic in config["topics"] for topic in info_item.topics):
                targets.append(expert_id)
        
        # 基于显式指定
        targets.extend(info_item.related_experts)
        
        # 去重
        return list(set(targets))
    
    def _filter_by_permission(self, targets: List[str], level: InfoLevel) -> List[str]:
        """根据权限过滤"""
        authorized = []
        
        for expert_id in targets:
            config = self.access_matrix.get(expert_id, {})
            allowed_levels = config.get("access", ["C"])
            
            if level.value in allowed_levels:
                authorized.append(expert_id)
        
        return authorized
    
    def _select_delivery_method(self, info_item: InfoItem) -> str:
        """选择分发方式"""
        if info_item.level == InfoLevel.STRATEGIC:
            return "immediate"  # 立即推送
        elif info_item.level == InfoLevel.SENSITIVE:
            return "push"  # 主动推送
        else:
            return "digest"  # 汇总推送
    
    def _distribute(self, info_item: InfoItem, targets: List[str], method: str) -> Dict:
        """执行分发"""
        print(f"   目标: {len(targets)} 位小伙伴")
        print(f"   方式: {method}")
        
        # 模拟分发
        return {
            "info_id": info_item.item_id,
            "targets": targets,
            "method": method,
            "delivered_at": datetime.now().isoformat(),
            "status": "delivered"
        }
    
    def _log_distribution(self, info_item: InfoItem, result: Dict):
        """记录分发日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "info_id": info_item.item_id,
            "title": info_item.title,
            "level": info_item.level.value,
            "targets_count": len(result["targets"]),
            "method": result["method"]
        }
        self.distribution_log.append(log_entry)
    
    def generate_routing_report(self) -> str:
        """生成分发路由报告"""
        report = f"""# 信息分发路由报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 👥 权限矩阵概览

| 级别 | 人数 | 可访问信息级 |
|------|------|-------------|
| L5 | 2人 | S, A, B, C |
| L4 | 6人 | S, A, B, C |
| L3 | 12人 | A, B, C |
| L2 | 10人 | B, C (部分A) |
| L1 | 3人 | B, C |

---

## 📊 今日分发统计

- 总分发次数: {len(self.distribution_log)}
- S级信息: {sum(1 for l in self.distribution_log if l['level'] == 'S')} 条
- A级信息: {sum(1 for l in self.distribution_log if l['level'] == 'A')} 条
- B级信息: {sum(1 for l in self.distribution_log if l['level'] == 'B')} 条
- C级信息: {sum(1 for l in self.distribution_log if l['level'] == 'C')} 条

---

## 🔀 路由规则

| 规则ID | 名称 | 目标组 | 方式 |
|--------|------|--------|------|
"""
        
        for rule in self.route_rules:
            report += f"| {rule.rule_id} | {rule.name} | {', '.join(rule.target_groups)} | {rule.delivery_method} |\n"
        
        report += """
---

*由信息分发路由器自动生成*
"""
        
        return report


# 使用示例
if __name__ == "__main__":
    router = InfoDistributionRouter()
    
    # 测试信息项
    test_info = InfoItem(
        item_id="INFO-001",
        title="AI芯片赛道新融资案例",
        content="某AI芯片公司完成5亿元融资...",
        source="TechCrunch",
        credibility="high",
        level=InfoLevel.A,
        topics=["趋势", "技术", "融资"],
        related_experts=["AI-001", "AI-004"],
        created_at=datetime.now().isoformat()
    )
    
    # 路由信息
    result = router.route_info(test_info)
    print(f"\n路由结果: {result}")
    
    # 生成报告
    print("\n" + "="*70)
    print(router.generate_routing_report()[:500] + "...")
