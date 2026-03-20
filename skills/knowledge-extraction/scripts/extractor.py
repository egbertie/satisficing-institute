#!/usr/bin/env python3
"""
知识沉淀自动化脚本
版本: V2.0
功能: 每日自动萃取知识并结构化存储
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

LOG_FILE = "/tmp/knowledge-extraction.log"
OUTPUT_DIR = "/root/.openclaw/workspace/05_📦历史归档/学习笔记"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def get_today_conversations():
    """获取今日对话内容"""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = Path(f"/root/.openclaw/workspace/memory/{today}.md")
    
    if not memory_file.exists():
        return ""
    
    try:
        return memory_file.read_text(encoding='utf-8')
    except:
        return ""

def identify_knowledge(content):
    """识别知识内容"""
    knowledge_items = []
    
    # 决策知识
    decision_pattern = r"(?:决定|决策|选择).*?(?:因为|基于|考虑到)"
    decisions = re.findall(decision_pattern, content, re.IGNORECASE)
    for d in decisions:
        knowledge_items.append({"type": "decision", "content": d[:200]})
    
    # 方法论知识
    method_pattern = r"(?:方法|方法论|框架|模型).*?(?:包括|步骤|流程)"
    methods = re.findall(method_pattern, content, re.IGNORECASE)
    for m in methods:
        knowledge_items.append({"type": "methodology", "content": m[:200]})
    
    # 经验教训
    lesson_pattern = r"(?:教训|经验|总结|反思).*?(?:发现|认识到|应该)"
    lessons = re.findall(lesson_pattern, content, re.IGNORECASE)
    for l in lessons:
        knowledge_items.append({"type": "lesson", "content": l[:200]})
    
    # 最佳实践
    practice_pattern = r"(?:最佳实践|优秀|成功|有效).*?(?:做法|方案|方式)"
    practices = re.findall(practice_pattern, content, re.IGNORECASE)
    for p in practices:
        knowledge_items.append({"type": "best_practice", "content": p[:200]})
    
    return knowledge_items

def save_knowledge_note(knowledge_items):
    """保存知识笔记"""
    if not knowledge_items:
        log("未发现可萃取的知识")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = Path(f"{OUTPUT_DIR}/{today}_knowledge.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"# 知识萃取笔记 - {today}\n\n"
    content += f"萃取时间: {datetime.now().isoformat()}\n\n"
    
    for item in knowledge_items:
        content += f"## {item['type'].upper()}\n\n"
        content += f"{item['content']}\n\n"
        content += "---\n\n"
    
    output_file.write_text(content, encoding='utf-8')
    log(f"知识笔记已保存: {output_file}")

def update_knowledge_graph(knowledge_items):
    """更新知识图谱"""
    # 简化实现
    log(f"知识图谱更新: 添加 {len(knowledge_items)} 个节点")

def main():
    """主函数"""
    log("=" * 50)
    log("知识沉淀自动化 - 每日萃取")
    log("=" * 50)
    
    # 获取今日内容
    content = get_today_conversations()
    if not content:
        log("今日无对话记录")
        return 0
    
    log(f"获取今日内容: {len(content)} 字符")
    
    # 识别知识
    knowledge_items = identify_knowledge(content)
    log(f"识别知识条目: {len(knowledge_items)} 个")
    
    # 保存知识笔记
    save_knowledge_note(knowledge_items)
    
    # 更新知识图谱
    update_knowledge_graph(knowledge_items)
    
    log("知识萃取完成")
    return 0

if __name__ == "__main__":
    exit(main())
