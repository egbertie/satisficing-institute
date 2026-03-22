# file-handler-universal Skill

统一文件处理器 - 整合DOCX、PDF、Excel、CSV等所有文件处理能力

---

## 功能概览

| 文件类型 | 读取 | 转换 | 上传 |
|----------|------|------|------|
| **.docx** | ✅ pandoc | ↔ Markdown | ✅ 飞书/Notion |
| **.pdf** | ✅ pypdf | → 文本 | ✅ 飞书Drive |
| **.xlsx** | ✅ openpyxl | ↔ CSV | ✅ 飞书Bitable |
| **.csv** | ✅ csv | ↔ Excel | ✅ 飞书 |
| **.md/.txt** | ✅ 原生 | ↔ DOCX | ✅ 多渠道 |
| **图片** | - | - | ✅ 飞书/Notion |

---

## 使用方法

### 1. 读取文件（任意格式转文本）

```bash
# 读取DOCX
python3 skills/file-handler-universal/file_handler.py read document.docx

# 读取PDF
python3 skills/file-handler-universal/file_handler.py read report.pdf

# 读取Excel
python3 skills/file-handler-universal/file_handler.py read data.xlsx

# 读取CSV
python3 skills/file-handler-universal/file_handler.py read data.csv
```

### 2. 转换文件格式

```bash
# DOCX → Markdown
python3 skills/file-handler-universal/file_handler.py convert document.docx md

# Markdown → DOCX
python3 skills/file-handler-universal/file_handler.py convert notes.md docx

# Excel → CSV
python3 skills/file-handler-universal/file_handler.py convert data.xlsx csv

# CSV → Excel
python3 skills/file-handler-universal/file_handler.py convert data.csv xlsx
```

### 3. 上传文件到云端

```bash
# 上传到飞书（默认）
python3 skills/file-handler-universal/file_handler.py upload document.pdf

# 上传到Notion
python3 skills/file-handler-universal/file_handler.py upload report.md notion

# 上传图片到飞书
python3 skills/file-handler-universal/file_handler.py upload chart.png feishu
```

---

## Python API

```python
from skills.file-handler-universal.file_handler import FileHandler

handler = FileHandler()

# 读取文件
content = handler.read_file("document.docx")
print(content)

# 转换文件
output_path = handler.convert_file("document.docx", "md")
print(f"Converted to: {output_path}")

# 上传文件
result = handler.upload_file("report.pdf", "feishu")
print(result)
```

---

## 依赖要求

| 依赖 | 用途 | 安装命令 |
|------|------|----------|
| pandoc | DOCX↔Markdown转换 | `apt-get install pandoc` |
| pypdf | PDF读取 | `pip install pypdf` |
| openpyxl | Excel处理 | `pip install openpyxl` |

---

## 修复记录

- **2026-03-22**: 创建统一文件处理器，整合分散的文件处理Skill
- **恢复Skill**: automate-excel, csvtoexcel, file-gateway, file-integrity, markdown-converter, markdown-exporter
