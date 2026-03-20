#!/usr/bin/env node
/**
 * 🚀 团队执行文化执行器 - 主执行脚本
 * Execution Culture Enforcer v1.0.0
 * 
 * 核心原则：
 * 1. 激进时间预估
 * 2. 相信极限潜能
 * 3. 完成即启动
 * 
 * 口号：向前赶，永不止步！
 */

const fs = require('fs');
const path = require('path');

class ExecutionCultureEnforcer {
  constructor() {
    this.config = this.loadConfig();
  }

  loadConfig() {
    const configPath = path.join(__dirname, 'skill.json');
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }

  /**
   * 应用激进时间预估
   */
  aggressiveEstimate(originalEstimate) {
    // 原计划的50% = 新截止时间
    const aggressive = originalEstimate * 0.5;
    
    console.log(`
⏱️ 激进时间预估
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
保守预估: ${originalEstimate} 小时
激进目标: ${aggressive} 小时 (50%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);

    return {
      original: originalEstimate,
      aggressive: aggressive,
      rule: '原计划的50%时间 = 新截止时间'
    };
  }

  /**
   * 检查任务沟通话术
   */
  checkCommunication(type, message) {
    const protocols = this.config.communication_protocols;
    const protocol = protocols[type];
    
    if (!protocol) {
      return { valid: false, error: '未知沟通类型' };
    }

    const isWrong = message.toLowerCase().includes('尽量') ||
                   message.toLowerCase().includes('可能') ||
                   message.toLowerCase().includes('等等');

    if (isWrong) {
      return {
        valid: false,
        feedback: '❌ 检测到旧思维模式！',
        suggestion: `应该说: "${protocol.correct}"`,
        correction: this.transformMessage(type, message)
      };
    }

    return {
      valid: true,
      feedback: '✅ 符合执行文化',
      message
    };
  }

  /**
   * 转换旧思维为新思维
   */
  transformMessage(type, oldMessage) {
    const transformations = {
      'receiving_task': {
        pattern: /尽量|可能|试试/,
        replacement: (match) => {
          const times = ['下午3点', '今天下午', '明天上午'];
          return `收到，${times[Math.floor(Math.random() * times.length)]}交付，我会提前。`;
        }
      },
      'progress_report': {
        pattern: /可能|大概|应该/,
        replacement: '已完成X%，预计提前2小时交付，同时我已启动下一项准备工作。'
      },
      'facing_difficulty': {
        pattern: /有难度|延期|做不到/,
        replacement: '遇到挑战，我正在尝试A/B/C三种加速方案，预计仍能按时甚至提前完成。'
      },
      'task_complete': {
        pattern: /完成.*查收|做完了/,
        replacement: '任务完成！已交付+立即启动下一项+预判了3个优化点准备实施。'
      }
    };

    const transform = transformations[type];
    if (transform) {
      if (typeof transform.replacement === 'function') {
        return oldMessage.replace(transform.pattern, transform.replacement);
      }
      return transform.replacement;
    }

    return oldMessage;
  }

  /**
   * 生成激进计划
   */
  generateAggressivePlan(tasks) {
    console.log(`
📋 激进计划表
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
任务类型        保守预估    激进目标    实际交付目标
─────────────────────────────────────────────────`);

    const planning = this.config.aggressive_planning;
    
    tasks.forEach(task => {
      const plan = planning[task.type];
      if (plan) {
        console.log(`${task.name.padEnd(15)} ${plan.conservative.padEnd(10)} ${plan.aggressive.padEnd(10)} ${plan.actual.padEnd(10)}`);
      }
    });

    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
原则: 激进目标 × 120%努力 = 超预期交付
`);
  }

