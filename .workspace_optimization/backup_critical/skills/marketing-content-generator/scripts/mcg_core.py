#!/usr/bin/env python3
"""
Marketing Content Generator Core - 营销内容生成核心模块
整合: adwords + copywriting + copywriting-zh-pro
功能: 100标题公式、AIDA/PAS/FAB框架、中文文案、跨境营销
"""

import argparse
import json
import sys
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# 100个标题公式库 (来自adwords)
# ═══════════════════════════════════════════════════════════════

HEADLINE_FORMULAS = {
    "digital": {  # 数字型 1-15
        "range": (1, 15),
        "formulas": [
            "[数字]个[方法]让你[好处]",
            "[数字]个[错误]正在毁掉你的[目标]",
            "[数字]分钟学会[技能]",
            "[数字]%的人不知道的[秘密]",
            "每天[数字]分钟，[时间]后[结果]",
            "[数字]步搞定[难题]",
            "只需[数字]元，获得[价值]",
            "前[数字]名[优惠]",
            "[数字]年经验总结的[干货]",
            "[数字]个理由让你选择[产品]",
            "[数字]个案例证明[效果]",
            "超过[数字]人已经[行动]",
            "[数字]天[挑战/变化]",
            "TOP[数字][类别]推荐",
            "[数字]招搞定[难题]"
        ]
    },
    "question": {  # 问题型 16-30
        "range": (16, 30),
        "formulas": [
            "你还在为[痛点]烦恼吗？",
            "为什么[反直觉]？",
            "[目标]，你做对了吗？",
            "怎样在[时间]内[成果]？",
            "你知道[令人惊讶的事实]吗？",
            "[痛点]怎么办？试试这个",
            "想要[好处]？先解决[问题]",
            "为什么别人[成果]而你不能？",
            "[目标]的秘密是什么？",
            "你属于哪种[类型]？",
            "是什么阻止了你[目标]？",
            "[行为]真的有效吗？",
            "如何避免[常见错误]？",
            "[身份]都在用的[方法]是什么？",
            "还在[旧方法]？试试[新方法]"
        ]
    },
    "benefit": {  # 好处型 31-45
        "range": (31, 45),
        "formulas": [
            "让你的[对象][好处]的终极指南",
            "不用[代价]也能[好处]",
            "[产品]：[好处1]+[好处2]+[好处3]",
            "从[现状]到[理想]只需[方法]",
            "[好处]，就是这么简单",
            "终于，一个让[对象][好处]的方法",
            "[好处]的[数字]个秘诀",
            "轻松实现[目标]的方法",
            "再也不用担心[痛点]",
            "让[对象]瞬间[好处]",
            "省[资源]又[好处]的[方案]",
            "[身份]必备的[工具/方法]",
            "一次解决[多个痛点]",
            "[好处]，从这里开始",
            "你值得拥有[好处]"
        ]
    },
    "urgent": {  # 恐惧/紧迫型 46-60
        "range": (46, 60),
        "formulas": [
            "警告：[不行动的后果]",
            "不要再[错误行为]了！",
            "最后[时间]！[优惠]即将结束",
            "[数字]%的人都犯了这个错",
            "你可能正在[不知不觉中的损失]",
            "再不[行动]就晚了",
            "限时[优惠]，错过等[时间]",
            "别让[痛点]毁掉你的[价值]",
            "[紧急情况]？你需要这个",
            "仅剩[数字]个名额",
            "今天不[行动]，明天[后果]",
            "[行业]大变革，你准备好了吗？",
            "[数字]个信号说明你需要[方案]",
            "停！在[行动]之前先看这个",
            "别人已经[行动]了，你呢？"
        ]
    },
    "story": {  # 故事/情感型 61-75
        "range": (61, 75),
        "formulas": [
            "我是如何从[困境]到[成功]的",
            "一个[身份]的[经历]告诉你",
            "他们说不可能，结果...",
            "[时间]前我[困境]，现在[成就]",
            "[客户名]：[产品]改变了我的[方面]",
            "从[数字]到[数字]，他只用了[方法]",
            "那些[成功的人]都知道的[秘密]",
            "一封来自[身份]的信",
            "我犯了[数字]个错误后才发现...",
            "[产品]背后的故事",
            "为什么我放弃[旧方法]选择[新方法]",
            "[数字]年[行业]老兵的真心话",
            "当[情境]时，[产品]救了我",
            "从怀疑到信赖：[客户]的[产品]之旅",
            "[身份]的一天是怎样的"
        ]
    },
    "authority": {  # 权威/社证型 76-90
        "range": (76, 90),
        "formulas": [
            "[权威机构]推荐的[产品]",
            "[数字]位[身份]的共同选择",
            "[行业]专家都在用的[方法]",
            "[权威人物]说：[观点]",
            "荣获[奖项]的[产品]",
            "被[媒体]报道的[产品/方法]",
            "[数字]年行业标准",
            "[知名客户]都在用",
            "好评率[数字]%的[产品]",
            "[排名]第一的[类别]",
            "复购率[数字]%的秘密",
            "[数字]+用户验证有效",
            "[认证/资质]认可的[产品]",
            "[行业]口碑之选",
            "来自[地域]的专业[方案]"
        ]
    },
    "unique": {  # 独特型 91-100
        "range": (91, 100),
        "formulas": [
            "[产品]≠[常见误解]",
            "全网最[特点]的[产品]",
            "只有[条件]才能享受的[服务]",
            "[产品]：重新定义[类别]",
            "一个[特点]的[产品]",
            "你从未见过的[类别]",
            "[对比]：[产品]vs[竞品]",
            "不走寻常路的[方案]",
            "[特点]+[特点]=[产品]",
            "如果[产品]会说话..."
        ]
    }
}

