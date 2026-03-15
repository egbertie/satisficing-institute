#!/usr/bin/env python3
"""
分级通知系统 - 智能路由通知到不同渠道
紧急/重要/普通/归档 四级
"""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path

class NotificationLevel(Enum):
    EMERGENCY = "emergency"    # 紧急：系统故障、安全告警
    IMPORTANT = "important"    # 重要：任务完成、决策提醒
    NORMAL = "normal"          # 普通：进度更新、日报
    ARCHIVE = "archive"        # 归档：日志、调试信息

class NotificationRouter:
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.notification_log = []
    
    def _load_config(self, config_path):
        """加载通知配置"""
        default_config = {
            "emergency": {
                "channels": ["feishu", "sms", "call"],
                "immediate": True,
                "sound": True,
                "hours": "00:00-23:59"  # 全天候
            },
            "important": {
                "channels": ["feishu"],
                "immediate": True,
                "sound": False,
                "hours": "08:00-23:00"
            },
            "normal": {
                "channels": ["notion"],
                "immediate": False,
                "sound": False,
                "hours": "09:00-21:00"
            },
            "archive": {
                "channels": ["log"],
                "immediate": False,
                "sound": False,
                "hours": "all"
            },
            "daily_report": {
                "time": "09:00",
                "channel": "feishu"
            },
            "weekly_report": {
                "time": "20:00",
                "day": "sunday",
                "channel": "feishu"
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                return {**default_config, **json.load(f)}
        
        return default_config
    
    def route(self, message, level=NotificationLevel.NORMAL, context=None):
        """路由通知到对应渠道"""
        level_str = level.value
        config = self.config.get(level_str, self.config["normal"])
        
        notification = {
            "timestamp": datetime.now().isoformat(),
            "level": level_str,
            "message": message,
            "context": context or {},
            "channels": config["channels"],
            "sent": False
        }
        
        # 检查时间窗口
        if not self._in_time_window(config.get("hours", "all")):
            notification["queued"] = True
            notification["reason"] = "outside_time_window"
            self._queue_notification(notification)
            return notification
        
        # 发送到各渠道
        for channel in config["channels"]:
            try:
                self._send_to_channel(channel, message, level_str, context)
                notification["sent"] = True
            except Exception as e:
                notification["errors"] = notification.get("errors", [])
                notification["errors"].append({"channel": channel, "error": str(e)})
        
        # 记录
        self.notification_log.append(notification)
        
        return notification
    
    def _in_time_window(self, hours):
        """检查当前是否在时间窗口内"""
        if hours == "all":
            return True
        
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        if "-" in hours:
            start, end = hours.split("-")
            return start <= current_time <= end
        
        return True
    
    def _send_to_channel(self, channel, message, level, context):
        """发送到具体渠道"""
        if channel == "feishu":
            return self._send_feishu(message, level, context)
        elif channel == "notion":
            return self._send_notion(message, level, context)
        elif channel == "log":
            return self._send_log(message, level, context)
        elif channel == "sms":
            return self._send_sms(message, level, context)
        elif channel == "call":
            return self._send_call(message, level, context)
        else:
            raise ValueError(f"Unknown channel: {channel}")
    
    def _send_feishu(self, message, level, context):
        """发送到飞书（待实现Webhook）"""
        # TODO: 实现飞书Webhook调用
        print(f"[飞书] [{level.upper()}] {message}")
        return True
    
    def _send_notion(self, message, level, context):
        """发送到Notion（待实现API）"""
        # TODO: 实现Notion API调用
        print(f"[Notion] [{level.upper()}] {message}")
        return True
    
    def _send_log(self, message, level, context):
        """记录到日志"""
        log_entry = f"{datetime.now().isoformat()} [{level.upper()}] {message}"
        print(f"[LOG] {log_entry}")
        return True
    
    def _send_sms(self, message, level, context):
        """发送短信（待实现）"""
        print(f"[SMS] [{level.upper()}] {message}")
        return True
    
    def _send_call(self, message, level, context):
        """拨打电话（待实现）"""
        print(f"[CALL] [{level.upper()}] {message}")
        return True
    
    def _queue_notification(self, notification):
        """排队通知（时间窗口外）"""
        queue_file = Path("/tmp/notification_queue.json")
        queue = []
        
        if queue_file.exists():
            queue = json.loads(queue_file.read_text())
        
        queue.append(notification)
        queue_file.write_text(json.dumps(queue, indent=2))
    
    def send_daily_report(self, summary):
        """发送日报"""
        message = f"""
📊 **满意解研究所 - 日报**

**日期**: {datetime.now().strftime('%Y-%m-%d')}

**今日完成**:
{summary.get('completed', '无')}

**进行中**:
{summary.get('in_progress', '无')}

**待决策**:
{summary.get('pending', '无')}

**明日计划**:
{summary.get('tomorrow', '无')}
"""
        return self.route(message, NotificationLevel.NORMAL)
    
    def send_weekly_report(self, summary):
        """发送周报"""
        message = f"""
📈 **满意解研究所 - 周报**

**周期**: {summary.get('week_range', '本周')}

**本周成就**:
{summary.get('achievements', '无')}

**项目进展**:
{summary.get('projects', '无')}

**下周重点**:
{summary.get('next_week', '无')}

**系统状态**:
- API使用: {summary.get('api_usage', 'N/A')}
- 任务完成率: {summary.get('task_completion', 'N/A')}
"""
        return self.route(message, NotificationLevel.NORMAL)
    
    def get_stats(self):
        """获取通知统计"""
        stats = defaultdict(lambda: {"count": 0, "sent": 0, "failed": 0})
        
        for n in self.notification_log:
            level = n["level"]
            stats[level]["count"] += 1
            if n.get("sent"):
                stats[level]["sent"] += 1
            if n.get("errors"):
                stats[level]["failed"] += 1
        
        return dict(stats)


# 便捷函数
def notify_emergency(message, context=None):
    """紧急通知"""
    router = NotificationRouter()
    return router.route(message, NotificationLevel.EMERGENCY, context)

def notify_important(message, context=None):
    """重要通知"""
    router = NotificationRouter()
    return router.route(message, NotificationLevel.IMPORTANT, context)

def notify_normal(message, context=None):
    """普通通知"""
    router = NotificationRouter()
    return router.route(message, NotificationLevel.NORMAL, context)

def notify_log(message, context=None):
    """归档日志"""
    router = NotificationRouter()
    return router.route(message, NotificationLevel.ARCHIVE, context)


if __name__ == "__main__":
    # 测试
    router = NotificationRouter()
    
    print("=== 分级通知测试 ===\n")
    
    notify_emergency("系统故障：API连接超时")
    notify_important("任务完成：P0三项开发完成")
    notify_normal("日报生成：今日总结已更新")
    notify_log("调试信息：搜索查询执行成功")
    
    print("\n=== 统计 ===")
    print(json.dumps(router.get_stats(), indent=2))
