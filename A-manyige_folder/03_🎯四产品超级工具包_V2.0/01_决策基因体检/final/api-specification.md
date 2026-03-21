# 决策基因体检 - 产品接口规范

## 一、接口架构概览

```
接口架构图

外部系统                      决策基因体检平台                      内部服务
┌──────────┐                ┌──────────────────┐                ┌──────────┐
│ 产品2    │◄──────────────►│                  │◄──────────────►│ 测评引擎  │
│ 诊断系统 │   用户数据传递  │   API Gateway    │                └──────────┘
└──────────┘                │                  │                ┌──────────┐
                            │   ┌──────────┐   │◄──────────────►│ 报告引擎  │
┌──────────┐                │   │ 认证层    │   │                └──────────┘
│ 产品3    │◄──────────────►│   │ 限流层    │   │                ┌──────────┐
│ 教练服务 │   专家对接      │   │ 路由层    │   │◄──────────────►│ AI服务    │
└──────────┘                │   └──────────┘   │                └──────────┘
                            │                  │                ┌──────────┐
┌──────────┐                │   ┌──────────┐   │◄──────────────►│ 常模服务  │
│ 产品4    │◄──────────────►│   │ REST API │   │                └──────────┘
│ SaaS工具 │   数据同步      │   │ WebSocket│   │                ┌──────────┐
└──────────┘                │   │ Webhook  │   │◄──────────────►│ 用户系统  │
                            │   └──────────┘   │                └──────────┘
┌──────────┐                │                  │                ┌──────────┐
│ 第三方   │◄──────────────►│   ┌──────────┐   │◄──────────────►│ 支付系统  │
│ 合作伙伴 │   API调用       │   │ SDK      │   │                └──────────┘
└──────────┘                │   │ 嵌入组件  │   │
                            │   └──────────┘   │
                            └──────────────────┘
```

## 二、核心接口定义

### 2.1 测评相关接口

#### 2.1.1 创建测评会话

```http
POST /api/v1/assessment/create
Content-Type: application/json
Authorization: Bearer {access_token}

请求体：
{
  "user_id": "user_12345",
  "assessment_type": "professional",  // basic | professional | enterprise
  "source": "web",  // web | app | miniapp | vr
  "metadata": {
    "industry": "saas",
    "stage": "series_a",
    "team_size": 15
  }
}

响应：
{
  "code": 200,
  "data": {
    "session_id": "sess_abc123",
    "assessment_type": "professional",
    "status": "created",
    "questions": [
      {
        "question_id": "q_001",
        "type": "scenario",
        "dimension": "risk_propensity",
        "content": "情境描述...",
        "options": [
          {"option_id": "A", "text": "选项A", "score": 5},
          {"option_id": "B", "text": "选项B", "score": 3}
        ],
        "has_time_limit": false
      }
    ],
    "total_questions": 58,
    "estimated_duration": "25-35分钟",
    "created_at": "2026-03-20T10:00:00Z",
    "expires_at": "2026-03-20T12:00:00Z"
  }
}
```

#### 2.1.2 提交答案

```http
POST /api/v1/assessment/submit
Content-Type: application/json
Authorization: Bearer {access_token}

请求体：
{
  "session_id": "sess_abc123",
  "answers": [
    {
      "question_id": "q_001",
      "option_id": "A",
      "reaction_time_ms": 3450,
      "mouse_trail": [...],  // 可选，鼠标轨迹
      "submitted_at": "2026-03-20T10:01:23Z"
    }
  ],
  "metadata": {
    "device_type": "desktop",
    "browser": "Chrome 120",
    "screen_resolution": "1920x1080"
  }
}

响应：
{
  "code": 200,
  "data": {
    "session_id": "sess_abc123",
    "answered_count": 25,
    "remaining_count": 33,
    "progress_percentage": 43,
    "estimated_remaining_minutes": 15,
    "next_question": {
      "question_id": "q_026",
      // ... 下一题详情
    }
  }
}
```

#### 2.1.3 完成测评