# ═══════════════════════════════════════════════════════════════
# 文案框架模板
# ═══════════════════════════════════════════════════════════════

FRAMEWORKS = {
    "aida": {
        "name": "AIDA框架",
        "description": "注意-兴趣-欲望-行动",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                    AIDA 文案框架                              ║
╚══════════════════════════════════════════════════════════════╝

🎯 ATTENTION (注意)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
使命: 在3秒内抓住眼球
技巧:
  • 震撼数据: "每天有XX人因为___而___"
  • 反常识: "你以为的___其实是错的"
  • 直击痛点: "还在为___烦恼？"

📌 文案: [填写吸睛标题]

📖 INTEREST (兴趣)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
使命: 让读者继续读下去
技巧:
  • 展开痛点: "你是否经历过___？"
  • 讲故事: "[客户名]也曾___"
  • 制造悬念: "解决方案比你想的简单..."

📌 文案: [填写引发兴趣的内容]

💖 DESIRE (欲望)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
使命: 让读者想要你的产品
技巧:
  • ✅ [好处1] 
  • ✅ [好处2]
  • ✅ [好处3]
  • 前后对比: 使用前___ vs 使用后___
  • 客户证言: "[真实评价]"

📌 文案: [填写激发欲望的内容]

🚀 ACTION (行动)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
使命: 促使立即行动
技巧:
  • 紧迫感: "限时/限量/限额"
  • 简化行动: "只需[1步]"
  • 降低门槛: "免费试用/0元体验"

📌 CTA: [填写行动号召]
"""
    },
    "pas": {
        "name": "PAS框架",
        "description": "问题-激化-解决",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                     PAS 文案框架                              ║
╚══════════════════════════════════════════════════════════════╝

😰 PROBLEM (问题)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
清晰描述目标用户面临的核心问题：

📌 问题陈述: [具体、清晰的问题描述]
👤 目标用户: [受影响的人群]
💔 痛点场景: [具体场景化描述]

🔥 AGITATE (激化)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
加深痛感，让用户意识到不解决问题的后果：

📌 后果描述: [如果不解决会怎样]
⏰ 紧迫性: [为什么现在必须解决]
📉 损失量化: [具体的时间/金钱/机会损失]
😟 情感放大: [焦虑、恐惧、挫败感]

💡 SOLUTION (解决方案)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
呈现你的产品/服务作为最佳解决方案：

📌 解决方案: [产品/服务名称]
⚡ 核心机制: [如何解决问题]
🎁 即时收益: [使用后立刻获得的好处]
📈 长期价值: [持续使用的效果]
🛡️ 风险逆转: [退款保证/试用期]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CTA: [立即行动号召]
"""
    },
    "fab": {
        "name": "FAB框架",
        "description": "特性-优势-收益",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                     FAB 文案框架                              ║
╚══════════════════════════════════════════════════════════════╝

FEATURE → ADVANTAGE → BENEFIT
特性 → 优势 → 收益

┌─────────────────────────────────────────────────────────────┐
│ 特性(Feature): 产品是什么/有什么                              │
│ 优势(Advantage): 为什么这个特性重要                           │
│ 收益(Benefit): 用户能获得什么价值                             │
└─────────────────────────────────────────────────────────────┘

示例1:
  特性: 40mm驱动单元
  优势: 比标准耳机大30%的振膜
  收益: 享受录音室级别的音质，每个音符都清晰动人

示例2:
  特性: AI自动化写作
  优势: 无需手动编写，系统自动生成
  收益: 每天节省2小时，把精力投入到更有创造力的工作中

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

请按FAB框架描述您的产品:

特性1: [填写]
  → 优势: [填写]
    → 收益: [填写]

特性2: [填写]
  → 优势: [填写]
    → 收益: [填写]

特性3: [填写]
  → 优势: [填写]
    → 收益: [填写]
"""
    },
    "4p": {
        "name": "4P框架",
        "description": "画面-承诺-证明-推动",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                      4P 文案框架                              ║
╚══════════════════════════════════════════════════════════════╝

🖼️ PICTURE (画面)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
在读者脑海中描绘一个生动的场景：

📌 场景描述: [让读者能够代入的画面]
💭 情感共鸣: [触发特定情感]
👁️ 视觉细节: [具体的感官描述]

🎁 PROMISE (承诺)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
给出明确、有力的承诺：

📌 核心承诺: [具体可量化的结果]
⏱️ 时间框架: [多久能见效]
🎯 适用人群: [谁可以获得这个结果]

📊 PROOF (证明)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
提供证据支撑你的承诺：

📌 数据证明: [具体数字、百分比]
💬 客户证言: [真实用户评价]
🏆 权威背书: [认证、奖项、媒体报道]
📈 案例对比: [使用前后的对比]

🚀 PUSH (推动)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
推动读者立即采取行动：

📌 行动号召: [清晰、有力的CTA]
⏰ 紧迫感: [为什么现在就要行动]
🎁 额外激励: [限时优惠/赠品]
🛡️ 风险消除: [退款保证/无风险承诺]
"""
    },
    "bab": {
        "name": "BAB框架",
        "description": "之前-之后-桥梁",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                     BAB 文案框架                              ║
╚══════════════════════════════════════════════════════════════╝

BEFORE → AFTER → BRIDGE
之前 → 之后 → 桥梁

┌─────────────────────────────────────────────────────────────┐
│ BEFORE (之前): 描述使用产品前的痛苦状态                       │
│ AFTER (之后): 描述使用产品后的理想状态                        │
│ BRIDGE (桥梁): 展示如何从前者到达后者                         │
└─────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

😰 BEFORE (之前)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
描述用户当前的痛苦、困扰或不满：

📌 现状描述: [填写]
😔 具体困扰: [填写]
💔 情感状态: [填写]
📉 造成损失: [填写]

✨ AFTER (之后)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
描绘使用产品后的理想状态：

📌 理想状态: [填写]
😊 具体改善: [填写]
❤️ 情感满足: [填写]
📈 获得收益: [填写]

🌉 BRIDGE (桥梁)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
展示产品如何连接"之前"和"之后"：

📌 产品名称: [填写]
⚙️ 核心机制: [如何起作用]
🎯 关键步骤: [1... 2... 3...]
⏱️ 见效时间: [多久能看到改变]
"""
    }
}

# ═══════════════════════════════════════════════════════════════
# 中文文案框架
# ═══════════════════════════════════════════════════════════════

ZH_FRAMEWORKS = {
    "痛点方案": {
        "name": "痛点-方案-收益",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                  痛点-方案-收益 框架                          ║
╚══════════════════════════════════════════════════════════════╝

😰 痛点: [用户面临的具体问题]
   场景化描述，让用户产生"对对对就是这样"的共鸣

💡 方案: [你的产品/服务如何解决]
   具体机制，避免空泛的形容词

🎁 收益: [用户获得的具体好处]
   可量化、可感知、有时间节点

示例:
  痛点: 每周花10小时做数据报表，加班到深夜
  方案: AI自动化报表工具，一键生成多维度分析
  收益: 每周节省8小时，准时下班，专注高价值工作
"""
    },
    "场景冲突": {
        "name": "场景-冲突-解决",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                  场景-冲突-解决 框架                          ║
╚══════════════════════════════════════════════════════════════╝

🎬 场景: [用户在什么情境下]
   具体的时间、地点、环境描述

⚡ 冲突: [遇到了什么阻碍/矛盾]
   理想与现实的差距，期望与结果的落差

✅ 解决: [如何化解冲突]
   产品作为解决方案的具体作用

示例:
  场景: 周末带孩子去公园，享受亲子时光
  冲突: 工作消息不断弹出，老板在群里@我
  解决: 智能工作助手自动回复紧急情况，让我真正放松陪伴家人
"""
    }
}

# ═══════════════════════════════════════════════════════════════
# 社媒平台模板 (来自copywriting-zh-pro)
# ═══════════════════════════════════════════════════════════════

SOCIAL_TEMPLATES = {
    "xiaohongshu": {
        "name": "小红书",
        "style": "种草文",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                     小红书种草文案                            ║
╚══════════════════════════════════════════════════════════════╝

📌 标题公式 (10选):
1. 被[人群]问爆的[产品]！真的绝了
2. 终于搞懂了[问题]！新手必看
3. 原来[结果]不是靠[常见误区]
4. [人群]一定要知道的[方法]
5. 被问爆的[产品]，一次讲清
6. 这件事做对后，我的[结果]真的不一样了
7. [数字]个[产品]使用心得，不踩坑
8. 用了[时间]，[结果]让我惊喜
9. [产品]真实测评，不吹不黑
10. 救命！这个[产品]真的[效果]

📝 正文结构:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【开头钩子】(2-3行)
[个人体验引入，制造共鸣]

【痛点共鸣】(3-5行)
[描述曾经的困扰，让读者点头]

【解决方案】(主体)
[产品介绍 + 使用体验]
• [卖点1]: [具体描述]
• [卖点2]: [具体描述]
• [卖点3]: [具体描述]

【效果展示】(数据/对比)
[使用前后的变化，真实感]

【购买建议】(可选)
[适合谁/不适合谁]

【CTA引导】
[收藏/评论/私信]

🏷️ 标签建议: #[话题1] #[话题2] #[话题3] #[话题4] #[话题5]
"""
    },
    "wechat": {
        "name": "公众号",
        "style": "深度文章",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                    公众号文章模板                             ║
╚══════════════════════════════════════════════════════════════╝

📌 标题建议 (10选):
1. [数字]个[方法]，让你的[结果]提升[百分比]
2. 为什么[反直觉观点]？深度解析
3. [年份]年[行业]趋势：[关键词]将改变一切
4. 从[现状]到[理想]：[人物]的[时间]转变之路
5. [行业]人必看：[主题]完整指南
6. 别再[错误做法]了！这才是正确方式
7. [热门话题]背后，隐藏着什么机会？
8. 我用[方法]，[时间]内实现了[结果]
9. 深度| [事件]对[行业]的[数字]大影响
10. [名人/公司]都在用的[方法]，到底是什么？

📝 文章结构:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【导语/引言】(150-200字)
• 场景引入或数据引入
• 点明文章价值
• 预告核心内容

【第一部分：问题/背景】(300-400字)
• 现状描述
• 痛点分析
• 常见误区

【第二部分：解决方案】(500-800字)
• 核心方法论
• 步骤详解
• 案例支撑

【第三部分：实操建议】(400-500字)
• 具体行动步骤
• 注意事项
• 资源推荐

【结语】(100-150字)
• 总结要点
• 行动号召
• 互动引导

💬 互动话题: [引导评论的问题]
"""
    },
    "douyin": {
        "name": "抖音",
        "style": "短视频脚本",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                    抖音短视频脚本                             ║
╚══════════════════════════════════════════════════════════════╝

🎬 3秒钩子 (黄金开场):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

请选择一种开场方式:
□ 如果你还在[旧做法]，先别急着[动作]
□ 很多人[问题]，不是因为[表面原因]，而是因为[真正原因]
□ 我用一个最简单的方法，解决了[问题]
□ 今天只讲一件事：怎么把[结果]做好
□ 这不是技巧问题，而是方向问题
□ [数字]秒告诉你[结果]的真相
□ 别再[错误做法]了！真的没用
□ 我发现一个[现象]，[数字]%的人都不知道

📜 完整脚本结构 (60秒):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【0-3秒】钩子
[3秒抓住注意力，停下滑动]

【3-10秒】问题共鸣
[描述用户痛点，引发共鸣]
📢 口播: "你是不是也..."
📝 字幕: [痛点关键词]

【10-25秒】解决方案
[介绍产品/方法]
📢 口播: "直到我发现了..."
📝 字幕: [核心卖点]

【25-45秒】效果证明
[展示结果/对比/数据]
📢 口播: "用了[时间]后..."
📝 字幕: [效果数据]

【45-60秒】CTA
[引导互动/购买]
📢 口播: "想要[结果]的，[行动]"
📝 字幕: [CTA文案]

🎵 BGM建议: [根据内容选择音乐风格]
"""
    },
    "moments": {
        "name": "朋友圈",
        "style": "软性文案",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                     朋友圈文案模板                            ║
╚══════════════════════════════════════════════════════════════╝

📌 文案类型选择:

类型1: 生活感悟型
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[日常观察/感悟]
+
[软性植入]
+
[低压力CTA]

类型2: 干货分享型
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[数字]个[方法]
• [要点1]
• [要点2]
• [要点3]
+
[个人经验]
+
[互动提问]

类型3: 客户见证型
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[客户故事简述]
+
[效果展示]
+
[限时福利]

类型4: 产品上新型
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[上新预告]
+
[核心卖点]
+
[限量/限时]
+
[购买方式]

类型5: 互动话题型
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[提出问题]
+
[分享观点]
+
[引导评论]

💡 CTA建议:
• 想了解的私信我
• 感兴趣的扣1
• 需要的发你资料
• 评论区见
"""
    }
}

# ═══════════════════════════════════════════════════════════════
# 电商文案模板
# ═══════════════════════════════════════════════════════════════

ECOMMERCE_TEMPLATES = {
    "amazon": {
        "name": "亚马逊Listing",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                    亚马逊Listing模板                          ║
╚══════════════════════════════════════════════════════════════╝

📌 标题 (200字符以内):
[品牌] + [核心关键词] + [关键特性] + [规格] + [适用场景]

示例结构:
[Product Name] - [Key Feature 1], [Key Feature 2], [Key Feature 3] - [Size/Color/Quantity] for [Target User]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 五点描述 (Bullet Points):

Bullet 1 - 核心卖点/差异化
[Emphasize the main benefit that sets you apart]

Bullet 2 - 关键功能/规格
[Key features and technical specifications]

Bullet 3 - 使用场景/适用人群
[Who it's for and when to use it]

Bullet 4 - 质量保证/售后
[Quality assurance, warranty, or satisfaction guarantee]

Bullet 5 - 赠品/附加价值
[What's included, bonuses, or additional value]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 产品描述 (HTML格式):

<h3>[Hook - 吸引注意]</h3>
<p>[Opening paragraph that addresses the main pain point]</p>

<h3>[Feature 1 Title]</h3>
<p>[Detailed description of feature and benefit]</p>

<h3>[Feature 2 Title]</h3>
<p>[Detailed description of feature and benefit]</p>

<h3>[Feature 3 Title]</h3>
<p>[Detailed description of feature and benefit]</p>

<h3>[Social Proof]</h3>
<p>[Reviews, ratings, or testimonials summary]</p>

<h3>[Call to Action]</h3>
<p>[Add to Cart button context]</p>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 后端关键词 (Search Terms):
[关键词1, 关键词2, 关键词3...] (250字节以内，无重复，无竞品品牌名)
"""
    },
    "shopify": {
        "name": "独立站产品页",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                   Shopify产品页模板                           ║
╚══════════════════════════════════════════════════════════════╝

🎯 首屏内容:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

产品名: [简洁有力，含核心关键词]
副标题: [一句话价值主张]
价格: [原价/折扣价对比]
评分: ⭐⭐⭐⭐⭐ ([数字] reviews)

CTA: [Add to Cart] [Buy It Now]
信任标识: 🔒 Secure Checkout | 🚚 Free Shipping | ↩️ 30-Day Returns

📸 产品图建议:
1. 主图 - 产品+使用场景
2. 功能图 - 核心卖点展示
3. 细节图 - 材质/做工特写
4. 尺寸图 - 规格参考
5. 场景图 - 生活方式展示
6. 对比图 - 与竞品/旧方案对比

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 产品描述结构:

【Hook - 首段】
[一句话抓住注意 + 核心承诺]

【Story - 品牌故事】(可选)
[为什么创造这个产品]
[创始人故事/品牌使命]

【Problem - 痛点共鸣】
[描述用户面临的问题]
[放大痛感]

【Solution - 解决方案】
[产品如何解决]
[核心机制]

【Features - 功能特性】
✓ [Feature 1]: [Benefit 1]
✓ [Feature 2]: [Benefit 2]
✓ [Feature 3]: [Benefit 3]
✓ [Feature 4]: [Benefit 4]
✓ [Feature 5]: [Benefit 5]

【Proof - 社会证明】
📊 [数据统计]
💬 [客户证言]
🏆 [认证/奖项]

【FAQ - 常见问题】
Q: [问题1]?
A: [答案1]

Q: [问题2]?
A: [答案2]

Q: [问题3]?
A: [答案3]

【Guarantee - 风险逆转】
🛡️ [退款保证]
📞 [客服支持]
"""
    },
    "detail": {
        "name": "中文详情页",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                    中文电商详情页模板                         ║
╚══════════════════════════════════════════════════════════════╝

📱 首屏 (黄金3秒):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
核心卖点一句话 + 主图视频/GIF

【核心卖点】
[一句话说出最重要的价值]

【信任标识】
[销量] [好评] [认证] [媒体报道]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 卖点展开区:

卖点1: [标题]
[详细描述] + [场景图]

卖点2: [标题]
[详细描述] + [场景图]

卖点3: [标题]
[详细描述] + [场景图]

卖点4: [标题]
[详细描述] + [场景图]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 适合人群:
✅ 适合: [人群1] / [人群2] / [人群3]
❌ 不适合: [人群描述]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 产品规格:
[参数表格]
• 尺寸:
• 重量:
• 材质:
• 颜色:
• 包装清单:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛡️ 服务保障:
[退换政策]
[质保说明]
[客服承诺]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ 常见问题 (FAQ):
Q1: [问题]? → A: [答案]
Q2: [问题]? → A: [答案]
Q3: [问题]? → A: [答案]
Q4: [问题]? → A: [答案]
Q5: [问题]? → A: [答案]
"""
    }
}

