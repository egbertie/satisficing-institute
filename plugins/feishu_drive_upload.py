#!/usr/bin/env python3
"""
飞书云盘文件上传插件
支持上传本地文件到飞书云空间

用法:
  python3 feishu_drive_upload.py <本地文件路径> [目标文件夹token]
  
示例:
  python3 feishu_drive_upload.py /path/to/file.pdf
  python3 feishu_drive_upload.py /path/to/file.pdf fldbcO1UuPz8VwnpPx5a92abcef
"""

import sys
import os
import json
import base64
import requests
from pathlib import Path

# 配置 - 从OpenClaw配置读取
FEISHU_CONFIG = {
    "app_id": "cli_a949c1e2f4f89cb3",
    "app_secret": "Z8hnq3wLrkjQrCes94N0xEqBlHPHjk6b"
}

# API端点
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"
TOKEN_URL = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
UPLOAD_URL = f"{FEISHU_API_BASE}/drive/v1/files/upload_all"
LIST_FILES_URL = f"{FEISHU_API_BASE}/drive/v1/files"


def get_tenant_access_token():
    """获取tenant_access_token"""
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {
        "app_id": FEISHU_CONFIG["app_id"],
        "app_secret": FEISHU_CONFIG["app_secret"]
    }
    
    try:
        resp = requests.post(TOKEN_URL, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") != 0:
            print(f"❌ 获取token失败: {result.get('msg')}")
            return None
            
        token = result.get("tenant_access_token")
        expire = result.get("expire", 0)
        print(f"✅ Token获取成功，有效期 {expire//3600} 小时")
        return token
        
    except Exception as e:
        print(f"❌ 请求token异常: {e}")
        return None


def upload_file_to_drive(token, file_path, parent_node=""):
    """上传文件到飞书云盘"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return None
    
    file_name = file_path.name
    file_size = file_path.stat().st_size
    
    print(f"📄 文件名: {file_name}")
    print(f"📦 大小: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
    print(f"📁 目标: {'根目录' if not parent_node else parent_node}")
    
    # 检查文件大小限制 (20MB)
    if file_size > 20 * 1024 * 1024:
        print(f"❌ 文件超过20MB限制，请使用分片上传")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 准备multipart/form-data
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_name, f, 'application/octet-stream')
        }
        data = {
            'file_name': file_name,
            'parent_type': 'explorer',
            'parent_node': parent_node or '',
            'size': str(file_size)
        }
        
        try:
            print("⏳ 正在上传...")
            resp = requests.post(UPLOAD_URL, headers=headers, files=files, data=data, timeout=120)
            
            # 打印详细响应
            print(f"   响应状态: {resp.status_code}")
            print(f"   响应内容: {resp.text[:500]}")
            
            resp.raise_for_status()
            result = resp.json()
            
            if result.get("code") != 0:
                print(f"❌ 上传失败: {result.get('msg')} (code: {result.get('code')})")
                print(f"   详细错误: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return None
            
            file_token = result.get("data", {}).get("file_token")
            print(f"✅ 上传成功!")
            print(f"🔗 File Token: {file_token}")
            return file_token
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP错误: {e}")
            print(f"   响应内容: {resp.text if 'resp' in locals() else 'N/A'}")
            return None
        except Exception as e:
            print(f"❌ 上传异常: {e}")
            import traceback
            traceback.print_exc()
            return None


def list_root_files(token):
    """列出云空间根目录文件"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        resp = requests.get(LIST_FILES_URL, headers=headers, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") != 0:
            print(f"❌ 获取文件列表失败: {result.get('msg')}")
            return []
        
        files = result.get("data", {}).get("files", [])
        print(f"\n📂 云空间根目录文件 ({len(files)}个):")
        print("-" * 60)
        for f in files:
            print(f"  • {f.get('name')} ({f.get('type')}) - {f.get('token')}")
        print("-" * 60)
        return files
        
    except Exception as e:
        print(f"❌ 获取文件列表异常: {e}")
        return []


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    # 检查是否是list命令
    if sys.argv[1] == "list":
        token = get_tenant_access_token()
        if token:
            list_root_files(token)
        sys.exit(0)
    
    file_path = sys.argv[1]
    parent_node = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print("=" * 60)
    print("🚀 飞书云盘文件上传")
    print("=" * 60)
    
    # 获取token
    token = get_tenant_access_token()
    if not token:
        sys.exit(1)
    
    # 上传文件
    file_token = upload_file_to_drive(token, file_path, parent_node)
    
    if file_token:
        print("=" * 60)
        print("✅ 任务完成")
        print("=" * 60)
        # 输出可用于分享的链接格式
        print(f"\n💡 分享链接格式:")
        print(f"   https://open.feishu.cn/open-apis/drive/v1/files/{file_token}")
        sys.exit(0)
    else:
        print("=" * 60)
        print("❌ 任务失败")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
