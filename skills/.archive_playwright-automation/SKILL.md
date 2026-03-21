---
name: playwright-automation
description: 使用Playwright进行浏览器自动化和测试。
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["npx"] },
        "emoji": "🎭",
      },
  }

# Playwright自动化 Skill

浏览器自动化测试和监控工具。

## 核心能力

### 1. 自动化测试
- 网页功能测试
- UI交互验证
- 截图对比

### 2. 定时监控
- 网站可用性检查
- 数据抓取
- 状态监控

### 3. RPA流程
- 重复操作自动化
- 表单填写
- 文件下载

## 使用示例

### 测试飞书文档
```javascript
const { test, expect } = require('@playwright/test');

test('飞书文档可访问', async ({ page }) => {
  await page.goto('https://feishu.cn/docx/xxx');
  await expect(page).toHaveTitle(/满意解/);
});
```

### 监控Notion页面
```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('https://notion.so/xxx');
  await page.screenshot({ path: 'notion.png' });
  await browser.close();
})();
```

## 命令行使用

```bash
# 安装浏览器
npx playwright install

# 运行测试
npx playwright test

# 生成报告
npx playwright show-report
```

## 蓝军测试场景

- 压力测试：多并发访问
- 兼容性测试：多浏览器
- 回归测试：功能验证