# ═══════════════════════════════════════════════════════════════
# 跨境营销文案 (Cross-Border)
# ═══════════════════════════════════════════════════════════════

CROSS_BORDER_TEMPLATES = {
    "meta_ads": {
        "name": "Meta广告文案",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                    Meta Ads (FB/IG) 文案                      ║
╚══════════════════════════════════════════════════════════════╝

📱 信息流广告结构:

【Primary Text】(主文案 - 125字符显示，可展开)
[Hook] + [Problem/Story] + [Solution] + [CTA]

【Headline】(标题 - 40字符)
[Benefit-focused headline]

【Description】(描述 - 30字符)
[Social proof or urgency]

【CTA Button】(按钮)
Shop Now / Learn More / Sign Up / Get Offer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 文案变体:

变体A - 痛点型:
Primary: Tired of [pain point]? You're not alone. [Number] people have switched to [product] and [result]. Try it risk-free for [days]. 👉 [CTA]
Headline: [Solve Pain Point] in [Timeframe]

变体B - 好奇型:
Primary: This [product category] is going viral for a reason... [Number] ⭐ reviews can't be wrong. See what everyone's talking about. 👇
Headline: The [Product] Everyone's Talking About

变体C - 权威型:
Primary: Trusted by [number]+ [target audience]. [Product] helps you [main benefit] without [common objection]. Rated [X]/5 by [publication].
Headline: Join [Number] Happy Customers

变体D - 紧迫型:
Primary: ⚠️ Only [number] left at this price! [Product] is flying off the shelves. Get [discount]% off + free shipping when you order today.
Headline: ⚡ Flash Sale: [Discount]% Off
"""
    },
    "google_ads": {
        "name": "Google广告文案",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                    Google Ads 文案模板                        ║
╚══════════════════════════════════════════════════════════════╝

🔍 搜索广告 (Responsive Search Ads):

【标题选项】(30字符以内，最多15个)
1. [关键词] - [Benefit]
2. [品牌] [Product]
3. [Benefit] Guaranteed
4. Save [Number]% on [Product]
5. [Product] | Free Shipping
6. Top-Rated [Category]
7. [Number]+ Reviews
8. Shop [Product] Today
9. [Urgency Word] - [Offer]
10. [Benefit] in [Timeframe]
11. [Brand] Official Store
12. [Product] Sale - [Date]
13. Best [Category] [Year]
14. [Discount]% Off Today
15. [Product] | [USP]

【描述选项】(90字符以内，最多4个)
1. [Product] with [key feature]. [Benefit] for [target audience]. [Trust signal]. Shop now!
2. Discover why [number]+ customers choose [brand]. [Main benefit]. Free returns.
3. Limited time: [offer details]. [Product] starting at [price]. Order today!
4. [Brand]'s [product] helps you [primary benefit]. [Secondary benefit]. [CTA]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📢 展示广告/发现广告:

【标题】(短标题40字符，长标题90字符)
短: [Product] - [Benefit]
长: [Product]: [Benefit] for [Target Audience] | [Brand]

【描述】(90字符)
[Product] helps [target audience] achieve [desired outcome] with [key feature]. [Trust signal + CTA]

【Business Name】(25字符)
[品牌名]
"""
    },
    "tiktok_ads": {
        "name": "TikTok广告文案",
        "template": """
╔══════════════════════════════════════════════════════════════╗
║                    TikTok Ads 文案模板                        ║
╚══════════════════════════════════════════════════════════════╝

🎵 TikTok信息流广告:

【视频脚本结构】(15-60秒)

0-3秒: HOOK (停下滑动)
• "POV: You finally found [solution]"
• "Wait for it... [result]"
• "If you [action], you need this"
• "Day [number] of using [product]"
• "Tell me you [problem] without telling me"

3-10秒: PROBLEM (建立共鸣)
• 展示使用前的状态
• 描述遇到的困扰
• 用表情/动作强化

10-25秒: SOLUTION (产品展示)
• 开箱/使用过程
• 核心功能展示
• 效果对比

25-45秒: RESULT (效果证明)
• 使用后的状态
• 数据/对比展示
• 满意反应

45-60秒: CTA (行动号召)
• "Link in bio"
• "Get yours now"
• "Limited stock"
• "Shop before it sells out"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 文案文本:

Caption格式:
[Hook emoji] [Short hook text]
[Problem/Solution in 1-2 lines]
[Benefit statement]

[CTA] 👆
[Hashtags: #product #category #trending]

文案变体:
1. "This is your sign to buy [product] ✨ #musthave #tiktokmademebuyit"
2. "The way this [product] changed my [aspect]... 🤯 Link in bio!"
3. "Stop scrolling if you [problem] 👀 Solution below ⬇️"
4. "I tested [product] for [time] and here are my honest thoughts..."
"""
    }
}

