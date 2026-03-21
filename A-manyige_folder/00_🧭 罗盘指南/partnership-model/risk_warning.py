#!/usr/bin/env python3
"""
合伙人风险预警体系 V1.0
早期信号识别 + 分级预警 + 干预建议
"""

import json
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class AlertLevel(Enum):
    GREEN = "green"       # 正常
    YELLOW = "yellow"     # 关注
    ORANGE = "orange"     # 警告
    RED = "red"           # 危险
    BLACK = "black"       # 危机

@dataclass
class RiskSignal:
    """风险信号"""
    signal_type: str
    description: str
    severity: AlertLevel
    stage: str  # matching/dating/commitment/operation
    indicators: List[str]
    suggested_action: str

@dataclass
class Alert:
    """预警信息"""
    alert_id: str
    timestamp: str
    level: AlertLevel
    title: str
    description: str
    signals: List[RiskSignal]
    interventions: List[str]
    escalation_path: str


class RiskEarlyWarningSystem:
    """
    合伙人风险早期预警系统
    基于10个案例提炼的风险信号库
    """
    
    def __init__(self):
        self.signal_database = self._build_signal_database()
    
    def _build_signal_database(self) -> List[RiskSignal]:
        """构建风险信号数据库（基于案例库提炼）"""
        return [
            # ===== 匹配期风险信号 =====
            RiskSignal(
                signal_type="价值观差异",
                description="核心价值观存在显著分歧",
                severity=AlertLevel.RED,
                stage="matching",
                indicators=[
                    "对商业伦理理解不同",
                    "长期目标不一致",
                    "对成功的定义不同",
                    "风险偏好差异大"
                ],
                suggested_action="立即进行深入对话，确认价值观契合度；如差异显著，建议终止合作"
            ),
            RiskSignal(
                signal_type="承诺不确定",
                description="对全职投入的时间表不明确",
                severity=AlertLevel.ORANGE,
                stage="matching",
                indicators=[
                    "希望保留现有职位",
                    "all-in时间表模糊",
                    "对退出条件敏感",
                    "家庭支持度不确定"
                ],
                suggested_action="明确all-in时间表，设定里程碑；如3个月内无法全职，重新评估"
            ),
            RiskSignal(
                signal_type="蜜月期过短",
                description="相识后迅速确定合作，缺乏充分了解",
                severity=AlertLevel.YELLOW,
                stage="matching",
                indicators=[
                    "认识2周内确定合伙",
                    "未共同经历过压力场景",
                    "未验证过冲突处理能力",
                    "背景调查不充分"
                ],
                suggested_action="延长磨合期，增加压力测试场景，验证冲突处理能力"
            ),
            
            # ===== 磨合期风险信号 =====
            RiskSignal(
                signal_type="沟通效率低下",
                description="信息传递不畅，决策缓慢",
                severity=AlertLevel.ORANGE,
                stage="dating",
                indicators=[
                    "重要信息未及时同步",
                    "会议效率低，议而不决",
                    "邮件/消息回复延迟",
                    "误解频繁发生"
                ],
                suggested_action="建立定期沟通机制，明确信息同步规范，引入沟通工具"
            ),
            RiskSignal(
                signal_type="决策权争夺",
                description="对关键决策权限存在分歧",
                severity=AlertLevel.ORANGE,
                stage="dating",
                indicators=[
                    "技术决策权争议",
                    "人事决策权争议",
                    "财务决策权争议",
                    "战略方向争议"
                ],
                suggested_action="明确决策权限矩阵，建立决策流程，设立否决权边界"
            ),
            RiskSignal(
                signal_type="资源投入不对等",
                description="双方时间、精力、资金投入不均衡",
                severity=AlertLevel.YELLOW,
                stage="dating",
                indicators=[
                    "一方兼职一方全职",
                    "资金投入差距大",
                    "精力投入明显不均",
                    "一方仍有其他项目"
                ],
                suggested_action="量化投入差异，设定补齐时间表；如无法对齐，调整股权比例"
            ),
            
            # ===== 承诺期风险信号 =====
            RiskSignal(
                signal_type="战略方向分歧",
                description="对公司发展方向存在根本分歧",
                severity=AlertLevel.RED,
                stage="commitment",
                indicators=[
                    "产品路线争议",
                    "市场选择分歧",
                    "技术路线争议",
                    "商业模式分歧"
                ],
                suggested_action="引入第三方顾问，进行战略工作坊；如无法统一，考虑分道扬镳"
            ),
            RiskSignal(
                signal_type="利益分配矛盾",
                description="股权、薪酬、奖金分配引发不满",
                severity=AlertLevel.ORANGE,
                stage="commitment",
                indicators=[
                    "股权比例争议",
                    "薪酬水平不满",
                    "奖金分配争议",
                    "期权兑现争议"
                ],
                suggested_action="重新审视利益分配方案，引入独立估值，必要时调整"
            ),
            RiskSignal(
                signal_type="信任危机",
                description="一方对另一方的诚信产生怀疑",
                severity=AlertLevel.RED,
                stage="commitment",
                indicators=[
                    "隐瞒重要信息",
                    "承诺不兑现",
                    "私下接触竞争对手",
                    "财务不透明"
                ],
                suggested_action="立即进行深度沟通，必要时引入调解人；如信任无法修复，考虑退出"
            ),
            
            # ===== 运营期风险信号 =====
            RiskSignal(
                signal_type="成长速度脱节",
                description="一方成长快，另一方跟不上",
                severity=AlertLevel.YELLOW,
                stage="operation",
                indicators=[
                    "能力差距拉大",
                    "责任分配失衡",
                    "话语权变化",
                    "心理落差明显"
                ],
                suggested_action="重新分工，提供培训机会；如差距持续扩大，考虑角色调整"
            ),
            RiskSignal(
                signal_type="退出机制触发",
                description="触发预设的退出条件",
                severity=AlertLevel.BLACK,
                stage="operation",
                indicators=[
                    "连续12个月无法达成一致",
                    "重大违约行为",
                    "核心目标连续未达成",
                    "一方明确提出退出"
                ],
                suggested_action="启动退出流程，按协议执行，保护各方合法权益"
            )
        ]
    
    def scan(self, stage: str, observations: List[str]) -> List[Alert]:
        """
        扫描风险信号
        
        Args:
            stage: 当前阶段 (matching/dating/commitment/operation)
            observations: 观察到的现象列表
        
        Returns:
            预警列表
        """
        alerts = []
        matched_signals = []
        
        # 匹配当前阶段的信号
        stage_signals = [s for s in self.signal_database if s.stage == stage]
        
        for signal in stage_signals:
            # 检查观察是否匹配信号指标
            match_count = 0
            for indicator in signal.indicators:
                if any(indicator.lower() in obs.lower() or obs.lower() in indicator.lower() 
                       for obs in observations):
                    match_count += 1
            
            # 匹配度超过50%触发预警
            if match_count >= len(signal.indicators) * 0.5:
                matched_signals.append(signal)
        
        # 按严重程度分组生成预警
        if matched_signals:
            alert = self._generate_alert(stage, matched_signals)
            alerts.append(alert)
        
        return alerts
    
    def _generate_alert(self, stage: str, signals: List[RiskSignal]) -> Alert:
        """生成预警"""
        # 确定最高风险等级
        severity_order = [AlertLevel.GREEN, AlertLevel.YELLOW, 
                         AlertLevel.ORANGE, AlertLevel.RED, AlertLevel.BLACK]
        max_level = max(signals, key=lambda s: severity_order.index(s.severity)).severity
        
        # 生成干预建议
        interventions = []
        for signal in signals:
            interventions.append(f"【{signal.signal_type}】{signal.suggested_action}")
        
        # 确定升级路径
        escalation = self._get_escalation_path(max_level)
        
        return Alert(
            alert_id=f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            level=max_level,
            title=f"{stage}阶段风险预警",
            description=f"检测到{len(signals)}个风险信号，最高级别{max_level.value}",
            signals=signals,
            interventions=interventions,
            escalation_path=escalation
        )
    
    def _get_escalation_path(self, level: AlertLevel) -> str:
        """获取升级路径"""
        paths = {
            AlertLevel.GREEN: "持续监控，无需升级",
            AlertLevel.YELLOW: "增加监控频率，准备干预方案",
            AlertLevel.ORANGE: "启动干预措施，48小时内反馈",
            AlertLevel.RED: "立即启动专家会诊，24小时内决策",
            AlertLevel.BLACK: "启动退出流程，保护各方权益"
        }
        return paths.get(level, "持续监控")
    
    def generate_monitoring_dashboard(self) -> str:
        """生成监控看板"""
        dashboard = """# 合伙人风险监控看板

## 各阶段风险信号库

| 阶段 | 信号数量 | 红色警报 | 橙色警报 | 黄色警报 |
|------|----------|----------|----------|----------|
"""
        
        for stage in ["matching", "dating", "commitment", "operation"]:
            stage_signals = [s for s in self.signal_database if s.stage == stage]
            red = len([s for s in stage_signals if s.severity == AlertLevel.RED])
            orange = len([s for s in stage_signals if s.severity == AlertLevel.ORANGE])
            yellow = len([s for s in stage_signals if s.severity == AlertLevel.YELLOW])
            
            dashboard += f"| {stage} | {len(stage_signals)} | {red} | {orange} | {yellow} |\n"
        
        dashboard += """
## 监控检查清单

### 匹配期 (Matching)
- [ ] 价值观深度对话已完成
- [ ] 全职承诺时间表已明确
- [ ] 背景调查已完成
- [ ] 冲突处理能力已验证

### 磨合期 (Dating)
- [ ] 沟通机制已建立
- [ ] 决策权限已明确
- [ ] 资源投入已对齐
- [ ] 工作方式已磨合

### 承诺期 (Commitment)
- [ ] 战略方向已统一
- [ ] 利益分配方案已确认
- [ ] 信任关系已建立
- [ ] 退出机制已设计

### 运营期 (Operation)
- [ ] 成长速度基本匹配
- [ ] 责任分工动态调整
- [ ] 退出机制定期复盘

---
*基于10个案例提炼的风险信号库*
"""
        return dashboard


