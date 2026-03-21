# 决策基因体检 - 技术实现方案

## 一、技术架构总览

```
系统架构图

┌─────────────────────────────────────────────────────────────────────────────┐
│                              接入层                                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │   CDN        │ │  WAF         │ │  API Gateway │ │  Load Balancer│        │
│  │  (静态资源)   │ │  (安全防护)   │ │  (路由/限流)  │ │  (负载均衡)   │        │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘        │
├─────────────────────────────────────────────────────────────────────────────┤
│                              应用层                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      微服务集群                                        │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ 测评服务  │ │ 报告服务  │ │ AI服务    │ │ 用户服务  │ │ 支付服务  │  │   │
│  │  │ (Go)     │ │ (Python) │ │ (Python) │ │ (Go)     │ │ (Go)     │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ 专家服务  │ │ 社区服务  │ │ 追踪服务  │ │ 通知服务  │ │ 分析服务  │  │   │
│  │  │ (Node)   │ │ (Node)   │ │ (Go)     │ │ (Go)     │ │ (Python) │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                              数据层                                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │  PostgreSQL  │ │  Redis       │ │  Elasticsearch│ │  ClickHouse  │        │
│  │  (主数据库)   │ │  (缓存)      │ │  (搜索引擎)   │ │  (分析数据库) │        │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                         │
│  │  MinIO       │ │  Kafka       │ │  Vector DB   │                         │
│  │  (对象存储)   │ │  (消息队列)   │ │  (向量数据库) │                         │
│  └──────────────┘ └──────────────┘ └──────────────┘                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                              AI/ML层                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │  LLM服务     │ │  评分模型     │ │  推荐模型     │ │  预测模型     │        │
│  │  (Claude/GPT)│ │  (Python)    │ │  (Python)    │ │  (Python)    │        │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 二、核心技术选型

### 2.1 后端技术栈

| 组件 | 选型 | 版本 | 说明 |
|-----|------|------|------|
| 主服务框架 | Go (Gin) | 1.22+ | 高性能，测评/用户/支付服务 |
| AI服务框架 | Python (FastAPI) | 0.100+ | 报告生成、模型推理 |
| 社区服务 | Node.js (NestJS) | 10+ | 专家/社区/追踪服务 |
| 数据库 | PostgreSQL | 15+ | 主数据库，JSONB支持 |
| 缓存 | Redis | 7+ | 会话、缓存、限流 |
| 消息队列 | Kafka | 3.6+ | 事件流、异步处理 |
| 搜索引擎 | Elasticsearch | 8+ | 案例/专家搜索 |
| 对象存储 | MinIO | latest | 报告PDF、头像 |
| 向量数据库 | Pinecone/Milvus | - | 案例匹配、语义搜索 |

### 2.2 前端技术栈

| 组件 | 选型 | 版本 | 说明 |
|-----|------|------|------|
| Web框架 | React | 18+ | 主应用 |
| 状态管理 | Zustand | 4+ | 轻量状态管理 |
| UI组件 | Ant Design | 5+ | 企业级组件库 |
| 可视化 | ECharts / D3.js | 5+ | 雷达图、对比图 |
| 移动端 | React Native | 0.73+ | 跨平台App |
| 小程序 | Taro | 3.6+ | 微信小程序 |
| VR | Unity / WebXR | - | VR场景 |

### 2.3 AI/ML技术栈

| 组件 | 选型 | 说明 |
|-----|------|------|
| LLM API | Claude 3.5 Sonnet / GPT-4 | AI解读、对话 |
| 嵌入模型 | text-embedding-3-large | 文本向量化 |
| 评分算法 | scikit-learn / XGBoost | 维度评分计算 |
| 推荐系统 | LightFM / Surprise | 专家/案例推荐 |
| 预测模型 | PyTorch | 决策质量预测 |

## 三、核心模块实现

### 3.1 测评引擎

#### 3.1.1 题目管理系统

```python
# 题库数据模型
class Question(BaseModel):
    question_id: str
    type: QuestionType  # scenario | cognitive | trap | consistency | style
    dimension: Dimension  # 8维度之一
    difficulty: int  # 1-5
    
    # 题目内容
    content: str
    context: Optional[str]  # 情境描述
    
    # 选项
    options: List[Option]
    
    # 计分规则
    scoring_rule: ScoringRule
    
    # 陷阱题标记
    is_trap: bool
    trap_indicator: Optional[str]  # 陷阱选项标识
    
    # 一致性检验配对
    consistency_pair: Optional[str]  # 配对题目ID

