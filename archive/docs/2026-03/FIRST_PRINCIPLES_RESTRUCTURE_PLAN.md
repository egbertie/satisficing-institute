# 第一性原则重构方案

**文档版本**: V1.0  
**生效日期**: 2026-03-19  
**文档级别**: P0基础设施规范

---

## 一、第一性原则框架

### 原则1: 单一职责 (Single Responsibility)
- 每个文件只有一个明确目的
- 每个文件夹只有一个明确职责
- 拒绝"杂物间"式目录

### 原则2: 无重复 (DRY - Don't Repeat Yourself)
- 同一内容只存一份
- 引用使用链接而非复制
- 自动检测重复文件

### 原则3: 无垃圾 (Zero Waste)
- 临时文件及时清理
- 过期版本定期归档
- 空文件夹零容忍

### 原则4: 清晰层级 (Clear Hierarchy)
- 最多4层目录深度
- 命名语义化、一致化
- 索引文件每个目录必备

### 原则5: 可追溯 (Traceability)
- 版本历史完整
- 变更记录清晰
- 责任归属明确

---

## 二、新目录架构设计

### 2.1 顶层架构（4层限制）

```
/root/.openclaw/workspace/
├── 📋 00-SYSTEM/              # 系统级配置与核心文档
├── 📦 01-PROJECTS/            # 当前活跃项目（PARA-Projects）
├── 🌐 02-AREAS/               # 责任领域（PARA-Areas）
├── 📚 03-RESOURCES/           # 资源库（PARA-Resources）
├── 🗃️ 04-ARCHIVES/            # 归档（PARA-Archives）
├── 🗑️ 05-TEMP/                # 临时工作区（自动清理）
└── 📖 README.md               # 根目录索引
```

### 2.2 详细架构

#### 📋 00-SYSTEM/ - 系统核心
```
00-SYSTEM/
├── CORE/                      # 系统核心文件
│   ├── AGENTS.md              # 代理配置
│   ├── USER.md                # 用户配置
│   ├── MEMORY.md              # 长期记忆
│   └── BOOTSTRAP.md           # 启动配置
├── CONFIG/                    # 配置文件
│   ├── global.json            # 全局配置
│   └── secrets.env            # 敏感配置（加密）
├── SKILLS/                    # 技能系统
│   ├── _index.json            # 技能索引
│   ├── skill-name/            # 每个技能一个目录
│   │   ├── SKILL.md           # 技能定义
│   │   ├── main.py            # 主程序
│   │   └── README.md          # 使用说明
│   └── ...
└── SCRIPTS/                   # 系统脚本
    ├── file-management/       # 文件管理脚本
    ├── backup/                # 备份脚本
    └── maintenance/           # 维护脚本
```

#### 📦 01-PROJECTS/ - 活跃项目
```
01-PROJECTS/
├── PROJECT-001-名称/          # 项目编号+名称
│   ├── README.md              # 项目简介
│   ├── PLAN.md                # 项目计划
│   ├── DELIVERABLES/          # 交付物
│   ├── WORKING/               # 工作文件
│   └── ARCHIVE/               # 项目归档
├── PROJECT-002-名称/
└── ...
```

#### 🌐 02-AREAS/ - 责任领域
```
02-AREAS/
├── DECISION-THEORY/           # 决策理论
├── PARTNERSHIP/               # 合伙人业务
├── BRAND/                     # 品牌建设
├── RESEARCH/                  # 研究体系
├── OPERATIONS/                # 运营管理
└── ...
```

#### 📚 03-RESOURCES/ - 资源库
```
03-RESOURCES/
├── LIBRARY/                   # 文献库
│   ├── PDF/                   # PDF文档
│   ├── DOCS/                  # 可编辑文档
│   └── LINKS.md               # 外部链接
├── TEMPLATES/                 # 模板库
├── KNOWLEDGE/                 # 知识库
│   ├── BASE/                  # 基础知识
│   └── EXPERTS/               # 专家知识
└── DATA/                      # 数据资源
```

#### 🗃️ 04-ARCHIVES/ - 归档区
```
04-ARCHIVES/
├── 2026-03/                   # 按月归档
├── 2026-02/
├── COMPLETED-PROJECTS/        # 已完成项目
├── OLD-VERSIONS/              # 历史版本
└── TRASH/                     # 待清理（30天后删除）
```

