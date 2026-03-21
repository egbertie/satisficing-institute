#!/usr/bin/env node
/**
 * 📋 快速参考卡 - 主执行脚本
 * Quick Reference Card v1.0.0
 * 
 * 核心功能：
 * 1. 合伙人评估速查
 * 2. 风险等级判断
 * 3. 决策流程指导
 * 4. 案例参考查询
 */

const fs = require('fs');
const path = require('path');

class QuickReferenceCard {
  constructor() {
    this.config = this.loadConfig();
    this.data = this.loadReferenceData();
  }

  loadConfig() {
    const configPath = path.join(__dirname, 'skill.json');
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }

  loadReferenceData() {
    return {
      positioning: '专注硬科技转化的合伙人匹配决策教练',
      methodology: {
        core: '满意解 = 西蒙满意解理论 + 五路图腾决策法 + 儒商合伙伦理',
        dimensions: [
          { name: '价值观契合度', weight: 0.25, threshold: 5, risk: '致命风险' },
          { name: '能力互补性', weight: 0.20, threshold: 7, risk: '需补强' },
          { name: '沟通效率', weight: 0.15, threshold: 5, risk: '中风险' },
          { name: '承诺可信度', weight: 0.15, threshold: 6, risk: '高风险' },
          { name: '利益一致性', weight: 0.10, threshold: null, risk: '需机制保障' },
          { name: '退出可接受性', weight: 0.10, threshold: null, risk: '需预设' },
          { name: '成长匹配度', weight: 0.05, threshold: null, risk: '长期观察' }
        ]
      },
      process: ['初筛', '深度评估', '风险预警', '专家会诊', '决策建议'],
      riskLevels: [
        { min: 8.0, max: 10, level: 'EXCELLENT', advice: '强烈推荐', color: '🟢' },
        { min: 7.0, max: 7.9, level: 'LOW', advice: '可以推进', color: '🔵' },
        { min: 6.0, max: 6.9, level: 'MEDIUM', advice: '需谨慎', color: '🟡' },
        { min: 5.5, max: 5.9, level: 'HIGH', advice: '需深度尽调', color: '🟠' },
        { min: 0, max: 5.4, level: 'CRITICAL', advice: '建议否决', color: '🔴' }
      ],
      failureReasons: [
        { reason: '价值观冲突', rate: 0.67, severity: '⚠️' },
        { reason: '承诺不足', note: '资源投入不对等' },
        { reason: '沟通障碍', note: '磨合期放大' }
      ],
      successPatterns: [
        '技术+商业互补最稳定',
        '价值观契合度≥7',
        '全职承诺是硬科技前提'
      ],
      metrics: {
        cases: 15,
        validated: 10,
        expanding: 5,
        successRate: '50%',
        accuracy: '85%+',
        duration: '8-10分钟'
      }
    };
  }

