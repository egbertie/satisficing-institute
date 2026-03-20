#!/bin/bash
# quality-assurance Cron配置
# 质量保证协议自动化监控

# 质量统计更新 - 每6小时更新
0 */6 * * * cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/confidence-stats.sh >> /tmp/quality-stats.log 2>&1

# 质量报告 - 每周日晚20:00生成
0 20 * * 0 cd /root/.openclaw/workspace && bash skills/quality-assurance/scripts/quality-report.sh weekly >> /tmp/quality-weekly.log 2>&1