# ═══════════════════════════════════════════════════════════════
# 核心功能函数
# ═══════════════════════════════════════════════════════════════

def show_headlines(headline_type="all", count=None):
    """显示标题公式"""
    if headline_type == "all":
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              🎯 100个营销标题公式库                          ║")
        print("╚══════════════════════════════════════════════════════════════╝\n")
        for cat, data in HEADLINE_FORMULAS.items():
            r = data["range"]
            print(f"\n【{data['range'][0]}-{data['range'][1]}】{cat.upper()} ({len(data['formulas'])}个)")
            print("━" * 50)
            for i, f in enumerate(data["formulas"], 1):
                num = r[0] + i - 1
                print(f"  {num:3d}. {f}")
    else:
        if headline_type in HEADLINE_FORMULAS:
            data = HEADLINE_FORMULAS[headline_type]
            r = data["range"]
            print(f"\n【{r[0]}-{r[1]}】{headline_type.upper()} 标题公式\n")
            formulas = data["formulas"][:count] if count else data["formulas"]
            for i, f in enumerate(formulas, 1):
                num = r[0] + i - 1
                print(f"  {num:3d}. {f}")
        else:
            print(f"❌ 未知的标题类型: {headline_type}")
            print(f"可用类型: {', '.join(HEADLINE_FORMULAS.keys())}")

