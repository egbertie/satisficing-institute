#!/bin/bash
# Task Coordinator 快速检查脚本

echo "================================"
echo "任务协调快速检查"
echo "================================"
echo ""

cd /root/.openclaw/workspace/skills/task-coordinator
python3 task_coordinator.py

echo ""
echo "================================"
echo "检查完成"
echo "================================"
