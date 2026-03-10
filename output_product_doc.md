# Portfolio Manager - 产品需求文档 (PRD)

> **版本**: v1.0  
> **状态**: 已确认  
> **最后更新**: 2026-03-10  
> **维护者**: clawdbot: pd

---

## 1. 产品概述

### 1.1 产品定位

Portfolio Manager 是一个中心化的项目组合管理系统，用于集中度量和管理用户（Neal）及其 AI Agents（Clawdbots）的所有项目与任务。

### 1.2 核心目标

- **单一真相源**: 所有项目状态在此汇总
- **资源可视化**: 清楚知道谁/什么在做什么
- **任务可追溯**: 每个任务有归属、有状态、有进度

### 1.3 目标用户

| 用户 | 角色 | 使用方式 |
|------|------|----------|
| **Neal** | 唯一用户、资源调度者 | 通过 Telegram 对话交互 |
| **Clawd** | 主 Agent、协调者 | 解析指令、协调执行 Agent |
| **pd/Dev/Test** | 执行 Agent | 接收任务、汇报进度 |

---

## 2. 需求描述

### 2.1 现状痛点

| 痛点 | 描述 |
|------|------|
| 信息分散 | 用户任务在 Apple Reminders，Bot 项目分散在各本地目录 |
| 缺乏统一视图 | 需打开多个地方才能了解全貌 |
| 资源负载不可见 | 不清楚每个 bot 同时在跟进多少项目 |
| 决策缺乏依据 | 难以在多个项目间做资源调配决策 |

### 2.2 功能需求

| 需求 ID | 需求 | 优先级 | 说明 |
|---------|------|--------|------|
| R1 | 统一任务 Dashboard | P0 | 一个地方看到所有项目状态 |
| R2 | 任务状态追踪 | P0 | 状态和描述实时可见 |
| R3 | 资源投入可视化 | P0 | 我 + 各 bot 的分配情况 |
| R4 | Apple Reminders 集成 | P0 | 双向同步 |
| R5 | Bot 项目聚合 | P0 | 从各项目 progress.json 聚合 |
| R6 | 任务分配 | P1 | Clawd 协调分配执行 Agent |
| R7 | 定时报告 | P1 | Telegram + iMessage 推送 |

### 2.3 非功能需求

| 需求 | 说明 |
|------|------|
| 对话交互 | 所有交互通过 Telegram 对话完成 |
| 实时查看 | 查询时实时聚合最新状态 |
| 数据分离 | Skill 代码与业务数据分离 |

---

## 3. 产品方案

### 3.1 架构设计

采用 **Skill + CLI 混合架构**:

```
用户对话 → Clawd(Skill) ──→ 调用 CLI 生成 Dashboard ──→ 返回结果
                  │                    │
                  │                    ├── 解析 Reminders API
                  │                    ├── 解析 progress.json
                  │                    └── 格式化输出
                  │
                  └── 协调 pd/Dev（通知任务分配）
                           │
                           ▼
                    配置定时任务 → Cron 定时调用 CLI → 发送报告
```

### 3.2 组件职责

| 组件 | 职责 | 实现 |
|------|------|------|
| **Portfolio Skill** | 对话交互、任务分配、配置定时任务 | OpenClaw Skill |
| **Portfolio CLI** | 数据操作、Dashboard 生成、定时报告发送 | Python 脚本 |
| **系统 Cron** | 定时触发报告 | crontab |

### 3.3 数据流

```
┌─────────────────────────────────────────────────────────────┐
│                        用户交互层                            │
├──────────────┬──────────────────┬───────────────────────────┤
│   Telegram   │   iMessage       │   对话 / 命令             │
└──────┬───────┴────────┬─────────┴───────────┬───────────────┘
       │                │                     │
       └────────────────┴─────────┬───────────┘
                                  ▼
                    ┌───────────────────────┐
                    │   Clawd (主 Agent)    │
                    │   Portfolio Skill     │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
       ┌─────────────┐   ┌──────────┐   ┌─────────────────┐
       │  自然语言    │   │ 任务分配  │   │   配置定时任务   │
       │  理解/响应   │   │ 协调 pd  │   │  (Cron 配置)    │
       └──────┬──────┘   └────┬─────┘   └────────┬────────┘
              │               │                  │
              └───────────────┴──────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   Portfolio CLI   │
                    │   (Python 脚本)   │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌────────────────┐   ┌──────────────────┐
│  Apple        │   │   progress.json│   │  Telegram/       │
│  Reminders    │   │   解析         │   │  iMessage 发送   │
└───────────────┘   └────────────────┘   └──────────────────┘
```

---

## 4. Dashboard 设计

### 4.1 摘要模式

```
📊 Portfolio 状态摘要 (2026-03-10)

项目总数: 8
├─ 🟢 进行中: 5
├─ 🟡 等待Review: 2
└─ 🔴 阻塞: 1

⚠️ 需要关注:
• [P0] 项目A - 今日到期 (pd 负责)
• [P1] 项目B - 等待 Review (Dev 提交)

💬 回复 "详情" 查看完整列表
回复 "项目A" 查看项目详情
```

### 4.2 详情模式

```
📋 项目详情列表

🔴 HIGH 优先级
─────────────────────
1. [项目A] 产品需求文档
   进度: 70% | 状态: 设计中
   负责: 🎯 pd | 截止日期: 今日
   下一步: 等待 Review

🟡 MEDIUM 优先级
─────────────────────
2. [项目B] 技术架构设计
   进度: 40% | 状态: 开发中
   负责: 📟 Dev | 截止日期: 3天后

🟢 LOW 优先级
─────────────────────
3. [日常-生活采购] 🏠
   待办: 3项 | 状态: 运营中
   负责: ☎️ Neal
```

### 4.3 展示字段