class Option(BaseModel):
    option_id: str
    text: str
    score: int  # 原始分
    weight: float = 1.0
```

#### 3.1.2 反应时采集

```javascript
// 前端反应时采集
class ReactionTimeCollector {
  constructor() {
    this.timings = {};
    this.startTime = null;
  }
  
  startQuestion(questionId) {
    this.startTime = performance.now();
    this.timings[questionId] = {
      firstInteraction: null,
      decisionTime: null,
      optionHoverTimes: {},
      changeCount: 0
    };
    
    // 监听首次交互
    document.addEventListener('mousemove', this.recordFirstInteraction);
    document.addEventListener('click', this.recordFirstInteraction);
  }
  
  recordFirstInteraction = () => {
    if (!this.timings[this.currentQuestion].firstInteraction) {
      this.timings[this.currentQuestion].firstInteraction = 
        performance.now() - this.startTime;
    }
  }
  
  recordOptionHover(optionId) {
    const now = performance.now();
    if (!this.timings[this.currentQuestion].optionHoverTimes[optionId]) {
      this.timings[this.currentQuestion].optionHoverTimes[optionId] = 0;
    }
    // 累加停留时间
  }
  
  submitAnswer(questionId, optionId) {
    this.timings[questionId].decisionTime = performance.now() - this.startTime;
    return this.timings[questionId];
  }
}
```

#### 3.1.3 评分引擎

```python
class ScoringEngine:
    def calculate_scores(self, answers: List[Answer]) -> DimensionScores:
        """
        计算8维度得分
        """
        scores = {}
        
        for dimension in Dimension:
            # 获取该维度所有题目
            dimension_questions = [
                a for a in answers 
                if a.question.dimension == dimension
            ]
            
            # 计算原始分
            raw_score = sum(
                a.option.score * a.question.scoring_rule.weight
                for a in dimension_questions
            )
            
            # 转换为标准分（0-100）
            normalized_score = self.normalize(
                raw_score, 
                dimension.min_raw_score,
                dimension.max_raw_score
            )
            
            # 反应时调整（可选）
            if dimension in REACTION_TIME_DIMENSIONS:
                rt_adjustment = self.calculate_rt_adjustment(
                    dimension_questions
                )
                normalized_score += rt_adjustment
            
            scores[dimension] = Score(
                raw=raw_score,
                normalized=normalized_score,
                percentile=self.lookup_percentile(dimension, normalized_score)
            )
        
        return scores
    
    def calculate_rt_adjustment(self, answers: List[Answer]) -> float:
        """
        基于反应时调整得分
        快速且准确 = +bonus
        快速但错误 = -penalty
        """
        # 实现逻辑...
        pass
```

### 3.2 报告生成引擎

#### 3.2.1 动态内容组装

```python
class ReportAssembler:
    def __init__(self):
        self.content_blocks = load_content_blocks()
        self.rules_engine = RulesEngine()
    
    def assemble_report(self, user_profile: UserProfile) -> Report:
        """
        根据用户画像动态组装报告
        """
        report = Report()
        
        # 1. 基础信息
        report.basic_info = self.generate_basic_info(user_profile)
        
        # 2. 维度解析（根据得分动态选择内容块）
        for dimension, score in user_profile.dimension_scores.items():
            content_block = self.select_content_block(
                dimension=dimension,
                score=score,
                user_profile=user_profile
            )
            report.dimension_analyses.append(content_block)
        
        # 3. 匹配案例
        report.case_studies = self.match_cases(user_profile)
        
        # 4. 对比分析
        report.comparisons = self.generate_comparisons(user_profile)
        
        # 5. AI洞察（异步生成）
        report.ai_insights = self.generate_ai_insights(user_profile)
        
        return report
    
    def select_content_block(self, dimension, score, user_profile) -> ContentBlock:
        """
        根据得分选择最合适的内容块
        """
        # 高分风格
        if score > 75:
            return self.content_blocks[dimension]['high'].select(
                industry=user_profile.industry,
                style=user_profile.cognitive_style
            )
        # 低分风格
        elif score < 40:
            return self.content_blocks[dimension]['low'].select(
                industry=user_profile.industry
            )
        # 中分
        else:
            return self.content_blocks[dimension]['medium']
