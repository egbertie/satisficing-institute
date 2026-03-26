#!/usr/bin/env python3
"""
Knowledge Graph Auto-Updater
知识图谱自动更新脚本 - Phase 3深挖迭代
自动从文档、Skill、日志中抽取实体和关系
"""

import os
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Set

class KnowledgeGraphUpdater:
    """知识图谱自动更新器"""
    
    def __init__(self, kg_path: str = "/root/.openclaw/workspace/backups/layer5_knowledge/kg_snapshot_v1.json"):
        self.kg_path = kg_path
        self.kg = self._load_kg()
        self.new_entities: List[Dict] = []
        self.new_relations: List[Dict] = []
        self.processed_files: Set[str] = set()
        
    def _load_kg(self) -> Dict:
        """加载现有知识图谱"""
        if os.path.exists(self.kg_path):
            with open(self.kg_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "knowledge_graph_snapshot": {
                "generated_at": datetime.now().isoformat(),
                "version": "v1.0",
                "entity_count": 0,
                "relation_count": 0,
                "format": "JSON-LD compatible",
                "core_entities": [],
                "key_relations": [],
                "expert_entities": [],
                "skill_entities": [],
                "document_entities": [],
                "auto_extracted": []
            }
        }
    
    def _save_kg(self):
        """保存知识图谱"""
        os.makedirs(os.path.dirname(self.kg_path), exist_ok=True)
        with open(self.kg_path, 'w', encoding='utf-8') as f:
            json.dump(self.kg, f, indent=2, ensure_ascii=False)
    
    def _extract_entities_from_skill(self, skill_path: str) -> List[Dict]:
        """从Skill中提取实体"""
        entities = []
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            skill_name = os.path.basename(os.path.dirname(skill_path))
            
            # 提取实体：Skill本身
            entities.append({
                "id": f"skill_{skill_name}",
                "type": "Skill",
                "name": skill_name,
                "source": skill_path,
                "confidence": 0.95,
                "extracted_at": datetime.now().isoformat(),
                "method": "auto_skill_scan"
            })
            
            # 提取标签/关键词
            tag_patterns = [
                r'tags:\s*\n((?:\s*-\s*\w+\n?)+)',
                r'##\s*(.+?)\n',
                r'@(\w+)'
            ]
            for pattern in tag_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, str) and len(match) < 50:
                        entities.append({
                            "id": f"concept_{hashlib.md5(match.encode()).hexdigest()[:8]}",
                            "type": "Concept",
                            "name": match.strip(),
                            "source": skill_path,
                            "confidence": 0.7,
                            "extracted_at": datetime.now().isoformat(),
                            "method": "auto_keyword_extract"
                        })
                        
        except Exception as e:
            print(f"[WARN] 提取Skill实体失败 {skill_path}: {e}")
        
        return entities
    
    def _extract_entities_from_doc(self, doc_path: str) -> List[Dict]:
        """从文档中提取实体"""
        entities = []
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_name = os.path.basename(doc_path)
            
            # 文档实体
            entities.append({
                "id": f"doc_{hashlib.md5(doc_path.encode()).hexdigest()[:8]}",
                "type": "Document",
                "name": doc_name,
                "source": doc_path,
                "confidence": 0.95,
                "extracted_at": datetime.now().isoformat(),
                "method": "auto_doc_scan"
            })
            
            # 提取人名（中文）
            person_pattern = r'([\u4e00-\u9fa5]{2,4})(?:博士|教授|先生|老师|研究员)'
            persons = re.findall(person_pattern, content)
            for person in set(persons):
                entities.append({
                    "id": f"person_{hashlib.md5(person.encode()).hexdigest()[:8]}",
                    "type": "Person",
                    "name": person,
                    "source": doc_path,
                    "confidence": 0.8,
                    "extracted_at": datetime.now().isoformat(),
                    "method": "auto_name_extract"
                })
            
            # 提取日期/事件
            date_pattern = r'(\d{4}-\d{2}-\d{2})'
            dates = re.findall(date_pattern, content)
            for date in set(dates):
                entities.append({
                    "id": f"event_{date}",
                    "type": "Event",
                    "name": f"Event_{date}",
                    "date": date,
                    "source": doc_path,
                    "confidence": 0.85,
                    "extracted_at": datetime.now().isoformat(),
                    "method": "auto_date_extract"
                })
                
        except Exception as e:
            print(f"[WARN] 提取文档实体失败 {doc_path}: {e}")
        
        return entities
    
    def _infer_relations(self, entities: List[Dict]) -> List[Dict]:
        """从实体中推断关系"""
        relations = []
        
        # 按来源分组，同来源的实体建立关系
        by_source: Dict[str, List[Dict]] = {}
        for e in entities:
            src = e.get("source", "")
            if src:
                by_source.setdefault(src, []).append(e)
        
        for source, ents in by_source.items():
            if len(ents) >= 2:
                # 建立共现关系
                for i, e1 in enumerate(ents):
                    for e2 in ents[i+1:]:
                        relations.append({
                            "source": e1["id"],
                            "relation": "co_occurs_with",
                            "target": e2["id"],
                            "confidence": 0.6,
                            "source_file": source,
                            "inferred_at": datetime.now().isoformat(),
                            "method": "auto_cooccurrence"
                        })
        
        return relations
    
    def scan_skills(self, skills_dir: str = "/root/.openclaw/workspace/skills"):
        """扫描所有Skill"""
        print(f"[INFO] 扫描Skill目录: {skills_dir}")
        skill_count = 0
        
        for root, dirs, files in os.walk(skills_dir):
            if "SKILL.md" in files:
                skill_path = os.path.join(root, "SKILL.md")
                if skill_path not in self.processed_files:
                    entities = self._extract_entities_from_skill(skill_path)
                    self.new_entities.extend(entities)
                    self.processed_files.add(skill_path)
                    skill_count += 1
        
        print(f"[INFO] 扫描完成: {skill_count}个Skill")
    
    def scan_docs(self, docs_dirs: List[str] = None):
        """扫描所有文档"""
        if docs_dirs is None:
            docs_dirs = [
                "/root/.openclaw/workspace/docs",
                "/root/.openclaw/workspace/memory"
            ]
        
        doc_count = 0
        for docs_dir in docs_dirs:
            if not os.path.exists(docs_dir):
                continue
            print(f"[INFO] 扫描文档目录: {docs_dir}")
            
            for root, dirs, files in os.walk(docs_dir):
                for file in files:
                    if file.endswith(('.md', '.txt')):
                        doc_path = os.path.join(root, file)
                        if doc_path not in self.processed_files:
                            entities = self._extract_entities_from_doc(doc_path)
                            self.new_entities.extend(entities)
                            self.processed_files.add(doc_path)
                            doc_count += 1
        
        print(f"[INFO] 扫描完成: {doc_count}个文档")
    
    def update_knowledge_graph(self):
        """更新知识图谱"""
        print("[INFO] 开始更新知识图谱...")
        
        # 扫描
        self.scan_skills()
        self.scan_docs()
        
        # 去重
        seen_ids = set()
        unique_entities = []
        for e in self.new_entities:
            if e["id"] not in seen_ids:
                seen_ids.add(e["id"])
                unique_entities.append(e)
        
        # 推断关系
        self.new_relations = self._infer_relations(unique_entities)
        
        # 合并到现有图谱
        existing_ids = {e["id"] for e in self.kg["knowledge_graph_snapshot"].get("core_entities", [])}
        existing_ids.update({e["id"] for e in self.kg["knowledge_graph_snapshot"].get("auto_extracted", [])})
        
        new_count = 0
        for e in unique_entities:
            if e["id"] not in existing_ids:
                self.kg["knowledge_graph_snapshot"].setdefault("auto_extracted", []).append(e)
                new_count += 1
        
        # 更新关系
        existing_rels = {(r["source"], r["relation"], r["target"]) 
                        for r in self.kg["knowledge_graph_snapshot"].get("key_relations", [])}
        for r in self.new_relations:
            rel_key = (r["source"], r["relation"], r["target"])
            if rel_key not in existing_rels:
                self.kg["knowledge_graph_snapshot"].setdefault("auto_relations", []).append(r)
        
        # 更新统计
        all_entities = (self.kg["knowledge_graph_snapshot"].get("core_entities", []) +
                       self.kg["knowledge_graph_snapshot"].get("auto_extracted", []))
        all_relations = (self.kg["knowledge_graph_snapshot"].get("key_relations", []) +
                        self.kg["knowledge_graph_snapshot"].get("auto_relations", []))
        
        self.kg["knowledge_graph_snapshot"]["entity_count"] = len(all_entities)
        self.kg["knowledge_graph_snapshot"]["relation_count"] = len(all_relations)
        self.kg["knowledge_graph_snapshot"]["generated_at"] = datetime.now().isoformat()
        self.kg["knowledge_graph_snapshot"]["version"] = "v1.1-auto"
        
        # 保存
        self._save_kg()
        
        print(f"[INFO] 知识图谱更新完成")
        print(f"  - 新增实体: {new_count}")
        print(f"  - 新增关系: {len(self.new_relations)}")
        print(f"  - 总实体数: {len(all_entities)}")
        print(f"  - 总关系数: {len(all_relations)}")
        
        return {
            "new_entities": new_count,
            "new_relations": len(self.new_relations),
            "total_entities": len(all_entities),
            "total_relations": len(all_relations)
        }
    
    def generate_report(self) -> str:
        """生成更新报告"""
        kg = self.kg["knowledge_graph_snapshot"]
        
        report = f"""# 知识图谱自动更新报告

**生成时间**: {datetime.now().isoformat()}
**版本**: {kg.get('version', 'v1.0')}

## 统计信息

| 指标 | 数值 |
|------|------|
| 总实体数 | {kg.get('entity_count', 0)} |
| 总关系数 | {kg.get('relation_count', 0)} |
| 核心实体 | {len(kg.get('core_entities', []))} |
| 专家实体 | {len(kg.get('expert_entities', []))} |
| 自动抽取 | {len(kg.get('auto_extracted', []))} |

## 实体类型分布

"""
        
        # 统计类型分布
        type_counts = {}
        all_ents = (kg.get('core_entities', []) + kg.get('expert_entities', []) + 
                   kg.get('auto_extracted', []))
        for e in all_ents:
            t = e.get('type', 'Unknown')
            type_counts[t] = type_counts.get(t, 0) + 1
        
        for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            report += f"- {t}: {count}\n"
        
        report += """
## 最近更新

"""
        
        # 最近抽取的实体
        recent = kg.get('auto_extracted', [])[-10:]
        for e in recent:
            report += f"- [{e.get('type', 'Unknown')}] {e.get('name', 'Unknown')} (置信度: {e.get('confidence', 0)})\n"
        
        return report

def main():
    """主函数"""
    print("=" * 60)
    print("知识图谱自动更新器 v1.1")
    print("=" * 60)
    
    updater = KnowledgeGraphUpdater()
    result = updater.update_knowledge_graph()
    
    print("\n" + "=" * 60)
    print("更新摘要:")
    print(f"  新增实体: {result['new_entities']}")
    print(f"  新增关系: {result['new_relations']}")
    print(f"  总实体数: {result['total_entities']}")
    print(f"  总关系数: {result['total_relations']}")
    print("=" * 60)
    
    # 生成报告
    report = updater.generate_report()
    report_path = "/root/.openclaw/workspace/backups/layer5_knowledge/kg_update_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存: {report_path}")

if __name__ == "__main__":
    main()
