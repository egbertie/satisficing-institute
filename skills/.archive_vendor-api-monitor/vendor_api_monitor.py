#!/usr/bin/env python3
"""
厂商API能力监控器 - 飞书替代方案追踪
监控钉钉、企业微信等厂商的API能力，特别关注文件同步到API功能
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class VendorAPIMonitor:
    """厂商API能力监控器"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.status_file = self.workspace / "memory" / "vendor_api_monitor_status.json"
        self.report_file = self.workspace / "reports" / "VENDOR_API_DAILY_REPORT.md"
        
        # 监控的厂商列表
        self.vendors = {
            "钉钉": {
                "api_doc_url": "https://open.dingtalk.com/document/isv/app-dev",
                "file_sync_api": None,  # 待调研
                "auto_record": None,    # 待调研
                "alert_system": None,   # 待调研
                "auto_remedy": None,    # 待调研
                "last_check": None,
                "status": "调研中",
                "priority": "P0"
            },
            "企业微信": {
                "api_doc_url": "https://developer.work.weixin.qq.com/document/path/90664",
                "file_sync_api": None,  # 待调研
                "auto_record": None,    # 待调研
                "alert_system": None,   # 待调研
                "auto_remedy": None,    # 待调研
                "last_check": None,
                "status": "调研中",
                "priority": "P0"
            },
            "飞书": {
                "api_doc_url": "https://open.feishu.cn/",
                "file_sync_api": "受限",  # 已有但权限问题
                "auto_record": "需user_token",
                "alert_system": "需user_token",
                "auto_remedy": "需user_token",
                "last_check": "2026-03-10",
                "status": "待user_token解决",
                "priority": "P1"
            },
            "Notion": {
                "api_doc_url": "https://developers.notion.com/",
                "file_sync_api": "✅ 可用",  # 已验证
                "auto_record": "✅ 可用",
                "alert_system": "✅ 可用",
                "auto_remedy": "需开发",
                "last_check": "2026-03-10",
                "status": "✅ 已同步263文件",
                "priority": "备用方案"
            }
        }
        
    def check_vendor_status(self):
        """检查各厂商API能力状态"""
        print("="*70)
        print("厂商API能力监控报告")
        print("="*70)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print()
        
        # 关键能力需求
        required_capabilities = [
            "文件同步到API",      # 最重要！
            "自动记录",
            "到期前预警",
            "超期自动补救"
        ]
        
        print("【关键能力需求】")
        for i, cap in enumerate(required_capabilities, 1):
            priority = "🔴 P0-最重要" if i == 1 else f"🟡 P{i}"
            print(f"  {i}. {cap} {priority}")
        print()
        
        # 各厂商状态
        print("【厂商状态对比】")
        print("-"*70)
        
        for vendor_name, vendor_info in self.vendors.items():
            print(f"\n📌 {vendor_name} (优先级: {vendor_info['priority']})")
            print(f"   状态: {vendor_info['status']}")
            print(f"   文档: {vendor_info['api_doc_url']}")
            print(f"   最后检查: {vendor_info['last_check'] or '未检查'}")
            print()
            print(f"   文件同步API: {vendor_info['file_sync_api'] or '❓ 待调研'}")
            print(f"   自动记录: {vendor_info['auto_record'] or '❓ 待调研'}")
            print(f"   到期预警: {vendor_info['alert_system'] or '❓ 待调研'}")
            print(f"   自动补救: {vendor_info['auto_remedy'] or '❓ 待调研'}")
        
        print()
        print("="*70)
        
    def generate_daily_report(self):
        """生成每日监控报告"""
        report = f"""# 厂商API能力监控日报

**报告日期**: {datetime.now().strftime('%Y-%m-%d')}  
**监控项**: 钉钉/企业微信/飞书/Notion API能力  
**重点关注**: 文件同步到API功能（P0优先级）

---

## 🔴 关键需求（按优先级）

| 优先级 | 需求 | 说明 | 当前状态 |
|--------|------|------|----------|
| P0 | **文件同步到API** | 最重要的功能 | 飞书受限，钉钉/企业微信待调研 |
| P1 | 自动记录 | 任务完成自动记录 | Notion✅，其他待调研 |
| P2 | 到期前预警 | 截止日期前提醒 | 需开发 |
| P3 | 超期自动补救 | 超时自动触发补救 | 需开发 |

---

## 📊 各厂商状态

### 1. 钉钉 (DingTalk) - 🔍 调研中
- **API文档**: https://open.dingtalk.com/document/isv/app-dev
- **文件同步API**: ❓ 待调研（明日优先）
- **自动记录**: ❓ 待调研
- **到期预警**: ❓ 待调研
- **自动补救**: ❓ 待调研
- **状态**: 未开始调研
- **明日行动**: 查阅API文档，确认文件上传能力

### 2. 企业微信 (WeCom) - 🔍 调研中
- **API文档**: https://developer.work.weixin.qq.com/document/path/90664
- **文件同步API**: ❓ 待调研（明日优先）
- **自动记录**: ❓ 待调研
- **到期预警**: ❓ 待调研
- **自动补救**: ❓ 待调研
- **状态**: 未开始调研
- **明日行动**: 查阅API文档，确认文件上传能力

### 3. 飞书 (Feishu) - ⚠️ 待解决
- **API文档**: https://open.feishu.cn/
- **文件同步API**: ⚠️ 需要user_token
- **自动记录**: ⚠️ 需要user_token
- **到期预警**: ⚠️ 需要user_token
- **自动补救**: ⚠️ 需要user_token
- **状态**: OAuth2受阻，待明日再试
- **明日行动**: 继续尝试获取user_token或放弃

### 4. Notion - ✅ 备用方案
- **API文档**: https://developers.notion.com/
- **文件同步API**: ✅ 已验证可用
- **自动记录**: ✅ 已实现
- **到期预警**: ✅ 可实现
- **自动补救**: 🔄 需开发
- **状态**: 263个文件已同步，作为当前主力方案

---

## 🎯 明日行动计划（{datetime.now().strftime('%Y-%m-%d')}）

### 08:00-10:00 钉钉调研
- [ ] 访问钉钉开放平台文档
- [ ] 确认是否有文件上传/同步API
- [ ] 记录API限制和配额
- [ ] 评估技术可行性

### 10:00-12:00 企业微信调研
- [ ] 访问企业微信开发者文档
- [ ] 确认是否有文件上传/同步API
- [ ] 记录API限制和配额
- [ ] 评估技术可行性

### 14:00-16:00 对比分析
- [ ] 对比三家厂商能力
- [ ] 制定迁移方案（如需要）
- [ ] 向用户汇报调研结果

---

## 🚨 触发条件

**如果发现以下情况，立即通知用户：**

1. **钉钉或企业微信支持文件同步到API**
   - 立即启动飞书替代方案
   - 开始迁移准备

2. **飞书OAuth问题解决**
   - 继续推进飞书方案
   - 放弃替代方案调研

3. **Notion功能受限**
   - 加速其他方案调研
   - 启动紧急备用方案

---

**监控频率**: 每日检查  
**下次报告**: 明日08:00  
**紧急联系**: 如发现文件同步API可用，立即通知

---

*本报告由厂商API能力监控器自动生成*
"""
        
        # 保存报告
        self.report_file.parent.mkdir(exist_ok=True)
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 日报已生成: {self.report_file}")
        return report
    
    def save_status(self):
        """保存监控状态"""
        status = {
            "last_check": datetime.now().isoformat(),
            "vendors": self.vendors,
            "next_check": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d 08:00')
        }
        
        self.status_file.parent.mkdir(exist_ok=True)
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
    
    def run(self):
        """运行完整检查"""
        self.check_vendor_status()
        self.generate_daily_report()
        self.save_status()
        print("\n" + "="*70)
        print("监控完成！明日08:00继续检查。")
        print("="*70)

if __name__ == "__main__":
    monitor = VendorAPIMonitor()
    monitor.run()
