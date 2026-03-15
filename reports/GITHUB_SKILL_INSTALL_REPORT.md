# GitHub Skill 安装报告 (P0批次)

**生成时间**: 2026-03-14 18:58:02  
**安装时长**: ~7分30秒  
**报告路径**: `/root/.openclaw/workspace/reports/GITHUB_SKILL_INSTALL_REPORT.md`

---

## 📊 安装概览

| 状态 | 数量 |
|------|------|
| ✅ 成功 | 2 |
| ⚠️ 不完整 | 2 |
| ❌ 未找到 | 6 |
| **总计** | **10** |

---

## ✅ 成功列表

### 1. markdown-converter
- **状态**: ✅ 已安装
- **路径**: `/root/.openclaw/workspace/skills/markdown-converter/`
- **SKILL.md**: ✅ 存在
- **描述**: 使用 markitdown 将文档(PDF, Word, PPT, Excel等)转换为 Markdown
- **安装方式**: 已预存在workspace中

### 2. github
- **状态**: ✅ 已安装
- **路径**: `/root/.openclaw/workspace/skills/github/`
- **SKILL.md**: ✅ 存在
- **描述**: 使用 `gh` CLI 与 GitHub 交互(issues, PRs, CI runs)
- **安装方式**: 已预存在workspace中

---

## ⚠️ 不完整列表 (需要修复)

### 3. brave-search
- **状态**: ⚠️ 不完整
- **路径**: `/root/.openclaw/workspace/skills/brave-search/`
- **问题**: 克隆中断，仅包含 `.git` 目录，无实际文件
- **建议**: 重新克隆或从 ClawHub 安装

### 4. cron-scheduling
- **状态**: ⚠️ 不完整
- **路径**: `/root/.openclaw/workspace/skills/cron-scheduling/`
- **问题**: 克隆中断，仅包含 `.git` 目录，无实际文件
- **建议**: 重新克隆或从 ClawHub 安装

---

## ❌ 未找到列表

以下 skill 在 GitHub 的 `clawhub/skills` 和 `openclaw/skills` 组织下均未找到对应仓库：

| # | Skill 名称 | 状态 | 可能原因 |
|---|-----------|------|---------|
| 5 | automate-excel | ❌ 未找到 | 可能使用不同名称或尚未发布 |
| 6 | duckdb-cli-ai-skills | ❌ 未找到 | 可能使用不同名称或尚未发布 |
| 7 | markdown-exporter | ❌ 未找到 | 可能使用不同名称或尚未发布 |
| 8 | mermaid-diagrams | ❌ 未找到 | 可能使用不同名称或尚未发布 |
| 9 | firecrawl-search | ❌ 未找到 | 可能使用不同名称或尚未发布 |
| 10 | copywriting | ❌ 未找到 | 可能使用不同名称或尚未发布 |

---

## 🔍 调查发现

### 1. OpenClaw Skills 仓库结构
- 官方 skills 托管在 `https://github.com/openclaw/skills`
- 该仓库作为 ClawHub (clawhub.com) 的备份，包含数千个 skills
- Skills 位于 `skills/<author>/<skill-name>` 或 `skills/<skill-name>/` 目录下

### 2. 搜索尝试
- 已尝试的仓库地址:
  - `https://github.com/clawhub/skills/<skill-name>` - 404
  - `https://github.com/openclaw/skills/<skill-name>` - 404
- API 查询显示目标 P0 skills 不在 openclaw/skills 仓库中

### 3. 可能的解决方案
根据搜索结果，这些 skill 可能：
1. **使用不同的仓库名称** - 需要进一步搜索确认
2. **作为 monorepo 的子目录存在** - 但查询未发现
3. **需要从 ClawHub 直接安装** - 使用 `npx clawhub@latest install <skill-name>`
4. **尚未公开发布** - 可能是私有或开发中

---

## 💡 替代方案

### 对于缺失的 skills，可以尝试：

1. **通过 ClawHub CLI 安装**
   ```bash
   npm i -g clawhub
   clawhub install brave-search
   clawhub install mermaid-diagrams
   # ... 其他 skill
   ```

2. **手动搜索正确的仓库名称**
   - 使用 GitHub 搜索: `site:github.com brave-search openclaw`
   - 检查 awesome-openclaw-skills 仓库

3. **使用功能类似的替代 skill**
   - `brave-search` → `tavily-web-search` 或 `exa-web-search-free`
   - `mermaid-diagrams` → `diagram-gen` 或 `mermaid-architect`
   - `automate-excel` → `csv-pipeline` 或 `duckdb`

---

## 📝 安装日志摘要

```
开始时间: 2026-03-14 18:50:32
结束时间: 2026-03-14 18:58:02

操作记录:
1. 尝试从 clawhub/skills 克隆 - 失败 (404)
2. 尝试从 openclaw/skills 克隆 - 失败 (404)
3. 验证已存在 skill - 2个完整, 2个不完整
4. API 查询 openclaw/skills 仓库 - P0 skills 未找到
```

---

## 🎯 建议行动

### 立即行动
1. ✅ **markdown-converter** 和 **github** 可立即使用
2. 🔄 修复 **brave-search** 和 **cron-scheduling** (删除后重新克隆)

### 后续跟进
1. 使用 `clawhub search "<keyword>"` 搜索 P0 skills 的正确名称
2. 联系 skill 维护者确认仓库位置
3. 考虑使用功能类似的替代 skills

---

## 📌 备注

- 报告生成环境: Linux 6.8.0-55-generic (x64)
- 网络状态: 部分 GitHub 请求超时或失败
- 安装方式: 以 Git 克隆为主，API 查询为辅

---

*报告由 OpenClaw Agent 自动生成*
