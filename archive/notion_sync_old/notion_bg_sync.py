#!/usr/bin/env python3
"""
Notion 后台同步脚本 - 无交互式输出
将所有文件同步到Notion，记录详细日志
"""
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

NOTION_TOKEN = "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"
API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
WORKSPACE = Path("/root/.openclaw/workspace")
PARENT_ID = "31fa8a0e-2bba-81fa-b98a-d61da835051e"
LOG_FILE = WORKSPACE / ".notion_bg_sync.log"
REPORT_FILE = WORKSPACE / "NOTION_BG_SYNC_REPORT.json"

def log(msg):
    """写日志"""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} {msg}\n")

def api_call(method, endpoint, data=None, retries=3):
    """API调用"""
    url = f"{API}/{endpoint}"
    for attempt in range(retries):
        try:
            if method == "POST":
                r = requests.post(url, headers=HEADERS, json=data, timeout=30)
            else:
                r = requests.get(url, headers=HEADERS, timeout=30)
            
            if r.status_code == 429:
                time.sleep(5)
                continue
            
            time.sleep(0.35)  # 速率限制
            
            if r.status_code in [200, 201]:
                return r.json()
            return {"error": f"HTTP {r.status_code}"}
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            return {"error": str(e)}
    return {"error": "Max retries"}

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
                return f.read()[:5000]
        except:
            pass
    return None

def sync_file(filepath, existing):
    """同步单个文件"""
    filename = filepath.name
    name = filepath.stem[:100]
    rel_path = str(filepath.relative_to(WORKSPACE))
    
    # 检查是否已存在
    if name in existing or filename in existing:
        return "skipped", rel_path
    
    # 读取内容
    content = read_file(filepath)
    if not content:
        return "failed", rel_path, "读取失败"
    
    # 清理内容
    content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')[:1200]
    
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
        existing.add(name)
        return "success", rel_path
    else:
        return "failed", rel_path, result.get("error", "Unknown")

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
    log("="*50)
    log("开始后台同步")
    log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 清空日志
    with open(LOG_FILE, 'w') as f:
        f.write("")
    
    # 查找文件
    files = find_files()
    log(f"发现 {len(files)} 个文件")
    
    # 获取已存在页面
    existing = get_existing()
    log(f"已存在 {len(existing)} 个页面")
    
    # 同步统计
    stats = {"total": len(files), "success": 0, "failed": 0, "skipped": 0, "failed_list": []}
    
    # 开始同步
    for i, filepath in enumerate(files, 1):
        result = sync_file(filepath, existing)
        
        if result[0] == "success":
            stats["success"] += 1
            if i % 20 == 0:
                log(f"[{i}/{len(files)}] 成功 {stats['success']}, 失败 {stats['failed']}, 跳过 {stats['skipped']}")
        elif result[0] == "failed":
            stats["failed"] += 1
            stats["failed_list"].append({"file": result[1], "reason": result[2] if len(result) > 2 else "Unknown"})
        else:
            stats["skipped"] += 1
    
    # 保存报告
    report = {
        "sync_time": datetime.now().isoformat(),
        **stats,
        "notion_url": f"https://notion.so/{PARENT_ID.replace('-', '')}"
    }
    
    with open(REPORT_FILE, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    log(f"同步完成")
    log(f"总计: {stats['total']}, 成功: {stats['success']}, 失败: {stats['failed']}, 跳过: {stats['skipped']}")
    log(f"报告: {REPORT_FILE}")

if __name__ == "__main__":
    main()
