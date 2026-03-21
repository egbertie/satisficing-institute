#!/usr/bin/env python3
"""
Mermaid图表生成器
用法: python3 generate_chart.py --type [flowchart|gantt|decision|pie] --input "描述"
"""

import argparse
import sys
import re
from datetime import datetime, timedelta

def generate_flowchart(description):
    """生成流程图"""
    # 解析关键词
    steps = re.split(r'[→\-]+', description)
    steps = [s.strip() for s in steps if s.strip()]
    
    mermaid = ["graph LR"]
    for i in range(len(steps) - 1):
        from_step = f"S{i}" if i > 0 else "Start"
        to_step = f"S{i+1}" if i < len(steps) - 2 else "End"
        mermaid.append(f"    {from_step}[{steps[i]}] --> {to_step}[{steps[i+1]}]")
    
    return "\n".join(mermaid)

def generate_gantt(description):
    """生成甘特图"""
    # 尝试解析时间段
    mermaid = ["gantt"]
    mermaid.append("    title 项目排期")
    mermaid.append("    dateFormat  YYYY-MM-DD")
    
    # 解析任务
    tasks = re.findall(r'(\w+)\s*[:：]\s*(\d+)\s*[周周天]', description)
    if tasks:
        start = datetime.now()
        for task, weeks in tasks:
            end = start + timedelta(weeks=int(weeks))
            mermaid.append(f"    {task}     :a1, {start.strftime('%Y-%m-%d')}, {end.strftime('%Y-%m-%d')}")
            start = end
    else:
        mermaid.append("    阶段1     :a1, 2026-01-01, 7d")
        mermaid.append("    阶段2     :after a1, 14d")
    
    return "\n".join(mermaid)

def generate_decision_tree(description):
    """生成决策树"""
    mermaid = ["graph TD"]
    mermaid.append("    Start([开始]) --> Q1{判断条件}")
    mermaid.append("    Q1 -->|是| A1[选项A]")
    mermaid.append("    Q1 -->|否| A2[选项B]")
    mermaid.append("    A1 --> End1([结束A])")
    mermaid.append("    A2 --> End2([结束B])")
    mermaid.append("    ")
    mermaid.append("    style Start fill:#e1f5ff")
    mermaid.append("    style End1 fill:#ccffcc")
    mermaid.append("    style End2 fill:#ffcccc")
    return "\n".join(mermaid)

def generate_pie(description):
    """生成饼图"""
    mermaid = ["pie title 数据分布"]
    mermaid.append('    "类别A" : 40')
    mermaid.append('    "类别B" : 30')
    mermaid.append('    "类别C" : 20')
    mermaid.append('    "其他" : 10')
    return "\n".join(mermaid)

def main():
    parser = argparse.ArgumentParser(description='Mermaid图表生成器')
    parser.add_argument('--type', choices=['flowchart', 'gantt', 'decision', 'pie'], required=True)
    parser.add_argument('--input', required=True, help='图表描述')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    generators = {
        'flowchart': generate_flowchart,
        'gantt': generate_gantt,
        'decision': generate_decision_tree,
        'pie': generate_pie
    }
    
    result = generators[args.type](args.input)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✅ 图表已保存到: {args.output}")
    else:
        print("🎨 生成的Mermaid图表:\n")
        print("```mermaid")
        print(result)
        print("```")
        print("\n📖 使用指引:")
        print("1. 复制上面的Mermaid代码")
        print("2. 打开 https://mermaid.live")
        print("3. 粘贴即见图形")
        print("4. 可导出PNG/SVG/PDF")

if __name__ == '__main__':
    main()
