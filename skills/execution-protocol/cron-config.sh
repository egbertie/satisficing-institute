#!/bin/bash
# execution-protocol Cron配置
# 执行流程协议自动化监控

# 任务链检查 - 每5分钟检查一次完成的任务
*/5 * * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/task-chain-checker.sh >> /tmp/exec-protocol-chain.log 2>&1

# 协议监控 - 每15分钟检查执行状态
*/15 * * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/protocol-check.sh >> /tmp/exec-protocol-monitor.log 2>&1

# 每日统计 - 每晚22:00生成当日统计
0 22 * * * cd /root/.openclaw/workspace && bash skills/execution-protocol/scripts/daily-stats.sh >> /tmp/exec-protocol-stats.log 2>&1