def show_framework(framework_type, **kwargs):
    """显示文案框架"""
    if framework_type in FRAMEWORKS:
        print(FRAMEWORKS[framework_type]["template"])
    elif framework_type in ZH_FRAMEWORKS:
        print(ZH_FRAMEWORKS[framework_type]["template"])
    else:
        print(f"❌ 未知的框架类型: {framework_type}")
        print(f"可用框架: {', '.join(list(FRAMEWORKS.keys()) + list(ZH_FRAMEWORKS.keys()))}")

def show_social_template(platform):
    """显示社媒模板"""
    if platform in SOCIAL_TEMPLATES:
        print(SOCIAL_TEMPLATES[platform]["template"])
    else:
        print(f"❌ 未知平台: {platform}")
        print(f"可用平台: {', '.join(SOCIAL_TEMPLATES.keys())}")

def show_ecommerce_template(platform):
    """显示电商模板"""
    if platform in ECOMMERCE_TEMPLATES:
        print(ECOMMERCE_TEMPLATES[platform]["template"])
    else:
        print(f"❌ 未知平台: {platform}")
        print(f"可用平台: {', '.join(ECOMMERCE_TEMPLATES.keys())}")

def generate_ad_copy(product, platform="universal", variants=3, **kwargs):
    """生成广告文案"""
    print(f"\n╔══════════════════════════════════════════════════════════════╗")
    print(f"║              🎯 广告文案生成                                  ║")
    print(f"╚══════════════════════════════════════════════════════════════╝")
    print(f"\n产品: {product}")
    print(f"平台: {platform}")
    print(f"变体数: {variants}\n")
    print("━" * 60)
    
    angles = ["benefit", "pain", "curiosity", "authority"]
    
    for i in range(min(variants, len(angles))):
        angle = angles[i % len(angles)]
        print(f"\n【变体 {i+1}】角度: {angle.upper()}")
        print("-" * 40)
        
        if angle == "benefit":
            print(f"标题: 让你的{product}效率提升300%的秘诀")
            print(f"描述: 数千用户验证，{product}帮你节省时间、降低成本、提升效果。立即免费试用！")
        elif angle == "pain":
            print(f"标题: 还在为{product}相关的问题烦恼？")
            print(f"描述: 每天都有人因为忽视这个问题而损失机会。{product}帮你彻底解决，不留后患。")
        elif angle == "curiosity":
            print(f"标题: 这个{product}技巧，90%的人都不知道")
            print(f"描述: 用了这个方法的用户，平均效果提升了5倍。点击查看详情...")
        elif angle == "authority":
            print(f"标题: 超过10,000家企业信赖的{product}解决方案")
            print(f"描述: 行业领导者都在用。{product}，专业品质保证。限时优惠中！")
        
        print(f"CTA: 立即了解 / 免费试用 / 查看详情")

