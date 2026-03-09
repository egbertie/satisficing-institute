# FigJam API 配置指南

## 1. 注册Figma账号
- 访问：https://www.figma.com
- 点击 "Sign up"
- 使用邮箱或Google账号注册
- 用户名建议：egbertie

## 2. 获取Personal Access Token
1. 登录Figma后，访问：https://www.figma.com/developers/api#access-tokens
2. 点击 "Personal access tokens"
3. 点击 "Create new token"
4. 名称：满意解研究所
5. 复制Token（格式：figd_xxxxxxxx）

## 3. 创建FigJam文件
使用API创建：
```bash
curl -X POST \
  -H "X-Figma-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "满意解组织架构", "type": "jam"}' \
  https://api.figma.com/v1/files
```

## 4. 添加图形元素
```bash
# 添加矩形（角色框）
curl -X POST \
  -H "X-Figma-Token: YOUR_TOKEN" \
  -d '{...}' \
  https://api.figma.com/v1/files/{file_key}/nodes
```

## 5. 实时协作链接
- 文件创建后，分享链接给用户
- 用户可实时查看和编辑

## 6. 嵌入Notion
在Notion中粘贴FigJam链接，自动嵌入
