#!/usr/bin/env python3
"""
记忆审计机制 - 自动检测和清理过时/重复/敏感信息
每周日自动执行
"""

import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class MemoryAuditor:
    def __init__(self, memory_dir="/root/.openclaw/workspace/memory"):
        self.memory_dir = Path(memory_dir)
        self.audit_report = []
    
    def run_audit(self):
        """执行完整审计"""
        print("🔍 开始记忆审计...")
        
        # 1. 过时信息检测
        stale_entries = self.detect_stale_entries()
        print(f"  📅 发现 {len(stale_entries)} 条过时信息")
        
        # 2. 重复信息检测
        duplicates = self.detect_duplicates()
        print(f"  🔄 发现 {len(duplicates)} 组重复信息")
        
        # 3. 敏感信息检测
        sensitive = self.detect_sensitive()
        print(f"  🔒 发现 {len(sensitive)} 条敏感信息")
        
        # 4. 生成审计报告
        report = self.generate_report(stale_entries, duplicates, sensitive)
        
        return report
    
    def detect_stale_entries(self, days=30):
        """检测过时条目（30天未引用）"""
        stale = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for md_file in self.memory_dir.glob("*.md"):
            content = md_file.read_text()
            
            # 提取日期标记
            dates = re.findall(r'\d{4}-\d{2}-\d{2}', content)
            
            if dates:
                latest_date = max(datetime.strptime(d, "%Y-%m-%d") for d in dates)
                if latest_date < cutoff:
                    stale.append({
                        "file": md_file.name,
                        "last_date": latest_date.strftime("%Y-%m-%d"),
                        "days_ago": (datetime.now() - latest_date).days
                    })
        
        return stale
    
    def detect_duplicates(self, similarity_threshold=0.8):
        """检测重复内容"""
        duplicates = []
        content_hashes = defaultdict(list)
        
        for md_file in self.memory_dir.glob("*.md"):
            content = md_file.read_text()
            
            # 分段哈希
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if len(para) > 50:  # 只检查长段落
                    para_hash = hashlib.md5(para.encode()).hexdigest()[:16]
                    content_hashes[para_hash].append({
                        "file": md_file.name,
                        "content_preview": para[:100] + "..."
                    })
        
        # 找出重复
        for h, entries in content_hashes.items():
            if len(entries) > 1:
                duplicates.append({
                    "hash": h,
                    "count": len(entries),
                    "locations": entries
                })
        
        return duplicates
    
    def detect_sensitive(self):
        """检测敏感信息"""
        sensitive_patterns = [
            (r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', "API Key"),
            (r'password["\']?\s*[:=]\s*["\']?\S+', "Password"),
            (r'secret["\']?\s*[:=]\s*["\']?\S+', "Secret"),
            (r'token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', "Token"),
            (r'\b\d{18}\b', "身份证号"),
            (r'1[3-9]\d{9}', "手机号"),
        ]
        
        sensitive = []
        
        for md_file in self.memory_dir.glob("*.md"):
            content = md_file.read_text()
            
            for pattern, ptype in sensitive_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    sensitive.append({
                        "file": md_file.name,
                        "type": ptype,
                        "count": len(matches),
                        "examples": matches[:3]  # 只显示前3个
                    })
        
        return sensitive
    
    def generate_report(self, stale, duplicates, sensitive):
        """生成审计报告"""
        report_path = self.memory_dir / f"audit_report_{datetime.now().strftime('%Y%m%d')}.md"
        
        report = f"""# 记忆审计报告

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**审计范围**: {self.memory_dir}  
**审计规则**: 过时(30天)/重复/敏感信息

---

## 📅 过时信息 ({len(stale)} 条)

"""
        
        if stale:
            for entry in stale:
                report += f"- **{entry['file']}**: 最后更新 {entry['last_date']} ({entry['days_ago']}天前)\n"
        else:
            report += "✅ 未发现过时信息\n"
        
        report += f"""

---

## 🔄 重复信息 ({len(duplicates)} 组)

"""
        
        if duplicates:
            for dup in duplicates[:10]:  # 只显示前10组
                report += f"\n**重复组 #{dup['hash'][:8]}** ({dup['count']} 处)\n"
                for loc in dup['locations']:
                    report += f"- {loc['file']}: `{loc['content_preview']}`\n"
        else:
            report += "✅ 未发现重复信息\n"
        
        report += f"""

---

## 🔒 敏感信息 ({len(sensitive)} 条)

"""
        
        if sensitive:
            for entry in sensitive:
                report += f"- **{entry['file']}**: 发现 {entry['count']} 处 {entry['type']}\n"
            report += "\n⚠️ **建议**: 敏感信息应移至 .env 文件或加密存储\n"
        else:
            report += "✅ 未发现敏感信息\n"
        
        report += f"""

---

## 🛠️ 建议操作

1. **过时信息**: 审核后决定是否归档或删除
2. **重复信息**: 合并或删除冗余内容
3. **敏感信息**: 立即迁移至安全存储

**下次审计**: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}
"""
        
        report_path.write_text(report)
        print(f"\n✅ 审计报告已保存: {report_path}")
        
        return {
            "stale_count": len(stale),
            "duplicate_count": len(duplicates),
            "sensitive_count": len(sensitive),
            "report_path": str(report_path)
        }
    
    def auto_cleanup(self, dry_run=True):
        """自动清理（默认试运行）"""
        print(f"\n{'[试运行]' if dry_run else '[实际执行]'} 自动清理...")
        
        # 这里可以实现自动清理逻辑
        # 但默认dry_run，需要用户确认后才真正执行
        
        return {"cleaned": 0, "dry_run": dry_run}


if __name__ == "__main__":
    auditor = MemoryAuditor()
    report = auditor.run_audit()
    
    print(f"\n{'='*50}")
    print("审计摘要:")
    print(f"  - 过时信息: {report['stale_count']} 条")
    print(f"  - 重复信息: {report['duplicate_count']} 组")
    print(f"  - 敏感信息: {report['sensitive_count']} 条")
    print(f"\n详细报告: {report['report_path']}")
