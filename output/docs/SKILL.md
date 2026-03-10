# Portfolio Manager

> 中心化的项目组合管理系统

复制到 ~/.openclaw/workspace/skills/portfolio/SKILL.md

## 概述

Portfolio Manager 用于集中度量和管理所有项目与任务，追踪资源和进度。

## 指令

| 指令模式 | 说明 | 示例 |
|---------|------|------|
| `^(状态|summary|status)$` | 查看 Portfolio 摘要 | "状态" |
| `^(详情|list|projects)$` | 查看项目详情列表 | "详情" |
| `^项目\s+(.+)$` | 查看指定项目 | "项目 portfolio-manager" |
| `^新建项目\s+(.+)$` | 创建新项目 | "新建项目 Tech Research" |
| `^分配\s+(.+)\s+给\s+(.+)$` | 分配 Agent | "分配 tech-research 给 dev" |
| `^设置优先级\s+(.+)\s+(高|中|低)$` | 设置优先级 | "设置优先级 tech-research 高" |

## 指令处理

当用户发送消息匹配上述指令时：

1. 解析指令和参数
2. 调用 `output.interfaces.skill.handle_message(message)`
3. 返回格式化结果

## 数据

- 项目数据: `output/data/projects.json`
- Agent 数据: `output/data/agents.json`

## 配置

在 `output/config/portfolio.json` 中配置数据源和通知渠道。

## 版本

v1.0.0 - MVP
