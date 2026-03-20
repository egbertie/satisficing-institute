"""
Jina AI API 测试脚本
搜索底座API：Embedding、Reader、ReRanker、分类器等

注册步骤:
1. 访问 https://jina.ai/?sui=apikey
2. 免费API密钥直接显示在页面，复制保存

免费额度 (每天):
- Embeddings: 500 RPM / 1M TPM
- r.reader: 200 RPM
- s.reader: 40 RPM
- Classifier: 200 RPM
- Segmenter: 200 RPM
- 无需信用卡，即时可用
"""

import requests
import os

# 从环境变量读取，或手动替换
JINA_API_KEY = os.getenv("JINA_API_KEY", "YOUR_JINA_API_KEY_HERE")

HEADERS = {
    "Authorization": f"Bearer {JINA_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def test_embeddings():
    """测试向量嵌入"""
    url = "https://api.jina.ai/v1/embeddings"
    data = {
        "model": "jina-embeddings-v3",
        "input": [
            "Jina AI是神经搜索专家",
            "向量嵌入用于语义搜索"
        ]
    }

    response = requests.post(url, json=data, headers=HEADERS)
    result = response.json()

    if "data" in result:
        print(f"✅ 生成 {len(result['data'])} 个向量")
        for item in result["data"]:
            vec = item["embedding"]
            print(f"  向量维度: {len(vec)}, 前3维: {vec[:3]}")
        print(f"Token使用: {result['usage']['total_tokens']}")
    else:
        print("错误:", result)

def test_reranker():
    """测试搜索结果重排序"""
    url = "https://api.jina.ai/v1/rerank"
    data = {
        "model": "jina-reranker-v2-base-multilingual",
        "query": "什么是机器学习？",
        "top_n": 2,
        "documents": [
            "机器学习是人工智能的一个分支",
            "Python是一种流行的编程语言",
            "深度学习是机器学习的一种方法"
        ]
    }

    response = requests.post(url, json=data, headers=HEADERS)
    result = response.json()

    if "results" in result:
        print("\n重排序结果:")
        for r in result["results"]:
            print(f"  [{r['relevance_score']:.2f}] {r['document']['text'][:30]}...")

def test_reader_url():
    """测试网页内容提取"""
    target_url = "https://github.com/about"
    url = f"https://r.jina.ai/http://{target_url}"

    # Reader API 不需要完整的headers
    headers = {"Authorization": f"Bearer {JINA_API_KEY}"}
    response = requests.get(url, headers=headers)

    print("\n网页提取 (r.reader):")
    content = response.text
    print(f"内容长度: {len(content)} 字符")
    print(f"前200字符:\n{content[:200]}...")

def test_search_reader():
    """测试搜索+阅读"""
    query = "Jina AI公司介绍"
    url = f"https://s.jina.ai/{requests.utils.quote(query)}"

    headers = {"Authorization": f"Bearer {JINA_API_KEY}"}
    response = requests.get(url, headers=headers)

    print("\n搜索阅读 (s.reader):")
    result = response.json()
    if "data" in result and len(result["data"]) > 0:
        item = result["data"][0]
        print(f"标题: {item['title']}")
        print(f"内容预览: {item['content'][:150]}...")

def test_classifier():
    """测试文本分类"""
    url = "https://api.jina.ai/v1/classify"
    data = {
        "model": "jina-embeddings-v3",
        "input": [
            "股票价格上涨了5%",
            "这部电影太精彩了",
            "新型电池技术突破"
        ],
        "labels": ["财经", "娱乐", "科技"]
    }

    response = requests.post(url, json=data, headers=HEADERS)
    result = response.json()

    if "data" in result:
        print("\n文本分类结果:")
        for item in result["data"]:
            print(f"  '{item['input']}' → {item['prediction']} (置信度: {item['score']:.2f})")

def test_segmenter():
    """测试文本分块"""
    url = "https://segment.jina.ai"
    data = {
        "content": "这是第一段。这是第二段，包含更多内容。这是第三段。",
        "return_chunks": True,
        "max_chunk_length": 100
    }

    response = requests.post(url, json=data, headers=HEADERS)
    result = response.json()

    if "data" in result:
        print("\n文本分块结果:")
        print(f"  Token数: {result['data']['num_tokens']}")
        print(f"  分块数: {result['data']['num_chunks']}")

def list_all_services():
    """列出Jina AI所有服务"""
    services = {
        "Embeddings": ("向量嵌入", "https://api.jina.ai/v1/embeddings"),
        "ReRanker": ("搜索结果重排序", "https://api.jina.ai/v1/rerank"),
        "r.reader": ("单网页内容提取", "https://r.jina.ai/http://URL"),
        "s.reader": ("搜索+阅读", "https://s.jina.ai/QUERY"),
        "Classifier": ("零样本分类", "https://api.jina.ai/v1/classify"),
        "Segmenter": ("文本分块", "https://segment.jina.ai"),
        "g.reader": ("事实核查", "https://g.jina.ai")
    }
    print("\nJina AI 所有服务:")
    for name, (desc, url) in services.items():
        print(f"  - {name}: {desc}")

if __name__ == "__main__":
    print("=" * 50)
    print("Jina AI API 测试")
    print("获取API Key: https://jina.ai/?sui=apikey")
    print("=" * 50)

    if JINA_API_KEY == "YOUR_JINA_API_KEY_HERE":
        print("\n⚠️ 请先设置 JINA_API_KEY 环境变量或修改脚本中的 API_KEY")
        print("获取方式: https://jina.ai/?sui=apikey (免费，即时可用)")
    else:
        print("\n开始测试各项服务...\n")

        test_embeddings()
        test_reranker()
        test_reader_url()
        test_search_reader()
        test_classifier()
        test_segmenter()
        list_all_services()

        print("\n✅ 所有测试完成!")
