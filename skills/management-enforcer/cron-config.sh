#!/bin/bash
# management-enforcer Cron配置
# 管理层执行者 - 诚实汇报+沟通协议+惩罚措施
# 生成时间: 2026-03-20

# 日报检查 - 每日22:30检查日报提交情况
echo "30 22 * * * cd /root/.openclaw/workspace && python3 skills/management-enforcer/scripts/enforcer.py report >> /tmp/management-enforcer.log 2>&1"

# 沟通响应检查 - 每4小时检查一次
echo "0 */4 * * * cd /root/.openclaw/workspace && python3 skills/management-enforcer/scripts/enforcer.py comm >> /tmp/management-enforcer.log 2>&1"

# 违规检测 - 每日09:30和14:30各一次
echo "30 9,14 * * * cd /root/.openclaw/workspace && python3 skills/management-enforcer/scripts/enforcer.py violation >> /tmp/management-enforcer.log 2>&1"

# 全面检查 - 每日02:00执行完整扫描
echo "0 2 * * * cd /root/.openclaw/workspace && python3 skills/management-enforcer/scripts/enforcer.py all >> /tmp/management-enforcer.log 2>&1"
