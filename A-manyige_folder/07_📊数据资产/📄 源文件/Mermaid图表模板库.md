# 🎨 Mermaid 图表模板库

> **用途：** 常用图表快速复制使用  
> **使用方法：** 复制代码 → 粘贴到 https://mermaid.live → 下载图形

---

## 1️⃣ 流程图（Flowchart）

### 项目工作流程
```mermaid
graph TD
    A[需求输入] --> B{任务分类}
    B -->|查询类| C[直接回复]
    B -->|执行类| D[启动子代理]
    B -->|紧急类| E[立即上报]
    
    C --> F[Markdown交付]
    D --> G[并行处理]
    G --> H[更新状态]
    E --> I[飞书通知]
    
    F --> J[入库文件夹]
    H --> J
    I --> K[等待响应]
    
    style A fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style E fill:#ffccbc,stroke:#bf360c,stroke-width:2px
    style J fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
```

### 决策树
```mermaid
graph TD
    A{是否阻塞?} -->|是| B[分析原因]
    A -->|否| C[正常推进]
    B -->{用户输入?}
    C --> D[更新进度]
    {用户输入?} -->|需要| E[立即请求]
    {用户输入?} -->|不需要| F[自主解决]
    E --> G[24h内清零]
    F --> G
```

---

## 2️⃣ 甘特图（Gantt）

### 项目里程碑排期
```mermaid
gantt
    title 满意解研究所里程碑规划
    dateFormat  YYYY-MM-DD
    section 基础建设
    项目启动           :done, a1, 2026-03-06, 1d
    资料库搭建         :done, a2, 2026-03-07, 1d
    专家档案          :done, a3, 2026-03-08, 1d
    
    section 系统完善
    基础设施          :done, a4, 2026-03-09, 1d
    管理规则          :done, a5, 2026-03-10, 1d
    
    section 官宣筹备
    物料准备          :active, a6, 2026-03-13, 3d
    预热发布          :a7, 2026-03-20, 1d
    正式官宣          :milestone, a8, 2026-03-25, 0d
```

---

## 3️⃣ 脑图（Mindmap）

### 满意解研究所知识体系
```mermaid
mindmap
  root((满意解研究所))
    方法论
      西蒙满意解理论
      儒商哲学
      决策科学
    工具
      TRL自评工具
      合伙人评估问卷
      压力测试手册
    专家团队
      黎红雷
      罗汉
      谢宝剑
    服务流程
      初次咨询
      深度评估
      匹配推荐
      持续跟踪
```

---

## 4️⃣ 饼图（Pie）

### 任务类型分布
```mermaid
pie title 本周任务类型分布
    "基础建设" : 20
    "内容创作" : 25
    "流程优化" : 30
    "系统集成" : 25
```

---

## 5️⃣ 时序图（Sequence）

### 双通道通信流程
```mermaid
sequenceDiagram
    participant U as 用户
    participant K as Kimi主通道
    participant F as 飞书第二通道
    
    U->>K: 发送指令
    K->>K: 处理任务
    K->>U: 正常回复
    
    Note over U,F: 紧急情况
    U->>F: "紧急情况，启用第二沟通渠道"
    F->>U: 第二通道已激活
    U->>F: 紧急事务沟通
    F->>U: 处理结果
    
    Note over U,F: 30分钟后
    F->>F: 自动回归静默
```

---

## 6️⃣ 状态图（State Diagram）

### 任务状态流转
```mermaid
stateDiagram-v2
    [*] --> 待启动
    待启动 --> 进行中 : 开始执行
    进行中 --> 已完成 : 任务完成
    进行中 --> 阻塞 : 遇到问题
    阻塞 --> 进行中 : 问题解决
    阻塞 --> 已取消 : 任务取消
    已完成 --> [*]
    已取消 --> [*]
```

---

## 📋 快速使用指南

### 步骤1：选择图表类型
- 流程关系 → Flowchart
- 时间规划 → Gantt
- 知识结构 → Mindmap
- 比例分布 → Pie
- 交互流程 → Sequence
- 状态变化 → State

### 步骤2：复制代码
点击代码块右上角复制按钮

### 步骤3：渲染图形
1. 打开 https://mermaid.live
2. 粘贴代码
3. 自动渲染

### 步骤4：导出使用
- PNG → 插入文档/PPT
- SVG → 矢量编辑
- PDF → 打印分享

---

## 💡 进阶技巧

### 自定义样式
```mermaid
graph TD
    A[默认样式]
    B[自定义样式]
    
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#f66,stroke-width:2px,color:#fff
```

### 子图分组
```mermaid
graph TD
    subgraph 第一阶段
        A[任务1] --> B[任务2]
    end
    
    subgraph 第二阶段
        C[任务3] --> D[任务4]
    end
    
    B --> C
```

---

*复制即用，快速出图。*
