# file-gateway Skill

将本地文件上传到多个渠道（飞书、Notion、邮件、Telegram）的统一网关。

## Purpose

解决用户无法直接读取本地文件的问题，提供一键分享到多个渠道的能力。

## Usage

### 命令行使用

```bash
# 上传到所有配置的渠道
file-gateway upload /path/to/file.md

# 上传到指定渠道
file-gateway upload /path/to/file.png --channels feishu,notion

# 上传到单个渠道
file-gateway upload /path/to/file.pdf --channel telegram
```

### Python API

```python
from skills.file_gateway.scripts.file_gateway import FileGateway

gateway = FileGateway()

# 上传到所有渠道
result = gateway.upload("/path/to/file.md")

# 上传到指定渠道
result = gateway.upload("/path/to/file.png", channels=["feishu", "notion"])

# 返回结果包含各渠道的上传状态和链接
print(result)
# {
#     "success": True,
#     "file": "/path/to/file.md",
#     "channels": {
#         "feishu": {"success": True, "url": "https://..."},
#         "notion": {"success": True, "url": "https://..."},
#         "telegram": {"success": False, "error": "..."}
#     }
# }
```

## Configuration

配置文件位置：`/root/.openclaw/skills/file-gateway/config/channels.json`

```json
{
    "feishu": {
        "enabled": true,
        "upload_method": "drive"
    },
    "notion": {
        "enabled": true,
        "token": "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",
        "parent_page_id": "your-parent-page-id"
    },
    "email": {
        "enabled": false,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "",
        "password": ""
    },
    "telegram": {
        "enabled": false,
        "bot_token": "",
        "chat_id": ""
    }
}
```

## Supported File Types

| 类型 | 扩展名 | 最佳上传渠道 |
|------|--------|--------------|
| 文档 | .md, .txt, .docx | Notion, Feishu Doc |
| 图片 | .png, .jpg, .jpeg, .gif, .webp | Feishu Drive, Telegram |
| 文档 | .pdf | Feishu Drive, Notion |
| 表格 | .xlsx, .csv | Feishu Bitable, Notion |

## Tools Provided

- `file-gateway.upload` - 上传文件到指定渠道

## Files

- `scripts/file_gateway.py` - 主程序
- `config/channels.json` - 渠道配置
- `utils/` - 工具函数
