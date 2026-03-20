#!/usr/bin/env node
/**
 * 🎨 多格式交付能力扩展计划 - 主执行脚本
 * Multi-Format Delivery v1.0.0
 * 
 * 核心功能：
 * 1. Mermaid图表生成
 * 2. 数据可视化
 * 3. PPT大纲生成
 * 4. 思维导图生成
 * 5. Gantt图生成
 */

const fs = require('fs');
const path = require('path');

class MultiFormatDeliver {
  constructor() {
    this.config = this.loadConfig();
    this.templates = this.loadTemplates();
  }

  loadConfig() {
    const configPath = path.join(__dirname, 'skill.json');
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }

  loadTemplates() {
    return {
      flowchart: {
        prefix: 'graph TD',
        example: `graph TD
    A[开始] --> B{判断}
    B -->|是| C[处理1]
    B -->|否| D[处理2]
    C --> E[结束]
    D --> E`
      },
      sequence: {
        prefix: 'sequenceDiagram',
        example: `sequenceDiagram
    participant A as 用户
    participant B as 系统
    A->>B: 请求
    B-->>A: 响应`
      },
      gantt: {
        prefix: 'gantt',
        example: `gantt
    title 项目排期
    dateFormat YYYY-MM-DD
    section 阶段1
    任务1 :a1, 2026-03-15, 3d
    任务2 :after a1, 2d`
      },
      mindmap: {
        prefix: 'mindmap',
        example: `mindmap
  root((中心主题))
    分支1
      子分支1
      子分支2
    分支2`
      },
      pie: {
        prefix: 'pie',
        example: `pie title 数据分布
    "类别A" : 40
    "类别B" : 30
    "类别C" : 30`
      }
    };
  }

  /**
   * 生成流程图
   */
  generateFlowchart(title, steps) {
    let mermaid = `graph TD\n`;
    
    // 添加样式定义
    mermaid += `    classDef default fill:#f9f,stroke:#333,stroke-width:2px\n`;
    mermaid += `    classDef highlight fill:#f96,stroke:#333,stroke-width:2px\n`;
    mermaid += `    classDef success fill:#9f9,stroke:#333,stroke-width:2px\n\n`;
    
    // 添加节点和连接
    const nodes = [];
    steps.forEach((step, i) => {
      const nodeId = String.fromCharCode(65 + i); // A, B, C...
      const nodeType = step.type || 'process';
      
      if (nodeType === 'decision') {
        mermaid += `    ${nodeId}{${step.name}}\n`;
      } else if (nodeType === 'start' || nodeType === 'end') {
        mermaid += `    ${nodeId}[${step.name}]\n`;
      } else {
        mermaid += `    ${nodeId}[${step.name}]\n`;
      }
      
      // 添加连接
      if (i < steps.length - 1) {
        const nextId = String.fromCharCode(65 + i + 1);
        if (step.branches) {
          step.branches.forEach(branch => {
            mermaid += `    ${nodeId} -->|${branch.label}| ${branch.target}\n`;
          });
        } else {
          mermaid += `    ${nodeId} --> ${nextId}\n`;
        }
      }
      
      // 应用样式
      if (step.style) {
        mermaid += `    class ${nodeId} ${step.style}\n`;
      }
    });
    
    return { type: 'mermaid', code: mermaid, title };
  }

  /**
   * 生成Gantt图
   */
  generateGantt(title, tasks) {
    let mermaid = `gantt\n    title ${title}\n    dateFormat YYYY-MM-DD\n\n`;
    
    let currentSection = '';
    tasks.forEach(task => {
      if (task.section && task.section !== currentSection) {
        currentSection = task.section;
        mermaid += `    section ${currentSection}\n`;
      }
      
      const status = task.done ? 'done,' : '';
      const after = task.after ? `, after ${task.after}` : '';
      const duration = task.duration || '1d';
      
      if (task.start) {
        mermaid += `    ${task.name} :${status}${task.id}, ${task.start}, ${duration}\n`;
      } else if (task.after) {
        mermaid += `    ${task.name} :${status}${task.id}${after}, ${duration}\n`;
      } else {
        mermaid += `    ${task.name} :${status}${task.id}, ${duration}\n`;
      }
    });
    
    return { type: 'mermaid', code: mermaid, title };
  }

  /**
   * 生成思维导图
   */
  generateMindmap(title, structure) {
    let mermaid = `mindmap\n  root((${title}))\n`;
    
    const renderBranch = (branch, indent = 2) => {
      const prefix = '  '.repeat(indent);
      let result = '';
      
      if (Array.isArray(branch)) {
        branch.forEach(item => {
          if (typeof item === 'string') {
            result += `${prefix}${item}\n`;
          } else if (typeof item === 'object') {
            Object.entries(item).forEach(([key, children]) => {
              result += `${prefix}${key}\n`;
              if (children) {
                result += renderBranch(children, indent + 1);
              }
            });
          }
        });
      }
      
      return result;
    };
    
    mermaid += renderBranch(structure);
    
    return { type: 'mermaid', code: mermaid, title };
  }

  /**
   * 生成PPT大纲
   */
  generatePPTOutline(title, slides) {
    let outline = `# ${title}\n\n`;
    
    slides.forEach((slide, i) => {
      outline += `## Slide ${i + 1}: ${slide.title}\n\n`;
      
      if (slide.content) {
        slide.content.forEach(item => {
          outline += `- ${item}\n`;
        });
      }
      
      if (slide.visual) {
        outline += `\n📊 视觉元素: ${slide.visual}\n`;
      }
      
      if (slide.note) {
        outline += `\n💬 演讲备注: ${slide.note}\n`;
      }
      
      outline += '\n---\n\n';
    });
    
    return { type: 'markdown', content: outline, title };
  }

