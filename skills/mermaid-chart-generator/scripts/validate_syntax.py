#!/usr/bin/env python3
"""
Mermaid语法验证器
用法: python3 validate_syntax.py --file [filename] 或 --code "code"
"""

import argparse
import re
import sys

def validate_mermaid(content):
    """验证Mermaid代码基本语法"""
    errors = []
    warnings = []
    
    lines = content.strip().split('\n')
    if not lines:
        return False, ["空内容"], []
    
    # 检查图表类型声明
    first_line = lines[0].strip()
    valid_starts = ['graph ', 'sequenceDiagram', 'gantt', 'pie ', 'classDiagram', 
                    'erDiagram', 'journey', 'flowchart ', 'mindmap']
    
    has_valid_start = any(first_line.startswith(v) for v in valid_starts)
    if not has_valid_start:
        errors.append(f"未识别的图表类型: {first_line}")
        errors.append("有效的图表类型: graph, flowchart, sequenceDiagram, gantt, pie, classDiagram, erDiagram")
    
    # 检查常见语法错误
    open_brackets = content.count('[') - content.count(']')
    open_braces = content.count('{') - content.count('}')
    open_parens = content.count('(') - content.count(')')
    
    if open_brackets != 0:
        errors.append(f"方括号不匹配: 差 {open_brackets} 个")
    if open_braces != 0:
        errors.append(f"花括号不匹配: 差 {open_braces} 个")
    if open_parens != 0:
        errors.append(f"圆括号不匹配: 差 {open_parens} 个")
    
    # 检查箭头语法 (graph/flowchart)
    if first_line.startswith(('graph', 'flowchart')):
        invalid_arrows = re.findall(r'--[^->\s]', content)
        if invalid_arrows:
            warnings.append("可能存在错误的箭头语法，应使用 --\u003e 或 ==\u003e")
    
    # 检查节点ID
    node_pattern = r'\b([a-zA-Z][a-zA-Z0-9]*)\s*\['
    nodes = re.findall(node_pattern, content)
    if len(nodes) < 2 and first_line.startswith(('graph', 'flowchart')):
        warnings.append("图表节点较少，确认是否完整")
    
    return len(errors) == 0, errors, warnings

def main():
    parser = argparse.ArgumentParser(description='Mermaid语法验证器')
    parser.add_argument('--file', help='Mermaid文件路径')
    parser.add_argument('--code', help='Mermaid代码字符串')
    
    args = parser.parse_args()
    
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif args.code:
        content = args.code
    else:
        print("❌ 请提供 --file 或 --code 参数")
        sys.exit(1)
    
    is_valid, errors, warnings = validate_mermaid(content)
    
    print("=" * 50)
    print("Mermaid语法验证报告")
    print("=" * 50)
    
    if is_valid:
        print("✅ 语法验证通过")
    else:
        print("❌ 语法验证失败")
    
    if errors:
        print("\n错误:")
        for e in errors:
            print(f"  ❌ {e}")
    
    if warnings:
        print("\n警告:")
        for w in warnings:
            print(f"  ⚠️  {w}")
    
    if not errors and not warnings:
        print("\n未发现错误或警告")
    
    print("=" * 50)
    sys.exit(0 if is_valid else 1)

if __name__ == '__main__':
    main()
