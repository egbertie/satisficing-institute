#!/usr/bin/env python3
"""
Notion 完整同步脚本 - 批量处理所有文档
创建于: 2026-03-10
目标: 同步 /root/.openclaw/workspace/ 下所有文档到 Notion
"""
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Notion API 配置
NOTION_TOKEN = "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"
NOTION_API_URL = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 工作区路径
WORKSPACE_DIR = Path("/root/.openclaw/workspace")

# 同步统计
stats = {
    "start_time": datetime.now(),
    "total_files": 0,
    "success": 0,
    "failed": 0,
    "skipped": 0,
    "failed_files": [],
    "skipped_files": [],
    "synced_files": []
}

def notion_request(method, endpoint, data=None, max_retries=3):
    """发送 Notion API 请求，带重试机制"""
    url = f"{NOTION_API_URL}/{endpoint}"
    
    for attempt in range(max_retries):
        try:
            if method == "GET":
                response = requests.get(url, headers=HEADERS, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=HEADERS, json=data, timeout=30)
            elif method == "PATCH":
                response = requests.patch(url, headers=HEADERS, json=data, timeout=30)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")
            
            # 速率限制处理
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                print(f"    ⏱️ 速率限制，等待 {retry_after} 秒...")
                time.sleep(retry_after)
                continue
            
            # 正常延迟 350ms
            time.sleep(0.35)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                if attempt < max_retries - 1:
                    print(f"    ⚠️ 请求失败，重试 {attempt+1}/{max_retries}: {error_msg}")
                    time.sleep(1)
                    continue
                return {"error": error_msg}
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"    ⚠️ 请求异常，重试 {attempt+1}/{max_retries}: {e}")
                time.sleep(1)
                continue
            return {"error": str(e)}
    
    return {"error": "Max retries exceeded"}

def create_page(parent_id, title, content_blocks=None):
    """创建 Notion 页面"""
    data = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {
                "title": [{"text": {"content": title[:100]}}]  # 标题长度限制
            }
        }
    }
    
    if content_blocks:
        data["children"] = content_blocks[:100]  # Notion限制最多100个blocks
    
    return notion_request("POST", "pages", data)

def content_to_blocks(content, max_blocks=90):
    """将内容转换为 Notion blocks，优化处理"""
    blocks = []
    lines = content.split('\n')
    current_text = ""
    in_code_block = False
    code_content = ""
    code_language = "plain text"
    
    def flush_paragraph():
        nonlocal current_text
        if current_text.strip():
            # 限制文本长度
            text = current_text.strip()[:2000]
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            })
            current_text = ""
    
    for line in lines:
        stripped = line.strip()
        
        # 代码块处理
        if stripped.startswith('```'):
            if in_code_block:
                # 结束代码块
                flush_paragraph()
                if code_content.strip():
                    blocks.append({
                        "object": "block",
                        "type": "code",
                        "code": {
                            "rich_text": [{"type": "text", "text": {"content": code_content[:2000]}}],
                            "language": code_language if code_language in [
                                "python", "javascript", "json", "markdown", "html", 
                                "css", "bash", "plain text", "sql", "java", "cpp"
                            ] else "plain text"
                        }
                    })
                code_content = ""
                in_code_block = False
            else:
                # 开始代码块
                flush_paragraph()
                code_language = stripped[3:].strip() or "plain text"
                in_code_block = True
            continue
        
        if in_code_block:
            code_content += line + "\n"
            continue
        
        # 空行处理
        if not stripped:
            flush_paragraph()
            continue
        
        # 标题处理
        if stripped.startswith('# ') and not in_code_block:
            flush_paragraph()
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[2:][:2000]}}]
                }
            })
        elif stripped.startswith('## ') and not in_code_block:
            flush_paragraph()
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[3:][:2000]}}]
                }
            })
        elif stripped.startswith('### ') and not in_code_block:
            flush_paragraph()
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[4:][:2000]}}]
                }
            })
        # 列表处理
        elif stripped.startswith('- ') or stripped.startswith('* '):
            flush_paragraph()
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[2:][:2000]}}]
                }
            })
        elif len(stripped) > 2 and stripped[0].isdigit() and stripped[1] == '.':
            flush_paragraph()
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[3:][:2000]}}]
                }
            })
        else:
            current_text += line + "\n"
    
    # 处理剩余内容
    flush_paragraph()
    
    # 限制 block 数量
    if len(blocks) > max_blocks:
        truncated = blocks[:max_blocks-1]
        truncated.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": "⚠️ 内容过长，已截断显示。请查看完整文件。"}}],
                "icon": {"emoji": "⚠️"}
            }
        })
        return truncated
    
    return blocks

