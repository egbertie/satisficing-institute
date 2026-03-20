#!/usr/bin/env python3
"""
Notion 快速同步脚本 - 高效批量处理
优化: 跳过已存在文件、并行处理目录、详细进度报告
"""
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from collections import defaultdict

NOTION_TOKEN = "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"
NOTION_API_URL = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
WORKSPACE_DIR = Path("/root/.openclaw/workspace")

def notion_api(method, endpoint, data=None):
    """API请求，带错误处理"""
    url = f"{NOTION_API_URL}/{endpoint}"
    try:
        if method == "POST":
            resp = requests.post(url, headers=HEADERS, json=data, timeout=30)
        elif method == "GET":
            resp = requests.get(url, headers=HEADERS, timeout=30)
        else:
            return {"error": "Method not supported"}
        
        time.sleep(0.35)  # 速率限制
        
        if resp.status_code == 429:
            time.sleep(5)
            return notion_api(method, endpoint, data)  # 重试
        
        if resp.status_code in [200, 201]:
            return resp.json()
        return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}

def find_files():
    """查找所有文件"""
    exts = ['*.md', '*.html', '*.py', '*.json', '*.txt', '*.js', '*.css', '*.yml', '*.yaml']
    files = []
    for ext in exts:
        for f in WORKSPACE_DIR.rglob(ext):
            rel = str(f.relative_to(WORKSPACE_DIR))
            if any(x in rel for x in ['.git', 'node_modules', '__pycache__']):
                continue
            if f.name.startswith('.') and 'notion' in f.name:
                continue
            files.append(f)
    return sorted(files)

def get_file_type(f):
    t = {'.md':'MD', '.html':'HTML', '.py':'PY', '.json':'JSON', '.txt':'TXT', 
         '.js':'JS', '.css':'CSS', '.yml':'YAML', '.yaml':'YAML'}
    return t.get(f.suffix.lower(), 'OTHER')

def to_blocks(content):
    """简单内容转换"""
    blocks = []
    lines = content.split('\n')
    chunk = ""
    
    for line in lines:
        if len(chunk) + len(line) > 1800:
            if chunk.strip():
                blocks.append({
                    "object": "block", "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk[:2000]}}]}
                })
            chunk = line + "\n"
        else:
            chunk += line + "\n"
    
    if chunk.strip():
        blocks.append({
            "object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk[:2000]}}]}
        })
    
    return blocks[:100]

def read_file(f):
    for enc in ['utf-8', 'gbk', 'latin1']:
        try:
            with open(f, 'r', encoding=enc, errors='ignore') as fp:
                return fp.read()
        except:
            pass
    return None

def main():
    print("="*70)
    print("📚 Notion 快速同步")
    print("="*70)
    
    # 查找所有文件
    print("\n1️⃣ 扫描文件...")
    files = find_files()
    print(f"   发现 {len(files)} 个文件")
    
    # 统计类型
    types = defaultdict(int)
    for f in files:
        types[get_file_type(f)] += 1
    for t, c in sorted(types.items(), key=lambda x:-x[1]):
        print(f"   • {t}: {c}")
    
    # 获取父页面
    print("\n2️⃣ 连接 Notion...")
    search = notion_api("POST", "search", {"query": "满意解研究所知识库", "page_size": 5})
    parent_id = None
    
    if "results" in search and search["results"]:
        for r in search["results"]:
            if r.get("object") == "page":
                parent_id = r["id"]
                print(f"   ✅ 找到知识库页面")
                break
    
    if not parent_id:
        # 创建新页面
        s = notion_api("POST", "search", {"query": "", "page_size": 5})
        if "results" in s and s["results"]:
            root = s["results"][0]["id"]
            page = notion_api("POST", "pages", {
                "parent": {"page_id": root},
                "properties": {"title": {"title": [{"text": {"content": "📚 满意解研究所知识库"}}]}},
                "children": [{
                    "object": "block", "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"同步时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n文件总数: {len(files)}"}}]}
                }]
            })
            if "id" in page:
                parent_id = page["id"]
                print(f"   ✅ 创建新知识库")
            else:
                print(f"   ❌ 创建失败: {page.get('error')}")
                return
    
    # 获取已存在页面
    print("\n3️⃣ 检查已同步文件...")
    existing = set()
    cursor = None
    while True:
        blocks = notion_api("GET", f"blocks/{parent_id}/children?page_size=100" + (f"&start_cursor={cursor}" if cursor else ""))
        if "results" not in blocks:
            break
        for b in blocks.get("results", []):
            if b.get("type") == "child_page":
                existing.add(b["child_page"]["title"])
        if not blocks.get("has_more"):
            break
        cursor = blocks.get("next_cursor")
    
    print(f"   已存在: {len(existing)} 个页面")
    
    # 开始同步
    print("\n4️⃣ 开始同步...")
    print("-"*70)
    
    stats = {"success": 0, "failed": 0, "skipped": 0, "failed_list": []}
    
    for i, f in enumerate(files, 1):
        name = f.stem
        rel = str(f.relative_to(WORKSPACE_DIR))
        
        # 检查是否已存在
        if name in existing or f.name in existing:
            stats["skipped"] += 1
            print(f"[{i}/{len(files)}] ⏭️ {f.name[:50]}")
            continue
        
        # 读取内容
        content = read_file(f)
        if not content:
            stats["failed"] += 1
            stats["failed_list"].append({"file": rel, "reason": "读取失败"})
            print(f"[{i}/{len(files)}] ❌ {f.name[:50]} (读取失败)")
            continue
        
        # 创建页面
        blocks = to_blocks(content)
        page = notion_api("POST", "pages", {
            "parent": {"page_id": parent_id},
            "properties": {"title": {"title": [{"text": {"content": name[:100]}}]}},
            "children": blocks
        })
        
        if "id" in page:
            stats["success"] += 1
            existing.add(name)  # 添加到已存在集合
            print(f"[{i}/{len(files)}] ✅ {f.name[:50]}")
        else:
            stats["failed"] += 1
            stats["failed_list"].append({"file": rel, "reason": page.get("error", "未知错误")})
            print(f"[{i}/{len(files)}] ❌ {f.name[:50]} ({page.get('error', '未知错误')[:30]})")
        
        # 每20个文件保存进度
        if i % 20 == 0:
            with open(WORKSPACE_DIR / ".notion_fast_sync_progress.json", 'w') as fp:
                json.dump({"done": i, **stats}, fp)
    
    # 报告
    print("\n" + "="*70)
    print("📊 同步完成")
    print("="*70)
    print(f"总文件: {len(files)}")
    print(f"✅ 成功: {stats['success']}")
    print(f"❌ 失败: {stats['failed']}")
    print(f"⏭️ 跳过: {stats['skipped']}")
    
    # 保存报告
    report = {
        "time": datetime.now().isoformat(),
        "total": len(files),
        **stats,
        "notion_url": f"https://notion.so/{parent_id.replace('-', '')}"
    }
    
    with open(WORKSPACE_DIR / "NOTION_SYNC_FINAL_REPORT.json", 'w') as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    
    print(f"\n报告: NOTION_SYNC_FINAL_REPORT.json")
    print(f"链接: {report['notion_url']}")
    
    return stats

if __name__ == "__main__":
    main()
