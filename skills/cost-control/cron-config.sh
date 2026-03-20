#!/bin/bash
# cost-control Cron配置
# 成本控制协议自动化监控

# 成本监控 - 每30分钟检查日限额
*/30 * * * * cd /root/.openclaw/workspace && bash skills/cost-control/scripts/daily-cost-check.sh >> /tmp/cost-monitor.log 2>&1

# 每日成本报告 - 每晚23:00生成
0 23 * * * cd /root/.openclaw/workspace && bash skills/cost-control/scripts/cost-stats.sh daily >> /tmp/cost-daily-report.log 2>&1

# 每周成本分析 - 每周日晚21:00生成
0 21 * * 0 cd /root/.openclaw/workspace && bash skills/cost-control/scripts/cost-stats.sh weekly >> /tmp/cost-weekly-report.log 2>&1
