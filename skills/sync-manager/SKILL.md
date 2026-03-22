# 同步管理Skill

自动数据同步管理工具，支持多目标同步、断点续传、自动重试和完整性校验。

## 功能特性

- **自动重试机制**：失败自动重试3次，支持指数退避
- **多目标同步**：支持Notion、GitHub、本地备份同步
- **断点续传**：记录进度，中断后从断点继续
- **完整性校验**：同步后自动检查数据完整性

## 使用方法

```bash
# 完整同步
python sync_manager.py sync-all

# 同步特定目标
python sync_manager.py sync --target notion
python sync_manager.py sync --target github
python sync_manager.py sync --target local

# 检查同步状态
python sync_manager.py status

# 清理断点记录
python sync_manager.py clean
```

## 配置文件

编辑 `config/sync.conf` 配置同步参数。

## 依赖

- Python 3.7+
- requests
- schedule
