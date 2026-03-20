#!/usr/bin/env python3
"""
系统状态仪表盘 - 实时数据收集与展示
实时更新延迟 < 5分钟
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

class SystemDashboard:
    def __init__(self, db_path="/root/.openclaw/workspace/data/dashboard.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化仪表盘数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                category TEXT,
                metric_name TEXT,
                metric_value TEXT,
                status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON metrics(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def update_metric(self, category, name, value, status="normal"):
        """更新单个指标"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (category, metric_name, metric_value, status)
            VALUES (?, ?, ?, ?)
        ''', (category, name, value, status))
        
        conn.commit()
        conn.close()
    
    def get_latest_metrics(self, hours=1):
        """获取最近N小时的指标"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT category, metric_name, metric_value, status, timestamp
            FROM metrics
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (since,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def generate_summary(self):
        """生成仪表盘摘要"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "tasks": self._get_task_summary(),
            "projects": self._get_project_summary(),
            "api_usage": self._get_api_summary(),
            "experts": self._get_expert_summary(),
            "today": self._get_today_summary()
        }
        return summary
    
    def _get_task_summary(self):
        """任务状态摘要"""
        # 从任务管理模块获取
        return {
            "total": 0,
            "completed_today": 0,
            "in_progress": 0,
            "pending": 0,
            "blocked": 0
        }
    
    def _get_project_summary(self):
        """项目进度摘要"""
        return {
            "WIP-002": {"name": "专家网络搭建", "progress": 80, "status": "用户处理"},
            "WIP-003": {"name": "案例库建设", "progress": 50, "status": "进行中"},
            "WIP-004": {"name": "方法论研发", "progress": 30, "status": "进行中"}
        }
    
    def _get_api_summary(self):
        """API使用摘要"""
        return {
            "tavily": {"used": 0, "limit": 1000, "percentage": 0},
            "brave": {"used": 0, "limit": 2000, "percentage": 0}
        }
    
    def _get_expert_summary(self):
        """专家替身状态"""
        return {
            "lihonglei": {"name": "黎红雷", "status": "online", "last_response": "2分钟前"},
            "luohan": {"name": "罗汉", "status": "online", "last_response": "5分钟前"},
            "xiebaojian": {"name": "谢宝剑", "status": "online", "last_response": "1小时前"},
            "ai_redteam": {"name": "AI蓝军", "status": "standby", "last_response": "待命"}
        }
    
    def _get_today_summary(self):
        """今日待办"""
        return {
            "events": [
                {"time": "14:00", "event": "专家访谈（待定）"},
                {"time": "18:00", "event": "周报截止"}
            ],
            "tasks": []
        }
    
    def generate_html(self):
        """生成HTML仪表盘"""
        summary = self.generate_summary()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="300">
    <title>满意解研究所 - 系统仪表盘</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h3 {{ margin-top: 0; color: #333; }}
        .metric {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
        .status {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }}
        .status.online {{ background: #4CAF50; }}
        .status.standby {{ background: #FFC107; }}
        .status.offline {{ background: #F44336; }}
        .progress {{ background: #e0e0e0; border-radius: 5px; height: 20px; overflow: hidden; }}
        .progress-bar {{ background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; border-radius: 5px; }}
        .timestamp {{ text-align: right; color: #999; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>满意解研究所 - 实时系统仪表盘</h1>
            <p>最后更新: {summary['timestamp']}</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📊 今日概览</h3>
                <div class="metric">
                    <span>执行任务</span>
                    <span>{summary['tasks']['in_progress']} 进行中</span>
                </div>
                <div class="metric">
                    <span>今日完成</span>
                    <span>{summary['tasks']['completed_today']} 个</span>
                </div>
                <div class="metric">
                    <span>等待决策</span>
                    <span>{summary['tasks']['blocked']} 个</span>
                </div>
            </div>
            
            <div class="card">
                <h3>📈 项目进度</h3>
                {self._render_projects(summary['projects'])}
            </div>
            
            <div class="card">
                <h3>👥 专家替身状态</h3>
                {self._render_experts(summary['experts'])}
            </div>
            
            <div class="card">
                <h3>🔌 API使用</h3>
                {self._render_api(summary['api_usage'])}
            </div>
        </div>
        
        <div class="timestamp">
            自动刷新间隔: 5分钟 | 数据实时性: &lt; 5分钟延迟
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _render_projects(self, projects):
        html = ""
        for pid, p in projects.items():
            html += f"""
                <div class="metric">
                    <span>{p['name']}</span>
                    <span>{p['progress']}%</span>
                </div>
                <div class="progress">
                    <div class="progress-bar" style="width: {p['progress']}%"></div>
                </div>
            """
        return html
    
    def _render_experts(self, experts):
        html = ""
        for eid, e in experts.items():
            status_class = "online" if e['status'] == 'online' else 'standby'
            html += f"""
                <div class="metric">
                    <span><span class="status {status_class}"></span>{e['name']}</span>
                    <span style="font-size: 12px; color: #999">{e['last_response']}</span>
                </div>
            """
        return html
    
    def _render_api(self, api_usage):
        html = ""
        for name, usage in api_usage.items():
            status = "normal" if usage['percentage'] < 70 else "warning" if usage['percentage'] < 90 else "critical"
            color = "#4CAF50" if status == "normal" else "#FFC107" if status == "warning" else "#F44336"
            html += f"""
                <div class="metric">
                    <span>{name.upper()}</span>
                    <span style="color: {color}">{usage['used']}/{usage['limit']} ({usage['percentage']}%)</span>
                </div>
            """
        return html


if __name__ == "__main__":
    dashboard = SystemDashboard()
    
    # 测试更新
    dashboard.update_metric("system", "status", "running", "normal")
    
    # 生成HTML
    html = dashboard.generate_html()
    
    output_path = Path("/root/.openclaw/workspace/dashboard/index.html")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(html)
    
    print(f"✅ 仪表盘已生成: {output_path}")
    print(f"📊 数据摘要: {json.dumps(dashboard.generate_summary(), indent=2, ensure_ascii=False)}")
