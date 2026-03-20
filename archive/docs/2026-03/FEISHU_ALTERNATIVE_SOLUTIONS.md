# 飞书同步替代方案（无需OAuth2用户授权）

> 问题：AI无法完成OAuth2登录流程，需要无需用户授权的替代方案

---

## 方案1：Webhook方式（推荐）

**原理**：用户一次性授权，获得长期有效的user_token，存储后我后续使用

### 实施步骤：

```python
# Step 1: 用户手动执行（一次性）
# 用户运行此脚本，完成授权，获得token

import requests

APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"
REDIRECT_URI = "http://localhost:8080/callback"

# 1. 生成授权URL
auth_url = f"https://open.feishu.cn/open-apis/oauthen/authorize?app_id={APP_ID}&redirect_uri={REDIRECT_URI}"
print(f"请访问此URL并授权：{auth_url}")

# 2. 用户授权后，复制code
# 3. 用code换token
code = input("请输入授权后得到的code：")

url = "https://open.feishu.cn/open-apis/oauthen/v1/access_token"
data = {
    "grant_type": "authorization_code",
    "client_id": APP_ID,
    "client_secret": APP_SECRET,
    "code": code,
    "redirect_uri": REDIRECT_URI
}
resp = requests.post(url, json=data)
result = resp.json()

# 4. 保存token（这个token我可以长期使用！）
user_token = result["access_token"]
refresh_token = result["refresh_token"]  # 用于刷新

print(f"User Token: {user_token}")
print(f"Refresh Token: {refresh_token}")
print("\n请将这些token保存到安全位置，后续API调用需要")
```

**优点**：
- 用户只需授权一次
- 我获得长期token（2小时，可刷新）
- 后续完全自动化

**缺点**：
- 首次需要用户手动操作
- token需要安全存储

---

## 方案2：飞书机器人@方式（最简单）

**原理**：把机器人添加到群，@机器人让机器人在群里创建文档

### 实施步骤：

1. **在飞书创建一个群**
2. **添加"Kimi决策助手-满意妞"机器人进群**
3. **在群里@机器人创建文档**

```python
# 通过群机器人发送消息，触发文档创建
# 机器人在群内的操作，文档默认在群空间，群成员可见

# 调用群机器人webhook
webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx"

message = {
    "msg_type": "interactive",
    "card": {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "创建新文档"},
        },
        "elements": [
            {
                "tag": "div",
                "text": {"tag": "plain_text", "content": "请点击下方按钮创建文档"}
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "创建文档"},
                        "type": "primary",
                        "value": {"action": "create_doc", "title": "测试文档"}
                    }
                ]
            }
        ]
    }
}

requests.post(webhook_url, json=message)
```

**优点**：
- 完全不需要OAuth2
- 文档在群空间，群成员天然可见
- 最简单直接

**缺点**：
- 文档在群里，不是个人云文档
- 需要用户手动点击按钮

---

## 方案3：云盘共享文件夹方式（立即可用）

**原理**：上传到"共享文件夹"，通过链接分享

### 实施步骤：

```python
# 1. 用户手动创建一个共享文件夹
# 2. 将文件夹token给我
# 3. 我上传文件到该文件夹

FOLDER_TOKEN = "用户提供的文件夹token"  # 如：nodcnF0Fr6J0SVqYGUURQ24jJLe

def upload_to_folder(file_path, folder_token):
    url = f"https://open.feishu.cn/open-apis/drive/v1/files/upload_all"
    
    # 使用tenant_token即可上传到指定文件夹
    headers = {"Authorization": f"Bearer {tenant_token}"}
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'parent_type': 'folder', 'parent_node': folder_token}
        resp = requests.post(url, headers=headers, files=files, data=data)
    
    return resp.json()

# 上传后，文件在共享文件夹，成员可见
```

**优点**：
- 使用现有的tenant_token即可
- 无需OAuth2
- 立即可用

**缺点**：
- 文件在云盘，不是在线文档
- 需要用户先创建共享文件夹

---

## 方案4：多维表格 - 应用权限方式

**原理**：申请bitable:app权限，应用直接读写多维表格

### 需要的权限：
- `bitable:app:read` - 读取多维表格
- `bitable:app:write` - 写入多维表格
- `bitable:record:read` - 读取记录
- `bitable:record:write` - 写入记录

### 实施步骤：

1. **在飞书开放平台申请上述权限**
2. **等待审核通过**
3. **使用tenant_token直接操作**

```python
# 申请权限后，可以直接用tenant_token操作

# 创建记录
url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_id}/tables/{table_id}/records"
headers = {"Authorization": f"Bearer {tenant_token}"}
data = {
    "fields": {
        "标题": "文档标题",
        "内容": "文档内容...",
        "分类": "核心文档"
    }
}
resp = requests.post(url, headers=headers, json=data)
```

**优点**：
- 完全自动化，无需用户交互
- 使用tenant_token即可

**缺点**：
- 需要申请特定权限
- 可能需要审核

---

## 📊 方案对比

| 方案 | 是否需要用户操作 | 复杂度 | 自动化程度 | 推荐度 |
|------|----------------|--------|-----------|--------|
| **Webhook** | 首次需要 | 中 | 高（后续自动） | ⭐⭐⭐⭐⭐ |
| **机器人@** | 每次需要点击 | 低 | 低 | ⭐⭐⭐ |
| **云盘上传** | 需要创建文件夹 | 低 | 高 | ⭐⭐⭐⭐ |
| **多维表格权限** | 需要申请权限 | 高 | 高 | ⭐⭐⭐⭐ |

---

## 🎯 我的建议

**短期（今天可用）**：
使用**方案3 - 云盘上传**，用户创建一个共享文件夹，给我folder_token，我立即上传所有文件。

**长期（本周内配置）**：
使用**方案1 - Webhook**，用户执行一次授权脚本，获得长期token，之后完全自动化。

---

**你选择哪个方案？我可以立即提供完整代码。**