def generate_landing_page(product, style="full", **kwargs):
    """生成落地页文案"""
    print(f"\n╔══════════════════════════════════════════════════════════════╗")
    print(f"║              🖥️ 落地页文案生成                                ║")
    print(f"╚══════════════════════════════════════════════════════════════╝")
    print(f"\n产品: {product}")
    print(f"风格: {style}\n")
    print("━" * 60)
    
    sections = ["Hero", "Problem", "Solution", "Features", "Social Proof", "CTA"]
    
    for section in sections:
        print(f"\n【{section} Section】")
        print("-" * 40)
        if section == "Hero":
            print(f"主标题: {product}——让效率提升10倍的秘密武器")
            print(f"副标题: 超过50,000用户信赖的选择")
            print(f"CTA: 立即免费试用")
        elif section == "Problem":
            print(f"痛点标题: 还在为这些问题烦恼吗？")
            print(f"• 花费大量时间在重复工作上")
            print(f"• 效果不理想，却找不到原因")
            print(f"• 团队协作效率低下")
        elif section == "Solution":
            print(f"方案标题: {product}，为你解决所有问题")
            print(f"核心优势:")
            print(f"• AI智能自动化")
            print(f"• 数据驱动决策")
            print(f"• 团队协作无缝衔接")
        elif section == "Features":
            print(f"功能亮点:")
            print(f"✓ 功能1: 描述与好处")
            print(f"✓ 功能2: 描述与好处")
            print(f"✓ 功能3: 描述与好处")
        elif section == "Social Proof":
            print(f"用户评价:")
            print(f"⭐⭐⭐⭐⭐ \"改变了我的工作方式\" - 用户A")
            print(f"⭐⭐⭐⭐⭐ \"效果超出预期\" - 用户B")
        elif section == "CTA":
            print(f"最终CTA: 准备好提升效率了吗？")
            print(f"按钮: 立即开始免费试用")
            print(f"风险逆转: 30天无理由退款保证")

