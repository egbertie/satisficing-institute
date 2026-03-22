# PDF处理应急方案

## 当前状态
- nano-pdf Skill安装受阻（ClawHub Rate limit）
- GitHub克隆失败（认证问题）

## 临时解决方案
使用现有工具链处理PDF：
1. 使用`browser` Skill截图PDF
2. 使用Python+pypdf直接提取文本（已验证可用）
3. 等待ClawHub恢复后正式安装nano-pdf

## 已验证可用的PDF处理脚本
```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
text = "\n".join([page.extract_text() for page in reader.pages])
```

## 下一步
- [ ] 监控ClawHub状态，稍后重试安装
- [ ] 或手动创建PDF处理Skill封装上述脚本
