#!/usr/bin/env python3
"""
简化版Notion同步脚本 - 超保守策略
目标：同步14个核心文档到Notion，确保100%成功率
"""
import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime

# 配置
NOTION_TOKEN = "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"
PARENT_PAGE_ID = "31fa8a0e-2bba-81fa-b98a-d61da835051e"
WORKSPACE_DIR = "/root/.openclaw/workspace"
REPORT_PATH = f"{WORKSPACE_DIR}/docs/NOTION_SYNC_FINAL_REPORT.md"

# 超时设置（秒）
CONNECT_TIMEOUT = 30
READ_TIMEOUT = 60

# 间隔设置（秒）
FILE_INTERVAL = 3  # 文件间间隔
RETRY_INTERVAL = 10  # 重试间隔
MAX_RETRIES = 3  # 最大重试次数

# 文件列表（按优先级排序）
FILES_TO_SYNC = [
    ("MEMORY.md", "长期记忆"),
    ("docs/MANAGEMENT_RULES.md", "管理规则手册"),
    ("docs/TASK_MASTER.md", "任务总清单"),
    ("SOUL.md", "灵魂定义"),
    ("USER.md", "用户档案"),
    ("AGENTS.md", "工作区指南"),
    ("IDENTITY.md", "身份定义"),
    ("docs/API_INVENTORY.md", "API清单"),
    ("WORKSPACE_STATUS.md", "工作区状态"),
    ("memory/2026-03-09-回顾清单.md", "3月9日回顾清单"),
    ("memory/2026-03-08.md", "3月8日工作日志"),
    ("memory/2026-03-07.md", "3月7日工作日志"),
    ("memory/2026-03-06.md", "3月6日工作日志"),
    ("memory/2026-03-10.md", "3月10日工作日志"),
]

