# 工作空间架构 V2.0

> ⚠️ **文档状态**：本文档为历史架构文档，相关内容已整合至 **满意解文档体系 V1.0**
>
> **建议阅读**：
> - [SATISFICING_INDEX_V1.0.md](SATISFICING_INDEX_V1.0.md) - 满意解业务体系统一入口
>
> ---
>
> **基于第一性原则重构的统一架构**  
> **版本**: 2.0（历史文档）  
> **日期**: 2026-03-15  
> **目标**: 从176个Skill精简至15个核心套件  
> **历史价值**: 工作空间架构设计记录，供参考

---

## 架构总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           工作空间架构 V2.0                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         CLI 统一入口层                               │   │
│  │                    claw <cmd> [subcmd] [options]                     │   │
│  │                                                                     │   │
│  │   audit    optimize    skill    doc    cron    memory    report     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                    ┌───────────────┼───────────────┐                        │
│                    │               │               │                        │
│                    ▼               ▼               ▼                        │
│  ┌─────────────────────┐ ┌───────────────┐ ┌─────────────────────┐         │
│  │    核心套件层        │ │   业务套件层   │ │    工具套件层        │         │
│  │   (Unified Suites)  │ │  (Domain)     │ │    (Tools)          │         │
│  ├─────────────────────┤ ├───────────────┤ ├─────────────────────┤         │
│  │ • intelligence      │ │ • satisficing │ │ • archive-handler   │         │
│  │ • document          │ │ • persona     │ │ • github            │         │
│  │ • data              │ │ • debater     │ │ • docker            │         │
│  │ • content           │ │ • prospect    │ │ • error-guard       │         │
│  │ • notify            │ │ • behavioral  │ │                     │         │
│  │ • automation        │ │ • expert      │ │                     │         │
│  │ • governance        │ │ • decision    │ │                     │         │
│  └─────────────────────┘ └───────────────┘ └─────────────────────┘         │
│                                    │                                        │
│                    ┌───────────────┼───────────────┐                        │
│                    │               │               │                        │
│                    ▼               ▼               ▼                        │
│  ┌─────────────────────┐ ┌───────────────┐ ┌─────────────────────┐         │
│  │    文档体系层        │ │   数据记忆层   │ │    自动化层          │         │
│  │   (Documents)       │ │  (Memory)     │ │    (Automation)     │         │
│  ├─────────────────────┤ ├───────────────┤ ├─────────────────────┤         │
│  │ • ARCHITECTURE.md   │ │ • CORE.md     │ │ • 晨间统一检查       │         │
│  │ • STRATEGY.md       │ │ • daily/      │ │ • 晚间统一报告       │         │
│  │ • SOP/              │ │ • decisions/  │ │ • 事件触发器         │         │
│  │ • RESEARCH/         │ │ • knowledge   │ │ • 异常告警          │         │
│  │ • DELIVERABLES/     │ │   -graph.json │ │                     │         │
│  └─────────────────────┘ └───────────────┘ └─────────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. CLI 统一入口层

### 1.1 设计原则

**第一性原理**: 用户不需要记住176个Skill的名称，只需要记住**7个核心命令**。

```
简化前: 176个Skill → 需要记住176个名称
简化后: 7个命令  → 只需要记住7个动词

节省: 96% 记忆负担
```

### 1.2 命令设计

```bash
# 检视命令
claw audit --all              # 全面审计
claw audit --skill [name]     # 审计指定Skill
claw audit --doc [name]       # 审计指定文档

# 优化命令
claw optimize --target [name] # 优化目标
claw optimize --auto          # 自动优化建议

# Skill管理
claw skill list               # 列出所有Skill
claw skill install [name]     # 安装Skill
claw skill remove [name]      # 移除Skill
claw skill update [name]      # 更新Skill

# 文档管理
claw doc list                 # 列出文档
claw doc search [keyword]     # 搜索文档
claw doc archive [name]       # 归档文档

# Cron管理
claw cron list                # 列出Cron
claw cron enable [name]       # 启用Cron
claw cron disable [name]      # 禁用Cron
claw cron merge               # 合并优化

# 记忆管理
claw memory search [keyword]  # 搜索记忆
claw memory summary           # 生成摘要
claw memory archive           # 归档旧记忆

# 报告生成
claw report daily             # 生成日报
claw report weekly            # 生成周报
claw report audit             # 生成审计报告
```

---

## 2. 核心套件层（Unified Suites）

### 2.1 unified-intelligence-suite（统一信息套件）

**合并源**: 12个 → 1个
- firecrawl-search
- multi-search-engine
- multi-source-search
- openclaw-tavily-search
- tavily
- company-search-kimi
- jina-ai-reader
- rss-ai-reader
- info-cleaner
- info-collection-workflow
- information-intelligence
- knowledge-collection-iteration