```http
POST /api/v1/assessment/complete
Content-Type: application/json
Authorization: Bearer {access_token}

请求体：
{
  "session_id": "sess_abc123",
  "completion_method": "normal"  // normal | timeout | user_abort
}

响应：
{
  "code": 200,
  "data": {
    "session_id": "sess_abc123",
    "status": "completed",
    "completion_time": "2026-03-20T10:32:15Z",
    "total_duration_seconds": 1935,
    "report_id": "rep_xyz789",
    "report_url": "https://app.decisiongene.com/report/xyz789",
    "data_quality_score": 92,
    "preliminary_scores": {
      "risk_propensity": 78,
      "information_processing": 65,
      // ... 其他维度预览
    }
  }
}
```

### 2.2 报告相关接口

#### 2.2.1 获取报告

```http
GET /api/v1/report/{report_id}
Authorization: Bearer {access_token}

响应：
{
  "code": 200,
  "data": {
    "report_id": "rep_xyz789",
    "user_id": "user_12345",
    "report_type": "professional",
    "generated_at": "2026-03-20T10:32:20Z",
    "report_status": "ready",
    
    // 8维度得分
    "dimension_scores": {
      "risk_propensity": {
        "score": 78,
        "percentile": 82,
        "level": "high",  // low | medium | high
        "description": "高风险偏好型..."
      },
      "information_processing": {
        "score": 65,
        "percentile": 55,
        "level": "medium",
        "description": "..."
      }
      // ... 其他6个维度
    },
    
    // 认知风格
    "cognitive_style": {
      "primary": "intuitive-efficient",
      "secondary": "opportunity-driven",
      "description": "直觉高效型+机会驱动型..."
    },
    
    // 常模对比
    "norm_comparison": {
      "industry": "saas",
      "industry_percentile": 75,
      "stage": "series_a",
      "stage_percentile": 68
    },
    
    // AI解读
    "ai_insights": {
      "summary": "您的决策风格呈现出...",
      "strengths": ["机会识别能力强", "决策速度快"],
      "weaknesses": ["损失厌恶较高", "过度自信"],
      "suggestions": ["建议1", "建议2"]
    },
    
    // 匹配资源
    "matched_resources": {
      "case_studies": [
        {
          "case_id": "case_001",
          "founder": "张一鸣",
          "similarity": 0.85,
          "key_lessons": [...]
        }
      ],
      "recommended_experts": [
        {
          "expert_id": "exp_005",
          "name": "李明",
          "match_score": 92,
          "specialization": [...]
        }
      ]
    },
    
    // 报告URL
    "report_url": "https://app.decisiongene.com/report/xyz789",
    "pdf_download_url": "https://app.decisiongene.com/report/xyz789.pdf",
    "share_token": "sh_tok_abc123"
  }
}
```

#### 2.2.2 生成PDF报告

```http
POST /api/v1/report/{report_id}/pdf
Content-Type: application/json
Authorization: Bearer {access_token}

请求体：
{
  "template": "professional",  // professional | concise | enterprise
  "include_sections": ["all"],  // 或指定 ["overview", "dimensions", "ai_insights"]
  "language": "zh-CN"
}

响应：
{
  "code": 200,
  "data": {
    "pdf_url": "https://cdn.decisiongene.com/reports/xyz789_professional.pdf",
    "expires_at": "2026-04-20T10:32:20Z",
    "file_size_bytes": 2456789
  }
}
```

### 2.3 AI解读接口

#### 2.3.1 开始AI对话

```http
POST /api/v1/ai/chat/start
Content-Type: application/json
Authorization: Bearer {access_token}

请求体：
{
  "report_id": "rep_xyz789",
  "context": "initial"  // initial | follow_up | specific_topic
}

响应：
{
  "code": 200,
  "data": {
    "chat_session_id": "chat_def456",
    "report_id": "rep_xyz789",
    "remaining_quota": 10,  // 专业版10次，尊享版无限
    "welcome_message": "您好！我是您的决策基因解读助手...",
    "suggested_questions": [
      "我的风险倾向具体意味着什么？",
      "我应该如何改进我的决策方式？",
      "有没有和我风格类似的成功案例？"
    ]
  }
}
```