def show_cross_border_template(channel):
    """显示跨境营销模板"""
    if channel in CROSS_BORDER_TEMPLATES:
        print(CROSS_BORDER_TEMPLATES[channel]["template"])
    else:
        print(f"❌ 未知渠道: {channel}")
        print(f"可用渠道: {', '.join(CROSS_BORDER_TEMPLATES.keys())}")

# ═══════════════════════════════════════════════════════════════
# 主命令处理
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Marketing Content Generator')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # headline命令
    headline_parser = subparsers.add_parser('headline', help='标题公式')
    headline_parser.add_argument('--type', default='all', help='标题类型')
    headline_parser.add_argument('--count', type=int, help='显示数量')
    
    # framework命令
    framework_parser = subparsers.add_parser('framework', help='文案框架')
    framework_parser.add_argument('framework_type', help='框架类型')
    
    # ad命令
    ad_parser = subparsers.add_parser('ad', help='广告文案')
    ad_parser.add_argument('--product', required=True, help='产品名称')
    ad_parser.add_argument('--platform', default='universal', help='平台')
    ad_parser.add_argument('--variants', type=int, default=3, help='变体数量')
    
    # landing命令
    landing_parser = subparsers.add_parser('landing', help='落地页文案')
    landing_parser.add_argument('--product', required=True, help='产品名称')
    landing_parser.add_argument('--style', default='full', help='风格')
    
    # social命令
    social_parser = subparsers.add_parser('social', help='社媒内容')
    social_parser.add_argument('platform', help='平台')
    
    # ecommerce命令
    ecommerce_parser = subparsers.add_parser('ecommerce', help='电商文案')
    ecommerce_parser.add_argument('platform', help='平台')
    
    # crossborder命令
    cb_parser = subparsers.add_parser('crossborder', help='跨境营销')
    cb_parser.add_argument('channel', help='渠道')
    
    args = parser.parse_args()
    
    if args.command == 'headline':
        show_headlines(args.type, args.count)
    elif args.command == 'framework':
        show_framework(args.framework_type)
    elif args.command == 'ad':
        generate_ad_copy(args.product, args.platform, args.variants)
    elif args.command == 'landing':
        generate_landing_page(args.product, args.style)
    elif args.command == 'social':
        show_social_template(args.platform)
    elif args.command == 'ecommerce':
        show_ecommerce_template(args.platform)
    elif args.command == 'crossborder':
        show_cross_border_template(args.channel)
    else:
        parser.print_help()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
