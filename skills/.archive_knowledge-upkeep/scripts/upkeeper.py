#!/usr/bin/env python3
"""
knowledge-upkeep 执行脚本
知识维护者 - 专家档案标注+记忆维护周期
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data" / "knowledge-upkeep"
LOG_FILE = Path("/tmp/knowledge-upkeep.log")

# 确保数据目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

class KnowledgeUpkeep:
    """知识维护者"""
    
    def __init__(self):
        self.experts_file = DATA_DIR / "experts.json"
        self.knowledge_file = DATA_DIR / "knowledge.json"
        self.maintenance_log_file = DATA_DIR / "maintenance_log.json"
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        self.experts = self._load_json(self.experts_file, [])
        self.knowledge = self._load_json(self.knowledge_file, [])
        self.maintenance_log = self._load_json(self.maintenance_log_file, [])
    
    def _load_json(self, path, default):
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return default
    
    def save_data(self):
        """保存数据"""
        with open(self.experts_file, 'w') as f:
            json.dump(self.experts, f, indent=2)
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
        with open(self.maintenance_log_file, 'w') as f:
            json.dump(self.maintenance_log, f, indent=2)
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry + "\n")
    
    # ========== 专家档案标注 ==========
    
    def update_expert_profiles(self):
        """更新专家档案"""
        self.log("=== 更新专家档案 ===")
        
        updated = 0
        
        for expert in self.experts:
            last_updated = datetime.fromisoformat(expert.get("last_updated", "2020-01-01"))
            
            # 检查是否需要更新（超过30天未更新）
            if datetime.now() - last_updated > timedelta(days=30):
                self.log(f"🔄 更新专家档案: {expert.get('name', expert['id'])}")
                self._update_single_expert(expert)
                updated += 1
        
        self.log(f"✅ 更新了 {updated} 个专家档案")
        return updated
    
    def _update_single_expert(self, expert):
        """更新单个专家档案"""
        # 分析项目历史，更新能力标签
        new_capabilities = self._analyze_project_contributions(expert)
        
        # 更新能力标签
        for cap in new_capabilities:
            existing = next((c for c in expert.get("capabilities", []) 
                           if c["name"] == cap["name"]), None)
            if existing:
                existing["level"] = cap["level"]
                existing["updated_at"] = datetime.now().isoformat()
            else:
                expert.setdefault("capabilities", []).append({
                    **cap,
                    "added_at": datetime.now().isoformat()
                })
        
        expert["last_updated"] = datetime.now().isoformat()
        expert["version"] = expert.get("version", 0) + 1
    
    def _analyze_project_contributions(self, expert):
        """分析项目贡献，提取能力"""
        # 实际应查询项目系统
        return []
    
    def generate_expert_recommendations(self):
        """生成专家推荐"""
        self.log("=== 生成专家推荐 ===")
        
        recommendations = []
        
        # 模拟根据当前需求推荐专家
        current_needs = self._get_current_skill_needs()
        
        for need in current_needs:
            matching_experts = self._find_matching_experts(need)
            if matching_experts:
                recommendations.append({
                    "need": need,
                    "recommended_experts": matching_experts[:3]  # 推荐前3名
                })
        
        self.log(f"✅ 生成了 {len(recommendations)} 条专家推荐")
        return recommendations
    
    def _get_current_skill_needs(self):
        """获取当前技能需求"""
        # 实际应从项目系统获取
        return [
            {"skill": "Python", "level": "expert", "domain": "backend"},
            {"skill": "Machine Learning", "level": "advanced", "domain": "ai"}
        ]
    
    def _find_matching_experts(self, need):
        """寻找匹配专家"""
        matches = []
        
        for expert in self.experts:
            score = self._calculate_match_score(expert, need)
            if score > 0:
                matches.append({
                    "expert_id": expert["id"],
                    "name": expert.get("name"),
                    "score": score,
                    "availability": expert.get("availability", "unknown")
                })
        
        # 按匹配度排序
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches
    
    def _calculate_match_score(self, expert, need):
        """计算匹配分数"""
        score = 0
        
        for cap in expert.get("capabilities", []):
            if cap["name"].lower() == need["skill"].lower():
                level_scores = {"novice": 1, "intermediate": 2, "advanced": 3, "expert": 4}
                required = level_scores.get(need["level"], 2)
                actual = level_scores.get(cap["level"], 1)
                
                if actual >= required:
                    score = actual * 25  # 基础分
                    
                    # 可用性加成
                    if expert.get("availability") == "available":
                        score += 20
                    
                    # 项目经验加成
                    projects = expert.get("projects", [])
                    relevant = [p for p in projects if need["domain"] in p.get("domains", [])]
                    score += len(relevant) * 5
        
        return min(score, 100)  # 最高100分
    
    # ========== 记忆维护周期 ==========
    
    def scan_knowledge_freshness(self):
        """扫描知识时效性"""
        self.log("=== 扫描知识时效性 ===")
        
        outdated = []
        need_update = []
        
        for item in self.knowledge:
            freshness_status = self._check_freshness(item)
            
            if freshness_status == "outdated":
                outdated.append(item)
                self.log(f"📦 知识过期建议归档: {item.get('title', item['id'])}")
            elif freshness_status == "needs_update":
                need_update.append(item)
                self.log(f"🔄 知识需要更新: {item.get('title', item['id'])}")
        
        self.log(f"✅ 发现 {len(need_update)} 项需更新, {len(outdated)} 项建议归档")
        return {"needs_update": len(need_update), "outdated": len(outdated)}
    
    def _check_freshness(self, item):
        """检查知识新鲜度"""
        last_updated = datetime.fromisoformat(item.get("last_updated", "2020-01-01"))
        age = datetime.now() - last_updated
        
        # 根据知识类型定义更新周期
        update_cycles = {
            "strategic": timedelta(days=90),    # 战略知识：季度
            "procedural": timedelta(days=30),   # 流程规范：月度
            "technical": timedelta(days=60),    # 技术文档：双月
            "project": timedelta(days=365),     # 项目文档：年度
            "market": timedelta(days=30)        # 市场信息：月度
        }
        
        knowledge_type = item.get("type", "general")
        cycle = update_cycles.get(knowledge_type, timedelta(days=90))
        
        # 归档期限是更新周期的2倍
        archive_threshold = cycle * 2
        
        if age > archive_threshold:
            return "outdated"
        elif age > cycle:
            return "needs_update"
        else:
            return "fresh"
    
    def send_update_reminders(self):
        """发送更新提醒"""
        self.log("=== 发送更新提醒 ===")
        
        reminders_sent = 0
        
        for item in self.knowledge:
            if self._check_freshness(item) == "needs_update":
                owner = item.get("owner")
                if owner:
                    self._send_reminder(owner, item)
                    reminders_sent += 1
        
        self.log(f"✅ 发送了 {reminders_sent} 条更新提醒")
        return reminders_sent
    
    def _send_reminder(self, owner, item):
        """发送提醒"""
        self.log(f"  📨 提醒 {owner} 更新: {item.get('title', item['id'])}")
        
        # 记录到维护日志
        self.maintenance_log.append({
            "type": "update_reminder",
            "knowledge_id": item["id"],
            "owner": owner,
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        })
    
    def archive_old_knowledge(self):
        """归档旧知识"""
        self.log("=== 归档旧知识 ===")
        
        archived = 0
        
        for item in self.knowledge:
            if self._check_freshness(item) == "outdated":
                # 软归档：标记状态，移至归档区
                item["status"] = "archived"
                item["archived_at"] = datetime.now().isoformat()
                archived += 1
                self.log(f"  📦 已归档: {item.get('title', item['id'])}")
        
        self.log(f"✅ 归档了 {archived} 项知识")
        return archived
    
    def evaluate_knowledge_value(self):
        """评估知识价值"""
        self.log("=== 评估知识价值 ===")
        
        for item in self.knowledge:
            # 计算使用频率
            usage_count = item.get("usage_count", 0)
            
            # 计算反馈评分
            feedback_scores = item.get("feedback_scores", [])
            avg_score = sum(feedback_scores) / len(feedback_scores) if feedback_scores else 0
            
            # 计算价值得分
            value_score = self._calculate_value_score(usage_count, avg_score, item)
            
            item["value_score"] = value_score
            item["value_assessed_at"] = datetime.now().isoformat()
        
        # 识别高价值知识和低价值知识
        high_value = [k for k in self.knowledge if k.get("value_score", 0) > 80]
        low_value = [k for k in self.knowledge if k.get("value_score", 0) < 30]
        
        self.log(f"✅ 高价值知识: {len(high_value)}, 低价值知识: {len(low_value)}")
        return {"high_value": len(high_value), "low_value": len(low_value)}
    
    def _calculate_value_score(self, usage_count, avg_score, item):
        """计算价值分数"""
        # 使用频率分 (0-40)
        usage_score = min(usage_count * 4, 40)
        
        # 反馈评分 (0-30)
        feedback_score = avg_score * 6
        
        # 时效性分 (0-20)
        freshness = self._check_freshness(item)
        freshness_scores = {"fresh": 20, "needs_update": 10, "outdated": 0}
        freshness_score = freshness_scores.get(freshness, 10)
        
        # 完整性分 (0-10)
        completeness_score = 10 if item.get("is_complete") else 5
        
        return usage_score + feedback_score + freshness_score + completeness_score
    
    def identify_knowledge_gaps(self):
        """识别知识缺口"""
        self.log("=== 识别知识缺口 ===")
        
        gaps = []
        
        # 分析搜索记录，找出高频但无结果的关键词
        search_keywords = self._get_search_keywords()
        
        for keyword in search_keywords:
            matching_knowledge = [k for k in self.knowledge 
                                  if keyword.lower() in k.get("title", "").lower() 
                                  or keyword.lower() in k.get("content", "").lower()]
            
            if not matching_knowledge:
                gaps.append({
                    "keyword": keyword,
                    "search_count": search_keywords[keyword],
                    "suggested_action": "create_knowledge"
                })
        
        self.log(f"✅ 识别了 {len(gaps)} 个知识缺口")
        for gap in gaps[:5]:  # 只显示前5个
            self.log(f"  🔍 缺口: {gap['keyword']} (搜索 {gap['search_count']} 次)")
        
        return gaps
    
    def _get_search_keywords(self):
        """获取搜索关键词"""
        # 实际应从搜索日志获取
        return {
            "deployment guide": 15,
            "API reference": 23,
            "troubleshooting": 18,
            "best practices": 12
        }
    
    # ========== 主运行 ==========
    
    def run(self, mode="all"):
        """运行检查"""
        self.log(f"\n{'='*50}")
        self.log(f"Knowledge Upkeep 启动 - 模式: {mode}")
        self.log(f"{'='*50}")
        
        results = {}
        
        if mode in ["all", "expert"]:
            results["experts_updated"] = self.update_expert_profiles()
            results["recommendations"] = self.generate_expert_recommendations()
        
        if mode in ["all", "knowledge"]:
            freshness = self.scan_knowledge_freshness()
            results.update(freshness)
            results["reminders_sent"] = self.send_update_reminders()
            results["archived"] = self.archive_old_knowledge()
            results["value_assessment"] = self.evaluate_knowledge_value()
            results["knowledge_gaps"] = self.identify_knowledge_gaps()
        
        if mode == "maintenance":
            results["reminders_sent"] = self.send_update_reminders()
            results["archived"] = self.archive_old_knowledge()
        
        self.save_data()
        
        self.log(f"\n{'='*50}")
        self.log(f"检查完成: {results}")
        self.log(f"{'='*50}\n")
        
        return results


def main():
    """主函数"""
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    upkeep = KnowledgeUpkeep()
    results = upkeep.run(mode)
    
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