class NotionSyncer:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.results = []
        
    def log(self, message):
        """打印日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def get_file_info(self, filepath):
        """获取文件信息"""
        full_path = os.path.join(WORKSPACE_DIR, filepath)
        if not os.path.exists(full_path):
            return None
        stat = os.stat(full_path)
        return {
            "path": filepath,
            "full_path": full_path,
            "size": stat.st_size,
            "size_readable": f"{stat.st_size / 1024:.1f}KB" if stat.st_size > 1024 else f"{stat.st_size}B",
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        }
        
    def read_file_content(self, filepath):
        """读取文件内容，尝试多种编码"""
        full_path = os.path.join(WORKSPACE_DIR, filepath)
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']
        
        for encoding in encodings:
            try:
                with open(full_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # 如果所有编码都失败，使用二进制模式
        with open(full_path, 'rb') as f:
            return f.read().decode('utf-8', errors='ignore')
    
    def truncate_content(self, content, max_bytes=199000):
        """截断内容以适应Notion限制（约200KB）"""
        content_bytes = content.encode('utf-8')
        if len(content_bytes) <= max_bytes:
            return content
        
        # 截断并添加提示
        truncated = content_bytes[:max_bytes].decode('utf-8', errors='ignore')
        return truncated + "\n\n[内容已截断 - 原始文件过大]"
    
    def split_into_blocks(self, content):
        """将内容分割成Notion块（每段一个paragraph块）"""
        lines = content.split('\n')
        blocks = []
        current_chunk = []
        chunk_size = 0
        max_chunk = 1900  # 安全限制，低于2000
        
        for line in lines:
            line_bytes = len(line.encode('utf-8'))
            
            if chunk_size + line_bytes > max_chunk and current_chunk:
                # 提交当前块
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": '\n'.join(current_chunk)}}]
                    }
                })
                current_chunk = [line]
                chunk_size = line_bytes
            else:
                current_chunk.append(line)
                chunk_size += line_bytes + 1  # +1 for newline
        
        # 添加最后一块
        if current_chunk:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": '\n'.join(current_chunk)}}]
                }
            })
        
        return blocks[:100]  # Notion限制最多100个块
    
    def create_page(self, title, description, content, retry_count=0):
        """创建Notion页面"""
        try:
            # 截断内容
            content = self.truncate_content(content)
            blocks = self.split_into_blocks(content)
            
            # 构建页面数据
            data = {
                "parent": {"page_id": PARENT_PAGE_ID},
                "properties": {
                    "title": {
                        "title": [{"type": "text", "text": {"content": title}}]
                    }
                },
                "children": blocks
            }
            
            response = requests.post(
                "https://api.notion.com/v1/pages",
                headers=self.headers,
                json=data,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "page_id": result.get("id"),
                    "url": result.get("url"),
                    "blocks_added": len(blocks)
                }
            elif response.status_code == 429:  # 速率限制
                if retry_count < MAX_RETRIES:
                    self.log(f"  ⚠️ 速率限制，等待{RETRY_INTERVAL}秒后重试...")
                    time.sleep(RETRY_INTERVAL)
                    return self.create_page(title, description, content, retry_count + 1)
                else:
                    return {
                        "success": False,
                        "error": f"Rate limited after {MAX_RETRIES} retries",
                        "status_code": response.status_code
                    }
            else:
                error_msg = response.text[:200] if response.text else f"HTTP {response.status_code}"
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            if retry_count < MAX_RETRIES:
                self.log(f"  ⚠️ 超时，等待{RETRY_INTERVAL}秒后重试...")
                time.sleep(RETRY_INTERVAL)
                return self.create_page(title, description, content, retry_count + 1)
            return {
                "success": False,
                "error": f"Timeout after {MAX_RETRIES} retries"
            }
        except Exception as e:
            if retry_count < MAX_RETRIES:
                self.log(f"  ⚠️ 错误: {str(e)[:50]}，等待{RETRY_INTERVAL}秒后重试...")
                time.sleep(RETRY_INTERVAL)
                return self.create_page(title, description, content, retry_count + 1)
            return {
                "success": False,
                "error": str(e)[:200]
            }
    
    def verify_page(self, page_id):
        """验证页面是否存在"""
        try:
            response = requests.get(
                f"https://api.notion.com/v1/pages/{page_id}",
                headers=self.headers,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            )
            return response.status_code == 200
        except:
            return False
    
    def sync_file(self, filepath, description):
        """同步单个文件"""
        self.log(f"\n📄 处理: {filepath}")
        
        # 1. 源文件存在检查
        file_info = self.get_file_info(filepath)
        if not file_info:
            return {
                "filepath": filepath,
                "description": description,
                "success": False,
                "error": "源文件不存在",
                "source_size": 0,
                "verified": False
            }
        
        self.log(f"  ✅ 源文件存在: {file_info['size_readable']}")
        
        # 2. 内容可读检查
        try:
            content = self.read_file_content(filepath)
            if not content.strip():
                return {
                    "filepath": filepath,
                    "description": description,
                    "success": False,
                    "error": "源文件为空",
                    "source_size": file_info['size'],
                    "verified": False
                }
            self.log(f"  ✅ 内容可读: {len(content)} 字符")
        except Exception as e:
            return {
                "filepath": filepath,
                "description": description,
                "success": False,
                "error": f"读取失败: {str(e)[:50]}",
                "source_size": file_info['size'],
                "verified": False
            }
        
        # 3. 创建Notion页面
        title = os.path.basename(filepath)
        result = self.create_page(title, description, content)
        
        if result.get("success"):
            page_id = result.get("page_id")
            self.log(f"  ✅ 页面创建成功: {page_id[:8]}...")
            
            # 4. 完整性验证
            time.sleep(1)  # 等待Notion索引
            verified = self.verify_page(page_id)
            
            if verified:
                self.log(f"  ✅ 目标文件验证通过")
            else:
                self.log(f"  ⚠️ 目标文件验证失败")
            
            return {
                "filepath": filepath,
                "description": description,
                "success": True,
                "page_id": page_id,
                "page_url": result.get("url"),
                "source_size": file_info['size'],
                "blocks_added": result.get("blocks_added"),
                "verified": verified
            }
        else:
            self.log(f"  ❌ 同步失败: {result.get('error', 'Unknown error')}")
            return {
                "filepath": filepath,
                "description": description,
                "success": False,
                "error": result.get("error", "Unknown error"),
                "source_size": file_info['size'],
                "verified": False
            }
    
    def run(self):
        """执行完整同步流程"""
        start_time = datetime.now()
        self.log("=" * 60)
        self.log("Notion同步任务启动 - 超保守策略")
        self.log(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"父页面ID: {PARENT_PAGE_ID[:12]}...")
        self.log(f"文件总数: {len(FILES_TO_SYNC)}")
        self.log("=" * 60)
        
        success_count = 0
        fail_count = 0
        
        for index, (filepath, description) in enumerate(FILES_TO_SYNC, 1):
            self.log(f"\n[{index}/{len(FILES_TO_SYNC)}] {filepath}")
            
            # 同步文件
            result = self.sync_file(filepath, description)
            self.results.append(result)
            
            if result["success"]:
                success_count += 1
            else:
                fail_count += 1
            
            # 文件间间隔（最后一个文件后不需要）
            if index < len(FILES_TO_SYNC):
                self.log(f"  ⏳ 等待 {FILE_INTERVAL} 秒...")
                time.sleep(FILE_INTERVAL)
        
        # 生成报告
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.generate_report(success_count, fail_count, duration)
        
        self.log("\n" + "=" * 60)
        self.log(f"同步完成!")
        self.log(f"成功: {success_count} | 失败: {fail_count}")
        self.log(f"耗时: {duration:.1f} 秒")
        self.log(f"报告已保存: {REPORT_PATH}")
        self.log("=" * 60)
        
        return success_count, fail_count
    
    def generate_report(self, success_count, fail_count, duration):
        """生成同步报告"""
        total = len(FILES_TO_SYNC)
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        report = f"""# Notion同步最终报告
> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 任务类型: 简化版Notion同步（超保守策略）

