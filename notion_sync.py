#!/usr/bin/env python3
"""
Markdown 文件同步到 Notion 知识库
"""
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

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

# 统计信息
stats = {
    "success": 0,
    "failed": 0,
    "failed_files": [],
    "start_time": datetime.now()
}

def notion_request(method, endpoint, data=None):
    """发送 Notion API 请求，带速率限制"""
    url = f"{NOTION_API_URL}/{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=HEADERS, json=data)
        else:
            raise ValueError(f"不支持的 HTTP 方法: {method}")
        
        # 速率限制：每个请求间隔 350ms
        time.sleep(0.35)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            print(f"  ❌ API 错误: {error_msg}")
            return {"error": error_msg}
    except Exception as e:
        print(f"  ❌ 请求异常: {e}")
        return {"error": str(e)}

def create_page(parent_id, title, content_blocks=None, is_database=False):
    """创建 Notion 页面"""
    data = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        }
    }
    
    if content_blocks:
        data["children"] = content_blocks
    
    return notion_request("POST", "pages", data)

def create_database(parent_id, title):
    """创建数据库页面"""
    data = {
        "parent": {"page_id": parent_id},
        "title": [{"text": {"content": title}}],
        "properties": {
            "标题": {"title": {}},
            "创建时间": {"date": {}},
            "标签": {"multi_select": {"options": []}}
        }
    }
    return notion_request("POST", "databases", data)

def split_content_to_blocks(content, max_length=2000):
    """将内容分割成 Notion blocks"""
    blocks = []
    lines = content.split('\n')
    current_chunk = ""
    
    for line in lines:
        # 检查添加这行后是否超过限制
        if len(current_chunk) + len(line) + 1 > max_length:
            # 保存当前块
            if current_chunk.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": current_chunk}}]
                    }
                })
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"
    
    # 添加最后一块
    if current_chunk.strip():
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": current_chunk}}]
            }
        })
    
    return blocks

def content_to_blocks(content):
    """将 Markdown 内容转换为 Notion blocks"""
    blocks = []
    lines = content.split('\n')
    current_paragraph = ""
    
    for line in lines:
        stripped = line.strip()
        
        # 空行处理
        if not stripped:
            if current_paragraph.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": current_paragraph.strip()}}]
                    }
                })
                current_paragraph = ""
            continue
        
        # 标题处理
        if stripped.startswith('# '):
            if current_paragraph.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": current_paragraph.strip()}}]
                    }
                })
                current_paragraph = ""
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[2:]}}]
                }
            })
        elif stripped.startswith('## '):
            if current_paragraph.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": current_paragraph.strip()}}]
                    }
                })
                current_paragraph = ""
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[3:]}}]
                }
            })
        elif stripped.startswith('### '):
            if current_paragraph.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": current_paragraph.strip()}}]
                    }
                })
                current_paragraph = ""
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[4:]}}]
                }
            })
        # 列表处理
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if current_paragraph.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": current_paragraph.strip()}}]
                    }
                })
                current_paragraph = ""
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[2:]}}]
                }
            })
        elif stripped.startswith('1. ') or stripped.startswith('2. ') or stripped.startswith('3. '):
            if current_paragraph.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": current_paragraph.strip()}}]
                    }
                })
                current_paragraph = ""
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[3:]}}]
                }
            })
        # 代码块处理
        elif stripped.startswith('```'):
            if current_paragraph.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": current_paragraph.strip()}}]
                    }
                })
                current_paragraph = ""
            # 简化的代码块处理（实际上应该收集多行）
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
        else:
            current_paragraph += line + "\n"
    
    # 添加最后一段
    if current_paragraph.strip():
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": current_paragraph.strip()}}]
            }
        })
    
    # 限制 blocks 数量（Notion API 限制）
    if len(blocks) > 100:
        # 合并过多的段落
        condensed_blocks = []
        current_text = ""
        for block in blocks:
            if block["type"] == "paragraph":
                for text_item in block["paragraph"]["rich_text"]:
                    current_text += text_item["text"]["content"] + "\n"
                if len(current_text) > 1500:
                    condensed_blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": current_text[:1500]}}]
                        }
                    })
                    current_text = current_text[1500:]
            else:
                if current_text.strip():
                    condensed_blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": current_text.strip()[:1500]}}]
                        }
                    })
                    current_text = ""
                condensed_blocks.append(block)
        
        if current_text.strip():
            condensed_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": current_text.strip()[:1500]}}]
                }
            })
        
        blocks = condensed_blocks[:100]  # 最多100个 blocks
    
    return blocks