class PartnershipHealthMonitor:
    """合伙人关系健康度监控器"""
    
    def __init__(self):
        self.warning_system = RiskEarlyWarningSystem()
        self.check_history = []
    
    def health_check(self, stage: str, observations: List[str]) -> Dict:
        """健康度检查"""
        alerts = self.warning_system.scan(stage, observations)
        
        # 计算健康度分数
        if not alerts:
            health_score = 100
            status = "健康"
        else:
            max_severity = max(a.level for a in alerts)
            severity_penalty = {
                AlertLevel.YELLOW: 10,
                AlertLevel.ORANGE: 25,
                AlertLevel.RED: 50,
                AlertLevel.BLACK: 100
            }
            health_score = max(0, 100 - severity_penalty.get(max_severity, 0))
            status = "需关注" if max_severity == AlertLevel.YELLOW else \
                     "警告" if max_severity == AlertLevel.ORANGE else \
                     "危险" if max_severity == AlertLevel.RED else "危机"
        
        check_result = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "health_score": health_score,
            "status": status,
            "alerts": [
                {
                    "level": a.level.value,
                    "title": a.title,
                    "signals": [s.signal_type for s in a.signals],
                    "interventions": a.interventions
                }
                for a in alerts
            ],
            "next_check": "建议24小时内复查" if alerts else "建议7天后复查"
        }
        
        self.check_history.append(check_result)
        return check_result


# 便捷函数
def check_partnership_health(stage: str, observations: List[str]) -> Dict:
    """快速检查合伙人健康度"""
    monitor = PartnershipHealthMonitor()
    return monitor.health_check(stage, observations)


def get_risk_monitoring_dashboard() -> str:
    """获取风险监控看板"""
    system = RiskEarlyWarningSystem()
    return system.generate_monitoring_dashboard()


if __name__ == "__main__":
    # 测试
    print("=== 风险预警系统测试 ===\n")
    
    # 模拟一个磨合期的观察
    observations = [
        "重要信息未及时同步",
        "会议效率低，经常议而不决",
        "一方还在兼职，另一方已经全职"
    ]
    
    result = check_partnership_health("dating", observations)
    
    print(f"健康度评分: {result['health_score']}/100")
    print(f"状态: {result['status']}")
    print(f"\n预警信息:")
    for alert in result['alerts']:
        print(f"  [{alert['level'].upper()}] {alert['title']}")
        print(f"    信号: {', '.join(alert['signals'])}")
        for intervention in alert['interventions']:
            print(f"    → {intervention}")
    
    print(f"\n{'='*50}")
    print("监控看板:")
    print(get_risk_monitoring_dashboard()[:500] + "...")
