-- 满意解研究所 CRM & PM 数据库结构
-- DuckDB Schema V1.0
-- 创建时间: 2026-03-14

-- ============================================
-- 1. 候选人表 (CRM核心)
-- ============================================
CREATE TABLE IF NOT EXISTS candidates (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    company VARCHAR,
    position VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    source VARCHAR, -- 来源: 推荐/会议/主动接触/其他
    status VARCHAR DEFAULT '初筛', -- 初筛/深度评估/决策中/签约/归档
    priority VARCHAR DEFAULT 'P2', -- P0/P1/P2/P3
    assigned_to VARCHAR, -- 分配给哪位评估官
    industry VARCHAR, -- 行业
    location VARCHAR, -- 地区
    trl_level INTEGER, -- 技术成熟度等级 1-9
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    next_action TEXT, -- 下一步行动
    next_date DATE -- 下次跟进日期
);

-- ============================================
-- 2. 沟通记录表
-- ============================================
CREATE TABLE IF NOT EXISTS communications (
    id VARCHAR PRIMARY KEY,
    candidate_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    method VARCHAR, -- 电话/视频/面谈/邮件/其他
    content TEXT NOT NULL,
    outcome VARCHAR, -- 结果: 积极/中性/消极/待观察
    next_action TEXT,
    next_date DATE,
    created_by VARCHAR, -- 记录人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

-- ============================================
-- 3. 五路图腾评估表
-- ============================================
CREATE TABLE IF NOT EXISTS assessments (
    id VARCHAR PRIMARY KEY,
    candidate_id VARCHAR NOT NULL,
    evaluator VARCHAR NOT NULL, -- 评估人
    liu_score INTEGER CHECK (liu_score BETWEEN 1 AND 10), -- 德馨
    simon_score INTEGER CHECK (simon_score BETWEEN 1 AND 10), -- 满意解
    guanyin_score INTEGER CHECK (guanyin_score BETWEEN 1 AND 10), -- 自在
    confucius_score INTEGER CHECK (confucius_score BETWEEN 1 AND 10), -- 仁爱
    huineng_score INTEGER CHECK (huineng_score BETWEEN 1 AND 10), -- 顿悟
    overall_score INTEGER, -- 综合评分
    recommendation VARCHAR, -- 建议: 强烈推荐/推荐/谨慎考虑/不推荐
    key_strengths TEXT, -- 核心优势
    key_risks TEXT, -- 主要风险
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

-- ============================================
-- 4. 评估项目表 (PM核心)
-- ============================================
CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR PRIMARY KEY,
    client_name VARCHAR NOT NULL, -- 客户名称
    client_company VARCHAR, -- 客户公司
    industry VARCHAR, -- 行业
    project_type VARCHAR, -- 项目类型: 合伙人评估/尽职调查/其他
    start_date DATE NOT NULL,
    deadline DATE,
    status VARCHAR DEFAULT '进行中', -- 未开始/进行中/已完成/暂停/取消
    progress INTEGER DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    peo_assigned VARCHAR, -- 项目进化官
    eeo_assigned VARCHAR, -- 经验萃取官
    revenue DECIMAL(10,2), -- 项目收入
    cost DECIMAL(10,2), -- 项目成本
    profit DECIMAL(10,2), -- 利润
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    notes TEXT
);

-- ============================================
-- 5. 任务表
-- ============================================
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR,
    candidate_id VARCHAR, -- 关联候选人（可选）
    title VARCHAR NOT NULL,
    description TEXT,
    assignee VARCHAR NOT NULL,
    due_date DATE,
    status VARCHAR DEFAULT '待办', -- 待办/进行中/已完成/阻塞
    priority VARCHAR DEFAULT 'P2', -- P0/P1/P2/P3
    estimated_hours INTEGER, -- 预估工时
    actual_hours INTEGER, -- 实际工时
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    blocked_reason TEXT, -- 阻塞原因
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

-- ============================================
-- 6. 专家会诊记录表
-- ============================================
CREATE TABLE IF NOT EXISTS expert_sessions (
    id VARCHAR PRIMARY KEY,
    candidate_id VARCHAR NOT NULL,
    session_date DATE NOT NULL,
    session_type VARCHAR, -- 初审/深度/决策
    experts_involved TEXT, -- 参与专家列表
    key_insights TEXT, -- 核心洞察
    decisions_made TEXT, -- 决策结论
    action_items TEXT, -- 行动项
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

-- ============================================
-- 7. 文档关联表
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR PRIMARY KEY,
    entity_type VARCHAR NOT NULL, -- candidate/project/task
    entity_id VARCHAR NOT NULL,
    doc_type VARCHAR, -- 简历/评估报告/会议纪要/合同/其他
    file_name VARCHAR,
    file_path VARCHAR,
    file_url VARCHAR, -- 飞书/Notion链接
    created_by VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 创建常用视图
-- ============================================

-- 候选人全景视图
CREATE OR REPLACE VIEW v_candidate_full AS
SELECT 
    c.*,
    COUNT(DISTINCT comm.id) as comm_count,
    COUNT(DISTINCT a.id) as assessment_count,
    AVG(a.overall_score) as avg_score,
    MAX(comm.date) as last_contact_date
FROM candidates c
LEFT JOIN communications comm ON c.id = comm.candidate_id
LEFT JOIN assessments a ON c.id = a.candidate_id
GROUP BY c.id;

-- 项目进度视图
CREATE OR REPLACE VIEW v_project_status AS
SELECT 
    p.*,
    COUNT(DISTINCT t.id) as total_tasks,
    COUNT(DISTINCT CASE WHEN t.status = '已完成' THEN t.id END) as completed_tasks,
    COUNT(DISTINCT CASE WHEN t.status = '阻塞' THEN t.id END) as blocked_tasks,
    COUNT(DISTINCT c.id) as candidate_count
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
LEFT JOIN candidates c ON c.id IN (
    SELECT candidate_id FROM tasks WHERE project_id = p.id
)
GROUP BY p.id;

-- 今日待办视图
CREATE OR REPLACE VIEW v_today_tasks AS
SELECT 
    t.*,
    p.client_name as project_name,
    c.name as candidate_name
FROM tasks t
LEFT JOIN projects p ON t.project_id = p.id
LEFT JOIN candidates c ON t.candidate_id = c.id
WHERE t.due_date = CURRENT_DATE
   OR (t.status = '阻塞' AND t.blocked_reason IS NOT NULL)
ORDER BY t.priority, t.due_date;

-- ============================================
-- 插入示例数据（可选）
-- ============================================

-- 示例候选人
INSERT INTO candidates (id, name, company, position, source, status, priority, assigned_to, industry)
VALUES 
('C001', '张三', '硬科技初创A', 'CEO', '会议推荐', '初筛', 'P0', 'Egbertie', 'AI芯片'),
('C002', '李四', '智能硬件B', 'CTO', '主动接触', '深度评估', 'P1', 'PEO-1', '机器人')
ON CONFLICT DO NOTHING;

-- 示例项目
INSERT INTO projects (id, client_name, industry, start_date, deadline, status, peo_assigned, eeo_assigned)
VALUES 
('P001', '硬科技初创A', 'AI芯片', '2026-03-01', '2026-04-01', '进行中', 'Egbertie', 'EEO-1'),
('P002', '智能硬件B', '机器人', '2026-03-10', '2026-04-15', '进行中', 'PEO-2', 'EEO-2')
ON CONFLICT DO NOTHING;

-- 示例任务
INSERT INTO tasks (id, project_id, candidate_id, title, assignee, due_date, priority, status)
VALUES 
('T001', 'P001', 'C001', '完成五路图腾评估', 'Egbertie', '2026-03-15', 'P0', '进行中'),
('T002', 'P001', 'C001', '安排专家会诊', 'EEO-1', '2026-03-20', 'P1', '待办')
ON CONFLICT DO NOTHING;

-- ============================================
-- 常用查询模板
-- ============================================

-- 查询1: 按状态统计候选人
-- SELECT status, COUNT(*) FROM candidates GROUP BY status;

-- 查询2: 本周待办任务
-- SELECT * FROM v_today_tasks WHERE due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL 7 DAYS;

-- 查询3: 高分候选人（综合评分>8）
-- SELECT * FROM v_candidate_full WHERE avg_score > 8;

-- 查询4: 阻塞任务清单
-- SELECT * FROM tasks WHERE status = '阻塞';

-- 查询5: 项目收入统计（按月）
-- SELECT DATE_TRUNC('month', completed_at) as month, SUM(revenue) FROM projects WHERE status = '已完成' GROUP BY 1;