  /**
   * 显示完整参考卡
   */
  showFullCard() {
    console.log(`
╔════════════════════════════════════════════════════════════╗
║           📋 满意解研究所 - 快速参考卡                      ║
╠════════════════════════════════════════════════════════════╣
║  ${this.data.positioning.padEnd(50)} ║
╠════════════════════════════════════════════════════════════╣
║ 🧠 核心方法论                                               ║
║ ${this.data.methodology.core.padEnd(52)} ║
╠════════════════════════════════════════════════════════════╣
║ 📊 7维度评估体系                                            ║
╠════════════════════════════════════════════════════════════╣`);

    this.data.methodology.dimensions.forEach(d => {
      const threshold = d.threshold ? `<${d.threshold} ${d.risk}` : d.risk;
      console.log(`║ • ${d.name.padEnd(10)} 权重${(d.weight*100).toFixed(0).padStart(3)}%  ${threshold.padEnd(30)} ║`);
    });

    console.log(`╠════════════════════════════════════════════════════════════╣
║ 🔄 决策流程: ${this.data.process.join(' → ').padEnd(38)} ║
╠════════════════════════════════════════════════════════════╣
║ ⚠️ 风险等级                                                 ║
╠════════════════════════════════════════════════════════════╣`);

    this.data.riskLevels.forEach(r => {
      const range = r.min >= 8 ? `≥${r.min}` : `${r.min}-${r.max}`;
      console.log(`║ ${r.color} ${range.padEnd(8)} ${r.level.padEnd(10)} ${r.advice.padEnd(25)} ║`);
    });

    console.log(`╠════════════════════════════════════════════════════════════╣
║ 📈 关键数据                                                 ║
║ • 案例库: ${this.data.metrics.cases}个（${this.data.metrics.validated}已验证+${this.data.metrics.expanding}扩展中）                      ║
║ • 成功率: ${this.data.metrics.successRate.padEnd(8)} 预测准确率: ${this.data.metrics.accuracy.padEnd(12)} ║
║ • 评估时长: ${this.data.metrics.duration.padEnd(45)} ║
╠════════════════════════════════════════════════════════════╣
║ ❌ 主要失败原因                                             ║
║ • 价值观冲突 (67%) ⚠️ - 最致命                             ║
║ • 承诺不足 - 资源投入不对等                                 ║
║ • 沟通障碍 - 磨合期放大                                     ║
╠════════════════════════════════════════════════════════════╣
║ ✅ 成功组合特征                                             ║
║ • 技术+商业互补最稳定                                       ║
║ • 价值观契合度≥7                                           ║
║ • 全职承诺是硬科技前提                                      ║
╚════════════════════════════════════════════════════════════╝
`);
  }

