#!/usr/bin/env python3
"""
TRL 自评工具 - Web API 版本
满意解研究所 · 硬科技合伙人匹配决策系统

用法: python trl_api.py
      然后访问 http://localhost:8080
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from typing import Dict, List


class TRLCalculator:
    """TRL 计算引擎"""
    
    TRL_LEVELS = {
        1: {"name": "基本原理发现", "risk": "极高", "stage": "种子轮/天使轮", 
            "partner": "技术联合创始人、学术合伙人"},
        2: {"name": "技术方案形成", "risk": "很高", "stage": "天使轮",
            "partner": "CTO、系统架构师"},
        3: {"name": "关键功能实验室验证", "risk": "高", "stage": "Pre-A轮",
            "partner": "工程合伙人、产品经理"},
        4: {"name": "组件/实验板验证", "risk": "中高", "stage": "A轮",
            "partner": "硬件合伙人、供应链专家"},
        5: {"name": "相关环境组件验证", "risk": "中", "stage": "A+轮",
            "partner": "运营合伙人、市场验证专家"},
        6: {"name": "系统/子系统原型验证", "risk": "中低", "stage": "B轮",
            "partner": "商业化合伙人、销售VP"},
        7: {"name": "操作环境原型演示", "risk": "低", "stage": "B+轮/C轮",
            "partner": "大客户销售、行业专家"},
        8: {"name": "系统完成并通过测试", "risk": "很低", "stage": "C轮/Pre-IPO",
            "partner": "规模化运营专家、财务合伙人"},
        9: {"name": "实际任务成功应用", "risk": "极低", "stage": "IPO/并购",
            "partner": "战略合伙人、并购专家"}
    }
    
    @staticmethod
    def calculate(answers: Dict[str, int]) -> Dict:
        """
        计算 TRL 等级
        
        输入示例:
        {
            "tech_stage": 5,      # 技术阶段 (1-9)
            "prototype": 5,       # 原型验证 (1-9)
            "test_env": 5,        # 测试环境 (1-9)
            "team": 5,            # 团队配置 (1-9)
            "customer": 5,        # 客户验证 (1-9)
            "supply_chain": 5,    # 供应链 (1-9)
            "ip": 5,              # 知识产权 (1-9)
            "funding": 5          # 资金需求 (1-9)
        }
        """
        scores = list(answers.values())
        avg_score = sum(scores) / len(scores)
        
        # 计算 TRL 等级
        if avg_score < 1.5: trl = 1
        elif avg_score < 2.5: trl = 2
        elif avg_score < 3.5: trl = 3
        elif avg_score < 4.5: trl = 4
        elif avg_score < 5.5: trl = 5
        elif avg_score < 6.5: trl = 6
        elif avg_score < 7.5: trl = 7
        elif avg_score < 8.5: trl = 8
        else: trl = 9
        
        return {
            "trl_level": trl,
            "trl_name": TRLCalculator.TRL_LEVELS[trl]["name"],
            "average_score": round(avg_score, 2),
            "total_score": sum(scores),
            "max_score": len(scores) * 9,
            "risk_level": TRLCalculator.TRL_LEVELS[trl]["risk"],
            "funding_stage": TRLCalculator.TRL_LEVELS[trl]["stage"],
            "partner_need": TRLCalculator.TRL_LEVELS[trl]["partner"],
            "dimension_scores": answers,
            "assessment_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


class TRLHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def do_GET(self):
        """处理 GET 请求"""
        if self.path == '/':
            self.send_html()
        elif self.path == '/api/trl/levels':
            self.send_json(TRLCalculator.TRL_LEVELS)
        elif self.path == '/api/trl/questions':
            self.send_json(self.get_questions())
        else:
            self.send_error(404)
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path == '/api/trl/calculate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            answers = json.loads(post_data.decode('utf-8'))
            result = TRLCalculator.calculate(answers)
            self.send_json(result)
        else:
            self.send_error(404)
    
    def send_html(self):
        """发送 HTML 页面"""
        html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRL 技术成熟度自评 - 满意解研究所</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
        }
        .question {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
        }
        .question h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 16px;
        }
        .options {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .option {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .option:hover {
            border-color: #667eea;
            background: #f0f4ff;
        }
        .option.selected {
            border-color: #667eea;
            background: #667eea;
            color: white;
        }
        .option input {
            margin-right: 10px;
        }
        .submit-btn {
            display: block;
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.3s;
        }
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .result {
            display: none;
            margin-top: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            color: white;
        }
        .result.show {
            display: block;
        }
        .trl-level {
            font-size: 72px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .trl-name {
            font-size: 24px;
            text-align: center;
            margin-bottom: 30px;
        }
        .result-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .result-item {
            background: rgba(255,255,255,0.15);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .result-item h4 {
            font-size: 14px;
            opacity: 0.8;
            margin-bottom: 8px;
        }
        .result-item p {
            font-size: 18px;
            font-weight: bold;
        }
        .partner-suggestion {
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }
        .partner-suggestion h4 {
            margin-bottom: 10px;
        }
        .score-bar {
            height: 8px;
            background: rgba(255,255,255,0.3);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        .score-fill {
            height: 100%;
            background: white;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 TRL 技术成熟度自评工具</h1>
        <p class="subtitle">满意解研究所 · 硬科技合伙人匹配决策系统</p>
        
        <form id="trlForm">
            <div id="questions"></div>
            <button type="submit" class="submit-btn">开始评估</button>
        </form>
        
        <div id="result" class="result">
            <div class="trl-level" id="trlLevel">-</div>
            <div class="trl-name" id="trlName">-</div>
            
            <div class="result-grid">
                <div class="result-item">
                    <h4>风险等级</h4>
                    <p id="riskLevel">-</p>
                </div>
                <div class="result-item">
                    <h4>适配融资阶段</h4>
                    <p id="fundingStage">-</p>
                </div>
                <div class="result-item">
                    <h4>综合得分</h4>
                    <p id="avgScore">-</p>
                </div>
            </div>
            
            <div class="partner-suggestion">
                <h4>🎯 合伙人匹配建议</h4>
                <p id="partnerNeed">-</p>
            </div>
        </div>
    </div>

    <script>
        const questions = [
            {
                id: "tech_stage",
                category: "技术研发",
                question: "您的核心技术目前处于什么阶段？",
                options: [
                    {value: 1, text: "仅完成理论研究/算法验证"},
                    {value: 2, text: "已形成技术方案和概要设计"},
                    {value: 3, text: "关键功能在实验室环境验证通过"},
                    {value: 4, text: "实验板/功能样机已制作完成"},
                    {value: 5, text: "在模拟环境/相关环境中验证通过"},
                    {value: 6, text: "高还原度原型系统已集成验证"},
                    {value: 7, text: "在实际操作环境中完成现场演示"},
                    {value: 8, text: "产品定型完成并通过全功能测试"},
                    {value: 9, text: "已实现批量生产和规模化应用"}
                ]
            },
            {
                id: "prototype",
                category: "原型验证",
                question: "您的产品原型验证程度如何？",
                options: [
                    {value: 1, text: "无实物原型，仅有仿真/理论模型"},
                    {value: 3, text: "有功能单元验证件，未系统集成"},
                    {value: 5, text: "系统集成原型完成，实验室验证通过"},
                    {value: 7, text: "工程样机完成，现场环境测试通过"},
                    {value: 9, text: "量产产品，已在市场规模化销售"}
                ]
            },
            {
                id: "test_env",
                category: "测试环境",
                question: "您的产品在哪些环境中完成了测试？",
                options: [
                    {value: 1, text: "仅理论分析/仿真验证"},
                    {value: 3, text: "实验室理想环境"},
                    {value: 5, text: "模拟/相关环境（接近真实条件）"},
                    {value: 7, text: "实际操作环境（真实场景）"},
                    {value: 9, text: "多样化实际应用场景，长期稳定运行"}
                ]
            },
            {
                id: "team",
                category: "团队配置",
                question: "您当前团队的技术-商业配比如何？",
                options: [
                    {value: 2, text: "纯技术团队，无商业化人员"},
                    {value: 4, text: "技术为主，有兼职市场人员"},
                    {value: 6, text: "技术+产品+市场，全职核心团队"},
                    {value: 8, text: "完整团队，含供应链、销售、运营"},
                    {value: 9, text: "规模化团队，各部门体系完善"}
                ]
            },
            {
                id: "customer",
                category: "客户验证",
                question: "您的产品客户验证情况如何？",
                options: [
                    {value: 1, text: "无客户接触，仅有市场调研"},
                    {value: 3, text: "有潜在客户意向/LOI"},
                    {value: 5, text: "有试点客户，正在试用验证"},
                    {value: 7, text: "有付费客户，完成商业验证"},
                    {value: 9, text: "大量客户，复购率高，口碑良好"}
                ]
            },
            {
                id: "supply_chain",
                category: "供应链",
                question: "您的供应链和生产准备情况如何？",
                options: [
                    {value: 2, text: "无供应链规划，实验室自制"},
                    {value: 4, text: "关键供应商已接触，有初步意向"},
                    {value: 6, text: "核心供应链已确定，小批量可行"},
                    {value: 8, text: "供应链体系完善，具备量产能力"},
                    {value: 9, text: "规模化生产，成本控制优秀"}
                ]
            },
            {
                id: "ip",
                category: "知识产权",
                question: "您的知识产权布局情况如何？",
                options: [
                    {value: 2, text: "无专利申请，技术秘密保护"},
                    {value: 4, text: "核心专利已申请/受理中"},
                    {value: 6, text: "核心专利已授权，有专利组合"},
                    {value: 8, text: "完善专利布局，含国际专利"},
                    {value: 9, text: "专利壁垒强大，行业标准制定者"}
                ]
            },
            {
                id: "funding",
                category: "资金需求",
                question: "您当前的资金需求主要用于什么？",
                options: [
                    {value: 2, text: "技术研发/原理验证"},
                    {value: 4, text: "原型开发/样机制作"},
                    {value: 6, text: "产品定型/小规模试产"},
                    {value: 8, text: "量产爬坡/市场推广"},
                    {value: 9, text: "规模化扩张/并购整合"}
                ]
            }
        ];

        // 渲染问题
        function renderQuestions() {
            const container = document.getElementById('questions');
            container.innerHTML = questions.map((q, idx) => `
                <div class="question">
                    <h3>【${q.category}】${idx + 1}. ${q.question}</h3>
                    <div class="options">
                        ${q.options.map(opt => `
                            <label class="option" onclick="selectOption('${q.id}', ${opt.value}, this)">
                                <input type="radio" name="${q.id}" value="${opt.value}">
                                <span>${opt.text}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>
            `).join('');
        }

        // 选择选项
        function selectOption(name, value, element) {
            document.querySelectorAll(`input[name="${name}"]`).forEach(el => {
                el.closest('.option').classList.remove('selected');
            });
            element.classList.add('selected');
            element.querySelector('input').checked = true;
        }

        // 提交表单
        document.getElementById('trlForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const answers = {};
            questions.forEach(q => {
                const selected = document.querySelector(`input[name="${q.id}"]:checked`);
                if (!selected) {
                    alert(`请完成第 ${questions.indexOf(q) + 1} 题`);
                    return;
                }
                answers[q.id] = parseInt(selected.value);
            });

            if (Object.keys(answers).length !== questions.length) return;

            const response = await fetch('/api/trl/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(answers)
            });
            
            const result = await response.json();
            
            document.getElementById('trlLevel').textContent = result.trl_level;
            document.getElementById('trlName').textContent = result.trl_name;
            document.getElementById('riskLevel').textContent = result.risk_level;
            document.getElementById('fundingStage').textContent = result.funding_stage;
            document.getElementById('avgScore').textContent = result.average_score + '/9';
            document.getElementById('partnerNeed').textContent = result.partner_need;
            
            document.getElementById('result').classList.add('show');
            document.getElementById('result').scrollIntoView({behavior: 'smooth'});
        });

        renderQuestions();
    </script>
</body>
</html>
        '''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_json(self, data):
        """发送 JSON 响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def get_questions(self) -> List[Dict]:
        """获取问题列表"""
        return [
            {"id": "tech_stage", "category": "技术研发", "question": "技术阶段"},
            {"id": "prototype", "category": "原型验证", "question": "原型程度"},
            {"id": "test_env", "category": "测试环境", "question": "测试环境"},
            {"id": "team", "category": "团队配置", "question": "团队配置"},
            {"id": "customer", "category": "客户验证", "question": "客户验证"},
            {"id": "supply_chain", "category": "供应链", "question": "供应链"},
            {"id": "ip", "category": "知识产权", "question": "知识产权"},
            {"id": "funding", "category": "资金需求", "question": "资金需求"}
        ]
    
    def log_message(self, format, *args):
        """静默日志"""
        pass


def run_server(port=8080):
    """启动服务器"""
    server = HTTPServer(('0.0.0.0', port), TRLHandler)
    print(f"=" * 60)
    print(f"  TRL 自评工具 Web API 已启动")
    print(f"  满意解研究所 · 硬科技合伙人匹配系统")
    print(f"=" * 60)
    print(f"\n  访问地址: http://localhost:{port}")
    print(f"  API 端点: http://localhost:{port}/api/trl/calculate")
    print(f"\n  按 Ctrl+C 停止服务")
    print(f"=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n服务已停止")


if __name__ == "__main__":
    run_server()
