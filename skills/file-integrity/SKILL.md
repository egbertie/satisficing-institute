# File Integrity Check Skill

## 功能概述

本Skill提供文件完整性检查功能，支持以下检查项：

1. **文件存在性检查** - 验证文件是否存在
2. **文件大小检查** - 验证文件大小大于指定字节数
3. **内容可读性检查** - 验证文件无编码错误，可正常读取
4. **关键章节完整性检查** - 通过正则匹配验证文件包含必需的标题结构

## 文件结构

```
file-integrity/
├── SKILL.md                    # 本文件
├── README.md                   # 使用说明
├── config/
│   └── check_rules.json        # 检查规则配置
└── scripts/
    └── integrity_checker.py    # 检查脚本
```

## 使用方法

### 基本用法

```bash
python scripts/integrity_checker.py --path /path/to/file --config config/check_rules.json
```

### 参数说明

- `--path`: 要检查的文件路径（必需）
- `--config`: 检查规则配置文件路径（必需）
- `--output`: 报告输出文件路径（可选，默认输出到控制台）
- `--format`: 报告格式，可选 `text` 或 `json`（可选，默认 `text`）

## 检查规则配置

配置文件使用JSON格式，支持以下检查项：

### 配置示例

```json
{
  "checks": {
    "exists": {
      "enabled": true,
      "critical": true
    },
    "size": {
      "enabled": true,
      "min_bytes": 1,
      "critical": true
    },
    "readable": {
      "enabled": true,
      "lines": 100,
      "critical": true
    },
    "structure": {
      "enabled": true,
      "required_headers": ["##"],
      "critical": false
    }
  },
  "report_template": "standard"
}
```

### 配置项说明

| 检查项 | 说明 | 参数 |
|--------|------|------|
| `exists` | 文件存在性检查 | `enabled`: 是否启用, `critical`: 失败时是否终止检查 |
| `size` | 文件大小检查 | `min_bytes`: 最小字节数 |
| `readable` | 可读性检查 | `lines`: 检查前N行 |
| `structure` | 结构检查 | `required_headers`: 必需的正则表达式列表 |

## 返回值

- `0`: 所有检查通过
- `1`: 有关键检查失败
- `2`: 有非关键检查失败
- `3`: 配置错误或参数错误

## 集成使用

### 在Python中调用

```python
from scripts.integrity_checker import FileIntegrityChecker

checker = FileIntegrityChecker('/path/to/config.json')
result = checker.check_file('/path/to/file.txt')
print(result.to_dict())
```

### CI/CD集成

```yaml
- name: Check File Integrity
  run: |
    python skills/file-integrity/scripts/integrity_checker.py \
      --path docs/README.md \
      --config skills/file-integrity/config/check_rules.json
```
