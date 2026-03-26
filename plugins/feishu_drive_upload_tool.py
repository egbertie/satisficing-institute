#!/usr/bin/env python3
"""
Feishu Drive Upload Tool - OpenClaw Tool Registration
飞书云盘上传工具 - OpenClaw工具注册脚本

此脚本将 feishu_drive_uploader.py 注册为 OpenClaw 工具
"""

import os
import sys
import json

# 工具定义
TOOL_DEFINITION = {
    "name": "feishu_drive_upload",
    "label": "飞书云盘上传",
    "description": """【飞书云盘上传】上传本地文件到飞书云空间。

功能:
- 上传文件到飞书云空间
- 自动压缩大文件 (>20MB)
- 支持指定文件夹位置
- 列出云空间文件

参数:
- action: upload/list
- file_path: 本地文件路径 (upload时需要)
- parent_node: 目标文件夹token (可选)
- file_name: 自定义文件名 (可选)
- compress: 是否强制压缩 (可选,默认自动判断)

返回:
- file_token: 文件在云空间的token
- file_name: 文件名
- size: 文件大小
- method: 上传方式 (direct/compressed/split)
""",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["upload", "list"],
                "description": "操作类型: upload(上传) 或 list(列出文件)"
            },
            "file_path": {
                "type": "string",
                "description": "本地文件路径 (upload时需要)"
            },
            "parent_node": {
                "type": "string",
                "description": "目标文件夹token (可选,默认根目录)"
            },
            "file_name": {
                "type": "string",
                "description": "自定义文件名 (可选)"
            },
            "compress": {
                "type": "boolean",
                "description": "是否强制压缩 (可选,默认自动判断)"
            }
        },
        "required": ["action"]
    }
}


def execute_tool(params: dict) -> str:
    """
    执行工具调用
    
    此函数将被OpenClaw调用
    """
    # 导入上传器
    script_dir = os.path.dirname(os.path.abspath(__file__))
    uploader_path = os.path.join(script_dir, "feishu_drive_uploader.py")
    
    if not os.path.exists(uploader_path):
        return json.dumps({
            "success": False,
            "error": f"上传器脚本不存在: {uploader_path}"
        }, ensure_ascii=False)
    
    # 动态导入
    import importlib.util
    spec = importlib.util.spec_from_file_location("feishu_drive_uploader", uploader_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    action = params.get("action")
    
    if action == "upload":
        file_path = params.get("file_path")
        if not file_path:
            return json.dumps({
                "success": False,
                "error": "upload action requires file_path parameter"
            }, ensure_ascii=False)
        
        return module.tool_upload(
            file_path=file_path,
            parent_node=params.get("parent_node", ""),
            file_name=params.get("file_name"),
            compress=params.get("compress", False)
        )
    
    elif action == "list":
        return module.tool_list(params.get("parent_node", ""))
    
    else:
        return json.dumps({
            "success": False,
            "error": f"Unknown action: {action}"
        }, ensure_ascii=False)


# OpenClaw工具调用入口
def main():
    """
    命令行入口 - 用于OpenClaw工具调用
    
    OpenClaw会通过stdin传入参数JSON
    """
    try:
        # 读取stdin
        input_data = sys.stdin.read()
        params = json.loads(input_data)
        
        # 执行工具
        result = execute_tool(params)
        
        # 输出结果
        print(result)
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"Invalid JSON input: {e}"
        }, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
