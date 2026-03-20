# 自建CRM与项目管理系统方案

**创建时间**: 2026-03-14  
**创建方式**: 基于现有工具组合 + 方法论定义  
**目标**: 不依赖外部skill，用已有能力构建

---

## 📋 现有工具盘点

| 工具 | 用途 | 状态 |
|------|------|------|
| n8n-workflow-automation | 工作流自动化 | ✅ 已安装 |
| agentic-workflow-automation | AI驱动编排 | ✅ 已安装 |
| data-analyst | 数据分析 | ✅ 已安装 |
| dashboard | 数据可视化 | ✅ 已安装 |
| Notion | 知识库/数据库 | ✅ 已配置 |
| 飞书多维表格 | 表格+自动化 | ✅ 已配置 |
| DuckDB | 本地数据库 | ✅ 已安装 |

---

## 🎯 CRM系统方案（合伙人关系管理）

### 核心实体
```
合伙人候选人
├── 基本信息（姓名、公司、职位、联系方式）
├── 来源渠道（推荐、会议、主动接触）
├── 评估状态（初筛→资料收集→深度访谈→决策→签约）
├── 沟通记录（时间、方式、内容、下一步）
├── 评分维度（五路图腾评分、能力评估、价值观匹配）
└── 关联文档（简历、评估报告、会议纪要）
```

### 技术实现

**方案A：Notion数据库（推荐）**
- 利用Notion的Relation功能关联候选人-沟通记录-评估报告
- 利用Rollup汇总评分和状态
- 利用Filter视图按状态筛选
- n8n自动化：状态变更→飞书通知

**方案B：飞书多维表格**
- 表格视图管理候选人列表
- 自动化流程：新增候选人→分配评估官→提醒跟进
- 与现有飞书机器人联动

**方案C：DuckDB本地数据库**
- SQL查询复杂关联
- Python脚本批量处理
- 导出Excel/CSV给团队

### 推荐：方案A + B 组合
- **Notion**: 长期存档、复杂关联、知识沉淀
- **飞书**: 实时协作、自动化提醒、移动端访问

---

## 🎯 项目管理系统方案（合伙人评估项目）

### 核心实体
```
评估项目
├── 项目信息（客户名称、行业、启动时间、截止日期）
├── 任务分解（资料收集→初筛→访谈→报告→交付）
├── 责任人分配（PEO、EEO、专家）
├── 进度跟踪（完成%、阻塞项、风险预警）
├── 交付物清单（评估报告、决策建议、风险清单）
└── 时间线（里程碑、关键节点）
```

### 技术实现

**利用现有工具组合：**

1. **任务管理**: 飞书任务 / Notion Task Board
2. **进度跟踪**: dashboard 生成甘特图/燃尽图
3. **文档协作**: Notion / 飞书文档
4. **自动化**: n8n
   - 任务到期前24h提醒
   - 状态变更同步多平台
   - 周报自动生成并发送

5. **数据存储**: 
   - 主数据：Notion数据库
   - 分析：DuckDB本地查询
   - 备份：GitHub + 飞书云文档

---

## 🔄 工作流程定义（n8n自动化）

### 流程1：新候选人入库
```
触发：飞书表单提交 / Notion新增
→ n8n捕获事件
→ 生成唯一ID
→ Notion创建记录
→ 飞书通知评估团队
→ 分配初筛责任人
→ 设置7天初筛提醒
```

### 流程2：评估进度跟踪
```
触发：每日9:00定时
→ 查询Notion待办任务
→ 筛选今日到期/逾期任务
→ dashboard生成进度报告
→ 飞书推送晨报
→ 阻塞项高亮提醒
```

### 流程3：评估完成归档
```
触发：Notion状态变更为"完成"
→ 收集所有关联文档
→ 生成PDF评估报告
→ 归档到GitHub
→ 飞书通知客户
→ 更新统计数据
```

---

## 📊 数据模型设计（DuckDB）

```sql
-- 候选人表
CREATE TABLE candidates (
    id TEXT PRIMARY KEY,
    name TEXT,
    company TEXT,
    position TEXT,
    source TEXT,
    status TEXT, -- 初筛/深度评估/决策/签约
    created_at TIMESTAMP,
    assigned_to TEXT,
    notes TEXT
);

-- 沟通记录表
CREATE TABLE communications (
    id TEXT PRIMARY KEY,
    candidate_id TEXT,
    date DATE,
    method TEXT, -- 电话/会议/邮件
    content TEXT,
    next_action TEXT,
    next_date DATE,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

-- 评估维度表（五路图腾）
CREATE TABLE assessments (
    id TEXT PRIMARY KEY,
    candidate_id TEXT,
    evaluator TEXT,
    liu_score INT, -- 德馨
    simon_score INT, -- 满意解
    guanyin_score INT, -- 自在
    confucius_score INT, -- 仁爱
    huineng_score INT, -- 顿悟
    overall_score INT,
    created_at TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

-- 项目表
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    client_name TEXT,
    industry TEXT,
    start_date DATE,
    deadline DATE,
    status TEXT,
    progress INT -- 0-100
);

-- 任务表
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    title TEXT,
    assignee TEXT,
    due_date DATE,
    status TEXT, -- 待办/进行中/完成/阻塞
    priority TEXT, -- P0/P1/P2/P3
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

---

## 🚀 实施步骤

### Phase 1: 基础搭建（今晚）
- [ ] 创建Notion数据库模板
- [ ] 配置飞书多维表格
- [ ] 编写DuckDB建表脚本
- [ ] 配置n8n基础工作流

### Phase 2: 自动化（明天）
- [ ] n8n连接Notion+飞书
- [ ] 设置定时任务
- [ ] 测试完整流程

### Phase 3: 优化（本周）
- [ ] dashboard可视化
- [ ] 数据分析和报表
- [ ] 团队培训

---

## 💡 优势

| 方面 | 自研方案优势 |
|------|-------------|
| **可控性** | 完全自主，无外部依赖 |
| **成本** | 零额外费用 |
| **定制化** | 完全匹配合伙人评估业务 |
| **安全性** | 数据本地/自有平台，无泄露风险 |
| **扩展性** | 基于现有工具，随时迭代 |

---

## 📎 交付物

1. `skills/crm-system/` - CRM方法论文档 + 配置模板
2. `skills/project-management/` - 项目管理文档 + 工作流定义
3. `database/crm_schema.sql` - DuckDB数据库结构
4. `workflows/n8n-crm-automation.json` - n8n工作流配置

**是否需要我立即开始Phase 1实施？** 🚀
