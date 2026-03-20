"""
GitHub Models API 测试脚本
免费访问 GPT-4o, GPT-4o-mini, Llama-3.1, DeepSeek-R1 等模型

注册步骤:
1. 访问 https://github.com/marketplace/models
2. 点击 "Get early access" 申请早期访问权限 (约5天审核)
3. 创建 Personal Access Token (Settings → Developer settings → PAT)
4. 勾选 'models' 权限，生成并保存token

免费额度:
- GPT-4o: 10 RPM, 50 RPD
- GPT-4o-mini: 15 RPM, 150 RPD
"""

from openai import OpenAI
import os

# 从环境变量读取，或手动替换
GITHUB_PAT = os.getenv("GITHUB_MODELS_PAT", "YOUR_GITHUB_PAT_HERE")

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=GITHUB_PAT
)

def test_chat():
    """测试基础对话"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一个 helpful 助手。"},
            {"role": "user", "content": "你好！请用一句话介绍自己。"}
        ],
        max_tokens=100
    )
    print("GPT-4o 回复:")
    print(response.choices[0].message.content)
    print(f"\nToken使用: {response.usage.total_tokens}")

def test_streaming():
    """测试流式输出"""
    stream = client.chat.completions.create(
        model="gpt-4o-mini",  # 小模型响应更快
        messages=[
            {"role": "user", "content": "写一首关于编程的短诗"}
        ],
        stream=True,
        max_tokens=200
    )
    print("\n流式输出:")
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()

def test_models():
    """列出可用模型"""
    models = ["gpt-4o", "gpt-4o-mini", "Llama-3.1-8B", "DeepSeek-R1"]
    print("\n可用模型:")
    for m in models:
        print(f"  - {m}")

if __name__ == "__main__":
    print("=" * 50)
    print("GitHub Models API 测试")
    print("=" * 50)

    if GITHUB_PAT == "YOUR_GITHUB_PAT_HERE":
        print("\n⚠️ 请先设置 GITHUB_MODELS_PAT 环境变量或修改脚本中的 GITHUB_PAT")
        print("获取方式: https://github.com/marketplace/models")
    else:
        test_chat()
        test_streaming()
        test_models()
        print("\n✅ 测试完成!")
