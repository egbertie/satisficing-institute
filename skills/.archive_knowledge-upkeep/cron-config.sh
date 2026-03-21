#!/bin/bash
# knowledge-upkeep Cron配置
# 知识维护者 - 专家档案标注+记忆维护周期
# 生成时间: 2026-03-20

# 专家档案更新 - 每日03:00执行
echo "0 3 * * * cd /root/.openclaw/workspace && python3 skills/knowledge-upkeep/scripts/upkeeper.py expert >> /tmp/knowledge-upkeep.log 2>&1"

# 知识时效性扫描 - 每日09:07执行
echo "7 9 * * * cd /root/.openclaw/workspace && python3 skills/knowledge-upkeep/scripts/upkeeper.py knowledge >> /tmp/knowledge-upkeep.log 2>&1"

# 更新提醒发送 - 每周一10:00发送
echo "0 10 * * 1 cd /root/.openclaw/workspace && python3 skills/knowledge-upkeep/scripts/upkeeper.py maintenance >> /tmp/knowledge-upkeep.log 2>&1"

# 知识价值评估 - 每月1日04:00执行
echo "0 4 1 * * cd /root/.openclaw/workspace && python3 skills/knowledge-upkeep/scripts/upkeeper.py knowledge >> /tmp/knowledge-upkeep.log 2>&1"

# 知识缺口识别 - 每周日22:00执行
echo "0 22 * * 0 cd /root/.openclaw/workspace && python3 skills/knowledge-upkeep/scripts/upkeeper.py knowledge >> /tmp/knowledge-upkeep.log 2>&1"