#### 2.3.2 发送消息

```http
POST /api/v1/ai/chat/message
Content-Type: application/json
Authorization: Bearer {access_token}

请求体：
{
  "chat_session_id": "chat_def456",
  "message": "我的风险倾向在行业内算什么水平？",
  "message_type": "text"  // text | voice
}

响应（流式）：
{
  "code": 200,
  "data": {
    "message_id": "msg_ghi789",
    "chat_session_id": "chat_def456",
    "response_type": "streaming",
    "stream_url": "wss://api.decisiongene.com/ai/stream/msg_ghi789"
  }
}

// 或通过SSE流式返回内容
```

### 2.4 产品间对接接口

#### 2.4.1 产品1→产品2：推荐诊断服务

```http
// 产品1调用，获取是否需要推荐诊断
GET /api/v1/recommendation/diagnosis
Authorization: Bearer {access_token}
Query: report_id=rep_xyz789

响应：
{
  "code": 200,
  "data": {
    "recommend": true,
    "priority": "high",  // high | medium | low
    "confidence": 0.85,
    "trigger_reasons": [
      {
        "type": "high_risk_score",
        "description": "决策风险评分72分，高于阈值",
        "weight": 0.3
      },
      {
        "type": "low_confidence",
        "description": "自信心得分35分，低于阈值", 
        "weight": 0.25
      }
    ],
    "recommended_focus_areas": [
      {
        "area": "止损决策",
        "evidence": "损失厌恶得分32分",
        "suggested_expert_type": "risk_management"
      }
    ],
    "handoff_data": {
      "token": "handoff_token_xxx",
      "expires_at": "2026-03-21T10:00:00Z",
      "data_package": {
        "assessment_summary": {...},
        "dimension_scores": {...},
        "flagged_areas": [...]
      }
    }
  }
}

// 产品2接收数据
POST https://product2.diagnosis.com/api/v1/intake/handoff
Content-Type: application/json
Authorization: Bearer {product2_token}

请求体：
{
  "handoff_token": "handoff_token_xxx",
  "source": "product1",
  "user_consent": true
}
```

#### 2.4.2 统一用户数据查询

```http
GET /api/v1/user/profile
Authorization: Bearer {access_token}

响应：
{
  "code": 200,
  "data": {
    "user_id": "user_12345",
    "profile": {
      "name": "张三",
      "industry": "saas",
      "stage": "series_a",
      "company": "某某科技"
    },
    "assessment_history": [
      {
        "report_id": "rep_xyz789",
        "completed_at": "2026-03-20T10:32:15Z",
        "dimension_scores": {...}
      }
    ],
    "service_history": {
      "product1": [...],
      "product2": [...],
      "product3": [...],
      "product4": [...]
    },
    "current_services": [
      {
        "product": "product3",
        "service_type": "1v1_coaching",
        "expert_id": "exp_005",
        "status": "active"
      }
    ]
  }
}
```

### 2.5 专家系统接口

#### 2.5.1 获取推荐专家

```http
GET /api/v1/experts/recommend
Authorization: Bearer {access_token}
Query: report_id=rep_xyz789&limit=3

响应：
{
  "code": 200,
  "data": {
    "recommendations": [
      {
        "rank": 1,
        "expert": {
          "expert_id": "exp_005",
          "name": "李明",
          "title": "资深创业教练",
          "avatar": "https://...",
          "specializations": ["战略决策", "融资决策"],
          "industries": ["saas", "tech"],
          "rating": 4.8,
          "review_count": 156
        },
        "match_analysis": {
          "total_score": 92,
          "factors": {
            "industry_match": 25,
            "stage_match": 20,
            "problem_match": 30,
            "style_complement": 15,
            "expert_quality": 2
          },
          "match_reason": "专注科技行业，擅长战略决策，可平衡您的直觉风格"
        },
        "availability": {
          "next_available": "2026-03-25T14:00:00Z",
          "slots_this_week": 3
        }
      }
    ]
  }
}
```

