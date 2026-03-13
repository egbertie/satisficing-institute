"""
Perplexity API 测试脚本
AI搜索增强对话，支持联网搜索

注册步骤:
1. 访问 https://www.perplexity.ai 注册账号
2. 访问 https://www.perplexity.ai/settings/api
3. 绑定信用卡 (Pro用户每月赠送$5免费积分)
4. 生成 API Key (格式: pplx-xxxxxxxx)

免费额度:
- Pro用户: 每月$5 API积分 (约300-500次调用)
"""

import requests
import os

# 从环境变量读取，或手动替换
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "YOUR_PERPLEXITY_API_KEY_HERE")

BASE_URL = "https://api.perplexity.ai/chat/completions"

def test_chat():
    """测试基础对话"""
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar",  # 基础联网模型
        "messages": [
            {"role": "system", "content": "你是一个 helpful 助手，请简洁回答。"},
            {"role": "user", "content": "今天有什么重要科技新闻？"}
        ],
        "max_tokens": 300
    }

    response = requests.post(BASE_URL, json=data, headers=headers)
    result = response.json()

    if "choices" in result:
        print("Perplexity 回复:")
        print(result["choices"][0]["message"]["content"])
        if "citations" in result:
            print(f"\n引用来源: {len(result['citations'])} 个")
    else:
        print("错误:", result)

def test_search():
    """测试深度搜索 (需要Pro)"""
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "user", "content": "深度分析2024年AI芯片市场格局"}
        ],
        "max_tokens": 1000
    }

    response = requests.post(BASE_URL, json=data, headers=headers)
    result = response.json()

    if "choices" in result:
        print("\n深度搜索回复:")
        content = result["choices"][0]["message"]["content"]
        print(content[:500] + "..." if len(content) > 500 else content)

def test_models():
    """列出推荐模型"""
    models = {
        "sonar": "基础联网模型，适合日常查询",
        "sonar-pro": "高级搜索，更强推理",
        "sonar-reasoning": "复杂推理任务"
    }
    print("\n可用模型:")
    for name, desc in models.items():
        print(f"  - {name}: {desc}")

if __name__ == "__main__":
    print("=" * 50)
    print("Perplexity API 测试")
    print("=" * 50)

    if PERPLEXITY_API_KEY == "YOUR_PERPLEXITY_API_KEY_HERE":
        print("\n⚠️ 请先设置 PERPLEXITY_API_KEY 环境变量或修改脚本中的 API_KEY")
        print("获取方式: https://www.perplexity.ai/settings/api")
    else:
        test_chat()
        test_search()
        test_models()
        print("\n✅ 测试完成!")
