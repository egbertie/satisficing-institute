---
name: data-analyst
description: 使用DuckDB进行本地数据分析。无需服务器，快速高效。
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"] },
        "emoji": "📊",
      },
  }

# 数据分析师 Skill

使用DuckDB进行高效本地数据分析。

## 核心能力

### 1. SQL分析
- 标准SQL查询
- 窗口函数
- 复杂JOIN操作

### 2. 数据导入
- CSV直接读取
- JSON解析
- Excel文件

### 3. 可视化
- 自动生成图表
- 数据洞察报告

## 使用示例

### 分析33角色状态
```sql
-- 角色负载分析
SELECT 
    层级,
    COUNT(*) as 角色数,
    AVG(完成进度) as 平均进度,
    COUNT(CASE WHEN 状态='🔴阻塞' THEN 1 END) as 阻塞数
FROM 角色状态表
GROUP BY 层级;
```

### 任务进度追踪
```sql
-- 延期任务统计
SELECT 
    负责人,
    COUNT(*) as 延期任务数,
    AVG(延期天数) as 平均延期
FROM 任务表
WHERE 状态='已延期'
GROUP BY 负责人
ORDER BY 延期任务数 DESC;
```

## Python集成

```python
import duckdb

# 连接数据库（内存或文件）
conn = duckdb.connect('satisficing.db')

# 执行查询
result = conn.execute("SELECT * FROM 角色表").fetchall()

# 读取CSV直接分析
df = conn.execute("SELECT * FROM 'data.csv'").fetchdf()
```

## 优势

- 无需服务器，本地运行
- 性能优异，处理百万级数据
- SQL标准，易于学习
- 免费开源
