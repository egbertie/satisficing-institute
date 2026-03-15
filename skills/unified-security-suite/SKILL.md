---
name: unified-security-suite
description: Unified security and compliance suite. Replaces security-guardian, error-guard, tuanziguardianclaw with single integrated interface. Use for: security scanning, vulnerability detection, error monitoring, compliance checking, incident response.
triggers: ["security", "vulnerability", "error", "guard", "scan", "安全", "漏洞"]
---

# Unified Security Suite

**统一安全与合规套件** - 整合安全扫描、错误监控、合规检查。

> 🎯 替代: security-guardian + error-guard + tuanziguardianclaw

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **安全扫描** | 代码扫描、依赖检查、配置审计 |
| **漏洞检测** | CVE监控、漏洞修复建议 |
| **错误监控** | 异常捕获、告警通知、根因分析 |
| **合规检查** | 法规遵循、最佳实践、审计报告 |
| **应急响应** | 事件处理、影响评估、修复跟踪 |

---

## 快速开始

```bash
# 安全扫描
security-suite scan --target ./src --type code,dependency,config

# 漏洞检测
security-suite vuln --check --notify --severity high

# 错误监控
security-suite monitor --service api-server --alert slack

# 合规检查
security-suite compliance --standard soc2 --report pdf
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| security-guardian | `security-suite` |
| error-guard | `security-suite monitor` |
| tuanziguardianclaw | `security-suite` |

---

**自建替代计数**: +3