  /**
   * 质量检查
   */
  qualityCheck(deliverable) {
    const baseline = this.config.quality_baseline;
    
    console.log(`
✅ 质量底线检查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【不可妥协】
`);
    
    baseline.non_negotiable.forEach((item, i) => {
      console.log(`  ${i + 1}. ${item} ${deliverable[item] ? '✓' : '✗'}`);
    });

    console.log(`
【可灵活处理】
`);
    
    baseline.flexible.forEach(item => {
      console.log(`  • ${item}`);
    });

    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
原则: V1.0先完成，V2.0再完美
`);
  }

  /**
   * 执行文化自检
   */
  dailySelfCheck() {
    const checklist = this.config.daily_checklist;
    
    console.log(`
📝 每日执行文化自检
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
日期: ${new Date().toLocaleDateString()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);

    checklist.forEach((item, i) => {
      const status = Math.random() > 0.3 ? '✅' : '❌'; // 模拟检查结果
      console.log(`${status} ${i + 1}. ${item}`);
    });

    const score = Math.floor(Math.random() * 30) + 70; // 模拟得分
    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
今日执行分数: ${score}/100
${score >= 80 ? '🚀 优秀！继续保持' : score >= 60 ? '⚡ 良好，还有提升空间' : '💪 需要加强执行'}
`);
  }

  /**
   * 处理困难情况
   */
  handleDifficulty(difficulty) {
    console.log(`
⚡ 困难处理指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
当前困难: ${difficulty}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ 错误做法:
  • "这个有点难，可能要延期"
  • "时间不够，质量可能受影响"
  • "先请示一下能不能延长时间"

✅ 正确做法:
  1️⃣  暂停评估 (1分钟): 真的做不到，还是没想到更快的方法？
  2️⃣  寻找捷径: 能不能并行？能不能简化？能不能借力？
  3️⃣  极限冲刺: 调动全部资源，集中突破
  4️⃣  交付再说: 先完成，后完美

💡 加速策略:
  • 并行处理: 同时做多件事
  • 简化范围: 先交付核心，再迭代
  • 借力: 寻求协助、使用工具
`);
  }

  /**
   * 显示文化宣言
   */
  showManifesto() {
    const principles = this.config.core_principles;
    
    console.log(`
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🚀 满意解研究所 · 团队执行文化 V1.0                   ║
║                                                              ║
║              向前赶，永不止步！                                 ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║  📌 铁律1: ${principles.principle_1.name.padEnd(42)} ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                              ║
║     新思维: "明天上午必须完成"                                 ║
║     新思维: "今天下午就交付"                                   ║
║     新思维: "现在就启动，马上出结果"                            ║
║                                                              ║
║     规则: 原计划的50%时间 = 新截止时间                          ║
║                                                              ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║  📌 铁律2: ${principles.principle_2.name.padEnd(42)} ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                              ║
║     新思维: "一定能完成"                                       ║
║     新思维: "我可以更快"                                       ║
║     新思维: "潜力还没发挥出来"                                  ║
║                                                              ║
║     规则: 不接受"做不到"的预设，用结果证明                       ║
║                                                              ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║  📌 铁律3: ${principles.principle_3.name.padEnd(42)} ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                              ║
║     新思维: "完成这个，立即干下一个！"                           ║
║     新思维: "不等反馈，预判问题提前做"                           ║
║     新思维: "并行推进，永不空转"                                ║
║                                                              ║
║     规则: 任务A完成 → 0延迟 → 立即启动任务B                     ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  💪 这不是压力测试，这是潜能释放。                               ║
║  💪 相信自己，相信团队，向前赶！                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
`);
  }

  /**
   * 显示帮助
   */
  showHelp() {
    console.log(`
🚀 团队执行文化执行器 v1.0.0

用法: node culture-enforcer.js <命令> [参数]

命令:
  manifesto                         显示文化宣言
  estimate <hours>                  激进时间预估
  plan                              生成激进计划表
  check <type> <message>            检查沟通话术
  quality                           质量底线检查
  selfcheck                         每日文化自检
  difficulty <description>          困难处理指南
  help                              显示帮助信息

沟通类型:
  receiving_task    接任务时
  progress_report   汇报进度时
  facing_difficulty 遇到困难时
  task_complete     完成任务时

示例:
  node culture-enforcer.js manifesto
  node culture-enforcer.js estimate 8
  node culture-enforcer.js check receiving_task "我尽量完成"
  node culture-enforcer.js difficulty "技术难题阻塞"
`);
  }
}

// CLI 入口
if (require.main === module) {
  const enforcer = new ExecutionCultureEnforcer();
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    enforcer.showManifesto();
    process.exit(0);
  }
  
  const command = args[0];
  
  switch (command) {
    case 'manifesto':
      enforcer.showManifesto();
      break;
    case 'estimate':
      if (!args[1]) {
        console.log('用法: estimate <hours>');
        process.exit(1);
      }
      enforcer.aggressiveEstimate(parseFloat(args[1]));
      break;
    case 'plan':
      enforcer.generateAggressivePlan([
        { name: '素材搜集', type: 'material_collection' },
        { name: '档案撰写', type: 'profile_writing' },
        { name: '研究任务', type: 'research_task' }
      ]);
      break;
    case 'check':
      if (args.length < 3) {
        console.log('用法: check <type> <message>');
        process.exit(1);
      }
      const result = enforcer.checkCommunication(args[1], args.slice(2).join(' '));
      console.log(result.feedback);
      if (!result.valid) {
        console.log(result.suggestion);
      }
      break;
    case 'quality':
      enforcer.qualityCheck({});
      break;
    case 'selfcheck':
      enforcer.dailySelfCheck();
      break;
    case 'difficulty':
      enforcer.handleDifficulty(args.slice(1).join(' ') || '未指定困难');
      break;
    case 'help':
    default:
      enforcer.showHelp();
  }
}

module.exports = ExecutionCultureEnforcer;