def read_file_content(file_path):
    """读取文件内容，处理不同编码"""
    encodings = ['utf-8', 'gbk', 'latin1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                return f.read()
        except Exception:
            continue
    return None

def get_file_type(file_path):
    """获取文件类型分类"""
    ext = file_path.suffix.lower()
    type_map = {
        '.md': 'Markdown',
        '.html': 'HTML',
        '.py': 'Python',
        '.json': 'JSON',
        '.txt': 'Text',
        '.js': 'JavaScript',
        '.css': 'CSS',
        '.yml': 'YAML',
        '.yaml': 'YAML'
    }
    return type_map.get(ext, 'Other')

def find_all_files():
    """查找所有需要同步的文件"""
    extensions = ['*.md', '*.html', '*.py', '*.json', '*.txt', '*.js', '*.css', '*.yml', '*.yaml']
    all_files = []
    
    for ext in extensions:
        for file_path in WORKSPACE_DIR.rglob(ext):
            # 跳过排除的目录
            rel_str = str(file_path.relative_to(WORKSPACE_DIR))
            skip = False
            for skip_dir in ['.git', 'node_modules', '__pycache__', '.pytest_cache']:
                if skip_dir in rel_str:
                    skip = True
                    break
            if skip:
                continue
            
            # 跳过同步脚本自身和进度文件
            if file_path.name.startswith('.notion_sync') or 'notion_sync' in file_path.name.lower():
                continue
            
            all_files.append(file_path)
    
    return sorted(all_files)

def get_existing_pages(parent_page_id):
    """获取已存在的页面列表"""
    existing = {}
    cursor = None
    
    while True:
        data = {"page_size": 100}
        if cursor:
            data["start_cursor"] = cursor
        
        result = notion_request("POST", f"blocks/{parent_page_id}/children", data)
        
        if "error" in result:
            break
        
        for block in result.get("results", []):
            if block.get("type") == "child_page":
                title = block.get("child_page", {}).get("title", "")
                existing[title] = block["id"]
        
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
    
    return existing

def sync_file(file_path, parent_page_id, existing_pages):
    """同步单个文件"""
    rel_path = file_path.relative_to(WORKSPACE_DIR)
    file_name = file_path.name
    file_stem = file_path.stem
    file_type = get_file_type(file_path)
    
    # 检查是否已存在
    if file_name in existing_pages or file_stem in existing_pages:
        stats["skipped"] += 1
        stats["skipped_files"].append(str(rel_path))
        return "skipped"
    
    # 读取文件内容
    content = read_file_content(file_path)
    if content is None:
        stats["failed"] += 1
        stats["failed_files"].append({"file": str(rel_path), "reason": "无法读取文件内容"})
        return "failed"
    
    # 准备页面标题和内容
    title = file_stem[:100]
    
    # 添加文件元信息
    meta_info = f"📄 文件路径: {rel_path}\n📁 文件类型: {file_type}\n📊 文件大小: {file_path.stat().st_size} bytes\n\n---\n\n"
    
    if file_type == 'Markdown':
        full_content = content
    else:
        full_content = meta_info + content
    
    # 转换为 blocks
    blocks = content_to_blocks(full_content)
    
    # 创建页面
    result = create_page(parent_page_id, title, blocks)
    
    if "error" in result:
        stats["failed"] += 1
        stats["failed_files"].append({"file": str(rel_path), "reason": result["error"]})
        return "failed"
    else:
        stats["success"] += 1
        stats["synced_files"].append({
            "file": str(rel_path),
            "notion_url": result.get("url", ""),
            "notion_id": result.get("id", "")
        })
        return "success"

def batch_sync(files, parent_page_id, existing_pages, batch_size=50):
    """批量同步文件"""
    total = len(files)
    
    for i, file_path in enumerate(files, 1):
        result = sync_file(file_path, parent_page_id, existing_pages)
        
        if result == "success":
            print(f"  [{i}/{total}] ✅ {file_path.name}")
        elif result == "skipped":
            print(f"  [{i}/{total}] ⏭️ {file_path.name} (已存在)")
        else:
            print(f"  [{i}/{total}] ❌ {file_path.name}")
        
        # 每 batch_size 个文件保存一次进度
        if i % batch_size == 0:
            save_progress()
            print(f"\n  💾 已保存进度 ({i}/{total})\n")

def save_progress():
    """保存同步进度"""
    progress = {
        "sync_time": datetime.now().isoformat(),
        "stats": {
            "total": stats["total_files"],
            "success": stats["success"],
            "failed": stats["failed"],
            "skipped": stats["skipped"]
        },
        "failed_files": stats["failed_files"],
        "synced_files": stats["synced_files"][-50:]  # 只保留最近50个
    }
    
    progress_file = WORKSPACE_DIR / ".notion_complete_sync_progress.json"
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def generate_report():
    """生成同步报告"""
    end_time = datetime.now()
    duration = (end_time - stats["start_time"]).total_seconds()
    
    report = {
        "report_title": "Notion 完整同步报告",
        "sync_time": end_time.isoformat(),
        "duration_seconds": duration,
        "duration_formatted": f"{int(duration // 60)}分{int(duration % 60)}秒",
        "workspace": "/root/.openclaw/workspace",
        "notion_workspace": "满意解研究所",
        "statistics": {
            "total_files": stats["total_files"],
            "success": stats["success"],
            "failed": stats["failed"],
            "skipped": stats["skipped"],
            "success_rate": f"{(stats['success'] / stats['total_files'] * 100):.1f}%" if stats["total_files"] > 0 else "0%"
        },
        "file_types": {},
        "failed_files": stats["failed_files"],
        "missing_files": stats["failed_files"]  # 缺失清单
    }
    
    # 统计文件类型
    for synced in stats["synced_files"]:
        ext = Path(synced["file"]).suffix.lower()
        report["file_types"][ext] = report["file_types"].get(ext, 0) + 1
    
    return report

def main():
    print("=" * 70)
    print("📚 Notion 完整同步任务")
    print("=" * 70)
    print(f"\n⏰ 开始时间: {stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 目标: 同步工作区所有文档到 Notion")
    
    # 1. 获取所有文件
    print("\n1️⃣ 扫描工作区文件...")
    all_files = find_all_files()
    stats["total_files"] = len(all_files)
    print(f"   ✅ 发现 {len(all_files)} 个文件")
    
    # 按类型统计
    type_count = defaultdict(int)
    for f in all_files:
        type_count[get_file_type(f)] += 1
    print(f"   📊 文件类型分布:")
    for ft, count in sorted(type_count.items(), key=lambda x: -x[1]):
        print(f"      • {ft}: {count}个")
    
    # 2. 查找或创建父页面
    print("\n2️⃣ 连接 Notion...")
    search_result = notion_request("POST", "search", {"query": "满意解研究所知识库", "page_size": 10})
    
    parent_page_id = None
    if "error" not in search_result and search_result.get("results"):
        for result in search_result["results"]:
            if result.get("object") == "page":
                title = result.get("properties", {}).get("title", {}).get("title", [{}])[0].get("text", {}).get("content", "")
                if "知识库" in title:
                    parent_page_id = result["id"]
                    print(f"   ✅ 找到现有知识库页面: {title}")
                    break
    
    if not parent_page_id:
        # 创建新父页面
        search_result = notion_request("POST", "search", {"query": "", "page_size": 10})
        if "error" not in search_result and search_result.get("results"):
            root_page = search_result["results"][0]
            root_id = root_page["id"]
            
            result = create_page(root_id, "📚 满意解研究所知识库", [{
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"完整文档同步\n创建于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n文件总数: {len(all_files)}"}}]
                }
            }])
            
            if "error" not in result:
                parent_page_id = result["id"]
                print(f"   ✅ 创建新知识库页面")
            else:
                print(f"   ❌ 无法创建父页面: {result['error']}")
                return
    
    # 3. 获取已存在的页面
    print("\n3️⃣ 检查已存在页面...")
    existing_pages = get_existing_pages(parent_page_id)
    print(f"   ✅ 发现 {len(existing_pages)} 个已存在页面")
    
    # 4. 开始同步
    print("\n4️⃣ 开始同步文件...")
    print("-" * 70)
    batch_sync(all_files, parent_page_id, existing_pages, batch_size=50)
    
    # 5. 生成报告
    print("\n" + "=" * 70)
    print("📊 同步完成报告")
    print("=" * 70)
    
    report = generate_report()
    
    print(f"\n📈 统计摘要:")
    print(f"   • 总文件数: {report['statistics']['total_files']}")
    print(f"   • ✅ 成功同步: {report['statistics']['success']}")
    print(f"   • ❌ 失败数量: {report['statistics']['failed']}")
    print(f"   • ⏭️ 跳过(已存在): {report['statistics']['skipped']}")
    print(f"   • 📈 成功率: {report['statistics']['success_rate']}")
    print(f"   • ⏱️ 耗时: {report['duration_formatted']}")
    
    print(f"\n📁 文件类型分布:")
    for ext, count in sorted(report['file_types'].items(), key=lambda x: -x[1]):
        print(f"   • {ext}: {count}个")
    
    if report['failed_files']:
        print(f"\n❌ 失败的文件 ({len(report['failed_files'])}个):")
        for item in report['failed_files'][:20]:  # 只显示前20个
            print(f"   • {item['file']}")
            print(f"     原因: {item['reason'][:80]}")
        if len(report['failed_files']) > 20:
            print(f"   ... 还有 {len(report['failed_files']) - 20} 个失败文件")
    
    # 保存详细报告
    report_file = WORKSPACE_DIR / "NOTION_COMPLETE_SYNC_REPORT.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 详细报告已保存: {report_file}")
    print(f"🔗 Notion 知识库: https://notion.so/{parent_page_id.replace('-', '')}")
    
    # 保存 Markdown 格式报告
    md_report = f"""# Notion 完整同步报告

## 📋 基本信息

| 项目 | 内容 |
|------|------|
| 同步时间 | {report['sync_time']} |
| 工作区 | {report['workspace']} |
| Notion工作空间 | {report['notion_workspace']} |
| 耗时 | {report['duration_formatted']} |

## 📈 同步统计

| 指标 | 数值 |
|------|------|
| 总文件数 | {report['statistics']['total_files']} |
| 成功同步 | {report['statistics']['success']} ✅ |
| 失败数量 | {report['statistics']['failed']} ❌ |
| 跳过(已存在) | {report['statistics']['skipped']} ⏭️ |
| 成功率 | {report['statistics']['success_rate']} |

## 📁 文件类型分布

"""
    for ext, count in sorted(report['file_types'].items(), key=lambda x: -x[1]):
        md_report += f"- **{ext}**: {count}个\n"
    
    if report['failed_files']:
        md_report += f"\n## ❌ 失败文件清单 ({len(report['failed_files'])}个)\n\n"
        for item in report['failed_files']:
            md_report += f"- `{item['file']}`\n  - 原因: {item['reason']}\n"
    
    md_report += f"\n---\n*报告生成时间: {report['sync_time']}*"
    
    md_report_file = WORKSPACE_DIR / "NOTION_COMPLETE_SYNC_REPORT.md"
    with open(md_report_file, 'w', encoding='utf-8') as f:
        f.write(md_report)
    
    print(f"📝 Markdown 报告已保存: {md_report_file}")
    
    return report

if __name__ == "__main__":
    main()
