#!/usr/bin/env python3
"""
决策安全红线检查脚本
版本: V2.0
功能: 自动检测并拦截危险内容
"""

import re
import sys
import json
from datetime import datetime

# 红线配置
RED_LINES = {
    "RED-001": {
        "name": "no_final_decision",
        "description": "不得给出最终合伙建议",
        "keywords": ["应该选谁", "建议选", "最终建议", "决定选", "推荐选", "我建议"],
        "action": "disclaimer",
        "severity": "high"
    },
    "RED-002": {
        "name": "no_legal_docs", 
        "description": "不得生成法律文件",
        "keywords": ["生成合同", "起草协议", "法律文件", "合伙协议", "股东协议", "公司章程"],
        "action": "block",
        "severity": "critical"
    },
    "RED-003": {
        "name": "no_financial_ops",
        "description": "不得操作资金股权",
        "keywords": ["股权分配", "资金操作", "转账", "投资金额", "融资方案", "估值计算"],
        "action": "convert",
        "severity": "critical"
    },
    "RED-004": {
        "name": "no_privacy_queries",
        "description": "不得查询隐私数据",
        "keywords": ["查背景", "征信", "隐私信息", "个人调查", "背调", "家庭情况"],
        "action": "redirect",
        "severity": "high"
    }
}

LOG_FILE = "/tmp/redline-triggers.log"

def log_trigger(red_id, context):
    """记录红线触发"""
    timestamp = datetime.now().isoformat()
    entry = f"[{timestamp}] RED_LINE_TRIGGERED: {red_id} | Context: {context}\n"
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(f"🚨 红线触发记录: {red_id}")

def check_red_lines(text):
    """检查文本是否触发红线"""
    triggered = []
    
    for red_id, config in RED_LINES.items():
        for keyword in config["keywords"]:
            if keyword in text:
                triggered.append({
                    "id": red_id,
                    "name": config["name"],
                    "description": config["description"],
                    "matched_keyword": keyword,
                    "action": config["action"],
                    "severity": config["severity"]
                })
                log_trigger(red_id, text[:100])
                break
    
    return triggered

def generate_safe_response(triggered, original_text):
    """生成安全响应"""
    responses = []
    
    for t in triggered:
        if t["id"] == "RED-001":
            responses.append("""
⚠️ **决策安全提示**

根据决策安全红线，AI不得给出最终合伙建议。

我可以为您提供：
- 合伙人评估框架
- 多维度分析矩阵
- 决策参考信息

最终决策请结合您的实际情况和专业顾问意见。
""")
        elif t["id"] == "RED-002":
            responses.append("""
⚠️ **法律文件安全提示**

AI生成的法律文件可能存在风险，不建议直接使用。

建议您：
- 咨询专业律师起草正式文件
- 使用我提供的框架与律师沟通
- 参考标准模板但需专业审核
""")
        elif t["id"] == "RED-003":
            responses.append("""
⚠️ **资金操作安全提示**

AI不提供直接的资金/股权操作服务。

我可以帮您：
- 分析股权分配逻辑
- 计算不同方案的影响
- 提供决策参考数据

具体操作请咨询财务/法务专业人士。
""")
        elif t["id"] == "RED-004":
            responses.append("""
⚠️ **隐私数据安全提示**

AI不得查询个人隐私数据。

您可以：
- 使用公开渠道自行查询
- 委托第三方背调机构
- 通过正式渠道获取授权信息
""")
    
    return "\n---\n".join(responses)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: redline-checker.py '<text to check>'")
        sys.exit(1)
    
    text = sys.argv[1]
    
    print("=== 决策安全红线检查 ===")
    print(f"检查文本: {text[:100]}...")
    
    triggered = check_red_lines(text)
    
    if triggered:
        print(f"\n🚨 发现 {len(triggered)} 条红线触发:")
        for t in triggered:
            print(f"  - {t['id']}: {t['description']}")
        
        safe_response = generate_safe_response(triggered, text)
        print("\n=== 安全响应 ===")
        print(safe_response)
        sys.exit(1)
    else:
        print("✅ 未触发任何红线")
        sys.exit(0)

if __name__ == "__main__":
    main()