### 2.3 A满意哥专属文件夹重构

原结构：过深层级（10层）  
新结构：扁平化（4层）

```
01-PROJECTS/
├── SATISFICING-CORE/          # 满意解核心业务
│   ├── ASSESSMENT/            # 评估工具
│   ├── CASE-LIBRARY/          # 案例库
│   └── PARTNERSHIP-MODEL/     # 合伙人模型
├── DELIVERABLES/              # 成果交付
│   ├── WORD/                  # Word成品
│   ├── DESIGN/                # 设计资产
│   └── PROTOTYPES/            # 产品原型
├── KNOWLEDGE-BASE/            # 知识库
│   ├── CORE-RESEARCH/         # 核心研究
│   ├── EXPERTS/               # 专家档案
│   └── TOOLS/                 # 工具话术
└── PERSONAL/                  # 个人专属
    ├── GROWTH/                # 成长记录
    └── TEAMS/                 # 团队档案
```

### 2.4 Downloads目录重构

```
kimi/downloads/
├── 00-INBOX/                  # 收件箱（待处理）
├── 01-DOCS/                   # 文档
│   ├── PDF/                   # PDF
│   ├── DOCX/                  # Word
│   └── MD/                    # Markdown
├── 02-MEDIA/                  # 媒体
│   ├── IMAGES/                # 图片
│   └── VIDEO/                 # 视频
├── 03-CODE/                   # 代码
│   ├── PYTHON/                # Python
│   ├── JS/                    # JavaScript
│   └── SHELL/                 # Shell
├── 04-ARCHIVE/                # 已处理归档
└── README.md                  # 下载目录说明
```

---

## 三、文件迁移方案

### 3.1 迁移优先级

| 阶段 | 内容 | 预计时间 | 风险 |
|------|------|---------|------|
| 阶段1 | 创建新结构+核心文件迁移 | 2小时 | 低 |
| 阶段2 | skills/系统迁移 | 4小时 | 中 |
| 阶段3 | A满意哥专属文件夹迁移 | 6小时 | 高 |
| 阶段4 | downloads清理 | 2小时 | 中 |
| 阶段5 | 旧结构清理 | 1小时 | 低 |

### 3.2 迁移映射表

| 原路径 | 新路径 | 操作 | 备注 |
|-------|-------|------|------|
| /docs/*.md | /00-SYSTEM/CORE/ | 移动 | 核心文档 |
| /skills/*/ | /00-SYSTEM/SKILLS/ | 移动 | 技能系统 |
| /memory/ | /00-SYSTEM/CORE/MEMORY/ | 合并 | 记忆整合 |
| /config/ | /00-SYSTEM/CONFIG/ | 移动 | 配置迁移 |
| /scripts/ | /00-SYSTEM/SCRIPTS/ | 移动 | 脚本迁移 |
| /deliverables/ | /01-PROJECTS/PROJECT-XXX/ | 分类 | 按项目归类 |
| /A满意哥专属文件夹/ | /01-PROJECTS/SATISFICING-CORE/ | 重构 | 扁平化 |
| /downloads/ | /03-RESOURCES/INBOX/ | 合并 | 重新分类 |
| /.workspace_optimization/ | /04-ARCHIVES/ | 归档 | 待清理 |
| /__pycache__/ | DELETE | 删除 | 缓存清理 |

### 3.3 迁移检查清单

```bash
# 迁移前检查
[ ] 完整备份当前状态
[ ] 验证所有脚本可执行
[ ] 通知相关人员

# 迁移中检查
[ ] 每批迁移后验证
[ ] 检查文件完整性
[ ] 更新索引文件

# 迁移后检查
[ ] 验证所有链接有效
[ ] 测试关键脚本
[ ] 更新文档引用
```

---

## 四、命名规范完整版

### 4.1 目录命名规范

| 类型 | 格式 | 示例 | 禁止 |
|------|------|------|------|
| 系统目录 | 大写+连字符 | 00-SYSTEM, 01-PROJECTS | 小写, 下划线 |
| 项目目录 | PROJECT-XXX-名称 | PROJECT-001-品牌升级 | emoji, 中文序号 |
| 技能目录 | 小写+连字符 | web-scraper, data-processor | 大写, 空格 |
| 日期目录 | YYYY-MM | 2026-03 | 其他格式 |