def get_all_markdown_files():
    """获取所有 Markdown 文件"""
    md_files = []
    for path in WORKSPACE_DIR.rglob("*.md"):
        # 跳过 .git 目录，但保留 .config 目录
        # 注意：路径中包含 .openclaw 是正常的工作区路径，不应跳过
        rel_parts = path.relative_to(WORKSPACE_DIR).parts
        if any(part.startswith('.') and part not in ['.config'] for part in rel_parts):
            continue
        # 排除脚本自身
        if path.name == "notion_sync.py" or path.name == "notion_sync_report.json":
            continue
        md_files.append(path)
    return sorted(md_files)

def get_relative_path(file_path):
    """获取相对于工作区的路径"""
    return file_path.relative_to(WORKSPACE_DIR)

def main():
    print("=" * 60)
    print("📚 Markdown 文件同步到 Notion 知识库")
    print("=" * 60)
    
    # 1. 搜索用户的工作区
    print("\n1️⃣ 搜索可用工作区...")
    search_result = notion_request("POST", "search", {"query": ""})
    
    if "error" in search_result:
        print(f"  ❌ 搜索失败: {search_result['error']}")
        return
    
    print(f"  ✅ 找到 {len(search_result.get('results', []))} 个工作区/页面")
    
    # 2. 创建父页面
    print("\n2️⃣ 创建父页面 '📚 满意解研究所知识库'...")
    
    # 使用第一个可用页面作为父页面
    available_pages = [r for r in search_result.get('results', []) if r.get('object') == 'page']
    if not available_pages:
        print("  ❌ 未找到可用页面，请确保 Notion 中有至少一个页面")
        return
    
    # 使用第一个可用页面创建我们的父页面
    root_parent_id = available_pages[0]['id']
    
    parent_page = create_page(
        root_parent_id,
        "📚 满意解研究所知识库",
        [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "本知识库存储满意解研究所的所有 Markdown 文档，按目录结构自动组织。\n\n同步时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}]
            }
        }]
    )
    
    if "error" in parent_page:
        print(f"  ❌ 创建父页面失败: {parent_page['error']}")
        return
    
    parent_page_id = parent_page['id']
    print(f"  ✅ 父页面创建成功 (ID: {parent_page_id})")
    
    # 3. 获取所有 Markdown 文件
    print("\n3️⃣ 扫描 Markdown 文件...")
    md_files = get_all_markdown_files()
    print(f"  ✅ 找到 {len(md_files)} 个 Markdown 文件")
    
    # 4. 按目录组织文件
    print("\n4️⃣ 按目录结构组织...")
    
    # 创建目录映射
    folder_pages = {}
    
    for md_file in md_files:
        rel_path = get_relative_path(md_file)
        parent_dirs = list(rel_path.parent.parts)
        
        # 创建目录层级
        current_parent_id = parent_page_id
        current_path = ""
        
        for dir_name in parent_dirs:
            if dir_name == '.':
                continue
            current_path = f"{current_path}/{dir_name}" if current_path else dir_name
            
            if current_path not in folder_pages:
                # 创建目录页面
                folder_page = create_page(
                    current_parent_id,
                    f"📁 {dir_name}",
                    [{
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": f"目录: {current_path}"}}]
                        }
                    }]
                )
                
                if "error" not in folder_page:
                    folder_pages[current_path] = folder_page['id']
                    print(f"  📁 创建目录: {current_path}")
                else:
                    print(f"  ⚠️ 目录创建失败: {current_path}")
                    continue
            
            current_parent_id = folder_pages.get(current_path, parent_page_id)
    
    print(f"  ✅ 创建 {len(folder_pages)} 个目录页面")
    
    # 5. 同步文件
    print("\n5️⃣ 开始同步文件...")
    print("-" * 60)
    
    for idx, md_file in enumerate(md_files, 1):
        rel_path = get_relative_path(md_file)
        parent_dirs = list(rel_path.parent.parts)
        
        # 确定父页面 ID
        if parent_dirs and parent_dirs[0] != '.':
            dir_path = "/".join(parent_dirs)
            target_parent_id = folder_pages.get(dir_path, parent_page_id)
        else:
            target_parent_id = parent_page_id
        
        # 读取文件内容
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            stats["failed"] += 1
            stats["failed_files"].append({"file": str(rel_path), "reason": f"读取失败: {e}"})
            print(f"  [{idx}/{len(md_files)}] ❌ {rel_path} - 读取失败")
            continue
        
        # 准备页面标题（去掉 .md 后缀）
        title = rel_path.stem
        
        # 转换内容为 blocks
        blocks = content_to_blocks(content)
        
        # 创建页面
        result = create_page(target_parent_id, title, blocks)
        
        if "error" not in result:
            stats["success"] += 1
            print(f"  [{idx}/{len(md_files)}] ✅ {rel_path}")
        else:
            stats["failed"] += 1
            error_msg = result.get('error', 'Unknown error')
            stats["failed_files"].append({"file": str(rel_path), "reason": error_msg})
            print(f"  [{idx}/{len(md_files)}] ❌ {rel_path} - {error_msg[:50]}")
    
    # 6. 生成报告
    print("\n" + "=" * 60)
    print("📊 同步报告")
    print("=" * 60)
    
    end_time = datetime.now()
    duration = (end_time - stats["start_time"]).total_seconds()
    
    print(f"\n📈 统计信息:")
    print(f"  • 总文件数: {len(md_files)}")
    print(f"  • 成功同步: {stats['success']}")
    print(f"  • 失败数量: {stats['failed']}")
    print(f"  • 目录页面: {len(folder_pages)}")
    print(f"  • 耗时: {duration:.1f} 秒")
    print(f"  • 平均速度: {len(md_files)/duration:.1f} 文件/秒")
    
    print(f"\n📁 知识库结构:")
    print(f"  📚 满意解研究所知识库")
    for folder_path in sorted(folder_pages.keys()):
        depth = folder_path.count('/')
        indent = "  " + "  " * depth
        folder_name = folder_path.split('/')[-1]
        print(f"{indent}📁 {folder_name}")
    
    if stats["failed_files"]:
        print(f"\n❌ 失败的文件 ({len(stats['failed_files'])}):")
        for item in stats["failed_files"]:
            print(f"  • {item['file']}")
            print(f"    原因: {item['reason'][:80]}...")
    
    print(f"\n🔗 Notion 父页面 ID: {parent_page_id}")
    print(f"🌐 访问链接: https://notion.so/{parent_page_id.replace('-', '')}")
    
    # 保存详细报告
    report = {
        "sync_time": datetime.now().isoformat(),
        "duration_seconds": duration,
        "total_files": len(md_files),
        "success_count": stats["success"],
        "failed_count": stats["failed"],
        "folder_count": len(folder_pages),
        "parent_page_id": parent_page_id,
        "failed_files": stats["failed_files"],
        "folder_structure": list(folder_pages.keys())
    }
    
    report_path = WORKSPACE_DIR / "notion_sync_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 详细报告已保存: {report_path}")

if __name__ == "__main__":
    main()
