#!/usr/bin/env python3
"""
满意解研究所 - 案例库管理系统 V1.0
案例采集 → 结构化存储 → 标签检索 → 洞察生成
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class CaseStatus(Enum):
    RAW = "raw"              # 原始采集
    PROCESSING = "processing" # 处理中
    STRUCTURED = "structured" # 已结构化
    ANALYZED = "analyzed"     # 已分析
    PUBLISHED = "published"   # 已发布

class PartnershipStage(Enum):
    """合伙人关系阶段"""
    MATCHING = "matching"         # 匹配期
    DATING = "dating"             # 磨合期（3-6月）
    COMMITMENT = "commitment"     # 承诺期（6-12月）
    OPERATION = "operation"       # 运营期（1-3年）
    EXIT = "exit"                 # 退出期

@dataclass
class PartnerProfile:
    """合伙人画像"""
    role: str                      # 角色：创始人/技术合伙人/运营合伙人
    background: str                # 背景
    strengths: List[str]           # 优势
    weaknesses: List[str]          # 劣势
    decision_style: str            # 决策风格
    values: List[str]              # 核心价值观

@dataclass
class PartnershipCase:
    """合伙人案例"""
    # 基础信息
    case_id: str
    title: str
    industry: str
    company_stage: str             # 初创期/成长期/成熟期
    partnership_stage: str
    
    # 合伙人信息
    founder: PartnerProfile
    partner: PartnerProfile
    
    # 关键事件
    meeting_story: str             # 相识故事
    conflict_events: List[Dict]    # 冲突事件
    resolution_events: List[Dict]  # 解决事件
    
    # 结果与洞察
    outcome: str                   # 成功/失败/进行中
    outcome_description: str       # 结果描述
    key_lessons: List[str]         # 关键教训
    satisficing_factors: Dict      # 满意解因素分析
    
    # 元数据
    source: str                    # 来源
    collector: str                 # 采集者
    collect_date: str
    status: str = "raw"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class CaseLibrary:
    """案例库管理器"""
    
    # 行业分类
    INDUSTRIES = [
        "硬科技/半导体",
        "硬科技/机器人",
        "硬科技/新材料",
        "硬科技/新能源",
        "硬科技/航空航天",
        "硬科技/生物医药",
        "硬科技/物联网",
        "硬科技/智能制造",
        "互联网/AI",
        "互联网/SaaS",
        "互联网/平台",
        "消费/品牌",
        "消费/零售",
        "其他"
    ]
    
    # 冲突类型
    CONFLICT_TYPES = [
        "股权分配分歧",
        "决策权争夺",
        "价值观冲突",
        "工作方式差异",
        "资源投入不对等",
        "退出机制争议",
        "战略方向分歧",
        "利益分配矛盾",
        "信任危机",
        "其他"
    ]
    
    # 满意解维度
    SATISFICING_DIMENSIONS = [
        "价值观契合度",
        "能力互补性",
        "承诺可信度",
        "沟通效率",
        "利益一致性",
        "退出可接受性",
        "成长匹配度"
    ]
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = "/root/.openclaw/workspace/data/case_library.db"
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 案例主表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                industry TEXT,
                company_stage TEXT,
                partnership_stage TEXT,
                founder_role TEXT,
                founder_background TEXT,
                partner_role TEXT,
                partner_background TEXT,
                meeting_story TEXT,
                outcome TEXT,
                outcome_description TEXT,
                key_lessons TEXT,  -- JSON数组
                satisficing_analysis TEXT,  -- JSON对象
                source TEXT,
                collector TEXT,
                collect_date TEXT,
                status TEXT DEFAULT 'raw',
                tags TEXT,  -- JSON数组
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 冲突事件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conflict_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                event_type TEXT,
                description TEXT,
                stage TEXT,
                severity INTEGER,  -- 1-5
                resolution TEXT,
                lessons TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        ''')
        
        # 标签表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                tag_name TEXT,
                tag_category TEXT,  -- industry/conflict/outcome/stage
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_industry ON cases(industry)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_outcome ON cases(outcome)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON cases(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags ON tags(tag_name)')
        
        conn.commit()
        conn.close()
    
    def add_case(self, case: PartnershipCase) -> str:
        """添加案例"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cases (
                case_id, title, industry, company_stage, partnership_stage,
                founder_role, founder_background, partner_role, partner_background,
                meeting_story, outcome, outcome_description,
                key_lessons, satisficing_analysis, source, collector, collect_date,
                status, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            case.case_id,
            case.title,
            case.industry,
            case.company_stage,
            case.partnership_stage,
            case.founder.role,
            case.founder.background,
            case.partner.role,
            case.partner.background,
            case.meeting_story,
            case.outcome,
            case.outcome_description,
            json.dumps(case.key_lessons, ensure_ascii=False),
            json.dumps(case.satisficing_factors, ensure_ascii=False),
            case.source,
            case.collector,
            case.collect_date,
            case.status,
            json.dumps(case.tags, ensure_ascii=False)
        ))
        
        # 添加冲突事件
        for event in case.conflict_events:
            cursor.execute('''
                INSERT INTO conflict_events 
                (case_id, event_type, description, stage, severity, resolution, lessons)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                case.case_id,
                event.get('type'),
                event.get('description'),
                event.get('stage'),
                event.get('severity', 3),
                event.get('resolution'),
                json.dumps(event.get('lessons', []), ensure_ascii=False)
            ))
        
        # 添加标签
        for tag in case.tags:
            cursor.execute('''
                INSERT INTO tags (case_id, tag_name, tag_category)
                VALUES (?, ?, ?)
            ''', (case.case_id, tag, self._classify_tag(tag)))
        
        conn.commit()
        conn.close()
        
        return case.case_id
    
    def _classify_tag(self, tag: str) -> str:
        """分类标签"""
        if tag in self.INDUSTRIES:
            return "industry"
        elif tag in self.CONFLICT_TYPES:
            return "conflict"
        elif tag in ["成功", "失败", "进行中"]:
            return "outcome"
        elif tag in [s.value for s in PartnershipStage]:
            return "stage"
        else:
            return "other"
    
    def search_cases(self, 
                     industry: str = None,
                     outcome: str = None,
                     tags: List[str] = None,
                     keywords: str = None,
                     limit: int = 20) -> List[Dict]:
        """搜索案例"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM cases WHERE 1=1"
        params = []
        
        if industry:
            query += " AND industry = ?"
            params.append(industry)
        
        if outcome:
            query += " AND outcome = ?"
            params.append(outcome)
        
        if keywords:
            query += " AND (title LIKE ? OR meeting_story LIKE ? OR outcome_description LIKE ?)"
            like_str = f"%{keywords}%"
            params.extend([like_str, like_str, like_str])
        
        if tags:
            # 子查询匹配标签
            tag_placeholders = ','.join('?' * len(tags))
            query += f" AND case_id IN (SELECT case_id FROM tags WHERE tag_name IN ({tag_placeholders}))"
            params.extend(tags)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        cases = []
        for row in rows:
            case = dict(row)
            # 解析JSON字段
            case['key_lessons'] = json.loads(case['key_lessons'] or '[]')
            case['satisficing_analysis'] = json.loads(case['satisficing_analysis'] or '{}')
            case['tags'] = json.loads(case['tags'] or '[]')
            cases.append(case)
        
        conn.close()
        return cases
    
    def get_case(self, case_id: str) -> Optional[Dict]:
        """获取单个案例详情"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        case = dict(row)
        case['key_lessons'] = json.loads(case['key_lessons'] or '[]')
        case['satisficing_analysis'] = json.loads(case['satisficing_analysis'] or '{}')
        case['tags'] = json.loads(case['tags'] or '[]')
        
        # 获取冲突事件
        cursor.execute("SELECT * FROM conflict_events WHERE case_id = ?", (case_id,))
        case['conflict_events'] = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return case
    
    def get_statistics(self) -> Dict:
        """获取案例库统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总数
        cursor.execute("SELECT COUNT(*) FROM cases")
        total = cursor.fetchone()[0]
        
        # 按结果统计
        cursor.execute("SELECT outcome, COUNT(*) FROM cases GROUP BY outcome")
        by_outcome = dict(cursor.fetchall())
        
        # 按行业统计
        cursor.execute("SELECT industry, COUNT(*) FROM cases GROUP BY industry")
        by_industry = dict(cursor.fetchall())
        
        # 按阶段统计
        cursor.execute("SELECT partnership_stage, COUNT(*) FROM cases GROUP BY partnership_stage")
        by_stage = dict(cursor.fetchall())
        
        # 热门标签
        cursor.execute('''
            SELECT tag_name, COUNT(*) as count 
            FROM tags 
            GROUP BY tag_name 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        top_tags = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_cases": total,
            "by_outcome": by_outcome,
            "by_industry": by_industry,
            "by_stage": by_stage,
            "top_tags": top_tags
        }
    
    def export_to_markdown(self, case_id: str, output_dir: str = None) -> str:
        """导出案例为Markdown"""
        case = self.get_case(case_id)
        if not case:
            return None
        
        if output_dir is None:
            output_dir = "/root/.openclaw/workspace/A满意哥专属文件夹/03_📚案例库/案例详情"
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        md_content = f"""# {case['title']}

## 基本信息
- **案例ID**: {case['case_id']}
- **行业**: {case['industry']}
- **公司阶段**: {case['company_stage']}
- **合伙阶段**: {case['partnership_stage']}
- **结果**: {case['outcome']}
- **来源**: {case['source']}
- **采集日期**: {case['collect_date']}

## 合伙人信息

### 创始人
- **角色**: {case['founder_role']}
- **背景**: {case['founder_background']}

### 合伙人
- **角色**: {case['partner_role']}
- **背景**: {case['partner_background']}

## 相识故事
{case['meeting_story']}

## 冲突事件
"""
        
        for event in case.get('conflict_events', []):
            md_content += f"""
### {event.get('event_type', '未命名冲突')}
- **阶段**: {event.get('stage', '未知')}
- **严重程度**: {event.get('severity', 3)}/5
- **描述**: {event.get('description', '无')}
- **解决方案**: {event.get('resolution', '无')}
"""
        
        md_content += f"""

## 结果
{case['outcome_description']}

## 关键教训
"""
        for lesson in case['key_lessons']:
            md_content += f"- {lesson}\n"
        
        md_content += f"""

## 满意解分析
"""
        for dim, score in case.get('satisficing_analysis', {}).items():
            md_content += f"- **{dim}**: {score}\n"
        
        md_content += f"""

## 标签
{', '.join(case['tags'])}

---
*采集者: {case['collector']} | 入库时间: {case['created_at']}*
"""
        
        output_path = Path(output_dir) / f"{case_id}.md"
        output_path.write_text(md_content, encoding='utf-8')
        
        return str(output_path)