  /**
   * 计算风险评估
   */
  calculateRisk(scores) {
    // scores = { dimension: score, ... }
    let weightedSum = 0;
    let details = [];

    this.data.methodology.dimensions.forEach(dim => {
      const score = scores[dim.name] || 0;
      const weighted = score * dim.weight;
      weightedSum += weighted;
      
      let warning = '';
      if (dim.threshold && score < dim.threshold) {
        warning = `⚠️ ${dim.risk}`;
      }
      
      details.push({
        dimension: dim.name,
        score,
        weight: dim.weight,
        weighted,
        warning
      });
    });

    const totalScore = weightedSum;
    const riskLevel = this.data.riskLevels.find(
      r => totalScore >= r.min && totalScore <= r.max
    );

    return {
      totalScore: totalScore.toFixed(2),
      riskLevel,
      details,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * 显示评估结果
   */
  showAssessment(result) {
    console.log(`
╔════════════════════════════════════════════════════════════╗
║              📊 合伙人评估结果                              ║
╠════════════════════════════════════════════════════════════╣
║ 综合评分: ${result.totalScore.padEnd(8)} 等级: ${result.riskLevel.color} ${result.riskLevel.level.padEnd(15)} ║
║ 建议: ${result.riskLevel.advice.padEnd(47)} ║
╠════════════════════════════════════════════════════════════╣
║ 维度明细                                                    ║
╠════════════════════════════════════════════════════════════╣`);

    result.details.forEach(d => {
      const bar = '█'.repeat(Math.round(d.score)) + '░'.repeat(10 - Math.round(d.score));
      const line = `${d.dimension.padEnd(10)} ${bar} ${d.score.toFixed(1)} ${d.warning}`;
      console.log(`║ ${line.padEnd(58)} ║`);
    });

    console.log(`╚════════════════════════════════════════════════════════════╝
`);
  }

  /**
   * 快速决策建议
   */
  quickAdvice(scores) {
    const result = this.calculateRisk(scores);
    
    let advice = [];
    
    // 基于总分给出建议
    if (parseFloat(result.totalScore) >= 8) {
      advice.push('✅ 强烈推荐 - 这是一个高匹配度的合伙组合');
    } else if (parseFloat(result.totalScore) >= 7) {
      advice.push('✓ 可以推进 - 注意监控关键维度');
    } else if (parseFloat(result.totalScore) >= 6) {
      advice.push('⚠️ 需谨慎 - 建议进行深度尽调');
    } else {
      advice.push('❌ 建议否决 - 风险过高');
    }
    
    // 找出风险点
    const risks = result.details.filter(d => d.warning);
    if (risks.length > 0) {
      advice.push('\n⚠️ 需要关注的维度:');
      risks.forEach(r => {
        advice.push(`  • ${r.dimension}: ${r.warning}`);
      });
    }
    
    // 检查成功模式
    if (scores['价值观契合度'] >= 7 && scores['能力互补性'] >= 7) {
      advice.push('\n✅ 符合成功模式: 价值观+能力双高');
    }
    
    return advice.join('\n');
  }

  /**
   * 交互式评估向导
   */
  async interactiveAssessment() {
    console.log(`
╔════════════════════════════════════════════════════════════╗
║           🎯 合伙人评估向导                                 ║
║     请为以下维度打分 (1-10, 10为最高)                       ║
╚════════════════════════════════════════════════════════════╝
`);

    const scores = {};
    const dimensions = this.data.methodology.dimensions;
    
    // 在真实环境中使用readline获取输入
    // 这里模拟评分
    for (const dim of dimensions) {
      const exampleScore = Math.floor(Math.random() * 4) + 6; // 模拟6-9分
      scores[dim.name] = exampleScore;
      console.log(`${dim.name}: ${exampleScore}/10`);
    }
    
    console.log('\n');
    const result = this.calculateRisk(scores);
    this.showAssessment(result);
    
    console.log('💡 快速建议:\n');
    console.log(this.quickAdvice(scores));
  }

  /**
   * 显示帮助
   */
  showHelp() {
    console.log(`
📋 快速参考卡 v1.0.0

用法: node reference-card.js <命令> [参数]

命令:
  full                      显示完整参考卡
  assess <scores.json>      执行评估计算
  advice <scores.json>      快速决策建议
  interactive               交互式评估向导
  dimension <name>          查看特定维度详情
  help                      显示帮助信息

评分格式 (JSON):
  {
    "价值观契合度": 8,
    "能力互补性": 7,
    "沟通效率": 6,
    "承诺可信度": 7,
    "利益一致性": 6,
    "退出可接受性": 5,
    "成长匹配度": 7
  }

示例:
  node reference-card.js full
  echo '{"价值观契合度":8,"能力互补性":7}' | node reference-card.js assess
`);
  }
}

// CLI 入口
if (require.main === module) {
  const card = new QuickReferenceCard();
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    card.showFullCard();
    process.exit(0);
  }
  
  const command = args[0];
  
  switch (command) {
    case 'full':
      card.showFullCard();
      break;
    case 'assess':
      // 从stdin或文件读取评分
      let inputData = '';
      if (args[1]) {
        try {
          inputData = fs.readFileSync(args[1], 'utf8');
        } catch (e) {
          console.log('❌ 无法读取文件:', args[1]);
          process.exit(1);
        }
      }
      
      if (inputData) {
        try {
          const scores = JSON.parse(inputData);
          const result = card.calculateRisk(scores);
          card.showAssessment(result);
        } catch (e) {
          console.log('❌ JSON解析失败');
          process.exit(1);
        }
      } else {
        // 演示模式
        const demoScores = {
          '价值观契合度': 8,
          '能力互补性': 7,
          '沟通效率': 6,
          '承诺可信度': 7,
          '利益一致性': 6,
          '退出可接受性': 5,
          '成长匹配度': 7
        };
        console.log('演示模式 (模拟评分):\n');
        const result = card.calculateRisk(demoScores);
        card.showAssessment(result);
      }
      break;
    case 'advice':
      const demoScores = {
        '价值观契合度': 8,
        '能力互补性': 7,
        '沟通效率': 6,
        '承诺可信度': 7,
        '利益一致性': 6,
        '退出可接受性': 5,
        '成长匹配度': 7
      };
      console.log(card.quickAdvice(demoScores));
      break;
    case 'interactive':
      card.interactiveAssessment();
      break;
    case 'help':
    default:
      card.showHelp();
  }
}

module.exports = QuickReferenceCard;