#### 2.5.2 预约专家

```http
POST /api/v1/experts/{expert_id}/book
Content-Type: application/json
Authorization: Bearer {access_token}

请求体：
{
  "report_id": "rep_xyz789",
  "preferred_time": "2026-03-25T14:00:00Z",
  "duration_minutes": 60,
  "topics": ["战略决策", "团队管理"],
  "notes": "希望重点讨论融资决策中的风险控制"
}

响应：
{
  "code": 200,
  "data": {
    "booking_id": "book_jkl012",
    "expert_id": "exp_005",
    "status": "confirmed",
    "scheduled_at": "2026-03-25T14:00:00Z",
    "duration_minutes": 60,
    "meeting_link": "https://meet.decisiongene.com/book_jkl012",
    "preparation_materials": {
      "report_summary": "https://...",
      "suggested_questions": [...]
    }
  }
}
```

### 2.6 社区相关接口

#### 2.6.1 匹配同类型创业者

```http
GET /api/v1/community/matches
Authorization: Bearer {access_token}
Query: match_type=similar&limit=5

响应：
{
  "code": 200,
  "data": {
    "match_type": "similar",
    "matches": [
      {
        "user_id": "user_67890",
        "nickname": "创业小A",
        "avatar": "https://...",
        "similarity_score": 88,
        "commonalities": {
          "decision_archetype": "intuitive-opportunist",
          "industry": "saas",
          "stage": "series_a"
        },
        "match_reason": "相似的决策风格，容易产生共鸣",
        "suggested_icebreakers": [
          "你们的决策风格很相似，都在机会识别上得分很高...",
          "你们都面临从0到1的阶段挑战..."
        ]
      }
    ]
  }
}
```

### 2.7 追踪系统接口

#### 2.7.1 创建追踪计划

```http
POST /api/v1/tracking/schedule
Content-Type: application/json
Authorization: Bearer {access_token}

请求体：
{
  "report_id": "rep_xyz789",
  "schedule_type": "standard",  // standard | custom
  "checkpoints": [
    {"days_after": 90, "type": "quarterly_review"},
    {"days_after": 180, "type": "half_year_assessment"},
    {"days_after": 365, "type": "annual_retest"}
  ],
  "reminder_settings": {
    "channels": ["app_push", "wechat", "email"],
    "advance_days": 3
  }
}

响应：
{
  "code": 200,
  "data": {
    "tracking_id": "track_mno345",
    "status": "active",
    "next_checkpoint": {
      "date": "2026-06-20",
      "type": "quarterly_review",
      "status": "scheduled"
    }
  }
}
```

## 三、Webhook规范

### 3.1 事件类型

| 事件 | 说明 | payload |
|-----|------|---------|
| `assessment.completed` | 测评完成 | 报告摘要+得分 |
| `report.generated` | 报告生成 | 报告ID+URL |
| `user.upgraded` | 用户升级 | 旧版本→新版本 |
| `expert.booked` | 专家预约 | 预约详情 |
| `tracking.due` | 追踪到期 | 追踪计划ID |

### 3.2 Webhook签名验证

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    """
    验证Webhook签名
    """
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

## 四、错误码定义

| 错误码 | 说明 | 处理建议 |
|-------|------|---------|
| 200 | 成功 | - |
| 400 | 请求参数错误 | 检查请求参数 |
| 401 | 未授权 | 检查token是否有效 |
| 403 | 权限不足 | 检查用户权限 |
| 404 | 资源不存在 | 检查ID是否正确 |
| 409 | 资源冲突 | 如重复提交 |
| 429 | 请求频率超限 | 降低请求频率 |
| 500 | 服务器错误 | 联系技术支持 |
| 503 | 服务暂时不可用 | 稍后重试 |

## 五、版本管理

- API版本通过URL路径标识：`/api/v1/...`
- 向后兼容保证：minor版本变更保持兼容
- 废弃通知：major版本变更提前90天通知

---

*文档版本：v1.0*
*API版本：v1.0*
*完成日期：2026-03-20*
