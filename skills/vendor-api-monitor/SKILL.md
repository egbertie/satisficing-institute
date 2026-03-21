# Skill: vendor-api-monitor

> **版本**: 5.0.0  
> **标准**: Level 5 (生产级监控)  
> **更新**: 2026-03-21

监控厂商 API 运行状态，包括可用性、性能、错误率和配额使用情况。支持钉钉、企业微信、飞书、Notion 等平台。

---

## S1: 输入 (Input)

### 配置文件
```yaml
# config.yaml
monitors:
  - name: "feishu_drive"
    vendor: "feishu"
    endpoint: "https://open.feishu.cn/open-apis/drive/v1/metas/batch_query"
    method: "POST"
    headers:
      Authorization: "Bearer ${FEISHU_TOKEN}"
    timeout: 10
    interval: 300  # 秒
    
  - name: "wecom_media"
    vendor: "wecom"
    endpoint: "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    method: "GET"
    params:
      corpid: "${WECOM_CORPID}"
      corpsecret: "${WECOM_SECRET}"
    timeout: 10
    interval: 300

# 监控指标配置
metrics:
  availability:
    target: 99.9  # %
    check_interval: 60  # 秒
    
  performance:
    response_time_p95: 2000  # ms
    response_time_p99: 5000  # ms
    
  error_rate:
    threshold: 1.0  # %
    window: 300     # 5分钟窗口
    
  quota:
    daily_limit: 10000
    warning_threshold: 80   # %
    critical_threshold: 95  # %

# 告警阈值
alerts:
  channels:
    - type: "file"
      path: "reports/alerts.json"
    - type: "webhook"
      url: "${ALERT_WEBHOOK_URL}"
      
  rules:
    - name: "api_down"
      condition: "availability < 100"
      severity: "critical"
      cooldown: 300  # 秒
      
    - name: "slow_response"
      condition: "p95_latency > 2000"
      severity: "warning"
      cooldown: 600
      
    - name: "high_error_rate"
      condition: "error_rate > 1.0"
      severity: "critical"
      cooldown: 300
      
    - name: "quota_exhausted"
      condition: "quota_used > 95"
      severity: "warning"
      cooldown: 3600
```

### 环境变量
```bash
# 飞书
export FEISHU_APP_ID="cli_xxxxx"
export FEISHU_APP_SECRET"xxxxx"

# 企业微信
export WECOM_CORPID="wwxxxxx"
export WECOM_SECRET"xxxxx"

# 钉钉
export DINGTALK_APP_KEY"xxxxx"
export DINGTALK_APP_SECRET"xxxxx"

# Notion
export NOTION_TOKEN"secret_xxxxx"

# 告警
export ALERT_WEBHOOK_URL"https://..."
```

---

## S2: 监控维度 (Monitoring Dimensions)

### 2.1 可用性监控 (Availability)
```python
# 每分钟探测一次
probe_result = http_get(endpoint, timeout=10)
availability = (success_count / total_count) * 100

# 目标: 99.9% SLA
# 计算: (1 - 0.001) * 24 * 60 = 1438.56 分钟可用/天
# 允许停机: 1.44 分钟/天
```

### 2.2 性能监控 (Performance)
```python
metrics = {
    "response_time_ms": [],      # 原始响应时间
    "p50_latency": percentile(50),
    "p95_latency": percentile(95),
    "p99_latency": percentile(99),
    "dns_lookup_ms": [],         # DNS解析时间
    "tcp_connect_ms": [],        # TCP连接时间
    "tls_handshake_ms": [],      # TLS握手时间
    "ttfb_ms": []                # Time To First Byte
}
```

### 2.3 错误率监控 (Error Rate)
```python
error_categories = {
    "4xx": "客户端错误 (认证/参数)",
    "5xx": "服务端错误",
    "timeout": "超时",
    "network": "网络错误",
    "ssl": "证书错误"
}

error_rate = (error_count / total_requests) * 100
```

### 2.4 配额监控 (Quota)
```python
quota_tracking = {
    "vendor": "feishu",
    "daily_limit": 10000,
    "used_today": 2456,
    "remaining": 7544,
    "usage_percent": 24.56,
    "reset_time": "00:00 UTC+8",
    "projected_exhaustion": "2026-03-25"  # 预计耗尽日期
}
```

---

## S3: 输出 (Output)

### 3.1 监控报告
```json
{
  "report_type": "api_monitor",
  "generated_at": "2026-03-21T20:30:00+08:00",
  "period": "1h",
  "summary": {
    "total_checks": 60,
    "failed_checks": 0,
    "availability": "100%",
    "avg_latency": "145ms",
    "p95_latency": "289ms"
  },
  "vendors": {
    "feishu": {
      "status": "healthy",
      "availability": 100,
      "p95_latency": 156,
      "error_rate": 0,
      "quota_remaining": "75.4%"
    }
  },
  "recommendations": [
    {
      "type": "optimization",
      "priority": "medium",
      "message": "飞书 API P99 延迟偏高，建议启用连接池复用"
    }
  ]
}
```

### 3.2 异常告警
```json
{
  "alert_id": "alt_202603212030",
  "timestamp": "2026-03-21T20:30:00+08:00",
  "severity": "critical",
  "vendor": "wecom",
  "endpoint": "gettoken",
  "condition": "availability < 100",
  "current_value": "0%",
  "threshold": "99.9%",
  "message": "企业微信 gettoken API 不可达",
  "suggested_action": "检查网络连接和 corpid/corpsecret 配置"
}
```

