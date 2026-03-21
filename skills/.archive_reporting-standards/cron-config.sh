#!/bin/bash
# reporting-standards Cron配置
# 汇报标准协议自动化

# 每日汇报生成 - 每晚20:00
0 20 * * * cd /root/.openclaw/workspace && bash skills/reporting-standards/scripts/generate-report.sh daily >> /tmp/daily-report.log 2>&1

# 周执行率报告 - 每周六晚22:00
0 22 * * 6 cd /root/.openclaw/workspace && bash skills/reporting-standards/scripts/generate-report.sh weekly >> /tmp/weekly-compliance.log 2>&1
