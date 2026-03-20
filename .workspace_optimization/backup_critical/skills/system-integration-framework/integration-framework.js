#!/usr/bin/env node
/**
 * 🏗️ 完整体系整合框架 - 主执行脚本
 * System Integration Framework v1.0.0
 * 
 * 核心功能：
 * 1. 体系架构展示
 * 2. 资产管理追踪
 * 3. KPI监控
 * 4. 检查清单执行
 * 5. 案例洞察分析
 */

const fs = require('fs');
const path = require('path');

class SystemIntegrationFramework {
  constructor() {
    this.config = this.loadConfig();
  }

  loadConfig() {
    const configPath = path.join(__dirname, 'skill.json');
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }

  /**
   * 显示体系架构
   */
  showArchitecture() {
    const arch = this.config.architecture;
    
    console.log(`
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🏗️ 满意解研究所 - 合伙人匹配决策体系                    ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │  📊 ${arch.output_layer.name.padEnd(46)} │  ║
║  │     • ${arch.output_layer.components.join('\n║  │     • ').padEnd(54)}║  ║
║  └───────────────────────┬────────────────────────────────┘  ║
║                          │                                    ║
║  ┌───────────────────────▼────────────────────────────────┐  ║
║  │  ⚙️  ${arch.collaboration_layer.name.padEnd(46)} │  ║
║  │     【P0】${arch.collaboration_layer.p0_components.join(' · ').padEnd(40)}║  ║
║  │     【P1】${arch.collaboration_layer.p1_components.join(' · ').padEnd(40)}║  ║
║  └───────────────────────┬────────────────────────────────┘  ║
║                          │                                    ║
║  ┌───────────────────────▼────────────────────────────────┐  ║
║  │  🚀  ${arch.product_layer.name.padEnd(46)} │  ║
║  │     • ${arch.product_layer.components.join('\n║  │     • ').padEnd(54)}║  ║
║  └───────────────────────┬────────────────────────────────┘  ║
║                          │                                    ║
║  ┌───────────────────────▼────────────────────────────────┐  ║
║  │  🧠  ${arch.methodology_layer.name.padEnd(46)} │  ║
║  │     理论: ${arch.methodology_layer.theories.join(' · ').padEnd(39)}║  ║
║  │     模型: ${arch.methodology_layer.models.join(' · ').padEnd(39)}║  ║
║  └───────────────────────┬────────────────────────────────┘  ║
║                          │                                    ║
║  ┌───────────────────────▼────────────────────────────────┐  ║
║  │  📚  ${arch.data_layer.name.padEnd(46)} │  ║
║  │     • ${arch.data_layer.components.join('\n║  │     • ').padEnd(54)}║  ║
║  │       ✅ ${arch.data_layer.breakdown.success}个成功  ❌ ${arch.data_layer.breakdown.failure}个失败  🔄 ${arch.data_layer.breakdown.ongoing}个进行中  │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
`);
  }

  /**
   * 显示资产清单
   */
  showAssets() {
    const assets = this.config.assets;
    
    console.log(`
📦 核心资产清单
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 已完成
`);
    assets.completed.forEach((item, i) => {
      console.log(`  ${i + 1}. ✓ ${item}`);
    });

    console.log(`
🔄 进行中
`);
    assets.in_progress.forEach((item, i) => {
      console.log(`  ${i + 1}. ⏳ ${item}`);
    });

    console.log(`
⏳ 待启动
`);
    assets.pending.forEach((item, i) => {
      console.log(`  ${i + 1}. ⏸ ${item}`);
    });

    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
  }

  /**
   * 显示KPI仪表板
   */
  showKPIs() {
    const kpis = this.config.kpis;
    
    console.log(`
📊 关键指标仪表板
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

指标                    目标        当前        达成率
───────────────────────────────────────────────────
`);

    Object.entries(kpis).forEach(([key, data]) => {
      const name = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      const rate = data.rate.padStart(6);
      const bar = this.renderProgressBar(parseInt(data.rate), 20);
      console.log(`${name.padEnd(22)} ${data.target.toString().padEnd(11)} ${data.current.toString().padEnd(11)} ${rate} ${bar}`);
    });

    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
  }

  /**
   * 渲染进度条
   */
  renderProgressBar(percentage, width = 20) {
    const filled = Math.round((percentage / 100) * width);
    const empty = width - filled;
    return '[' + '█'.repeat(filled) + '░'.repeat(empty) + ']';
  }