  /**
   * 生成数据可视化图表
   */
  generateDataViz(type, data, options = {}) {
    const charts = {
      pie: (data) => {
        let mermaid = `pie title ${options.title || '数据分布'}\n`;
        data.forEach(item => {
          mermaid += `    "${item.label}" : ${item.value}\n`;
        });
        return mermaid;
      },
      
      bar: (data) => {
        // Mermaid不原生支持柱状图，使用xychart-beta
        let mermaid = `xychart-beta\n    title "${options.title || '柱状图'}"\n`;
        if (options.xAxis) {
          mermaid += `    x-axis [${options.xAxis.join(', ')}]\n`;
        }
        if (options.yAxis) {
          mermaid += `    y-axis "${options.yAxis.label || '数值'}" ${options.yAxis.min || 0} --> ${options.yAxis.max || 100}\n`;
        }
        mermaid += `    bar [${data.map(d => d.value).join(', ')}]\n`;
        return mermaid;
      }
    };
    
    const generator = charts[type];
    if (generator) {
      return { type: 'mermaid', code: generator(data), title: options.title };
    }
    
    return null;
  }

  /**
   * 生成周报可视化
   */
  generateWeeklyReportViz(weekData) {
    const slides = [
      { 
        title: '本周概览', 
        content: [
          `完成任务: ${weekData.completed || 0} 项`,
          `进行中: ${weekData.inProgress || 0} 项`,
          `延期: ${weekData.delayed || 0} 项`,
          `完成率: ${weekData.rate || 0}%`
        ],
        visual: '完成率环形图'
      },
      {
        title: '任务类型分布',
        content: Object.entries(weekData.byType || {}).map(([k, v]) => `${k}: ${v}`),
        visual: '饼图'
      },
      {
        title: '下周计划',
        content: (weekData.nextWeek || []).map(t => t),
        visual: 'Gantt图'
      }
    ];
    
    return this.generatePPTOutline(`${weekData.week || '本周'}复盘报告`, slides);
  }

  /**
   * 渲染Mermaid代码块
   */
  renderMermaid(mermaidCode, title = '图表') {
    return `
## ${title}

\`\`\`mermaid
${mermaidCode}
\`\`\`

**使用方式：**
1. 复制上方代码
2. 打开 https://mermaid.live
3. 粘贴即可预览和导出

`;
  }

  /**
   * CLI帮助信息
   */
  showHelp() {
    console.log(`
🎨 多格式交付能力扩展计划 v1.0.0

用法: node multi-format.js <命令> [参数]

命令:
  flowchart <title>     生成流程图 (JSON数据从stdin)
  gantt <title>         生成Gantt图 (JSON数据从stdin)
  mindmap <title>       生成思维导图 (JSON数据从stdin)
  ppt <title>           生成PPT大纲 (JSON数据从stdin)
  pie <title>           生成饼图 (JSON数据从stdin)
  weekly <title>        生成周报可视化 (JSON数据从stdin)
  help                  显示帮助信息

示例:
  echo '[{"name":"开始","type":"start"},{"name":"处理"}]' | node multi-format.js flowchart "流程"
  
内置模板:
  - flowchart: 流程图
  - sequence: 时序图
  - gantt: Gantt图
  - mindmap: 思维导图
  - pie: 饼图
`);
  }
}

// CLI 入口
if (require.main === module) {
  const deliver = new MultiFormatDeliver();
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    deliver.showHelp();
    process.exit(0);
  }
  
  const command = args[0];
  const title = args[1] || '未命名';
  
  // 从stdin读取JSON数据
  let inputData = '';
  process.stdin.setEncoding('utf8');
  
  if (process.stdin.isTTY) {
    // 没有管道输入，显示模板
    switch (command) {
      case 'flowchart':
        console.log('\n📝 流程图模板:\n');
        console.log(deliver.templates.flowchart.example);
        break;
      case 'gantt':
        console.log('\n📅 Gantt图模板:\n');
        console.log(deliver.templates.gantt.example);
        break;
      case 'mindmap':
        console.log('\n🧠 思维导图模板:\n');
        console.log(deliver.templates.mindmap.example);
        break;
      case 'pie':
        console.log('\n🥧 饼图模板:\n');
        console.log(deliver.templates.pie.example);
        break;
      default:
        deliver.showHelp();
    }
    process.exit(0);
  }
  
  process.stdin.on('data', chunk => {
    inputData += chunk;
  });
  
  process.stdin.on('end', () => {
    let data = [];
    try {
      data = JSON.parse(inputData || '[]');
    } catch (e) {
      console.log('⚠️ JSON解析失败，使用默认数据');
    }
    
    let result = null;
    
    switch (command) {
      case 'flowchart':
        result = deliver.generateFlowchart(title, data);
        console.log(deliver.renderMermaid(result.code, result.title));
        break;
      case 'gantt':
        result = deliver.generateGantt(title, data);
        console.log(deliver.renderMermaid(result.code, result.title));
        break;
      case 'mindmap':
        result = deliver.generateMindmap(title, data);
        console.log(deliver.renderMermaid(result.code, result.title));
        break;
      case 'ppt':
        result = deliver.generatePPTOutline(title, data);
        console.log(result.content);
        break;
      case 'pie':
        result = deliver.generateDataViz('pie', data, { title });
        console.log(deliver.renderMermaid(result.code, result.title));
        break;
      case 'weekly':
        result = deliver.generateWeeklyReportViz(data);
        console.log(result.content);
        break;
      default:
        deliver.showHelp();
    }
  });
}

module.exports = MultiFormatDeliver;