```

#### 3.2.2 AI解读生成

```python
class AIInsightGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    def generate_insights(self, user_profile: UserProfile) -> AIInsights:
        """
        生成AI个性化解读
        """
        prompt = self.build_prompt(user_profile)
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.7,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # 解析并结构化输出
        insights = self.parse_response(response.content[0].text)
        
        return insights
    
    def build_prompt(self, user_profile: UserProfile) -> str:
        return f"""
        请为以下创业者生成决策基因解读：
        
        ## 用户画像
        - 行业：{user_profile.industry}
        - 阶段：{user_profile.stage}
        - 认知风格：{user_profile.cognitive_style}
        
        ## 维度得分
        {self.format_dimension_scores(user_profile.dimension_scores)}
        
        ## 输出要求
        1. 综合洞察（200字）
        2. 核心优势（2-3点）
        3. 关注领域（2-3点）
        4. 具体行动建议（3条）
        5. 风险提示（1-2条）
        
        请使用专业但易懂的语言，避免过度学术化。
        """
```

### 3.3 推荐系统

#### 3.3.1 专家匹配

```python
class ExpertMatchingEngine:
    def __init__(self):
        self.expert_vectors = self.load_expert_vectors()
    
    def match_experts(self, user_profile: UserProfile, top_k=3) -> List[ExpertMatch]:
        """
        基于向量相似度匹配专家
        """
        # 将用户画像转为向量
        user_vector = self.vectorize_user(user_profile)
        
        # 计算与所有专家的相似度
        similarities = []
        for expert_id, expert_vector in self.expert_vectors.items():
            sim = cosine_similarity(user_vector, expert_vector)
            similarities.append((expert_id, sim))
        
        # 排序并返回Top K
        top_experts = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
        
        return [
            ExpertMatch(
                expert=self.get_expert(expert_id),
                score=sim,
                reasoning=self.generate_reasoning(user_profile, expert_id)
            )
            for expert_id, sim in top_experts
        ]
    
    def vectorize_user(self, user_profile: UserProfile) -> np.ndarray:
        """
        将用户画像转为向量
        """
        features = [
            # 8维度得分
            user_profile.dimension_scores['risk_propensity'].normalized / 100,
            user_profile.dimension_scores['information_processing'].normalized / 100,
            # ... 其他维度
            
            # 行业编码
            self.encode_industry(user_profile.industry),
            
            # 阶段编码
            self.encode_stage(user_profile.stage),
        ]
        
        return np.array(features)
```

### 3.4 数据存储方案

#### 3.4.1 数据库Schema

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(100),
    avatar_url TEXT,
    industry VARCHAR(50),
    stage VARCHAR(50),
    company_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 测评会话表
CREATE TABLE assessment_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    assessment_type VARCHAR(20),  -- basic | professional | enterprise
    status VARCHAR(20),  -- created | in_progress | completed | abandoned
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_duration_seconds INTEGER,
    data_quality_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 答案表
CREATE TABLE answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES assessment_sessions(id),
    question_id VARCHAR(50),
    option_id VARCHAR(10),
    reaction_time_ms INTEGER,
    first_interaction_ms INTEGER,
    mouse_trail JSONB,  -- 鼠标轨迹数据
    submitted_at TIMESTAMP
);

-- 报告表
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES assessment_sessions(id),
    user_id UUID REFERENCES users(id),
    report_type VARCHAR(20),
    dimension_scores JSONB,  -- 8维度得分
    cognitive_style VARCHAR(50),
    ai_insights JSONB,
    generated_at TIMESTAMP,
    access_token VARCHAR(100) UNIQUE,  -- 分享token
    expires_at TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_answers_session ON answers(session_id);
CREATE INDEX idx_reports_user ON reports(user_id);
CREATE INDEX idx_reports_token ON reports(access_token);
```