### 4.2 文件命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 文档 | 大驼峰+版本 | BrandStrategyV1.0.md |
| 代码 | 小写+下划线 | file_analyzer.py |
| 配置 | 小写+连字符 | app-config.json |
| 临时 | 日期前缀+描述 | 20260319_temp_data.json |
| 归档 | ARCHIVE_原文件名 | ARCHIVE_BrandStrategyV0.9.md |

### 4.3 版本命名规范

```
V主版本.次版本.修订版本-状态

示例:
V1.0.0-stable    # 稳定版
V1.1.0-beta      # 测试版
V2.0.0-draft     # 草稿版
```

---

## 五、版本控制规范

### 5.1 Git工作流

```
main        ← 稳定分支，只接受合并
├── develop ← 开发分支，日常开发
├── feature/xxx  ← 功能分支
├── hotfix/xxx   ← 热修分支
└── archive/xxx  ← 归档分支
```

### 5.2 提交规范

```
类型(范围): 简短描述

详细描述（可选）

关联: #issue编号

类型:
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

示例:
feat(file-system): 重构目录结构，实施PARA方法

docs(naming): 更新命名规范文档

关联: #123
```

### 5.3 文件版本管理

| 场景 | 策略 | 工具 |
|------|------|------|
| 文档迭代 | 同文件版本标记 | Git历史 |
| 大文件变更 | 版本号+归档 | 文件命名 |
| 配置变更 | 环境分离 | 分支管理 |
| 代码迭代 | 语义化版本 | Git标签 |

---

## 六、清理策略

### 6.1 自动清理规则

| 文件类型 | 保留期限 | 操作 |
|---------|---------|------|
| 临时文件(*.tmp) | 7天 | 自动删除 |
| 日志文件(*.log) | 30天 | 压缩归档 |
| 缓存文件(*.pyc) | 即时 | 提交前清理 |
| 下载收件箱 | 14天 | 提醒归档 |
| 回收站 | 30天 | 自动删除 |

### 6.2 手动清理检查清单

**每周检查**:
- [ ] 05-TEMP/ 目录清理
- [ ] downloads/00-INBOX/ 处理
- [ ] 空目录检查

**每月检查**:
- [ ] 重复文件扫描
- [ ] 大文件审查
- [ ] 归档文件整理
- [ ] 备份策略验证

**每季度检查**:
- [ ] 完整结构审计
- [ ] 命名规范检查
- [ ] 权限审查

### 6.3 清理脚本

```bash
#!/bin/bash
# cleanup.sh - 自动清理脚本

# 清理临时文件
find 05-TEMP/ -type f -mtime +7 -delete

# 清理空目录
find . -type d -empty -delete

# 清理pycache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 压缩旧日志
find logs/ -name "*.log" -mtime +30 -exec gzip {} \;

echo "清理完成: $(date)"
```

---

## 七、执行时间表

| 时间 | 任务 | 负责人 | 产出 |
|------|------|--------|------|
| 00:00-02:00 | 创建新结构 | 自动化 | 新目录架构 |
| 02:00-04:00 | 核心文件迁移 | 自动化 | 系统文件就位 |
| 04:00-06:00 | skills系统迁移 | 半自动 | 技能目录重构 |
| 06:00-08:00 | 验证测试 | 人工 | 测试报告 |
| 08:00-10:00 | A满意哥文件夹迁移 | 人工 | 核心业务重构 |
| 10:00-12:00 | downloads清理 | 半自动 | 下载目录重构 |
| 12:00-14:00 | 旧结构清理 | 自动化 | 空间释放 |
| 14:00-16:00 | 文档更新 | 人工 | README更新 |

---

## 八、验收标准

- [ ] 所有文件位置明确、无遗漏
- [ ] 重复文件100%清除
- [ ] 空文件夹100%清除
- [ ] 目录层级不超过4层
- [ ] 每个目录都有README索引
- [ ] 自动化脚本可执行
- [ ] Skill文档完整可用
- [ ] 可追溯未来90天的文件变更

---

*文档版本: V1.0*  
*最后更新: 2026-03-19*  
*负责团队: 基础设施组*