  /**
   * 执行检查清单
   */
  runChecklist() {
    const checklist = this.config.checklist;
    
    console.log(`
✅ 整合检查清单
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 文档整合
`);
    
    checklist.document_integration.completed.forEach(item => {
      console.log(`  ✓ ${item}`);
    });
    checklist.document_integration.pending.forEach(item => {
      console.log(`  ⏳ ${item}`);
    });

    console.log(`
💻 代码整合
`);
    checklist.code_integration.completed.forEach(item => {
      console.log(`  ✓ ${item}`);
    });

    console.log(`
🗄️ 数据整合
`);
    checklist.data_integration.completed.forEach(item => {
      console.log(`  ✓ ${item}`);
    });
    checklist.data_integration.pending.forEach(item => {
      console.log(`  ⏳ ${item}`);
    });

    const completion = Math.round(
      ((checklist.document_integration.completed.length +
        checklist.code_integration.completed.length +
        checklist.data_integration.completed.length) /
       (checklist.document_integration.completed.length +
        checklist.document_integration.pending.length +
        checklist.code_integration.completed.length +
        checklist.data_integration.completed.length +
        checklist.data_integration.pending.length)) * 100
    );

    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
整体完成度: ${completion}%
`);
  }

  /**
   * 显示案例洞察
   */
  showInsights() {
    const insights = this.config.case_insights;
    
    console.log(`
💡 案例库洞察 (15个案例验证)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 关键发现
`);

    insights.critical_findings.forEach((finding, i) => {
      console.log(`  ${i + 1}. ${finding.finding}: ${finding.value}`);
    });

    console.log(`
📌 新增洞察 (CASE-011~015)
`);

    insights.new_insights.forEach((insight, i) => {
      console.log(`  • ${insight}`);
    });

    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
  }

  /**
   * 显示下一步计划
   */
  showNextSteps() {
    const steps = this.config.next_steps;
    
    console.log(`
📋 下一步行动计划
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ 即时 (30分钟内)
`);
    steps.immediate.forEach((item, i) => {
      console.log(`  ${i + 1}. ${item}`);
    });

    console.log(`
📅 短期 (今天)
`);
    steps.short_term.forEach((item, i) => {
      console.log(`  ${i + 1}. ${item}`);
    });

    console.log(`
📆 中期 (本周)
`);
    steps.medium_term.forEach((item, i) => {
      console.log(`  ${i + 1}. ${item}`);
    });

    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
  }

  /**
   * 生成整合报告
   */
  generateReport() {
    const report = `
# 完整体系整合报告

生成时间: ${new Date().toLocaleString()}
框架版本: V1.0

## 体系架构
- 数据层: 案例库(${this.config.architecture.data_layer.breakdown.success}成功/${this.config.architecture.data_layer.breakdown.failure}失败/${this.config.architecture.data_layer.breakdown.ongoing}进行中)
- 方法论层: 3大理论 + 3大模型
- 产品层: V2.0已上线，V2.1开发中
- 协作层: P0P1完整组件

## KPI达成情况
${Object.entries(this.config.kpis).map(([k, v]) => `- ${k}: ${v.rate}`).join('\n')}

## 下一步行动
${this.config.next_steps.immediate.map(i => `- [ ] ${i}`).join('\n')}
`;

    const reportPath = path.join(process.cwd(), 'integration-report.md');
    fs.writeFileSync(reportPath, report);
    console.log(`✅ 报告已生成: ${reportPath}`);
    return reportPath;
  }

  /**
   * 显示帮助
   */
  showHelp() {
    console.log(`
🏗️ 完整体系整合框架 v1.0.0

用法: node integration-framework.js <命令>

命令:
  architecture    显示体系架构
  assets          显示资产清单
  kpis            显示KPI仪表板
  checklist       执行检查清单
  insights        显示案例洞察
  next            显示下一步计划
  report          生成整合报告
  full            显示完整概览
  help            显示帮助信息

示例:
  node integration-framework.js full
  node integration-framework.js report
`);
  }
}

// CLI 入口
if (require.main === module) {
  const framework = new SystemIntegrationFramework();
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    framework.showArchitecture();
    process.exit(0);
  }
  
  const command = args[0];
  
  switch (command) {
    case 'architecture':
      framework.showArchitecture();
      break;
    case 'assets':
      framework.showAssets();
      break;
    case 'kpis':
      framework.showKPIs();
      break;
    case 'checklist':
      framework.runChecklist();
      break;
    case 'insights':
      framework.showInsights();
      break;
    case 'next':
      framework.showNextSteps();
      break;
    case 'report':
      framework.generateReport();
      break;
    case 'full':
      framework.showArchitecture();
      framework.showKPIs();
      framework.runChecklist();
      break;
    case 'help':
    default:
      framework.showHelp();
  }
}

module.exports = SystemIntegrationFramework;
