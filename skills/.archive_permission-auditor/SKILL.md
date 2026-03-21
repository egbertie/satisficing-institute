# Permission Auditor Skill

## Purpose
审计和管理所有第三方服务权限

## 5-Standard Compliance

| Standard | Implementation |
|----------|----------------|
| 全局考虑 | 覆盖所有服务的权限清单管理 |
| 系统考虑 | 需求识别→权限申请→验证→使用→定期复核闭环 |
| 迭代机制 | 权限变更自动记录，定期复核必要性 |
| Skill化 | 标准化接口：audit/request/verify/renew |
| 自动化 | 每周检查权限完整度，到期前预警 |

## Commands
- `audit` - 审计当前权限
- `request` - 申请新权限
- `verify` - 验证权限有效性
- `renew` - 续期即将到期权限
