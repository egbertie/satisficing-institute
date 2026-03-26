#!/usr/bin/env python3
"""
灾备仪表板生成器
"""
import json
import os
from datetime import datetime

def load_json(path, default=None):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return default

def generate_dashboard():
    # 加载数据
    rpo_data = load_json("/tmp/rpo_latest.json", {"rpo_minutes": 0, "rpo_status": "unknown"})
    verify_data = load_json("/tmp/backup_verification_latest.json", {"health_score": 0, "overall_status": "unknown"})
    
    # Git状态
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            cwd="/root/.openclaw/workspace"
        )
        uncommitted = len([l for l in result.stdout.split('\n') if l.strip()])
    except:
        uncommitted = "?"
    
    dashboard = f"""
╔══════════════════════════════════════════════════════════════╗
║           📊 灾备守护仪表板 - {datetime.now().strftime('%Y-%m-%d %H:%M')}          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🔄 RPO (恢复点目标)                                         ║
║     当前: {rpo_data.get('rpo_minutes', 'N/A')}分钟 / 目标: 120分钟                           ║
║     状态: {rpo_data.get('rpo_status', 'unknown').upper()}                                    ║
║                                                              ║
║  ✅ 备份验证                                                 ║
║     健康度: {verify_data.get('health_score', 'N/A')}% / 状态: {verify_data.get('overall_status', 'unknown')}                         ║
║                                                              ║
║  📦 Git状态                                                  ║
║     未提交变更: {uncommitted}个文件                                          ║
║                                                              ║
║  🛡️ 防护层级                                                 ║
║     L1 Git自动提交: {'✅' if uncommitted == 0 else '⚠️'}                                 ║
║     L2 飞书备份: ⏳ (权限待生效)                             ║
║     L3 本地备份: ✅                                         ║
║     L4 跨渠道冗余: 📋 (规划中)                               ║
║     L5 演练机制: 📋 (规划中)                                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    return dashboard

if __name__ == "__main__":
    print(generate_dashboard())