### 3.3 优化建议
| 问题 | 建议 | 预期效果 |
|------|------|----------|
| P95延迟>2s | 启用连接池，复用 TCP 连接 | 延迟降低 40-60% |
| 偶发 429 | 实现指数退避重试 | 减少 90% 限流错误 |
| 配额消耗快 | 启用响应缓存，TTL 300s | 减少 50% 请求量 |
| 超时频繁 | 调整超时策略，区分读写 | 提升可用性感知 |

---

## S4: 自动化执行 (Automation)

### Cron 配置
```bash
# 每分钟探测
* * * * * cd /workspace/skills/vendor-api-monitor && python3 scripts/probe.py

# 每小时生成报告
0 * * * * cd /workspace/skills/vendor-api-monitor && python3 scripts/report.py

# 每日深度分析
0 9 * * * cd /workspace/skills/vendor-api-monitor && python3 scripts/analyze.py --daily
```

### 连续执行模式
```bash
# 后台守护进程
python3 scripts/daemon.py --config config.yaml

# 系统服务配置
systemctl enable vendor-api-monitor
systemctl start vendor-api-monitor
```

---

## S5: 数据准确性验证 (Validation)

### 5.1 交叉验证
```python
# 方法1: 直接 HTTP 探测
direct_result = http_probe(endpoint)

# 方法2: 对比厂商状态页
status_page = fetch_vendor_status_page(vendor)

# 方法3: 多节点探测 (如有多个监控点)
node_results = [probe_from_node(n) for n in monitoring_nodes]
consensus = majority_vote(node_results)
```

### 5.2 数据一致性检查
```python
validation_rules = [
    "p99 >= p95 >= p50",           # 百分位数单调性
    "availability <= 100",          # 可用性上限
    "error_rate >= 0",              # 错误率非负
    "quota_used + quota_remaining == quota_total"
]
```

### 5.3 基准测试
```bash
# 使用已知稳定的参照 API 验证监控逻辑
python3 scripts/validate.py --benchmark https://httpbin.org/get
```

---

## S6: 局限标注 (Limitations)

### ⚠️ 已知限制

1. **无法检测业务逻辑错误**
   - 监控只验证 API 可达性和基础响应
   - 不验证返回数据的业务正确性
   - 示例: API 返回 200 但数据为空，监控视为正常

2. **网络层盲区**
   - 监控点与真实用户网络环境可能不同
   - 无法检测区域性网络问题
   - CDN/边缘节点问题可能未被覆盖

3. **配额精度限制**
   - 部分厂商不暴露实时配额 API
   - 配额消耗通过本地计数估算，可能与实际有偏差
   - 跨应用共享配额难以准确追踪

4. **认证状态盲区**
   - Token 过期可能在探测间隔中发生
   - 无法提前预警即将过期的凭证

5. **速率限制策略不透明**
   - 厂商可能实施动态限流
   - 固定阈值可能不适用所有场景

---

## S7: 对抗测试 (Chaos Engineering)

### 7.1 故障模拟
```bash
# 测试网络超时
python3 scripts/chaos.py --fault timeout --duration 30s

# 测试高延迟
python3 scripts/chaos.py --fault latency --latency 5000ms --duration 60s

# 测试错误响应
python3 scripts/chaos.py --fault error --error-rate 50 --duration 60s

# 测试证书错误
python3 scripts/chaos.py --fault ssl --duration 30s
```

### 7.2 压力测试
```bash
# 模拟高并发
python3 scripts/load_test.py --rps 100 --duration 5m

# 测试配额耗尽场景
python3 scripts/quota_test.py --exhaust-percent 95
```

### 7.3 恢复测试
```bash
# 验证告警恢复通知
python3 scripts/chaos.py --fault timeout --duration 60s --verify-recovery
```

---

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置环境
```bash
cp config.example.yaml config.yaml
# 编辑 config.yaml，填入你的 API 凭证
```

### 运行监控
```bash
# 单次检查
python3 vendor_api_monitor.py

# 持续监控
python3 scripts/daemon.py

# 生成报告
python3 scripts/report.py --format markdown
```

### 运行自检
```bash
python3 scripts/self_check.py
```

---

## 目录结构

```
vendor-api-monitor/
├── SKILL.md                    # 本文件
├── config.yaml                 # 监控配置
├── config.example.yaml         # 配置模板
├── requirements.txt            # Python依赖
├── vendor_api_monitor.py       # 主监控脚本
├── manifest.json               # Skill元数据
├── scripts/
│   ├── probe.py               # 探测脚本
│   ├── report.py              # 报告生成
│   ├── daemon.py              # 守护进程
│   ├── chaos.py               # 对抗测试
│   ├── validate.py            # 数据验证
│   └── self_check.py          # 自检脚本
├── reports/                   # 报告输出
│   └── YYYY-MM-DD/
└── data/                      # 监控数据
    └── metrics.jsonl
```

---

## API 参考

### 飞书 API
- 文档: https://open.feishu.cn/document
- 状态页: https://status.feishu.cn
- 配额: 20 QPS (默认)

### 企业微信 API
- 文档: https://developer.work.weixin.qq.com/document
- 配额: 2000 次/分钟

### 钉钉 API
- 文档: https://open.dingtalk.com/document
- 配额: 5000 次/分钟

### Notion API
- 文档: https://developers.notion.com/reference
- 配额: 3 req/sec

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 5.0.0 | 2026-03-21 | 提升至 Level 5 标准，完整 7-S 规范 |
| 1.0.0 | 2026-03-21 | 初始版本，静态能力对比 |