**功能**:
```python
class IntelligenceSuite:
    def search(self, query, sources=['web', 'news', 'academic']):
        """统一搜索入口"""
        pass
    
    def collect(self, topic, schedule='daily'):
        """定时信息采集"""
        pass
    
    def monitor(self, keywords, channels):
        """关键词监控"""
        pass
    
    def distill(self, raw_data):
        """信息萃取"""
        pass
```

**CLI接口**:
```bash
claw intelligence search "硬科技投资趋势"
claw intelligence collect --topic "AI行业" --schedule daily
claw intelligence monitor --keywords "合伙人,融资" --channels "news,wechat"
```

### 2.2 unified-document-suite（统一文档套件）

**合并源**: 9个 → 1个
- document-processor
- feishu-doc-manager
- feishu-docx-powerwrite
- feishu-file-sender
- notion
- notion-api
- notion-api-skill
- obsidian
- markdown-converter

**功能**:
```python
class DocumentSuite:
    def read(self, path, format='auto'):
        """读取文档"""
        pass
    
    def write(self, path, content, format='md'):
        """写入文档"""
        pass
    
    def convert(self, source, target_format):
        """格式转换"""
        pass
    
    def sync(self, source, target):
        """多平台同步"""
        pass
```

**CLI接口**:
```bash
claw doc read /path/to/file.pdf
claw doc convert input.md --to docx
claw doc sync notion --to feishu
```

### 2.3 unified-data-suite（统一数据套件）

**合并源**: 6个 → 1个
- data-processor-suite
- data-analyst
- chart-generator
- automate-excel
- csvtoexcel
- duckdb-cli-ai-skills

**功能**:
```python
class DataSuite:
    def analyze(self, data, method='auto'):
        """数据分析"""
        pass
    
    def visualize(self, data, chart_type):
        """数据可视化"""
        pass
    
    def transform(self, data, rules):
        """数据转换"""
        pass
```

### 2.4 unified-content-suite（统一内容套件）

**合并源**: 5个 → 1个
- marketing-content-generator
- copywriting-zh-pro
- adwords
- ai-social-media-content
- social-media-content-calendar

**功能**:
```python
class ContentSuite:
    def generate(self, topic, format='article', style='professional'):
        """内容生成"""
        pass
    
    def adapt(self, content, platform):
        """多平台适配"""
        pass
    
    def schedule(self, content, time):
        """内容排期"""
        pass
```

### 2.5 unified-notify-suite（统一通知套件）

**合并源**: 6个 → 1个
- notification-router
- feishu-messaging
- feishu-send-file
- slack
- email-daily-summary
- news-summary

**功能**:
```python
class NotifySuite:
    def send(self, message, channels=['claw']):
        """统一发送"""
        pass
    
    def route(self, event, rules):
        """智能路由"""
        pass
```

### 2.6 unified-automation-suite（统一自动化套件）

**合并源**: 5个 → 1个
- cron-optimization-manager
- daily-reminder-auditor
- task-coordinator
- autonomous-execution-system
- continuous-improvement-engine

**功能**:
```python
class AutomationSuite:
    def schedule(self, task, time, repeat=None):
        """任务调度"""
        pass
    
    def monitor(self, metrics):
        """监控告警"""
        pass
    
    def audit(self, scope='all'):
        """自动审计"""
        pass
```

### 2.7 unified-governance-suite（统一治理套件）

**合并源**: 4个 → 1个
- decision-governance
- workspace-integrity-guardian
- skill-integration-optimizer
- cross-skill-orchestrator

**功能**:
```python
class GovernanceSuite:
    def audit(self, scope):
        """全面审计"""
        pass
    
    def optimize(self, target):
        """自动优化"""
        pass
    
    def guard(self, action):
        """安全守护"""
        pass
```

---

## 3. 业务套件层（Domain Suites）

### 3.1 satisficing-partner-decision（满意解决策套件）

**核心功能**:
- 合伙人评估
- 决策支持
- 风险评估
- 模式匹配

### 3.2 client-persona-simulator（客户替身套件）

**包含替身**:
- 陈明远（科学家型）
- 张建国（创业者型）
- 李晓雯（跨界转型型）

### 3.3 multi-agent-debater（多智能体辩论套件）

**参与方**:
- 黎红雷替身（伦理视角）
- 罗汉替身（数学视角）
- 客户替身（需求视角）
- 蓝军替身（批判视角）

### 3.4 prospect-theory（前景理论套件）

### 3.5 behavioral-design（行为设计套件）

### 3.6 expert-digital-twin-trainer（专家训练套件）

---

## 4. 文档体系架构

### 4.1 目录结构

