#!/bin/bash
# decision-guardian Cron配置
# 决策守护者 - 蓝军机制+预审机制+冲突升级规则
# 生成时间: 2026-03-20

# 蓝军启动检查 - 每小时检查是否有新决策需要蓝军审查
echo "0 * * * * cd /root/.openclaw/workspace && python3 skills/decision-guardian/scripts/guardian.py redteam >> /tmp/decision-guardian.log 2>&1"

# 预审触发检查 - 每日09:00和15:00各一次
echo "0 9,15 * * * cd /root/.openclaw/workspace && python3 skills/decision-guardian/scripts/guardian.py prereview >> /tmp/decision-guardian.log 2>&1"

# 冲突升级检查 - 每2小时检查一次待解决冲突
echo "0 */2 * * * cd /root/.openclaw/workspace && python3 skills/decision-guardian/scripts/guardian.py escalation >> /tmp/decision-guardian.log 2>&1"

# 全面检查 - 每日01:00执行完整扫描
echo "0 1 * * * cd /root/.openclaw/workspace && python3 skills/decision-guardian/scripts/guardian.py all >> /tmp/decision-guardian.log 2>&1"

# 蓝军演习 - 每月1日进行一次蓝军演习
echo "0 10 1 * * cd /root/.openclaw/workspace && python3 skills/decision-guardian/scripts/guardian.py redteam >> /tmp/decision-guardian.log 2>&1"
