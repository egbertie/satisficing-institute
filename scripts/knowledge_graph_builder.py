#!/usr/bin/env python3
"""
知识内容提取与图谱构建 V1.0
提取关键内容，建立知识关联
"""

import json
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
KNOWLEDGE_DIR = WORKSPACE / "knowledge"
INDEX_FILE = KNOWLEDGE_DIR / "system" / "full_index.json"
GRAPH_FILE = KNOWLEDGE_DIR / "system" / "knowledge_graph.json"

def extract_title(content):
    """提取标题"""
    # 匹配 # 标题
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def extract_summary(content, max_len=200):
    """提取摘要"""
    # 去掉markdown标记，取前200字符
    text = re.sub(r'[#*`\[\]\(\)\|]', '', content)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_len] + "..." if len(text) > max_len else text

def extract_entities(content):
    """提取关键实体"""
    entities = {
        "people": [],
        "tasks": [],
        "concepts": []
    }
    
    # 提取人名（简单规则：大写字母开头的中文名或英文名）
    people_pattern = r'(?:黎红雷|罗汉|谢宝剑|方翊沣|陈国祥|XU先生|Egbertie)'
    entities["people"] = list(set(re.findall(people_pattern, content)))
    
    # 提取任务ID
    task_pattern = r'(?:TODO|WIP|FORG|URG)-\d+'
    entities["tasks"] = list(set(re.findall(task_pattern, content)))
    
    # 提取核心概念
    concept_patterns = [
        r'五路图腾',
        r'合伙人',
        r'满意解',
        r'决策',
        r'方法论'
    ]
    for pattern in concept_patterns:
        if re.search(pattern, content):
            entities["concepts"].append(pattern)
    
    return entities

def build_knowledge_graph():
    """构建知识图谱"""
    print("开始构建知识图谱...")
    
    # 读取索引
    if not INDEX_FILE.exists():
        print("错误: 先运行 knowledge_full_index.py")
        return
    
    index = json.loads(INDEX_FILE.read_text())
    
    # 提取关键文档内容
    nodes = []
    edges = []
    
    # 处理战略文档
    print("处理战略文档...")
    for doc in index["categories"]["战略文档"]:
        path = WORKSPACE / doc["path"]
        if path.exists() and doc["size"] < 100000:  # 只处理小于100KB的文件
            try:
                content = path.read_text(encoding='utf-8')
                title = extract_title(content) or doc["path"]
                summary = extract_summary(content)
                entities = extract_entities(content)
                
                node = {
                    "id": doc["path"],
                    "type": "战略文档",
                    "title": title,
                    "summary": summary,
                    "entities": entities,
                    "size": doc["size"]
                }
                nodes.append(node)
            except Exception as e:
                print(f"Error processing {path}: {e}")
    
    # 处理专家档案
    print("处理专家档案...")
    experts_dir = KNOWLEDGE_DIR / "data" / "experts"
    for yaml_file in experts_dir.glob("*.yaml"):
        try:
            content = yaml_file.read_text()
            # 简单提取姓名
            name_match = re.search(r'name:\s*(.+)', content)
            name = name_match.group(1).strip() if name_match else yaml_file.stem
            
            node = {
                "id": f"experts/{yaml_file.name}",
                "type": "专家",
                "title": name,
                "summary": f"专家档案: {name}",
                "entities": {"people": [name], "tasks": [], "concepts": ["专家"]}
            }
            nodes.append(node)
        except Exception as e:
            print(f"Error processing {yaml_file}: {e}")
    
    # 处理案例
    print("处理案例库...")
    cases_dir = KNOWLEDGE_DIR / "data" / "cases"
    for case_file in cases_dir.glob("*.md"):
        try:
            content = case_file.read_text()
            title = extract_title(content) or case_file.stem
            summary = extract_summary(content)
            
            node = {
                "id": f"cases/{case_file.name}",
                "type": "案例",
                "title": title,
                "summary": summary,
                "entities": extract_entities(content)
            }
            nodes.append(node)
        except Exception as e:
            print(f"Error processing {case_file}: {e}")
    
    # 建立关联（简单的关键词匹配）
    print("建立知识关联...")
    for i, node1 in enumerate(nodes):
        for node2 in nodes[i+1:]:
            # 检查是否有共同的人
            common_people = set(node1.get("entities", {}).get("people", [])) & \
                          set(node2.get("entities", {}).get("people", []))
            
            if common_people:
                edges.append({
                    "source": node1["id"],
                    "target": node2["id"],
                    "relation": "关联",
                    "common_entities": list(common_people)
                })
    
    # 保存图谱
    graph = {
        "generated_at": datetime.now().isoformat(),
        "stats": {
            "nodes": len(nodes),
            "edges": len(edges)
        },
        "nodes": nodes,
        "edges": edges
    }
    
    GRAPH_FILE.write_text(json.dumps(graph, indent=2, ensure_ascii=False))
    print(f"知识图谱已保存: {GRAPH_FILE}")
    print(f"节点: {len(nodes)}, 关联: {len(edges)}")
    
    return graph

if __name__ == "__main__":
    build_knowledge_graph()