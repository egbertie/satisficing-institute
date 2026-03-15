#!/usr/bin/env node
/**
 * 🌟 组织建设者 - 主执行脚本
 * Organization Builder v1.0.0
 * 
 * 核心功能：
 * 1. 六大永动引擎管理
 * 2. 三大支撑体系
 * 3. 资源调度
 * 4. 指标监控
 */

const fs = require('fs');
const path = require('path');

class OrganizationBuilder {
  constructor() {
    this.config = this.loadConfig();
  }

  loadConfig() {
    const configPath = path.join(__dirname, 'skill.json');
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }

  /**
   * 显示六大引擎状态
   */
  showEngines() {
    const engines = this.config.six_engines;
    
    console.log(`
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🚀 永不停歇进化体系 · 六大永动引擎                    ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  引擎1: 🏢 ${engines.business_iteration.name.padEnd(46)}║
║  ───────────────────────────────────────────────────────────  ║
║  层级: ${engines.business_iteration.layer.padEnd(50)}║
║  维度: ${engines.business_iteration.aspects.join(' · ').padEnd(48)}║
║  频率: ${engines.business_iteration.frequency.padEnd(50)}║
║                                                              ║
║  引擎2: 🎯 ${engines.product_development.name.padEnd(46)}║
║  ───────────────────────────────────────────────────────────  ║
║  产品:                                                      ║
`);
    engines.product_development.products.forEach(p => {
      const status = p.version || p.stage;
      const priority = p.priority ? `[${p.priority}]` : '';
      console.log(`║    ${priority} ${p.name.padEnd(20)} ${status.padEnd(10)} → ${p.goal.padEnd(25)}║`);
    });

    console.log(`║                                                              ║
║  引擎3: 📚 ${engines.methodology_evolution.name.padEnd(46)}║
║  ───────────────────────────────────────────────────────────  ║
║  模块:                                                      ║
`);
    engines.methodology_evolution.modules.forEach(m => {
      const status = m.version || m.stage;
      console.log(`║    • ${m.name.padEnd(20)} ${status.padEnd(10)} → ${m.goal.padEnd(25)}║`);
    });

    console.log(`║                                                              ║
║  引擎4: 👤 ${engines.digital_twin_improvement.name.padEnd(46)}║
║  ───────────────────────────────────────────────────────────  ║
║  角色:                                                      ║
`);
    engines.digital_twin_improvement.roles.forEach(r => {
      const icon = r.status === '运行中' ? '✅' : '⏳';
      console.log(`║    ${icon} ${r.name.padEnd(25)} ${r.status.padEnd(10)} → ${r.improvement.padEnd(20)}║`);
    });

    console.log(`║                                                              ║
║  引擎5: 💡 ${engines.skill_iteration.name.padEnd(46)}║
║  ───────────────────────────────────────────────────────────  ║
║  维度:                                                      ║
`);
    engines.skill_iteration.dimensions.forEach(d => {
      console.log(`║    • ${d.focus.padEnd(20)}: ${d.current.padEnd(20)} → ${d.evolution.padEnd(15)}║`);
    });

    console.log(`║                                                              ║
║  引擎6: 🎮 ${engines.toolkit_development.name.padEnd(46)}║
║  ───────────────────────────────────────────────────────────  ║
║  产品:                                                      ║
`);
    engines.toolkit_development.products.forEach(p => {
      const bar = this.renderProgressBar(parseInt(p.progress) || 0, 10);
      console.log(`║    ${bar} ${p.name.padEnd(15)} ${p.progress.padStart(4)} → ${p.goal.padEnd(20)}║`);
    });

    console.log(`║                                                              ║
╚══════════════════════════════════════════════════════════════╝
`);
  }

  /**
   * 显示支撑体系
   */
  showSupportSystems() {
    const support = this.config.support_systems;
    
    console.log(`
🔧 三大支撑体系
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 数据资产积累
`);
    support.data_assets.assets.forEach(a => {
      console.log(`  • ${a.type.padEnd(15)} 当前: ${a.current.padEnd(15)} → ${a.goal}`);
    });

    console.log(`
⚙️ 运营体系优化
`);
    support.operations.modules.forEach(m => {
      const icon = m.status.includes('已建立') || m.status.includes('%') ? '✅' : '⏳';
      console.log(`  ${icon} ${m.name.padEnd(20)} ${m.status.padEnd(15)} → ${m.goal}`);
    });

    console.log(`
🌐 生态建设
`);
    support.ecosystem.modules.forEach(m => {
      const icon = m.current !== '0' ? '✅' : '⏳';
      console.log(`  ${icon} ${m.name.padEnd(20)} 当前: ${m.current.padEnd(15)} → ${m.goal}`);
    });

    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
  }

  /**
   * 渲染进度条
   */
  renderProgressBar(percentage, width = 10) {
    const filled = Math.round((percentage / 100) * width);
    const empty = width - filled;
    return '[' + '█'.repeat(filled) + '░'.repeat(empty) + ']';
  }

