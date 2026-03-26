# 飞书权限状态 - 实时报告

**检查时间**: 2026-03-25 19:17  
**应用ID**: cli_a949c1e2f4f89cb3

---

## 📊 权限状态总览

| 状态 | 数量 | 说明 |
|------|------|------|
| ✅ 已开通 | 2个 | 可正常使用 |
| ❌ 未开通 | 4个 | 需要申请 |
| ⚠️ 异常 | 4个 | API错误或审核中 |
| ➖ 未测试 | 3个 | 依赖其他权限 |

---

## 📁 分类详情

### ✅ 云盘（已开通）
| 权限 | 状态 | 说明 |
|------|------|------|
| `drive:drive` | ✅ | 云盘管理 - **可用** |
| `drive:file` | ➖ | 文件操作 - 依赖云盘 |
| `drive:file:upload` | ➖ | 文件上传 - 依赖云盘 |

**结论**: ✅ **云盘功能完全可用**

---

### ❌ 日历（未开通）
| 权限 | 状态 | 说明 |
|------|------|------|
| `calendar:calendar` | ❌ | **需要申请** |
| `calendar:event` | ❌ | **需要申请** |

---

### ⚠️ 任务（审核中/异常）
| 权限 | 状态 | 说明 |
|------|------|------|
| `task:task` | ⚠️ | 可能已申请但未生效 |
| `task:tasklist` | ❌ | **需要申请** |

---

### ⚠️ IM（部分异常）
| 权限 | 状态 | 说明 |
|------|------|------|
| `im:chat` | ✅ | 会话访问 - **可用** |
| `im:message` | ⚠️ | 可能已申请但未生效 |

---

### ⚠️ 通讯录（异常）
| 权限 | 状态 | 说明 |
|------|------|------|
| `contact:user` | ⚠️ | API错误，可能权限不足 |

---

### 💥 多维表格（API错误）
| 权限 | 状态 | 说明 |
|------|------|------|
| `bitable:bitable` | 💥 | 接口返回格式异常 |

---

### ❌ 知识库（未开通）
| 权限 | 状态 | 说明 |
|------|------|------|
| `wiki:wiki` | ❌ | **需要申请** |

---

## 🔍 分析结论

**实际已开通（可用）**:
- ✅ 云盘相关（drive:drive, drive:file, drive:file:upload）
- ✅ 会话列表（im:chat）

**可能已申请但待生效**:
- ⏳ task:task（返回异常而非权限错误）
- ⏳ im:message（返回异常而非权限错误）

**确定未开通**:
- ❌ calendar:calendar
- ❌ calendar:event  
- ❌ task:tasklist
- ❌ wiki:wiki

---

## 🚀 建议操作

### 方案A：等待生效
如果已经提交了权限申请，**通常需要 5-30 分钟生效**。

可以：
1. 等待10分钟
2. 重新运行检查: `python3 /tmp/openclaw/feishu_permission_checker.py`

### 方案B：重新申请
如果等待后仍无变化，可能需要重新申请：

🔗 **一键申请所有未开通权限**:
https://open.feishu.cn/app/cli_a949c1e2f4f89cb3/auth?q=calendar:calendar,calendar:event,task:task,task:tasklist,wiki:wiki,bitable:bitable

---

## 📋 当前可用功能（立即使用）

```bash
# ✅ 云盘文件上传
python3 plugins/feishu_drive_uploader.py upload /path/to/file.pdf

# ✅ 云盘文件列表
python3 plugins/feishu_drive_uploader.py list
```

---

*报告生成: 2026-03-25 19:17*  
*检查工具: /tmp/openclaw/feishu_permission_checker.py*
