# 满意解研究所 · Skill与API完整清单

**统计时间**: 2026-03-10 22:48  
**范围**: 全部自创Skill + 外接API

---

## 🛠️ 一、自创Skill（自建）

### 1. 任务管理Skill
| 项目 | 详情 |
|------|------|
| **名称** | task-manager |
| **路径** | `skills/task-manager/` |
| **主要作用** | 任务跟踪、状态管理、进度报告 |
| **核心文件** | SKILL.md, track-tasks.py, daily-report.md, reminder-rules.json |
| **链接情况** | 本地运行，无需外部连接 |
| **运作状态** | ✅ 正常运行 |
| **产出成果** | TASK_MASTER.md（42项任务跟踪）、每日晨报模板 |

### 2. 任务协调管理Skill V2.0 ⭐
| 项目 | 详情 |
|------|------|
| **名称** | task-coordinator |
| **路径** | `skills/task-coordinator/` |
| **主要作用** | 智能协调任务执行模式（sequential/parallel/notify_user）、学习迭代、资源调度 |
| **核心文件** | task_coordinator_v2.py, config/rules.json, config/strategy.json |
| **链接情况** | 本地运行 + 每小时cron定时检查 |
| **运作状态** | ✅ 正常运行，已部署定时任务 |
| **产出成果** | 自动检测过期任务、启动并行补救、生成协调报告 |
| **特色能力** | 风险评分、自动模式切换、决策记录、持续优化策略 |

### 3. 飞书文档Skill
| 项目 | 详情 |
|------|------|
| **名称** | feishu-doc |
| **路径** | `skills/feishu-doc/` |
| **主要作用** | 飞书云文档读写操作 |
| **核心文件** | SKILL.md |
| **链接情况** | 链接飞书API（cli_a927c5dfa4381cc6）|
| **运作状态** | ⚠️ 受限（权限问题待解决）|
| **产出成果** | 文档创建成功，但权限隔离导致用户不可见 |

### 4. 飞书知识库Skill
| 项目 | 详情 |
|------|------|
| **名称** | feishu-wiki |
| **路径** | `skills/feishu-wiki/` |
| **主要作用** | 飞书Wiki空间操作 |
| **核心文件** | SKILL.md |
| **链接情况** | 链接飞书API |
| **运作状态** | ⚠️ 待配置 |
| **产出成果** | 暂未使用 |

### 5. 外部工具配置Skill
| 项目 | 详情 |
|------|------|
| **名称** | 外部工具配置 |
| **路径** | `.config/` |
| **主要作用** | 存储外部工具配置信息 |
| **核心文件** | 外部工具配置信息.md, excalidraw/docker-compose.yml, figjam-create.sh |
| **链接情况** | 本地配置 |
| **运作状态** | ✅ 已配置 |
| **产出成果** | Excalidraw本地部署配置、FigJam创建脚本 |

---

## 🔌 二、外接API与集成

### 1. Kimi API（月之暗面）
| 项目 | 详情 |
|------|------|
| **提供商** | 月之暗面（Moonshot AI）|
| **API Key** | Allegretto限额内 |
| **主要作用** | 代码生成、中文处理、长文本分析 |
| **链接状态** | ✅ 正常 |
| **使用频率** | 高（当前对话）|
| **产出成果** | 全部文档生成、代码编写、任务协调 |

### 2. GitHub API
| 项目 | 详情 |
|------|------|
| **提供商** | GitHub |
| **API Key** | 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（已验证）|
| **主要作用** | 代码托管、版本控制、备份、Actions自动化 |
| **链接状态** | ✅ 正常 |
| **使用频率** | 中 |
| **产出成果** | 245个文件Git备份、GitHub Models API待配置 |

### 3. GitHub Models API（待配置）
| 项目 | 详情 |
|------|------|
| **提供商** | GitHub |
| **API Key** | 同上 |
| **主要作用** | 免费GPT-4o模型调用 |
| **链接状态** | ⏳ 待配置（计划3/11配置）|
| **使用频率** | 待启动 |
| **预期成果** | Claude API的免费替代方案 |

### 4. Notion API
| 项目 | 详情 |
|------|------|
| **提供商** | Notion |
| **API Key** | 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（已验证）|
| **主要作用** | 知识库同步、文档协作 |
| **链接状态** | ✅ 正常 |
| **使用频率** | 中（正在同步）|
| **产出成果** | 263个文件准备同步、工作空间：满意解研究所 |

### 5. Jina AI API
| 项目 | 详情 |
|------|------|
| **提供商** | Jina AI |
| **API Key** | jina_448e2c72ff414835b8b35eebf13d7840C9XK6Je9WwRIikSJVfRM44tYoZD8（已验证）|
| **主要作用** | 网页内容提取、文本向量化 |
| **链接状态** | ✅ 正常 |
| **使用频率** | 低 |
| **产出成果** | 网页提取测试成功 |

### 6. Perplexity API
| 项目 | 详情 |
|------|------|
| **提供商** | Perplexity |
| **API Key** | sk-ofRU1F9plRRXyeL6qN5NH3dNXEXp7JaNunA2IEXuSwhY73dd（已配置）|
| **主要作用** | AI搜索、实时信息查询（300次/天免费）|
| **链接状态** | ✅ 已配置（待详细测试）|
| **使用频率** | 低 |
| **预期成果** | 高质量信息检索 |

