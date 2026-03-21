# 四产品API规范

> 产品间数据交互与系统集成接口标准

---

## 🔌 接口设计原则

### 核心原则
1. **单一数据源**：每个实体只有一个真相源
2. **最小权限**：仅传输必要的最小数据集
3. **版本控制**：API版本化，向后兼容
4. **异步优先**：长耗时操作采用异步模式
5. **幂等性**：重复调用不造成副作用

### 技术标准
- **协议**：HTTPS + RESTful
- **数据格式**：JSON
- **认证**：OAuth 2.0 + JWT
- **限流**：每分钟100次（标准），1000次（企业）
- **超时**：30秒（同步），24小时（异步回调）

---

## 📡 核心API列表

### 1. 客户档案接口

#### 获取客户决策档案
```http
GET /api/v1/customers/{customer_id}/decision-profile
Authorization: Bearer {jwt_token}
```

**响应示例**：
```json
{
  "customer_id": "cust_123456",
  "name": "张三",
  "company": "未来科技",
  "dna_profile": {
    "information": 75,
    "risk": 60,
    "time": 80,
    "interpersonal": 45,
    "stress": 70,
    "values": 85,
    "decision_type": "数据型稳健派",
    "blind_spots": [
      {
        "type": "团队协作风险",
        "risk_level": "高",
        "mitigation": "建立决策分工机制"
      }
    ]
  },
  "totem_mapping": {
    "LIU": {"value_purity": 85, "time_orientation": 80},
    "SIMON": {"rational_framework": 75},
    "GUANYIN": {"stress_management": 70},
    "CONFUCIUS": {"partner_ethics": 45},
    "HUINENG": {"limit_testing": 60}
  },
  "assessment_history": [
    {
      "product": "决策基因体检",
      "date": "2026-03-15",
      "score": 72
    }
  ],
  "updated_at": "2026-03-20T10:30:00Z"
}
```

**调用场景**：
- 产品2启动时获取客户决策基因
- 产品3查看客户历史决策模式
- 产品4生成年度仪表盘

---

### 2. 产品1 → 产品2 转化接口

#### 提交产品1结果并触发产品2推荐
```http
POST /api/v1/recommendations/diagnosis
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "customer_id": "cust_123456",
  "product1_result": {
    "assessment_id": "dna_789",
    "scores": {
      "information": 75,
      "risk": 60,
      "time": 80,
      "interpersonal": 45,
      "stress": 70,
      "values": 85
    },
    "decision_type": "数据型稳健派",
    "high_risk_blind_spots": ["团队协作风险"]
  },
  "trigger_conditions": ["high_risk_blind_spots", "partner_recruitment_plan"]
}
```

**响应示例**：
```json
{
  "recommendation_id": "rec_456",
  "recommended_products": ["product2_diagnosis"],
  "priority": "high",
  "reason": "检测到团队协作风险盲区，建议进行合伙人匹配诊断",
  "suggested_packages": [
    {
      "name": "标准版诊断",
      "price": 58000,
      "discount": 0.9,
      "final_price": 52200,
      "includes": ["双人72小时评估", "50页诊断报告", "契约建议"]
    }
  ],
  "follow_up_actions": [
    {
      "type": "advisor_call",
      "timing": "within_24h",
      "script_version": "v2.1"
    },
    {
      "type": "email_sequence",
      "sequence_id": "seq_partner_risk"
    }
  ],
  "created_at": "2026-03-20T10:30:00Z"
}
```

**回调接口**（产品2状态更新）：
```http
POST /api/v1/callbacks/product2-status
{
  "customer_id": "cust_123456",
  "product2_status": "completed",
  "pfi_score": 72,
  "risk_level": "medium",
  "next_recommended_product": "product3_coaching"
}
```

---

### 3. 产品2 → 产品3 转化接口