#### 3.4.2 缓存策略

```python
# Redis缓存键设计
CACHE_KEYS = {
    # 会话缓存（临时，2小时）
    'session': 'session:{session_id}',
    
    # 报告缓存（长期，30天）
    'report': 'report:{report_id}',
    
    # 常模数据（长期，7天）
    'norm': 'norm:{industry}:{stage}:{dimension}',
    
    # 用户配额（短期，实时）
    'quota': 'quota:{user_id}:{service}',
    
    # AI对话缓存（短期，1小时）
    'chat': 'chat:{chat_session_id}',
    
    # 限流计数（短期，1分钟）
    'rate_limit': 'ratelimit:{client_id}:{endpoint}'
}
```

## 四、安全设计

### 4.1 数据安全

| 安全措施 | 实现方式 |
|---------|---------|
| 传输加密 | TLS 1.3 |
| 存储加密 | AES-256-GCM |
| 敏感数据脱敏 | 手机号/邮箱加密存储 |
| 数据库访问控制 | 最小权限原则，行级安全 |
| 审计日志 | 所有敏感操作记录 |

### 4.2 接口安全

| 安全措施 | 实现方式 |
|---------|---------|
| 认证 | JWT Token，有效期2小时 |
| 刷新机制 | Refresh Token，有效期30天 |
| 限流 | 100请求/分钟/用户 |
| 防重放 | 请求签名+时间戳校验 |
| CORS | 白名单域名 |

### 4.3 隐私合规

- GDPR/CCPA合规
- 数据最小化原则
- 用户数据导出/删除
- 明确的数据使用授权

## 五、性能优化

### 5.1 报告生成优化

```
报告生成性能目标：

┌─────────────────────────────────────────────────────────────┐
│  基础报告（免费版）     │  < 1秒   │  同步生成             │
│  专业报告              │  < 3秒   │  异步生成+流式展示     │
│  尊享报告              │  < 10秒  │  异步生成+通知         │
└─────────────────────────────────────────────────────────────┘

优化策略：
1. 预计算常模百分位
2. 内容块缓存
3. AI解读异步生成
4. 流式输出（SSE）
```

### 5.2 数据库优化

- 读写分离
- 分库分表（按用户ID哈希）
- 热点数据缓存
- 慢查询监控

## 六、部署架构

```
生产环境部署

┌─────────────────────────────────────────────────────────────┐
│                      Kubernetes集群                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Namespace: production                               │    │
│  │                                                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │  API Pods   │  │  AI Pods    │  │  Worker Pods│  │    │
│  │  │  x5         │  │  x3         │  │  x2         │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  │                                                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │  Ingress    │  │  HPA        │  │  Monitoring │  │    │
│  │  │  (Nginx)    │  │  (自动扩缩容) │  │  (Prometheus│  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

云服务：
- 阿里云/腾讯云：ECS + RDS + Redis + OSS
- 或AWS：EKS + RDS + ElastiCache + S3
```

## 七、监控与运维

### 7.1 监控指标

| 类别 | 指标 | 告警阈值 |
|-----|------|---------|
| 可用性 | 服务可用率 | <99.9% |
| 性能 | API响应时间P99 | >500ms |
| 性能 | 报告生成时间 | >10s |
| 业务 | 测评完成率 | <80% |
| 错误 | 5xx错误率 | >0.1% |

### 7.2 日志规范

```json
{
  "timestamp": "2026-03-20T10:32:15Z",
  "level": "INFO",
  "service": "assessment-service",
  "trace_id": "trace_abc123",
  "span_id": "span_def456",
  "user_id": "user_12345",
  "action": "submit_answer",
  "duration_ms": 45,
  "status": "success",
  "metadata": {
    "session_id": "sess_abc123",
    "question_id": "q_025"
  }
}
```

---

*文档版本：v1.0*
*完成日期：2026-03-20*
