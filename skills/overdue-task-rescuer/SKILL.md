# Overdue Task Rescuer Skill

## Purpose
自动检测逾期任务并执行补救

## 5-Standard Compliance

| Standard | Implementation |
|----------|----------------|
| 全局考虑 | 覆盖所有任务的逾期检测与补救 |
| 系统考虑 | 扫描→评估→补救→验证→根因分析闭环 |
| 迭代机制 | 补救后分析根因，优化预防机制 |
| Skill化 | 标准化接口：scan/assess/rescue/verify/analyze |
| 自动化 | 每日扫描逾期任务，自动触发补救 |

## Commands
- `scan` - 扫描逾期任务
- `assess` - 评估补救方案
- `rescue` - 执行补救
- `verify` - 验证补救结果
- `analyze` - 根因分析