#### 提交PFI结果并触发陪跑推荐
```http
POST /api/v1/recommendations/coaching
Content-Type: application/json

{
  "customer_id": "cust_123456",
  "product2_result": {
    "diagnosis_id": "dia_321",
    "pfi_score": 68,
    "grade": "B",
    "risk_level": "medium",
    "dimension_scores": {
      "wulu_alignment": 75,
      "capability_complement": 80,
      "values_alignment": 60,
      "communication": 65,
      "stress_response": 70,
      "trust": 55,
      "commitment": 60
    },
    "repairable_issues": ["沟通模式", "压力响应"],
    "contract_recommendation": "控股型"
  }
}
```

**响应示例**：
```json
{
  "recommendation_id": "rec_789",
  "recommended_products": ["product3_coaching"],
  "priority": "medium",
  "reason": "匹配度良好但存在可修复的沟通和压力响应问题，建议陪跑服务",
  "suggested_packages": [
    {
      "name": "季度陪跑",
      "price": 128000,
      "focus_areas": ["沟通技巧", "冲突管理", "压力应对"],
      "includes": ["月度复盘", "24小时响应", "决策日志系统"]
    }
  ],
  "estimated_improvement": "3个月后可提升PFI评分10-15分"
}
```

---

### 4. 产品3 → 产品4 转化接口

#### 提交陪跑成果并触发年度顾问推荐
```http
POST /api/v1/recommendations/advisory
Content-Type: application/json

{
  "customer_id": "cust_123456",
  "product3_result": {
    "coaching_id": "coach_654",
    "duration_months": 6,
    "decisions_supported": 24,
    "average_quality_score": 4.2,
    "satisfaction_score": 4.8,
    "improvement_areas": ["战略决策", "团队管理"],
    "maturity_assessment": "ready_for_advisory"
  }
}
```

**响应示例**：
```json
{
  "recommendation_id": "rec_999",
  "recommended_products": ["product4_advisory"],
  "priority": "high",
  "reason": "客户决策能力显著提升，企业进入成长期，适合年度顾问服务",
  "suggested_packages": [
    {
      "name": "基础版年度顾问",
      "price": 480000,
      "includes": ["决策仪表盘", "季度董事会支持", "专家网络调用"]
    }
  ],
  "proposal_timeline": "陪跑结束前1个月启动提案"
}
```

---

### 5. 统一决策记录接口

#### 记录决策事件
```http
POST /api/v1/decisions
Content-Type: application/json

{
  "customer_id": "cust_123456",
  "decision": {
    "type": "strategic",
    "title": "B轮融资时机选择",
    "complexity": "high",
    "urgency": "high",
    "context": "产品刚完成PMF，竞品开始模仿",
    "options": [
      {
        "id": "opt_1",
        "description": "立即启动，抓住窗口期",
        "pros": ["抢占市场先机", "资金充裕"],
        "cons": ["估值可能不高", "准备时间紧"]
      },
      {
        "id": "opt_2",
        "description": "再等3个月，数据更扎实",
        "pros": ["估值更高", "准备更充分"],
        "cons": ["窗口可能关闭", "竞品抢先"]
      }
    ],
    "five_totems_calibration": {
      "LIU": 4,
      "SIMON": 5,
      "GUANYIN": 3,
      "CONFUCIUS": 4,
      "HUINENG": 4
    },
    "cognitive_biases_checked": ["锚定效应", "从众心理", "损失厌恶"],
    "final_choice": "opt_1",
    "confidence_level": 4,
    "expected_outcome": "3个月内完成B轮，估值X亿",
    "review_date": "2026-06-20"
  }
}
```

**响应示例**：
```json
{
  "decision_id": "dec_111",
  "status": "recorded",
  "estimated_quality_score": 4.3,
  "suggestions": [
    "考虑引入外部视角验证",
    "设定明确的里程碑检查点"
  ],
  "next_actions": [
    {
      "type": "review_reminder",
      "date": "2026-06-20",
      "template": "decision_review"
    }
  ]
}
```

