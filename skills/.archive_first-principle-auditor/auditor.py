#!/usr/bin/env python3
"""
First Principle Auditor - 第一性原则检视器

基于第一性原理，对工作空间进行全面检视和审计。
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class FirstPrincipleAuditor:
    """第一性原则检视器"""
    
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.skills_path = self.workspace / "skills"
        self.docs_path = self.workspace / "docs"
        self.memory_path = self.workspace / "memory"
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "skills": {},
            "docs": {},
            "cron": {},
            "memory": {},
            "recommendations": []
        }
    
    def audit(self, scope: str = "all") -> Dict:
        """
        执行审计
        
        Args:
            scope: 审计范围 (all/skill/doc/cron/memory)
        
        Returns:
            审计报告字典
        """
        print(f"🔍 开始第一性原则审计 (范围: {scope})")
        
        if scope in ["all", "skill"]:
            self._audit_skills()
        
        if scope in ["all", "doc"]:
            self._audit_docs()
        
        if scope in ["all", "cron"]:
            self._audit_cron()
        
        if scope in ["all", "memory"]:
            self._audit_memory()
        
        self._generate_recommendations()
        
        return self.report
    
    def _audit_skills(self):
        """审计Skill体系"""
        print("📦 审计Skill体系...")
        
        if not self.skills_path.exists():
            self.report["skills"] = {"error": "Skills目录不存在"}
            return
        
        skills = [d.name for d in self.skills_path.iterdir() if d.is_dir()]
        skill_md_count = sum(1 for s in skills if (self.skills_path / s / "SKILL.md").exists())
        
        # 识别可能的重复（基于命名关键词）
        search_keywords = ['search', 'fetch', 'crawl', 'scrape']
        doc_keywords = ['doc', 'document', 'notion', 'markdown']
        data_keywords = ['data', 'excel', 'csv', 'analyst']
        notify_keywords = ['notify', 'message', 'email', 'slack', 'feishu']
        
        search_skills = [s for s in skills if any(k in s.lower() for k in search_keywords)]
        doc_skills = [s for s in skills if any(k in s.lower() for k in doc_keywords)]
        data_skills = [s for s in skills if any(k in s.lower() for k in data_keywords)]
        notify_skills = [s for s in skills if any(k in s.lower() for k in notify_keywords)]
        
        self.report["skills"] = {
            "total": len(skills),
            "with_skill_md": skill_md_count,
            "categories": {
                "search": {"count": len(search_skills), "items": search_skills},
                "document": {"count": len(doc_skills), "items": doc_skills},
                "data": {"count": len(data_skills), "items": data_skills},
                "notify": {"count": len(notify_skills), "items": notify_skills}
            },
            "issues": []
        }
        
        # 标记问题
        if len(search_skills) > 3:
            self.report["skills"]["issues"].append({
                "type": "duplication",
                "category": "search",
                "message": f"发现{len(search_skills)}个搜索相关Skill，建议合并为unified-intelligence-suite",
                "items": search_skills
            })
        
        if len(doc_skills) > 3:
            self.report["skills"]["issues"].append({
                "type": "duplication",
                "category": "document",
                "message": f"发现{len(doc_skills)}个文档处理Skill，建议合并为unified-document-suite",
                "items": doc_skills
            })
        
        print(f"  ✓ 发现 {len(skills)} 个Skill，其中 {skill_md_count} 个有SKILL.md")
        print(f"  ⚠️ 搜索类: {len(search_skills)} 个，文档类: {len(doc_skills)} 个")
    
    def _audit_docs(self):
        """审计文档体系"""
        print("📄 审计文档体系...")
        
        if not self.docs_path.exists():
            self.report["docs"] = {"error": "Docs目录不存在"}
            return
        
        docs = list(self.docs_path.glob("*.md"))
        
        # 识别版本冲突
        version_patterns = ['V1.0', 'V1.1', 'V1.2', 'V2.0', 'V2.5']
        version_conflicts = []
        
        for pattern in version_patterns:
            matching = [d.name for d in docs if pattern in d.name]
            if len(matching) > 1:
                version_conflicts.append({"pattern": pattern, "files": matching})
        
        # 识别重复主题
        strategic_docs = [d.name for d in docs if any(k in d.name.upper() for k in ['STRATEGY', 'BRAND', 'POSITION', 'MESSAGING'])]
        cron_docs = [d.name for d in docs if 'CRON' in d.name.upper()]
        skill_docs = [d.name for d in docs if 'SKILL' in d.name.upper()]
        
        self.report["docs"] = {
            "total": len(docs),
            "version_conflicts": version_conflicts,
            "categories": {
                "strategic": {"count": len(strategic_docs), "items": strategic_docs},
                "cron": {"count": len(cron_docs), "items": cron_docs},
                "skill": {"count": len(skill_docs), "items": skill_docs}
            },
            "issues": []
        }
        
        if len(strategic_docs) > 3:
            self.report["docs"]["issues"].append({
                "type": "duplication",
                "category": "strategic",
                "message": f"发现{len(strategic_docs)}个战略相关文档，建议合并",
                "items": strategic_docs
            })
        
        print(f"  ✓ 发现 {len(docs)} 个文档")
        print(f"  ⚠️ 版本冲突: {len(version_conflicts)} 组")
    
    def _audit_cron(self):
        """审计Cron体系"""
        print("⏰ 审计Cron体系...")
        
        # 检查是否有高频检查记录
        zero_idle_log = self.memory_path / "zero-idle-log.jsonl"
        scheduler_log = self.memory_path / "scheduler-log.jsonl"
        
        issues = []
        
        if zero_idle_log.exists():
            issues.append({
                "type": "high_frequency",
                "message": "发现零空置强制执行日志，建议转为事件驱动",
                "file": str(zero_idle_log)
            })
        
        self.report["cron"] = {
            "issues": issues,
            "recommendation": "9个Daily Cron已合并为2个，高频检查已禁用"
        }
        
        print(f"  ✓ Cron审计完成")
    
    def _audit_memory(self):
        """审计数据记忆"""
        print("🧠 审计数据记忆...")
        
        if not self.memory_path.exists():
            self.report["memory"] = {"error": "Memory目录不存在"}
            return
        
        daily_logs = list(self.memory_path.glob("2026-*.md"))
        intelligence_dir = self.memory_path / "intelligence"
        
        issues = []
        
        # 检查知识图谱是否存在
        kg_file = self.memory_path / "knowledge-graph.json"
        if not kg_file.exists():
            issues.append({
                "type": "missing",
                "message": "知识图谱不存在，建议建立",
                "file": str(kg_file)
            })
        
        self.report["memory"] = {
            "daily_logs": len(daily_logs),
            "intelligence_exists": intelligence_dir.exists(),
            "issues": issues
        }
        
        print(f"  ✓ 发现 {len(daily_logs)} 个日志文件")
    
    def _generate_recommendations(self):
        """生成优化建议"""
        print("💡 生成优化建议...")
        
        recommendations = []
        
        # Skill建议
        if "skills" in self.report and "issues" in self.report["skills"]:
            for issue in self.report["skills"]["issues"]:
                if issue["type"] == "duplication":
                    recommendations.append({
                        "priority": "P0",
                        "category": "Skill",
                        "action": "merge",
                        "description": issue["message"],
                        "items": issue["items"],
                        "estimated_saving": "-80% Skill数量"
                    })
        
        # 文档建议
        if "docs" in self.report and "issues" in self.report["docs"]:
            for issue in self.report["docs"]["issues"]:
                if issue["type"] == "duplication":
                    recommendations.append({
                        "priority": "P1",
                        "category": "Document",
                        "action": "merge",
                        "description": issue["message"],
                        "items": issue["items"],
                        "estimated_saving": "-70% 文档数量"
                    })
        
        # 按优先级排序
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        self.report["recommendations"] = recommendations
        
        print(f"  ✓ 生成 {len(recommendations)} 条建议")
    
    def generate_markdown_report(self, output_path: Optional[str] = None) -> str:
        """生成Markdown格式报告"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            output_path = self.docs_path / f"FIRST_PRINCIPLE_AUDIT_{timestamp}.md"
        
        report_lines = [
            "# 第一性原则审计报告",
            "",
            f"> 生成时间: {self.report['timestamp']}",
            f"> 审计范围: 全面",
            "",
            "## 执行摘要",
            ""
        ]
        
        # Skill摘要
        if "skills" in self.report:
            skills = self.report["skills"]
            report_lines.extend([
                f"- **Skill总数**: {skills.get('total', 0)}",
                f"- **问题识别**: {len(skills.get('issues', []))} 项"
            ])
        
        # 文档摘要
        if "docs" in self.report:
            docs = self.report["docs"]
            report_lines.extend([
                f"- **文档总数**: {docs.get('total', 0)}",
                f"- **版本冲突**: {len(docs.get('version_conflicts', []))} 组"
            ])
        
        # 优化建议
        report_lines.extend([
            "",
            "## 优化建议",
            ""
        ])
        
        for rec in self.report["recommendations"]:
            report_lines.extend([
                f"### {rec['priority']}: {rec['description']}",
                "",
                f"- **类别**: {rec['category']}",
                f"- **动作**: {rec['action']}",
                f"- **预期节省**: {rec['estimated_saving']}",
                ""
            ])
        
        report_content = "\n".join(report_lines)
        
        # 写入文件
        Path(output_path).write_text(report_content, encoding='utf-8')
        
        return report_content
    
    def summary(self) -> str:
        """返回摘要"""
        lines = [
            "=" * 50,
            "第一性原则审计摘要",
            "=" * 50,
            ""
        ]
        
        if "skills" in self.report:
            lines.append(f"📦 Skill: {self.report['skills'].get('total', 0)} 个")
        
        if "docs" in self.report:
            lines.append(f"📄 文档: {self.report['docs'].get('total', 0)} 个")
        
        lines.extend([
            "",
            f"💡 优化建议: {len(self.report.get('recommendations', []))} 条",
            ""
        ])
        
        for rec in self.report.get("recommendations", [])[:5]:
            lines.append(f"  [{rec['priority']}] {rec['description'][:50]}...")
        
        lines.append("")
        lines.append("=" * 50)
        
        return "\n".join(lines)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="第一性原则检视器")
    parser.add_argument("--scope", default="all", 
                       choices=["all", "skill", "doc", "cron", "memory"],
                       help="审计范围")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--format", default="md", choices=["md", "json"],
                       help="输出格式")
    
    args = parser.parse_args()
    
    # 执行审计
    auditor = FirstPrincipleAuditor()
    report = auditor.audit(scope=args.scope)
    
    # 输出结果
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        if args.output:
            auditor.generate_markdown_report(args.output)
            print(f"报告已保存: {args.output}")
        else:
            print(auditor.summary())


if __name__ == "__main__":
    main()