# 便捷函数
def create_case_library() -> CaseLibrary:
    """创建案例库实例"""
    return CaseLibrary()


def add_sample_cases():
    """添加示例案例"""
    lib = CaseLibrary()
    
    # 示例案例1：成功匹配
    case1 = PartnershipCase(
        case_id="CASE-001",
        title="AI芯片初创企业：技术极客与商业老兵的成功联姻",
        industry="硬科技/半导体",
        company_stage="初创期",
        partnership_stage="operation",
        founder=PartnerProfile(
            role="CEO/技术创始人",
            background="清华电子系博士，10年AI芯片研发经验",
            strengths=["技术深度", "产品 vision", "学术资源"],
            weaknesses=["商业经验不足", "融资能力弱"],
            decision_style="理性分析型",
            values=["技术创新", "长期主义", "学术诚信"]
        ),
        partner=PartnerProfile(
            role="COO/运营合伙人",
            background="华为15年，芯片产品线总监，MBA",
            strengths=["供应链管理", "商业运营", "团队管理"],
            weaknesses=["技术细节理解有限"],
            decision_style="数据驱动型",
            values=["结果导向", "客户第一", "高效执行"]
        ),
        meeting_story="通过共同的校友介绍相识。初次见面讨论了4小时，从技术路线到商业模式高度契合。",
        conflict_events=[
            {
                "type": "股权分配分歧",
                "stage": "dating",
                "severity": 4,
                "description": "初期对股权比例有不同看法",
                "resolution": "引入第三方顾问，按贡献和预期价值重新设计",
                "lessons": ["早期明确股权设计", "引入专业顾问"]
            }
        ],
        resolution_events=[],
        outcome="成功",
        outcome_description="公司成立3年，完成B轮融资，估值10亿。两人合作默契，分工明确。",
        key_lessons=[
            "能力互补比背景相似更重要",
            "早期冲突是磨合的必经过程",
            "第三方顾问能有效化解僵局",
            "价值观一致是长期合作基础"
        ],
        satisficing_factors={
            "价值观契合度": 9,
            "能力互补性": 9,
            "承诺可信度": 8,
            "沟通效率": 8,
            "利益一致性": 7,
            "退出可接受性": 7,
            "成长匹配度": 8
        },
        source="行业访谈",
        collector="满意妞",
        collect_date="2026-03-15",
        status="published",
        tags=["硬科技/半导体", "成功", "技术+商业", "股权分配分歧", "operation"]
    )
    
    lib.add_case(case1)
    print(f"✅ 案例 {case1.case_id} 已入库")
    
    return lib


if __name__ == "__main__":
    # 初始化并添加示例
    print("=== 案例库初始化 ===\n")
    lib = add_sample_cases()
    
    # 显示统计
    stats = lib.get_statistics()
    print(f"\n案例库统计:")
    print(f"  总数: {stats['total_cases']}")
    print(f"  按结果: {stats['by_outcome']}")
    
    # 搜索测试
    print(f"\n搜索测试:")
    results = lib.search_cases(industry="硬科技/半导体")
    for r in results:
        print(f"  - {r['title']} ({r['outcome']})")
    
    # 导出测试
    path = lib.export_to_markdown("CASE-001")
    print(f"\n✅ 案例已导出: {path}")