| 字段 | 说明 | 来源 |
|------|------|------|
| 项目名称 | 简短标识 | Reminders 列表名 / 项目登记 |
| 进度百分比 | 完成度 | progress.json |
| 状态 | 当前阶段 | progress.json |
| 负责 Agent | Emoji + 名称 | projects.yaml 分配 |
| 优先级 | 🔴/🟡/🟢 | Reminders / 项目登记 |
| 截止日期 | 到期提醒 | Reminders / 项目登记 |
| 下一步 | 待办事项 | progress.json 当前任务 |

---

## 5. 数据模型

### 5.1 核心实体

**项目 (Project)**
```yaml
id: string              # 唯一标识
name: string            # 显示名称
type: enum              # dedicated | operation
source: enum            # reminders | bot-project
priority: enum          # high | medium | low
status: enum            # active | paused | completed
local_path: string      # 本地地址
github_url: string      # GitHub 地址（可选）
agents: [agent_id]      # 参与的 Agent 列表
created_at: date
updated_at: date
```

**任务 (Task)**
```yaml
id: string              # 唯一标识
project_id: string      # 所属项目
name: string            # 任务名称
status: enum            # todo | in_progress | review | done
assignee: agent_id      # 负责人
due_date: date          # 截止日期
priority: enum          # high | medium | low
```

**Agent**
```yaml
id: string              # 唯一标识
name: string            # 显示名称
emoji: string           # 可视化标识
type: string            # 职责类型
communication:          # 通信配置
  channel: string
  url: string
config_path: string     # 配置位置
status: enum            # active | inactive
```

### 5.2 Schema 契约

**progress.json Schema** (v1.0)

文件位置: `output/schemas/progress-schema.v1.json`

| 字段 | 必填 | 说明 |
|------|------|------|
| `project_id` | ✅ | 项目唯一标识 |
| `project_name` | ✅ | 显示名称 |
| `current_phase` | ✅ | 当前阶段 |
| `progress_percentage` | ✅ | 0-100 整数 |
| `status` | ✅ | active/paused/blocked/completed |
| `tasks` | ✅ | 任务数组 |
| `agents` | ✅ | 参与 Agent 列表 |
| `blockers` | ❌ | 阻塞项 |
| `updated_at` | ✅ | ISO 8601 时间戳 |

**任务状态枚举**: `todo`, `in_progress`, `review`, `done`, `blocked`

---

## 6. 命令/指令设计

### 6.1 用户指令

| 指令 | 说明 | 示例 |
|------|------|------|
| `状态` / `summary` | 查看摘要 Dashboard | "状态" |
| `详情` / `list` | 查看详情列表 | "详情" |
| `项目 {名称}` | 查看项目详情 | "项目 产品需求" |
| `新建项目 {名称}` | 登记新项目 | "新建项目 技术调研" |
| `分配 {项目} 给 {Agent}` | 分配负责人 | "分配 技术调研 给 Dev" |
| `设置优先级 {项目} {高/中/低}` | 修改优先级 | "设置优先级 技术调研 高" |

### 6.2 Agent 协调指令

Clawd 通过内部调用或对话渠道通知执行 Agent：

```
Clawd → pd: "你被分配至项目 '技术调研'，本地地址: ~/projects/tech-research/"
```

---

## 7. 集成规范

### 7.1 对项目管理 Skill 的要求

项目管理 Skill 必须同时输出：
- `progress.md` - 人类可读
- `progress.json` - 机器可读（符合 Schema v1.0）

**写入流程**:
1. 按 schema 构建 JSON 数据
2. 校验数据格式
3. 双写文件（原子性）
4. 失败回滚

详见: `output/docs/skill-integration.md`

### 7.2 数据源

| 数据源 | 同步方式 | 说明 |
|--------|----------|------|
| Apple Reminders | 实时 API 调用 | 列表 = 项目，任务 = 事项 |
| Bot progress.json | 读取本地文件 | 按 schema 解析 |

---

## 8. 验收标准

| 标准 ID | 标准 | 验证方式 |
|---------|------|----------|
| A1 | 在一个地方看到所有项目 | Dashboard 展示 Reminders 项目 + Bot 项目 |
| A2 | 清楚资源分配 | 每个项目显示参与的 Agent |
| A3 | 快速识别优先级 | high 优先级项目在前，有 🔴 标识 |
| A4 | 不遗漏阻塞任务 | Dashboard 高亮显示等待 Review/阻塞状态 |
| A5 | 对话交互顺畅 | 自然语言指令可被正确解析执行 |
| A6 | 定时报告送达 | Telegram/iMessage 定时收到报告 |
| A7 | 数据格式一致 | progress.json 符合 schema v1.0 |

---

## 9. 后续迭代

### 9.1 本次不做（MVP 之后）

| 功能 | 原因 |
|------|------|
| 项目依赖关系 | 当前无此需求 |
| 时间工时追踪 | 避免过度设计 |
| 复杂度量指标 | MVP 后按需添加 |
| GitHub 集成 | MVP 后按需添加 |
| Web Dashboard | 当前对话渠道足够 |
| Agent 工作负载统计 | 当前规模小 |

### 9.2 未来扩展

- 支持更多数据源（GitHub Issues、Notion 等）
- 项目依赖关系可视化
- 更丰富的度量指标
- Web Dashboard 界面

---

## 10. 相关文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 项目章程 | `Project_Goal.md` | 完整的设计过程记录 |
| Schema 契约 | `output/schemas/progress-schema.v1.json` | JSON Schema 定义 |
| 集成指南 | `output/docs/skill-integration.md` | 供其他 Skill 参考 |
| 决策记录 | `decisions.md` | 关键决策记录 |

---

*本文档由 clawdbot: pd 基于 Project_Goal.md 整理生成*
