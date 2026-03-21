# Optimization Rollback Guard Skill

## 功能概述
为优化提供回滚保障，优化前自动创建快照，支持一键回滚，确保系统可恢复。

## 核心功能
- **版本快照** - 优化前自动备份
- **版本管理** - 保留最近7个版本
- **一键回滚** - 快速恢复到指定版本
- **回滚验证** - 验证回滚后状态

## 使用方法

### 命令
```bash
# 创建快照
openclaw agent --skill optimization-rollback-guard --task create-snapshot --desc "优化Cron配置"

# 回滚到版本
openclaw agent --skill optimization-rollback-guard --task rollback --version v-20260315-120000

# 清理旧版本
openclaw agent --skill optimization-rollback-guard --task cleanup-versions
```

### Python调用
```python
from skills.optimization_rollback_guard import VersionManager

manager = VersionManager()
version_id = manager.create_snapshot("优化Cron配置")
# ... 优化失败 ...
manager.rollback(version_id)
```

## 回滚验证清单
- [ ] 核心文件存在性
- [ ] Skill可执行性
- [ ] Cron配置有效
- [ ] 数据一致性

## 数据存储
见 `data/versions/`

## 作者
满意解研究所 - 持续优化系统

## 版本
v1.0.0 - 2026-03-15
