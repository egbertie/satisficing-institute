# Notion同步保障方案 - 多策略并行文档

> 文档版本: 1.0  
> 更新日期: 2026-03-10  
> 适用场景: 263个文件批量同步到Notion

---

## 一、现状概述

### 同步任务状态
| 指标 | 数值 |
|------|------|
| 总文件数 | 263 |
| 已成功 | 8 |
| 已失败 | 14 |
| 待同步 | 255 |

### 主要问题
1. **连接中断** - `RemoteDisconnected` 远程连接被关闭
2. **速率限制** - 429 Too Many Requests
3. **API格式错误** - 400 Bad Request（内容块结构问题）
4. **网络超时** - 请求响应时间过长

---

## 二、三策略并行方案

### 方案A：GitHub Actions自动化 ⭐推荐

#### 特点
- **长期稳定**: 基于GitHub基础设施，网络环境稳定
- **定时执行**: 每日凌晨自动运行
- **自动重试**: 失败自动重试，无需人工干预
- **历史记录**: 完整执行日志和报告

#### 工作流程
```yaml
# .github/workflows/notion-sync.yml
触发条件:
  - 每日凌晨 02:00 (UTC+8)
  - 手动触发 (workflow_dispatch)
  - 推送特定标签

执行步骤:
  1. 检出代码
  2. 设置 Python 3.11
  3. 安装依赖
  4. 执行 notion_sync_optimized.py
  5. 上传报告到Artifacts
  6. 发送通知 (成功/失败)

批次策略:
  - 每批10个文件
  - 批次间隔60秒
  - 单文件重试3次
  - 连接超时60秒，读取超时120秒
```

#### 环境变量配置
```bash
# GitHub Secrets 配置
NOTION_TOKEN=ntn_xxxxx
NOTION_PARENT_PAGE_ID=31fa8a0e-2bba-81fa-b98a-d61da835051e
WORKSPACE_DIR=/github/workspace
BATCH_SIZE=10
MAX_RETRIES=5
```

#### 执行命令
```bash
# 本地测试
cd /root/.openclaw/workspace
python notion_sync_optimized.py --batch-size 10

# 查看进度
python -c "import json; print(json.load(open('.notion_sync_v4_progress.json')))"

# 重置进度
python notion_sync_optimized.py --reset
```

---

### 方案B：Jina AI + Notion组合 🤖智能处理

#### 特点
- **AI预处理**: 使用Jina AI优化内容结构
- **智能分块**: 自动将长内容分块处理
- **异步并发**: 提高同步效率
- **格式优化**: 自动转换Markdown为Notion块

#### 技术架构
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  本地文件    │ -> │  Jina AI    │ -> │ Notion API  │
│  (Markdown) │    │ (内容优化)   │    │ (页面创建)  │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### 处理流程
1. **内容读取** - 多编码支持，容错处理
2. **Jina处理** - 结构化分析，智能分块
3. **块转换** - 转换为Notion Block格式
4. **异步上传** - 并发创建页面和添加内容
5. **进度保存** - 断点续传支持

#### 启动方式
```bash
# 方式1: 使用Jina API (需要API Key)
export JINA_API_KEY=your_key_here
python notion_sync_jina.py

# 方式2: 本地处理 (无需API Key)
python notion_sync_jina.py  # 自动回退到本地处理

# 方式3: 干运行测试
python notion_sync_jina.py --dry-run
```

#### 性能参数
| 参数 | 默认值 | 说明 |
|------|--------|------|
| MAX_CONCURRENT | 3 | 并发请求数 |
| BATCH_SIZE | 5 | 批次大小 |
| NOTION_RATE_LIMIT | 0.5 | 请求间隔(秒) |
| FILE_INTERVAL | 3.0 | 文件间隔(秒) |

---

### 方案C：本地脚本 + 手动触发 💪保底方案

#### 特点
- **断点续传** - 随时中断，随时恢复
- **连接池复用** - 减少连接开销
- **指数退避** - 智能重试间隔
- **完整日志** - 详细记录便于排查

#### 核心功能
```python
# notion_sync_optimized.py 核心特性

1. ConnectionPool
   - HTTP连接池复用
   - urllib3重试策略
   - 连接保持和复用

2. ProgressManager
   - JSON进度持久化
   - 已完成文件跳过
   - 失败文件重试计数

3. 智能分块
   - 按段落分割
   - 标题识别(H1/H2/H3)
   - 长度控制(每块<1900字节)

4. 重试机制
   - 指数退避: 2^n 秒
   - 最大重试: 5次
   - 特定错误处理(429/超时/连接错误)
```

#### 使用场景
| 场景 | 推荐方案 | 命令 |
|------|----------|------|
| 首次全量同步 | C | `python notion_sync_optimized.py` |
| 增量同步 | C | `python notion_sync_optimized.py` |
| 定时自动同步 | A | GitHub Actions自动触发 |
| 大批量文件 | B | `python notion_sync_jina.py` |
| 网络不稳定 | C | 本地执行，断点续传 |

---

## 三、执行计划

### 阶段一：立即可执行（今天）

#### 1. 本地脚本同步（方案C）
```bash
# 进入工作目录
cd /root/.openclaw/workspace

# 检查进度
cat .notion_sync_v4_progress.json 2>/dev/null || echo "无进度文件"

# 开始同步（从断点续传）
python notion_sync_optimized.py

# 或者指定批次大小
python notion_sync_optimized.py --batch-size 5
```