```
docs/
├── README.md                    # 总索引导航
├── ARCHITECTURE.md              # 架构文档（V2.0）
├── STRATEGY.md                  # 战略文档（最新版）
│
├── SOP/                         # 标准操作流程
│   ├── README.md
│   ├── cron-management.md
│   ├── skill-management.md
│   ├── meeting-management.md
│   ├── backup-management.md
│   └── first-principle-audit.md
│
├── RESEARCH/                    # 研究报告
│   ├── README.md
│   ├── alphago-insights.md
│   ├── qpms-framework.md
│   └── partner-case-studies.md
│
├── DELIVERABLES/                # 交付文档
│   ├── README.md
│   ├── brand-messaging.md
│   ├── partner-assessment-tool.md
│   └── training-materials.md
│
└── ARCHIVE/                     # 归档（按月）
    ├── 2026-03/
    ├── 2026-02/
    └── ...
```

### 4.2 版本管理规则

```
版本命名: V{主版本}.{次版本}.{修订}
示例: V2.1.3

主版本（Major）: 架构级变更
次版本（Minor）: 功能新增/重大改进
修订（Patch）: Bug修复/小调整

文档头模板:
---
title: [文档标题]
version: V2.1.3
last_updated: 2026-03-15
status: [draft/review/active/archived]
author: [作者]
---
```

---

## 5. 数据记忆架构

### 5.1 目录结构

```
memory/
├── README.md                    # 记忆索引
├── CORE.md                      # 核心记忆（精简）
│
├── daily/                       # 每日日志
│   ├── 2026-03-15.md
│   ├── 2026-03-14.md
│   └── ...
│
├── intelligence/                # 情报收集
│   ├── 2026-03/
│   │   ├── ai-industry.json
│   │   └── partner-news.json
│   └── ...
│
├── decisions/                   # 重要决策
│   ├── D-001-strategy-pivot.md
│   ├── D-002-skill-merge.md
│   └── ...
│
├── knowledge-graph.json         # 知识图谱
│
└── ARCHIVE/                     # 归档
    └── YYYY-MM/
```

### 5.2 知识图谱结构

```json
{
  "entities": [
    {"id": "E1", "type": "skill", "name": "unified-search"},
    {"id": "E2", "type": "doc", "name": "ARCHITECTURE.md"},
    {"id": "E3", "type": "decision", "name": "Cron合并优化"}
  ],
  "relations": [
    {"from": "E1", "to": "E2", "type": "documented_in"},
    {"from": "E3", "to": "E1", "type": "impacts"}
  ]
}
```

---

## 6. 自动化架构

### 6.1 Cron架构 V2.0

```
Daily Cron（合并后）:
├── 晨间统一检查（09:00）
│   ├── 安全检查
│   ├── 资讯采集
│   ├── milestone检查
│   └── 晨报生成（汇总以上结果）
│
├── 晚间统一报告（22:00）
│   ├── 提醒审计
│   ├── 自主执行摘要
│   └── 日报生成
│
└── 每日站会（09:30）- 保留独立

事件驱动（取代高频检查）:
├── 文件变更 → 触发相关检查
├── 任务状态变更 → 触发协调
├── 异常检测 → 触发告警
└── 用户指令 → 触发执行
```

### 6.2 事件触发器

```python
class EventTrigger:
    def on_file_change(self, path):
        """文件变更时触发"""
        if path.startswith('skills/'):
            self.trigger_skill_check()
        elif path.startswith('docs/'):
            self.trigger_doc_index_update()
    
    def on_task_status_change(self, task_id, new_status):
        """任务状态变更时触发"""
        if new_status == 'blocked':
            self.notify_user()
        elif new_status == 'completed':
            self.update_dashboard()
```

---

## 7. 实施路线图

### Phase 1: 基础设施（Week 1-2）

- [ ] 创建 unified-* 套件框架
- [ ] 实现 CLI 统一入口
- [ ] 完成 Cron 合并实施

### Phase 2: 套件迁移（Week 3-4）

- [ ] 迁移 intelligence 套件
- [ ] 迁移 document 套件
- [ ] 迁移 data 套件
- [ ] 迁移 content 套件

### Phase 3: 完善优化（Week 5-6）

- [ ] 迁移 notify 套件
- [ ] 迁移 automation 套件
- [ ] 迁移 governance 套件
- [ ] 重构文档体系

### Phase 4: 知识图谱（Week 7-8）

- [ ] 建立知识图谱
- [ ] 完善搜索能力
- [ ] 建立反馈循环

---

## 8. 关键指标

| 指标 | 当前(V1.0) | 目标(V2.0) | 变化 |
|-----|-----------|-----------|-----|
| Skill数量 | 176 | 15 | -91% |
| 套件数量 | 0 | 7 | +7 |
| 命令数量 | 176 | 7 | -96% |
| 文档数量 | 134 | ~40 | -70% |
| Daily Cron | 9 | 2 | -78% |
| Token/日 | ~50K | ~15K | -70% |
| 管理时间/月 | ~50h | ~10h | -80% |

---

*文档版本: V2.0*  
*最后更新: 2026-03-15*  
*状态: 草案（待审批）*
