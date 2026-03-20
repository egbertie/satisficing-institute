#!/usr/bin/env python3
"""
Notion 高速同步脚本 - 并发处理
使用线程池和队列优化同步速度
"""
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import threading

NOTION_TOKEN = "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"
API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
WORKSPACE = Path("/root/.openclaw/workspace")
PARENT_ID = "31fa8a0e-2bba-81fa-b98a-d61da835051e"

# 统计
stats = {"total": 0, "success": 0, "failed": 0, "skipped": 0, "failed_list": []}
lock = threading.Lock()
existing_pages = set()

def api_call(method, endpoint, data=None):
    """API调用"""
    url = f"{API}/{endpoint}"
    try:
        if method == "POST":
            r = requests.post(url, headers=HEADERS, json=data, timeout=30)
        else:
            r = requests.get(url, headers=HEADERS, timeout=30)
        
        if r.status_code == 429:
            time.sleep(5)
            return api_call(method, endpoint, data)
        
        time.sleep(0.35)  # 速率限制
        
        if r.status_code in [200, 201]:
            return r.json()
        return {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_existing():
    """获取已存在页面"""
    result = api_call("GET", f"blocks/{PARENT_ID}/children?page_size=100")
    pages = set()
    if "results" in result:
        for block in result["results"]:
            if block.get("type") == "child_page":
                pages.add(block["child_page"]["title"])
    return pages

def read_file(filepath):
    """读取文件"""
    for enc in ['utf-8', 'gbk', 'latin1']:
        try:
            with open(filepath, 'r', encoding=enc, errors='ignore') as f:
                return f.read()[:8000]  # 限制内容大小
        except:
            pass
    return None

def sync_file(filepath):
    """同步单个文件"""
    filename = filepath.name
    name = filepath.stem[:100]
    rel_path = str(filepath.relative_to(WORKSPACE))
    
    # 检查是否已存在
    if name in existing_pages or filename in existing_pages:
        with lock:
            stats["skipped"] += 1
        return "skipped", filename
    
    # 读取内容
    content = read_file(filepath)
    if not content:
        with lock:
            stats["failed"] += 1
            stats["failed_list"].append({"file": rel_path, "reason": "读取失败"})
        return "failed", filename
    
    # 清理内容
    content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')[:1500]
    
    # 创建页面
    result = api_call("POST", "pages", {
        "parent": {"page_id": PARENT_ID},
        "properties": {"title": {"title": [{"text": {"content": name}}]}},
        "children": [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
        }]
    })
    
    if "id" in result:
        with lock:
            stats["success"] += 1
            existing_pages.add(name)
        return "success", filename
    else:
        with lock:
            stats["failed"] += 1
            stats["failed_list"].append({"file": rel_path, "reason": result.get("error", "Unknown")})
        return "failed", filename

def find_files():
    """查找所有文件"""
    exts = ['*.md', '*.html', '*.py', '*.json', '*.txt', '*.js', '*.css', '*.yml', '*.yaml']
    files = []
    for ext in exts:
        for f in WORKSPACE.rglob(ext):
            rel = str(f.relative_to(WORKSPACE))
            if any(x in rel for x in ['.git', 'node_modules', '__pycache__']):
                continue
            if '.notion' in f.name:
                continue
            files.append(f)
    return sorted(files)

def main():
    print("="*70)
    print("📚 Notion 高速同步")
    print("="*70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 查找文件
    print("\n1️⃣ 扫描文件...")
    files = find_files()
    stats["total"] = len(files)
    print(f"   发现 {len(files)} 个文件")
    
    # 获取已存在页面
    print("\n2️⃣ 获取已存在页面...")
    global existing_pages
    existing_pages = get_existing()
    print(f"   已存在: {len(existing_pages)} 个")
    
    # 开始同步
    print("\n3️⃣ 开始同步...")
    print("-"*70)
    
    start_time = time.time()
    completed = 0
    
    # 使用单线程顺序处理（由于API速率限制）
    for i, filepath in enumerate(files, 1):
        status, name = sync_file(filepath)
        completed += 1
        
        icon = {"success": "✅", "failed": "❌", "skipped": "⏭️"}[status]
        print(f"[{i}/{len(files)}] {icon} {name[:50]}")
        
        # 每50个显示进度
        if i % 50 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(files) - i) / rate if rate > 0 else 0
            print(f"\n💾 进度: {i}/{len(files)}, 速度: {rate:.1f}文件/秒, 预计剩余: {int(eta)}秒\n")
    
    # 报告
    elapsed = time.time() - start_time
    print("\n" + "="*70)
    print("📊 同步完成")
    print("="*70)
    print(f"总文件: {stats['total']}")
    print(f"✅ 成功: {stats['success']}")
    print(f"❌ 失败: {stats['failed']}")
    print(f"⏭️ 跳过: {stats['skipped']}")
    print(f"⏱️ 耗时: {int(elapsed//60)}分{int(elapsed%60)}秒")
    print(f"🚀 速度: {stats['total']/elapsed:.1f}文件/秒")
    
    # 保存报告
    report = {
        "time": datetime.now().isoformat(),
        "duration_seconds": elapsed,
        **stats,
        "notion_url": f"https://notion.so/{PARENT_ID.replace('-', '')}"
    }
    
    with open(WORKSPACE / "NOTION_FINAL_SYNC_REPORT.json", 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n报告: NOTION_FINAL_SYNC_REPORT.json")
    print(f"链接: {report['notion_url']}")
    
    return stats

if __name__ == "__main__":
    main()
