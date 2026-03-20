# 工作空间整理前状态报告

生成时间: 2026-03-18 22:37 GMT+8

---

## 一、总体统计

| 指标 | 数量 |
|------|------|
| 一级目录文件夹 | 47 |
| 一级目录文件 | 206 |
| 总文件夹数 | 937 |
| 总文件数 | 5067 |

---

## 二、问题诊断

### 1. 同名/相似名称文件夹（4组）

| 文件夹A | 大小 | 文件夹B | 大小 | 建议操作 |
|---------|------|---------|------|----------|
| disaster-recovery | 136K | disaster_recovery | 20K | 合并到 disaster-recovery |
| perceptual-intelligence | 264K | perceptual_intelligence | 108K | 合并到 perceptual-intelligence |
| config | 44K | .config | - | config是配置，.config可能是隐藏配置，需检查 |
| scripts | 480K | .scripts | - | .scripts可能是隐藏脚本，需检查 |

### 2. 异常文件夹（3个）

| 文件夹名 | 问题描述 | 建议操作 |
|---------|---------|----------|
| History} | 名字包含非法字符 `}` | 重命名或删除 |
| ! | 单字符名字，含义不明 | 检查内容后重命名或归档 |
| 1 | 单数字名字，含义不明 | 检查内容后重命名或归档 |

### 3. 空文件夹统计

发现空文件夹：约 58 个

主要分布区域：
- `./A满意哥专属文件夹/` 下有多个嵌套空文件夹
- `./knowledge_base/` 下有一些空agents/resources文件夹
- `./disaster_recovery/` 下有一些空备份文件夹
- `./.git/` 相关空文件夹（保留）
- `./skills/` 下有一些空文件夹

### 4. 一级目录松散文件分析

**206个松散文件**，按类型分布：

| 类别 | 数量 | 建议处理方式 |
|------|------|--------------|
| ROLE-*.md (角色定义) | 17 | 移入 personas/roles/ |
| notion_sync*.py (同步脚本) | 9 | 移入 scripts/notion/ |
| notion_*.json/logs (同步日志) | 15 | 移入 logs/notion/ 或清理 |
| 组织架构V*.md | 7 | 移入 docs/organization/history/ |
| 测试文件 (test_*.py) | 5 | 移入 test_files/ |
| 技能相关 (skill*.md) | 6 | 移入 docs/skills/ |
| 压缩/清理相关 (COMPRESSION*.md) | 3 | 移入 archive/ 或删除 |
| 其他文档 | 154 | 按主题分类到 docs/ 各子目录 |

### 5. excalidraw 相关文件夹（3个）

- excalidraw-app (68K)
- excalidraw-docker (28K) 
- excalidraw-local (8K)

建议：合并为 excalidraw/，子目录区分不同部署方式

---

## 三、空间占用分析（前20）

| 路径 | 大小 | 类型 |
|------|------|------|
| A满意哥专属文件夹 | 7.8M | 客户专属 |
| skills | 4.8M | 技能库 |
| docs | 2.0M | 文档 |
| knowledge_base | 2.0M | 知识库 |
| memory | 1.6M | 记忆 |
| backups | 1.4M | 备份 |
| deliverables | 608K | 交付物 |
| 满意解研究所资料库 | 508K | 资料库 |
| 本地文档包 | 500K | 文档包 |
| feishu_export | 500K | 飞书导出 |
| scripts | 480K | 脚本 |
| perceptual-intelligence | 264K | 感知智能 |
| partner-match-system | 268K | 合伙人系统 |
| reports | 308K | 报告 |
| perceptual_intelligence | 108K | 感知智能(重复) |
| constructivist-decision-theory | 108K | 决策理论 |
| data | 124K | 数据 |
| logs | 128K | 日志 |
| disaster-recovery | 136K | 灾难恢复 |
| templates | 80K | 模板 |

---

## 四、整理建议

### Phase 2 执行计划

1. **合并重复文件夹** (4组)
2. **清理空文件夹** (~58个)
3. **修复异常文件夹** (3个)
4. **文件归类** (按主题建立子目录)
5. **建立归档机制** (archive/ 目录)

### 建议的新目录结构

```
/root/.openclaw/workspace/
├── archive/              # 归档历史文件
├── backups/              # 备份（已有）
├── clients/              # 客户专属资料
│   └── a-man/           # A满意哥专属
├── config/               # 配置（统一）
├── data/                 # 数据（已有）
├── docs/                 # 文档（已有，优化内部结构）
├── logs/                 # 日志（已有）
├── memory/               # 记忆（已有）
├── scripts/              # 脚本（统一）
├── skills/               # 技能（已有）
├── templates/            # 模板（已有）
├── tools/                # 工具（已有）
└── [核心文件]            # AGENTS.md, SOUL.md, USER.md等
```
