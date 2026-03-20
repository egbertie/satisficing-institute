# API Failover Manager Skill

## Purpose
监控API可用性，自动故障切换

## 5-Standard Compliance

| Standard | Implementation |
|----------|----------------|
| 全局考虑 | 覆盖所有关键API的监控与切换 |
| 系统考虑 | 检测→告警→切换→恢复→记录闭环 |
| 迭代机制 | 故障后分析，更新切换策略 |
| Skill化 | 标准化接口：monitor/switch/restore/report |
| 自动化 | 每分钟检测API状态，自动切换 |

## Commands
- `monitor` - 监控API状态
- `switch` - 切换到备用API
- `restore` - 恢复主API
- `report` - 生成可用性报告