  /**
   * 显示资源调度
   */
  showResourceSchedule() {
    const schedule = this.config.resource_schedule;
    
    console.log(`
⏰ 资源调度矩阵
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

时段              主引擎                    辅引擎              占用
─────────────────────────────────────────────────────────
`);

    Object.entries(schedule).forEach(([period, data]) => {
      const periodName = {
        'daytime': '09:00-18:00',
        'evening': '18:00-23:00',
        'night': '23:00-09:00',
        'weekend': '周末'
      }[period];
      console.log(`${periodName.padEnd(17)} ${data.primary.padEnd(25)} ${data.secondary.padEnd(18)} ${data.allocation}`);
    });

    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

冲突解决规则:
  1. P0级阻塞 → 暂停其他引擎，全力冲刺
  2. 资源竞争 → 按"交付>学习>生态"优先级分配
  3. AI算力限制 → 重任务放夜间，轻任务白天并行
`);
  }

  /**
   * 显示指标仪表板
   */
  showMetrics() {
    const metrics = this.config.metrics;
    
    console.log(`
📈 成果双向进化指标
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

成长指标 (向内)
─────────────────────────────────────────────────
`);

    Object.entries(metrics.growth).forEach(([key, data]) => {
      const name = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      console.log(`${name.padEnd(20)} 当前: ${data.current.toString().padEnd(10)} 3月: ${data.m3.toString().padEnd(10)} 6月: ${data.m6}`);
    });

    console.log(`
成果指标 (向外)
─────────────────────────────────────────────────
`);

    Object.entries(metrics.outcomes).forEach(([key, data]) => {
      const name = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      console.log(`${name.padEnd(20)} 当前: ${data.current.toString().padEnd(10)} 3月: ${data.m3.toString().padEnd(10)} 6月: ${data.m6}`);
    });

    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
  }

  /**
   * 执行今日任务
   */
  executeToday() {
    const engines = this.config.six_engines;
    
    console.log(`
📋 今日执行任务清单
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【商业计划迭代】
`);
    engines.business_iteration.aspects.forEach(a => {
      console.log(`  ☐ ${a}`);
    });

    console.log(`
【产品开发】
`);
    engines.product_development.products.filter(p => p.priority === 'P1').forEach(p => {
      console.log(`  ☐ ${p.name} (${p.goal})`);
    });

    console.log(`
【方法论迭代】
`);
    engines.methodology_evolution.modules.forEach(m => {
      console.log(`  ☐ ${m.name}`);
    });

    console.log(`
【数字替身完善】
`);
    engines.digital_twin_improvement.roles.forEach(r => {
      console.log(`  ☐ ${r.name}`);
    });

    console.log(`
【学习进化】
  ☐ AI工具链研究
  ☐ 硬科技行业资讯

【工具开发】
`);
    engines.toolkit_development.products.filter(p => parseInt(p.progress) > 0).forEach(p => {
      console.log(`  ☐ ${p.name} (${p.progress})`);
    });

    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
  }

  /**
   * 生成进化报告
   */
  generateReport() {
    const report = `
# 永不停歇进化体系报告

生成时间: ${new Date().toLocaleString()}
版本: V1.0

## 六大引擎状态
- 商业计划迭代: 运行中
- 产品研发开发: 运行中
- 方法论迭代: 运行中
- 数字替身完善: 运行中
- 学习进化: 运行中
- 工具开发: 运行中

## 成长指标
- 方法论文档: ${this.config.metrics.growth.methodology_docs.current} → 目标3月${this.config.metrics.growth.methodology_docs.m3}
- Skill数量: ${this.config.metrics.growth.skill_count.current} → 目标3月${this.config.metrics.growth.skill_count.m3}

## 今日完成
- [ ] 商业计划复盘
- [ ] 产品开发推进
- [ ] 方法论深化
- [ ] 数字替身训练
- [ ] 学习进化
- [ ] 工具开发

---
*只要资源允许，6大引擎永不停止*
*成长与成果，双向进化，螺旋上升*
`;

    const reportPath = path.join(process.cwd(), 'evolution-report.md');
    fs.writeFileSync(reportPath, report);
    console.log(`✅ 进化报告已生成: ${reportPath}`);
    return reportPath;
  }

  /**
   * 显示帮助
   */
  showHelp() {
    console.log(`
🌟 组织建设者 (永不停歇进化体系) v1.0.0

用法: node org-builder.js <命令>

命令:
  engines         显示六大引擎状态
  support         显示三大支撑体系
  schedule        显示资源调度
  metrics         显示指标仪表板
  today           显示今日任务清单
  report          生成进化报告
  full            显示完整概览
  help            显示帮助信息

六大永动引擎:
  1. 商业计划迭代
  2. 产品研发开发
  3. 方法论迭代
  4. 数字替身完善
  5. 学习进化
  6. 工具开发

示例:
  node org-builder.js full
  node org-builder.js today
  node org-builder.js report
`);
  }
}

// CLI 入口
if (require.main === module) {
  const builder = new OrganizationBuilder();
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    builder.showEngines();
    process.exit(0);
  }
  
  const command = args[0];
  
  switch (command) {
    case 'engines':
      builder.showEngines();
      break;
    case 'support':
      builder.showSupportSystems();
      break;
    case 'schedule':
      builder.showResourceSchedule();
      break;
    case 'metrics':
      builder.showMetrics();
      break;
    case 'today':
      builder.executeToday();
      break;
    case 'report':
      builder.generateReport();
      break;
    case 'full':
      builder.showEngines();
      builder.showSupportSystems();
      builder.showMetrics();
      break;
    case 'help':
    default:
      builder.showHelp();
  }
}

module.exports = OrganizationBuilder;