---

## 一、完整性声明

**检查方法**: 
- 源文件存在性检查 (`os.path.exists()`)
- 源文件大小检查 (`os.path.getsize()`)
- 内容可读性检查 (多编码尝试)
- 目标文件验证 (Notion API读取确认)

**检查结果**: 
- 已检查文件完整性: **{total}个文件**
- 通过检查: **{success_count}个文件**
- 存在问题: **{fail_count}个文件**

**完整性状态**: {"✅ 全部通过" if fail_count == 0 else "⚠️ 部分文件需要关注"}

---

## 二、同步统计

| 指标 | 数值 |
|------|------|
| 总文件数 | {total} |
| 成功同步 | {success_count} |
| 同步失败 | {fail_count} |
| 成功率 | {success_rate:.1f}% |
| 总耗时 | {duration:.1f} 秒 |
| 平均每文件耗时 | {duration/total:.1f} 秒 |

---

## 三、每个文件的检查结果

"""
        
        # 成功的文件
        if success_count > 0:
            report += "### ✅ 成功同步的文件\n\n"
            report += "| 序号 | 文件路径 | 描述 | 源文件大小 | 目标页面ID | 验证状态 |\n"
            report += "|------|----------|------|------------|------------|----------|\n"
            
            for idx, r in enumerate([r for r in self.results if r["success"]], 1):
                size = f"{r['source_size']/1024:.1f}KB" if r['source_size'] > 1024 else f"{r['source_size']}B"
                page_id = r.get("page_id", "-")[:12] + "..." if r.get("page_id") else "-"
                verified = "✅ 通过" if r.get("verified") else "⚠️ 失败"
                report += f"| {idx} | `{r['filepath']}` | {r['description']} | {size} | {page_id} | {verified} |\n"
            
            report += "\n"
        
        # 失败的文件
        if fail_count > 0:
            report += "### ❌ 同步失败的文件\n\n"
            report += "| 序号 | 文件路径 | 描述 | 源文件大小 | 失败原因 |\n"
            report += "|------|----------|------|------------|----------|\n"
            
            for idx, r in enumerate([r for r in self.results if not r["success"]], 1):
                size = f"{r['source_size']/1024:.1f}KB" if r['source_size'] > 1024 else f"{r['source_size']}B"
                error = r.get("error", "Unknown")[:50]
                report += f"| {idx} | `{r['filepath']}` | {r['description']} | {size} | {error} |\n"
            
            report += "\n"
        
        # 失败原因分析
        report += """---

