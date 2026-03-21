# API Configuration Manager Skill

## Purpose
管理所有第三方API的配置、注册和状态监控

## 5-Standard Compliance

| Standard | Implementation |
|----------|----------------|
| 全局考虑 | 覆盖GitHub Models/Perplexity/Jina AI/Excalidraw等 |
| 系统考虑 | 注册→配置→验证→监控→更新闭环 |
| 迭代机制 | 定期检查配置有效性，自动更新失效配置 |
| Skill化 | 标准化接口：register/configure/verify/monitor |
| 自动化 | 自动检测未配置API，自动触发注册流程 |

## APIs Managed
- GitHub Models
- Perplexity
- Jina AI
- Excalidraw
- Claude (备用)
