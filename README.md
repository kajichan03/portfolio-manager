# Portfolio Manager

集中度量、管理所有资源和任务

## 项目目标

建立一个中心化的项目组合管理系统，追踪：
- **资源**：我 (Neal) 和各种 Clawdbot
- **任务**：所有推进中的项目

## 核心原则

1. **单一真相源**：所有项目状态在此汇总
2. **资源可视化**：清楚知道谁/什么在做什幺
3. **任务可追溯**：每个任务有归属、有状态、有进度

## 目录结构

```
portfolio-manager/
├── README.md           # 本文件
├── resources/          # 资源定义
│   ├── me.md          # 我的信息、能力、限制
│   └── bots/          # 各 Clawdbot 配置
├── projects/          # 项目清单
│   ├── active/        # 进行中
│   ├── backlog/       # 待开始
│   └── archived/      # 已归档
├── tasks/             # 任务追踪
│   ├── today.md       # 今日任务
│   ├── week.md        # 本周任务
│   └── pending.md     # 待处理
└── metrics/           # 度量指标
    └── dashboard.md   # 总览看板
```

## 快速开始

1. 定义资源 → `resources/`
2. 登记项目 → `projects/active/`
3. 分解任务 → `tasks/`
4. 更新状态 → 每日/每周回顾

---

*创建时间: 2026-03-10*
