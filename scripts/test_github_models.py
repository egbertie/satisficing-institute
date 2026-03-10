#!/usr/bin/env python3
"""
GitHub Models API 测试脚本
测试 GPT-4o 连接和功能
"""

import json
import os
import sys
import time
from datetime import datetime

def test_github_models_api():
    """测试 GitHub Models API 连接"""
    
    print("=" * 60)
    print("🧪 GitHub Models API 测试 (GPT-4o)")
    print("=" * 60)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查依赖
    try:
        import requests
        print("✅ requests 库已安装")
    except ImportError:
        print("❌ 缺少 requests 库，正在安装...")
        os.system(f"{sys.executable} -m pip install requests -q")
        import requests
        print("✅ requests 库安装完成")
    
    print()
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "github_models.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 配置加载成功: {config['name']}")
        print(f"   端点: {config['endpoint']}")
        print(f"   模型: {config['model']}")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False
    
    print()
    
    # 准备请求
    endpoint = config['endpoint']
    api_key = config['auth']['token']
    model = config['model']
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试 1: 简单对话
    print("📝 测试 1: 简单对话...")
    try:
        response = requests.post(
            f"{endpoint}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "你是一个有用的助手。"},
                    {"role": "user", "content": "你好！请简单介绍一下自己。"}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ 连接成功!")
            print(f"🤖 AI回复: {content[:100]}...")
            print(f"📊 Token使用: 提示 {data['usage']['prompt_tokens']}, 输出 {data['usage']['completion_tokens']}, 总计 {data['usage']['total_tokens']}")
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False
    
    print()
    
    # 测试 2: 中文对话
    print("📝 测试 2: 中文对话能力...")
    try:
        response = requests.post(
            f"{endpoint}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": "用一句话总结人工智能的重要性。"}
                ],
                "temperature": 0.5,
                "max_tokens": 100
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ 中文对话成功!")
            print(f"🤖 AI回复: {content}")
        else:
            print(f"❌ 中文对话失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试错误: {e}")
    
    print()
    
    # 测试 3: 代码能力
    print("📝 测试 3: 代码生成能力...")
    try:
        response = requests.post(
            f"{endpoint}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": "写一个Python函数，计算斐波那契数列的第n项。"}
                ],
                "temperature": 0.3,
                "max_tokens": 200
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ 代码生成成功!")
            print(f"🤖 AI回复:")
            print("-" * 40)
            print(content)
            print("-" * 40)
        else:
            print(f"❌ 代码生成失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试错误: {e}")
    
    print()
    print("=" * 60)
    print("✅ 所有测试完成!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_github_models_api()
    sys.exit(0 if success else 1)