#### 2. Jina AI方案（方案B）
```bash
# 干运行测试
python notion_sync_jina.py --dry-run

# 正式执行
python notion_sync_jina.py
```

### 阶段二：自动化配置（本周）

#### GitHub Actions配置
文件位置: `.github/workflows/notion-sync.yml`

```yaml
name: Notion Sync

on:
  schedule:
    - cron: '0 18 * * *'  # 每天凌晨 02:00 UTC+8
  workflow_dispatch:      # 手动触发

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install requests
      
      - name: Sync to Notion
        env:
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_PARENT_PAGE_ID: ${{ secrets.NOTION_PARENT_PAGE_ID }}
        run: python notion_sync_optimized.py --batch-size 10
      
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: sync-report
          path: docs/NOTION_SYNC_V4_REPORT.md
      
      - name: Upload progress
        uses: actions/upload-artifact@v4
        with:
          name: sync-progress
          path: .notion_sync_v4_progress.json
```

### 阶段三：监控优化（持续）

#### 监控指标
| 指标 | 目标值 | 监控方式 |
|------|--------|----------|
| 同步成功率 | >95% | 报告统计 |
| 平均处理时间 | <5秒/文件 | 日志分析 |
| API错误率 | <2% | 错误日志 |
| 断点恢复时间 | <30秒 | 进度文件 |

---

## 四、故障排查

### 常见问题

#### 1. Connection aborted / RemoteDisconnected
```
原因: 网络连接不稳定或Notion服务端关闭连接
解决: 
  - 增加超时时间: CONNECT_TIMEOUT=60 READ_TIMEOUT=120
  - 启用连接池复用
  - 使用指数退避重试
```

#### 2. 429 Too Many Requests
```
原因: 请求频率过高触发速率限制
解决:
  - 增加请求间隔: FILE_INTERVAL=3.0 BATCH_INTERVAL=10.0
  - 检查Retry-After头部
  - 降低并发数: MAX_CONCURRENT=2
```

#### 3. 400 Bad Request
```
原因: 内容块格式不符合API要求
解决:
  - 简化内容块结构
  - 检查块大小(<1900字节)
  - 过滤特殊字符
```

#### 4. 断点续传失效
```
原因: 进度文件损坏或版本不兼容
解决:
  - 重置进度: python notion_sync_optimized.py --reset
  - 检查进度文件格式
  - 手动编辑进度文件
```

### 诊断命令
```bash
# 检查网络连通性
curl -I https://api.notion.com/v1

# 测试API Token
export NOTION_TOKEN=your_token
curl -H "Authorization: Bearer $NOTION_TOKEN" \
     -H "Notion-Version: 2022-06-28" \
     https://api.notion.com/v1/users/me

# 查看日志
tail -f logs/notion_sync_v4.log

# 统计待同步文件数
python -c "
import json
with open('.notion_sync_v4_progress.json') as f:
    p = json.load(f)
    completed = len(p['completed_files'])
    failed = len(p['failed_files'])
    print(f'已完成: {completed}, 失败: {failed}')
"
```

---

## 五、文件清单

### 输出文件
| 文件 | 说明 |
|------|------|
| `notion_sync_optimized.py` | 优化版同步脚本（方案C） |
| `notion_sync_jina.py` | Jina AI方案（方案B） |
| `notion_sync_multi_strategy.md` | 本策略文档 |
| `.notion_sync_v4_progress.json` | 同步进度 |
| `.notion_sync_jina_progress.json` | Jina方案进度 |
| `docs/NOTION_SYNC_V4_REPORT.md` | V4同步报告 |
| `docs/NOTION_SYNC_JINA_REPORT.md` | Jina方案报告 |
| `logs/notion_sync_v4.log` | V4运行日志 |
| `logs/notion_sync_jina.log` | Jina运行日志 |

---

## 六、决策树

```
需要同步到Notion？
├── 文件数 < 10
│   └── 使用 notion_sync_v3.py（简化版）
├── 文件数 10-50
│   ├── 网络稳定？
│   │   ├── 是 -> 使用 notion_sync_optimized.py
│   │   └── 否 -> 使用 GitHub Actions
├── 文件数 > 50
│   ├── 需要AI优化？
│   │   ├── 是 -> 使用 notion_sync_jina.py
│   │   └── 否 -> 使用 notion_sync_optimized.py
└── 需要定时自动同步？
    └── 配置 GitHub Actions
```

---

## 七、附录

### A. 环境变量完整列表

```bash
# Notion配置
NOTION_TOKEN=ntn_xxxxx
NOTION_PARENT_PAGE_ID=xxxxx

# 路径配置
WORKSPACE_DIR=/root/.openclaw/workspace

# Jina配置
JINA_API_KEY=optional_key

# 同步参数
BATCH_SIZE=10
MAX_RETRIES=5
FILE_INTERVAL=2.0
BATCH_INTERVAL=10.0
CONNECT_TIMEOUT=30
READ_TIMEOUT=120
BACKOFF_FACTOR=2.0
MAX_CONCURRENT=3
NOTION_RATE_LIMIT=0.5
```

### B. 快速启动命令

```bash
# 方案C - 本地优化版
cd /root/.openclaw/workspace
python notion_sync_optimized.py

# 方案B - Jina AI版
python notion_sync_jina.py

# 方案A - GitHub Actions
# 在GitHub仓库的Actions标签页中触发

# 查看所有方案状态
ls -la notion_sync_*.py
ls -la .notion_sync_*_progress.json
ls -la logs/
```

---

*本文档由Notion同步保障方案自动生成*  
*最后更新: 2026-03-10*
