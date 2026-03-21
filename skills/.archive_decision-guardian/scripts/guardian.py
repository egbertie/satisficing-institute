#!/usr/bin/env python3
"""
decision-guardian 执行脚本
决策守护者 - 蓝军机制+预审机制+冲突升级规则
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data" / "decision-guardian"
LOG_FILE = Path("/tmp/decision-guardian.log")

# 确保数据目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

class DecisionGuardian:
    """决策守护者"""
    
    def __init__(self):
        self.redteam_file = DATA_DIR / "redteam_reviews.json"
        self.prereview_file = DATA_DIR / "pre_reviews.json"
        self.escalation_file = DATA_DIR / "escalations.json"
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        self.redteam_reviews = self._load_json(self.redteam_file, [])
        self.pre_reviews = self._load_json(self.prereview_file, [])
        self.escalations = self._load_json(self.escalation_file, [])
    
    def _load_json(self, path, default):
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return default
    
    def save_data(self):
        """保存数据"""
        with open(self.redteam_file, 'w') as f:
            json.dump(self.redteam_reviews, f, indent=2)
        with open(self.prereview_file, 'w') as f:
            json.dump(self.pre_reviews, f, indent=2)
        with open(self.escalation_file, 'w') as f:
            json.dump(self.escalations, f, indent=2)
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry + "\n")
    
    # ========== 蓝军机制 ==========
    
    def check_redteam_triggers(self):
        """检查蓝军启动条件"""
        self.log("=== 检查蓝军启动条件 ===")
        
        # 检查待启动蓝军的决策
        pending_decisions = self._get_pending_decisions()
        
        triggered = []
        for decision in pending_decisions:
            if decision.get("level") in ["S", "A"]:
                self.log(f"🎯 S/A级决策触发蓝军审查: {decision['id']}")
                self._initiate_redteam_review(decision)
                triggered.append(decision['id'])
        
        return len(triggered)
    
    def conduct_redteam_review(self, decision_id=None):
        """执行蓝军审查"""
        self.log("=== 执行蓝军审查 ===")
        
        # 获取待审查的决策
        if decision_id:
            review = self._get_review_by_decision(decision_id)
        else:
            review = self._get_next_pending_review()
        
        if not review:
            self.log("✅ 无待审查决策")
            return 0
        
        self.log(f"🔍 审查决策: {review['decision_id']}")
        
        # 执行审查清单
        vulnerabilities = self._run_review_checklist(review)
        
        # 生成报告
        report = self._generate_redteam_report(review, vulnerabilities)
        
        self.log(f"📊 发现 {len(vulnerabilities)} 个漏洞")
        for v in vulnerabilities:
            self.log(f"  [{v['severity'].upper()}] {v['category']}: {v['description'][:50]}")
        
        return len(vulnerabilities)
    
    def _get_pending_decisions(self):
        """获取待决策列表"""
        # 实际应从决策系统获取
        return []
    
    def _initiate_redteam_review(self, decision):
        """启动蓝军审查"""
        review = {
            "id": f"rt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "decision_id": decision["id"],
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "vulnerabilities": [],
            "verdict": None
        }
        self.redteam_reviews.append(review)
        self.log(f"  ✅ 蓝军审查已启动: {review['id']}")
    
    def _get_review_by_decision(self, decision_id):
        """根据决策ID获取审查"""
        for review in self.redteam_reviews:
            if review["decision_id"] == decision_id and review["status"] == "in_progress":
                return review
        return None
    
    def _get_next_pending_review(self):
        """获取下一个待审查"""
        for review in self.redteam_reviews:
            if review["status"] == "in_progress":
                return review
        return None
    
    def _run_review_checklist(self, review):
        """运行审查清单"""
        vulnerabilities = []
        
        # 逻辑层面检查
        logic_checks = [
            {"check": "assumption_validation", "desc": "关键假设是否验证"},
            {"check": "causal_fallacy", "desc": "是否存在因果混淆"},
            {"check": "survivorship_bias", "desc": "是否考虑沉默数据"}
        ]
        
        for check in logic_checks:
            # 模拟检查（实际应分析决策内容）
            if self._simulate_check_failure():
                vulnerabilities.append({
                    "category": "logic",
                    "severity": "medium",
                    "description": check["desc"],
                    "check": check["check"]
                })
        
        # 执行层面检查
        execution_checks = [
            {"check": "resource_sufficiency", "desc": "资源是否充足"},
            {"check": "capability_match", "desc": "能力是否匹配"},
            {"check": "timeline_feasibility", "desc": "时间是否合理"}
        ]
        
        for check in execution_checks:
            if self._simulate_check_failure():
                vulnerabilities.append({
                    "category": "execution",
                    "severity": "high",
                    "description": check["desc"],
                    "check": check["check"]
                })
        
        return vulnerabilities
    
    def _simulate_check_failure(self):
        """模拟检查失败（实际应真实检查）"""
        import random
        return random.random() < 0.1  # 10%概率发现问题
    
    def _generate_redteam_report(self, review, vulnerabilities):
        """生成蓝军报告"""
        report = {
            "review_id": review["id"],
            "generated_at": datetime.now().isoformat(),
            "vulnerabilities": vulnerabilities,
            "overall_risk": self._calculate_overall_risk(vulnerabilities),
            "recommendation": self._generate_recommendation(vulnerabilities)
        }
        review["vulnerabilities"] = vulnerabilities
        review["report"] = report
        return report
    
    def _calculate_overall_risk(self, vulnerabilities):
        """计算整体风险"""
        if not vulnerabilities:
            return "low"
        
        severities = [v["severity"] for v in vulnerabilities]
        if "high" in severities:
            return "high"
        elif "medium" in severities:
            return "medium"
        return "low"
    
    def _generate_recommendation(self, vulnerabilities):
        """生成建议"""
        if not vulnerabilities:
            return "pass"
        
        high_count = sum(1 for v in vulnerabilities if v["severity"] == "high")
        if high_count > 0:
            return "conditional_pass"
        return "pass_with_suggestions"
    
    # ========== 预审机制 ==========
    
    def check_pre_review_triggers(self):
        """检查预审触发条件"""
        self.log("=== 检查预审触发条件 ===")
        
        pending_proposals = self._get_pending_proposals()
        
        triggered = []
        for proposal in pending_proposals:
            if self._needs_pre_review(proposal):
                self.log(f"📋 提案触发预审: {proposal['id']}")
                self._initiate_pre_review(proposal)
                triggered.append(proposal['id'])
        
        return len(triggered)
    
    def conduct_pre_review(self, proposal_id=None):
        """执行预审"""
        self.log("=== 执行预审 ===")
        
        if proposal_id:
            review = self._get_prereview_by_proposal(proposal_id)
        else:
            review = self._get_next_pending_prereview()
        
        if not review:
            self.log("✅ 无待预审提案")
            return 0
        
        self.log(f"🔍 预审提案: {review['proposal_id']}")
        
        # 并行审查各领域
        findings = self._run_parallel_review(review)
        
        # 生成预审意见
        opinion = self._generate_pre_review_opinion(review, findings)
        
        self.log(f"📊 预审完成: {opinion['verdict']}")
        
        return len(findings)
    
    def _get_pending_proposals(self):
        """获取待审提案"""
        return []
    
    def _needs_pre_review(self, proposal):
        """判断是否需要预审"""
        budget = proposal.get("budget", 0)
        impact = proposal.get("impact_level", "low")
        return budget > 100000 or impact in ["high", "critical"]
    
    def _initiate_pre_review(self, proposal):
        """启动预审"""
        review = {
            "id": f"pr_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "proposal_id": proposal["id"],
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "findings": {}
        }
        self.pre_reviews.append(review)
    
    def _get_prereview_by_proposal(self, proposal_id):
        """根据提案ID获取预审"""
        for review in self.pre_reviews:
            if review["proposal_id"] == proposal_id and review["status"] == "in_progress":
                return review
        return None
    
    def _get_next_pending_prereview(self):
        """获取下一个待预审"""
        for review in self.pre_reviews:
            if review["status"] == "in_progress":
                return review
        return None
    
    def _run_parallel_review(self, review):
        """并行审查"""
        domains = ["technical", "business", "legal", "financial"]
        findings = {}
        
        for domain in domains:
            # 模拟各领域审查
            findings[domain] = self._simulate_domain_review(domain)
        
        review["findings"] = findings
        return findings
    
    def _simulate_domain_review(self, domain):
        """模拟领域审查"""
        import random
        
        issues = []
        if random.random() < 0.3:
            issues.append({
                "severity": random.choice(["minor", "major"]),
                "description": f"{domain}领域发现问题"
            })
        
        return {
            "status": "completed",
            "issues": issues,
            "recommendation": "conditional_pass" if issues else "pass"
        }
    
    def _generate_pre_review_opinion(self, review, findings):
        """生成预审意见"""
        all_issues = []
        for domain, result in findings.items():
            all_issues.extend(result.get("issues", []))
        
        major_issues = [i for i in all_issues if i["severity"] == "major"]
        
        if major_issues:
            verdict = "conditional_pass"
        elif all_issues:
            verdict = "pass_with_suggestions"
        else:
            verdict = "pass"
        
        opinion = {
            "review_id": review["id"],
            "verdict": verdict,
            "findings": findings,
            "generated_at": datetime.now().isoformat()
        }
        
        review["opinion"] = opinion
        review["status"] = "completed"
        
        return opinion
    
    # ========== 冲突升级机制 ==========
    
    def check_pending_conflicts(self):
        """检查待解决冲突"""
        self.log("=== 检查待解决冲突 ===")
        
        escalated = 0
        
        for conflict in self.escalations:
            if conflict["status"] != "resolved":
                if self._should_escalate(conflict):
                    self._escalate_conflict(conflict)
                    escalated += 1
        
        return escalated
    
    def _should_escalate(self, conflict):
        """判断是否应升级"""
        level = conflict.get("level", "L1")
        started_at = datetime.fromisoformat(conflict["started_at"])
        elapsed = datetime.now() - started_at
        
        escalation_time = {
            "L1": timedelta(hours=2),
            "L2": timedelta(hours=4),
            "L3": timedelta(hours=8),
            "L4": timedelta(hours=24)
        }
        
        return elapsed > escalation_time.get(level, timedelta(hours=24))
    
    def _escalate_conflict(self, conflict):
        """升级冲突"""
        escalation_levels = ["L1", "L2", "L3", "L4", "L5"]
        current_idx = escalation_levels.index(conflict["level"])
        
        if current_idx < len(escalation_levels) - 1:
            new_level = escalation_levels[current_idx + 1]
            conflict["level"] = new_level
            conflict["escalated_at"] = datetime.now().isoformat()
            self.log(f"⬆️ 冲突 {conflict['id']} 升级至 {new_level}")
        else:
            self.log(f"🔴 冲突 {conflict['id']} 已达最高级，需最高决策者介入")
    
    # ========== 主运行 ==========
    
    def run(self, mode="all"):
        """运行检查"""
        self.log(f"\n{'='*50}")
        self.log(f"Decision Guardian 启动 - 模式: {mode}")
        self.log(f"{'='*50}")
        
        results = {}
        
        if mode in ["all", "redteam"]:
            results["redteam_triggered"] = self.check_redteam_triggers()
            results["vulnerabilities"] = self.conduct_redteam_review()
        
        if mode in ["all", "prereview"]:
            results["prereview_triggered"] = self.check_pre_review_triggers()
            results["prereview_findings"] = self.conduct_pre_review()
        
        if mode in ["all", "escalation"]:
            results["conflicts_escalated"] = self.check_pending_conflicts()
        
        self.save_data()
        
        self.log(f"\n{'='*50}")
        self.log(f"检查完成: {results}")
        self.log(f"{'='*50}\n")
        
        return results


def main():
    """主函数"""
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    guardian = DecisionGuardian()
    results = guardian.run(mode)
    
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