#### 更新决策结果
```http
PUT /api/v1/decisions/{decision_id}/outcome
{
  "actual_outcome": "completed",
  "result_summary": "顺利完成B轮，估值超预期",
  "quality_score": 5,
  "lessons_learned": "抓住窗口比追求完美更重要",
  "would_do_differently": null
}
```

---

## 🔐 认证与安全

### JWT Token结构
```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "cust_123456",
    "role": "customer",
    "products": ["product1", "product2"],
    "iat": 1700000000,
    "exp": 1700086400
  }
}
```

### 权限矩阵

| 角色 | 读取自己 | 写入自己 | 读取他人 | 写入他人 | 管理 |
|------|----------|----------|----------|----------|------|
| **客户** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **顾问** | ✅ (服务中) | ✅ (服务中) | ❌ | ❌ | ❌ |
| **管理员** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **系统** | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 📊 数据同步机制

### 实时同步（WebSocket）

用于高时效性场景：
- 紧急决策请求
- 顾问在线状态
- 系统通知推送

```javascript
// WebSocket连接示例
const ws = new WebSocket('wss://api.satisficing.com/ws/v1');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'jwt_token'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'urgent_decision_request') {
    // 处理紧急决策请求
  }
};
```

### 批量同步（每日）

用于数据仓库和分析：
```http
POST /api/v1/sync/batch
{
  "sync_type": "daily",
  "tables": ["customers", "assessments", "decisions"],
  "since": "2026-03-19T00:00:00Z"
}
```

---

## 🧪 测试环境

### 沙箱环境
- **URL**：`https://sandbox-api.satisficing.com/v1`
- **数据**：隔离的测试数据
- **限制**：每分钟10次请求
- **有效期**：24小时

### 测试账号
```
测试客户：test_customer_001
测试顾问：test_advisor_001
测试管理员：test_admin_001
通用密码：Test@123456
```

---

## 📚 错误码规范

| 状态码 | 错误码 | 说明 | 处理建议 |
|--------|--------|------|----------|
| 400 | INVALID_REQUEST | 请求参数错误 | 检查参数格式 |
| 401 | UNAUTHORIZED | 认证失败 | 刷新Token |
| 403 | FORBIDDEN | 权限不足 | 联系管理员 |
| 404 | NOT_FOUND | 资源不存在 | 检查ID是否正确 |
| 429 | RATE_LIMITED | 限流 | 降低请求频率 |
| 500 | INTERNAL_ERROR | 服务器错误 | 稍后重试 |

**错误响应格式**：
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "缺少必填字段：customer_id",
    "details": {
      "field": "customer_id",
      "reason": "required"
    },
    "request_id": "req_abc123",
    "timestamp": "2026-03-20T10:30:00Z"
  }
}
```

---

## 🔄 版本管理

### 版本策略
- **URL版本**：`/api/v1/`, `/api/v2/`
- **向后兼容**：v1在v2发布后维持12个月
- **弃用通知**：提前6个月邮件通知

### 变更日志

| 版本 | 日期 | 变更内容 | 影响 |
|------|------|----------|------|
| v1.0 | 2026-03 | 初始版本 | - |
| v1.1 | 2026-06 | 新增产品3→4接口 | 新增功能 |
| v1.2 | 2026-09 | 优化决策记录API | 性能提升 |

---

## 📋 实施检查清单

### 开发阶段
- [ ] API文档编写（Swagger/OpenAPI）
- [ ] 接口Mock服务搭建
- [ ] 单元测试覆盖>80%
- [ ] 集成测试通过
- [ ] 安全审计通过

### 上线阶段
- [ ] 生产环境部署
- [ ] 监控告警配置
- [ ] 限流策略生效
- [ ] 日志收集正常
- [ ] 文档更新完成

### 运维阶段
- [ ] 每日监控检查
- [ ] 每周性能分析
- [ ] 每月安全扫描
- [ ] 每季度容量规划

---

> **关联文档**：> - 产品架构总览.md
> - 转化漏斗设计.md
> - 统一术语表.md