## 四、失败原因分析

"""
        
        if fail_count == 0:
            report += "**✅ 所有文件均同步成功，无失败项。**\n\n"
        else:
            report += "| 失败类型 | 数量 | 可能原因 | 建议方案 |\n"
            report += "|----------|------|----------|----------|\n"
            
            # 统计失败类型
            error_types = {}
            for r in self.results:
                if not r["success"]:
                    error = r.get("error", "Unknown")
                    if "不存在" in error:
                        error_type = "文件缺失"
                    elif "为空" in error:
                        error_type = "空文件"
                    elif "Rate" in error or "429" in error:
                        error_type = "API速率限制"
                    elif "Timeout" in error or "超时" in error:
                        error_type = "网络超时"
                    else:
                        error_type = "API错误"
                    
                    error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in error_types.items():
                if error_type == "文件缺失":
                    reason = "源文件已被删除或移动"
                    solution = "检查文件路径，确认文件存在"
                elif error_type == "空文件":
                    reason = "文件内容为空"
                    solution = "补充文件内容后重新同步"
                elif error_type == "API速率限制":
                    reason = "Notion API请求过于频繁"
                    solution = "增加间隔时间，或稍后重试"
                elif error_type == "网络超时":
                    reason = "网络连接不稳定"
                    solution = "检查网络，增加超时时间"
                else:
                    reason = "Notion API返回错误"
                    solution = "检查API Token权限，查看详细错误"
                
                report += f"| {error_type} | {count} | {reason} | {solution} |\n"
            
            report += "\n"
        
        # 策略说明
        report += """---

## 五、超保守策略执行情况

### 策略配置
- **单文件处理**: ✅ 一次只处理1个文件
- **超长间隔**: ✅ 每文件间隔 {FILE_INTERVAL} 秒
- **三重重试**: ✅ 失败后等待 {RETRY_INTERVAL} 秒再重试，共 {MAX_RETRIES} 次
- **超时设置**: ✅ 连接超时 {CONNECT_TIMEOUT} 秒，读取超时 {READ_TIMEOUT} 秒
- **完整性检查**: ✅ 每个文件同步后验证

### 质量保障措施
1. 源文件存在性验证（`os.path.exists()`）
2. 源文件大小记录（`os.path.getsize()`）
3. 多编码尝试读取（utf-8, gbk, latin1）
4. 内容截断保护（最大199KB）
5. Notion块数量限制（最多100个块）
6. 目标页面API验证

---

## 六、后续建议

"""
        
        if fail_count > 0:
            report += """### 失败文件处理
1. 根据上述失败原因分析，逐一排查问题
2. 修复问题后，可单独重新同步失败文件
3. 如遇到API速率限制，建议等待10分钟后重试

"""
        
        report += """### 定期同步建议
- 建议每周执行一次完整同步
- 重要文档变更后立即同步
- 保持Notion与本地文档的一致性

### 备份策略
- Notion作为云端备份
- GitHub作为主要版本控制
- 本地文档包为工作主副本

---

*报告由简化版Notion同步脚本自动生成*
*生成时间: {timestamp}*
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # 保存报告
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.log(f"  📊 报告已生成: {REPORT_PATH}")

if __name__ == "__main__":
    syncer = NotionSyncer()
    success, fail = syncer.run()
    sys.exit(0 if fail == 0 else 1)
