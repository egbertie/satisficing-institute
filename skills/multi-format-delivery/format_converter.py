#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多格式交付能力 - 格式转换器
Multi-Format Delivery Converter

功能：
- 文本转Mermaid图表
- 数据转可视化
- PPT大纲生成
"""

import os
import sys
import json
import re
from pathlib import Path

class FormatConverter:
    """格式转换器"""
    
    # Mermaid模板库
    TEMPLATES = {
        "flowchart": """graph TD
    {nodes}
    {edges}
    
    {styles}""",
        
        "gantt": """gantt
    title {title}
    dateFormat YYYY-MM-DD
    
    {tasks}""",
        
        "pie": """pie title {title}
    {data}""",
        
        "mindmap": """mindmap
  root(({title}))
    {branches}""",
        
        "xychart": """xychart-beta
    title \"{title}\"
    x-axis {x_labels}
    y-axis \"{y_title}\" {y_range}
    bar {y_data}""",
    }
    
    def __init__(self):
        pass
    
    def detect_content_type(self, content):
        """检测内容类型"""
        content = content.lower()
        
        if any(kw in content for kw in ["流程", "步骤", "过程", "stage", "process"]):
            return "flowchart"
        elif any(kw in content for kw in ["时间", "排期", "计划", "timeline", "schedule"]):
            return "gantt"
        elif any(kw in content for kw in ["比例", "分布", "占比", "percentage", "distribution"]):
            return "pie"
        elif any(kw in content for kw in ["思维导图", "脑图", "mindmap", "结构"]):
            return "mindmap"
        elif any(kw in content for kw in ["数据", "统计", "chart", "graph", "柱状"]):
            return "xychart"
        else:
            return "flowchart"  # 默认
    
    def generate_flowchart(self, steps):
        """生成流程图"""
        nodes = []
        edges = []
        styles = []
        
        for i, step in enumerate(steps):
            node_id = f"A{i}"
            if "判断" in step or "?" in step:
                nodes.append(f"{node_id}{{{{{step}}}}}"
)
            elif "开始" in step or "结束" in step:
                nodes.append(f"{node_id}(({step}))")
            else:
                nodes.append(f"{node_id}[{step}]")
            
            if i < len(steps) - 1:
                edges.append(f"{node_id} --> A{i+1}")
        
        template = self.TEMPLATES["flowchart"]
        return template.format(
            nodes="\n    ".join(nodes),
            edges="\n    ".join(edges),
            styles=""
        )
    
    def generate_gantt(self, title, tasks):
        """生成Gantt图"""
        task_str = ""
        for task in tasks:
            name = task.get("name", "任务")
            start = task.get("start", "2026-03-15")
            duration = task.get("duration", "3d")
            task_str += f"    {name} : {start}, {duration}\n"
        
        template = self.TEMPLATES["gantt"]
        return template.format(title=title, tasks=task_str)
    
    def generate_pie(self, title, data):
        """生成饼图"""
        data_str = ""
        for item, value in data.items():
            data_str += f'    "{item}" : {value}\n'
        
        template = self.TEMPLATES["pie"]
        return template.format(title=title, data=data_str)
    
    def convert(self, content, chart_type=None):
        """主转换函数"""
        if chart_type is None:
            chart_type = self.detect_content_type(content)
        
        # 简单解析步骤（实际应用需要更复杂的NLP）
        steps = [s.strip() for s in content.split("→") if s.strip()]
        
        if chart_type == "flowchart":
            mermaid_code = self.generate_flowchart(steps)
        else:
            mermaid_code = f"%% 请提供{chart_type}类型所需的具体数据格式"
        
        return {
            "chart_type": chart_type,
            "mermaid_code": mermaid_code,
            "usage_guide": "复制代码到 https://mermaid.live 预览"
        }

def main():
    """主入口"""
    converter = FormatConverter()
    
    if len(sys.argv) < 2:
        print("Usage: python3 format_converter.py [text_content]")
        print("Example: python3 format_converter.py '开始→处理→结束'")
        sys.exit(1)
    
    content = sys.argv[1]
    result = converter.convert(content)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