### 7. Claude API（暂不可用）
| 项目 | 详情 |
|------|------|
| **提供商** | Anthropic |
| **API Key** | sk-ant-api03-M3DvotVTaZ-n4ak8h7s0YmmWujyeC4XwYoVxUxlL...（已配置）|
| **主要作用** | 复杂编程、代码生成 |
| **链接状态** | ❌ 403 Forbidden（地区限制）|
| **使用频率** | 暂停 |
| **替代方案** | GitHub Models GPT-4o |

### 8. 飞书开放平台API
| 项目 | 详情 |
|------|------|
| **提供商** | 飞书（Lark）|
| **App ID** | cli_a927c5dfa4381cc6 |
| **主要作用** | 文档创建、权限管理、消息推送 |
| **链接状态** | ⚠️ 受限（tenant_token可用，user_token待获取）|
| **使用频率** | 调试中 |
| **产出成果** | 文档创建成功（但权限隔离）、技术问题总结文档 |

---

## 🤖 三、ClawHub Skill（外部安装）

### 1. GitHub Integration
| 项目 | 详情 |
|------|------|
| **名称** | github-integration |
| **安装状态** | ✅ 已安装（20:16完成）|
| **主要作用** | GitHub深度集成、Webhook自动配置 |
| **链接情况** | 链接GitHub API |
| **运作状态** | ✅ 正常 |
| **产出成果** | 自动同步、Actions触发 |

### 2. Notion Integration
| 项目 | 详情 |
|------|------|
| **名称** | notion-integration |
| **安装状态** | ✅ 已安装（20:16完成）|
| **主要作用** | Notion数据库同步模块 |
| **链接情况** | 链接Notion API |
| **运作状态** | ✅ 正常 |
| **产出成果** | 知识库自动同步 |

### 3. Slack Integration
| 项目 | 详情 |
|------|------|
| **名称** | slack-integration |
| **安装状态** | ⏳ 待重试（GitHub API限流）|
| **主要作用** | Slack增强通知 |
| **链接情况** | 待安装 |
| **运作状态** | 未启动 |

---

## 🎨 四、AI图片生成能力

### 计划使用（未配置API）
| 项目 | 详情 |
|------|------|
| **DALL-E 3** | OpenAI - 计划使用 |
| **Midjourney** | 独立服务 - 计划使用 |
| **Stable Diffusion** | 本地部署 - 备选方案 |
| **当前状态** | 准备Prompt提示词，手动复制到AI工具生成 |
| **产出成果** | 五路图腾信息图（进行中）|

---

## 📊 五、系统工具与脚本

### Python工具
| 名称 | 作用 | 状态 |
|------|------|------|
| trl_assessment.py | TRL自评工具（命令行）| ✅ 完成 |
| trl_api.py | TRL自评工具（Web版）| 🔄 80% |
| backup_manager.py | 备份管理 | ✅ 完成 |
| notion_sync.py | Notion同步 | ✅ 运行中 |
| feishu_*.py (8个) | 飞书API脚本 | ✅ 调试完成 |
| task_coordinator_v2.py | 任务协调引擎 | ✅ 运行中 |
| ai_image_generator.py | AI图片生成 | ⏳ 准备中 |

### Shell脚本
| 名称 | 作用 | 状态 |
|------|------|------|
| check.sh | 快速检查 | ✅ |
| full_file_inventory.sh | 文件盘点 | ✅ |
| figjam-create.sh | FigJam创建 | ✅ |

---

## 📈 六、运作情况总览

### 正常运行 ✅（7个）
1. Kimi API（主要对话）
2. GitHub API（备份）
3. Notion API（知识库）
4. Jina AI（网页提取）
5. 任务协调Skill V2.0（定时检查）
6. 任务管理Skill（跟踪）
7. GitHub Integration Skill

### 配置中/待优化 🔄（5个）
1. Notion Integration Skill（刚安装）
2. Notion完整同步（子代理运行中，明早8点完成）
3. 五路图腾AI生成（Prompt准备中）
4. Perplexity API（待深度测试）
5. TRL Web版（80%完成）

### 暂停/问题 ❌（2个）
1. Claude API（403地区限制）
2. 飞书OAuth（user_token获取受阻）

### 待配置 ⏳（3个）
1. GitHub Models API（GPT-4o，计划3/11）
2. Excalidraw本地部署（配置就绪）
3. Slack Integration（等待重试）

---

## 🏆 七、产出成果汇总

### 文档类（405个文件）
- 核心方法论：8份
- 管理体系：6份
- 专家体系：4份
- 33人知识库：69份
- 技术文档：15份
- 记忆日志：12份
- 报告：6份

### 工具类
- TRL自评工具（命令行+Web版）
- 任务协调引擎V2.0
- 备份管理脚本
- Notion同步工具

### 配置类
- 5个API配置（GitHub/Notion/Jina/Perplexity/Claude）
- 3个定时任务（安全检查/任务协调/文档同步）
- 飞书应用配置

---

**总Skill数：7个（4自创+3外接）**  
**总API数：8个（5正常+1问题+2待配置）**  
**总产出：424个文件 + 多个工具**

**24小时团队，AI生成任务已启动！** 🚀🎨