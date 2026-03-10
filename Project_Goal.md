# Portfolio Manager - Project Goal

> **维护者**: Neal  
> **最后更新**: 2026-03-10  
> **状态**: 需求已澄清，进入产品设计阶段

---

## 1. 项目背景

### 1.1 现状问题

| 问题 | 描述 |
|------|------|
| **信息分散** | 我的任务在 Apple Reminders，Bot 的项目分散在各 bot 本地目录 |
| **缺乏统一视图** | 需要打开多个地方才能了解所有项目全貌 |
| **资源负载不可见** | 不清楚每个 bot 同时在跟进多少项目 |
| **优先级决策缺乏依据** | 难以在多个项目间做资源调配决策 |

### 1.2 核心痛点

> 没有统一视图，难以整体把控所有进行中的项目。

---

## 2. 项目目标

### 2.1 总体目标

**集中度量、管理所有的资源和任务**

建立一个中心化的项目组合管理系统，实现：
- **单一真相源**：所有项目状态在此汇总
- **资源可视化**：清楚知道谁/什么在做什么
- **任务可追溯**：每个任务有归属、有状态、有进度

### 2.2 目标用户

| 用户 | 角色 | 使用场景 |
|------|------|----------|
| **Neal** | 唯一用户、资源调度者、优先级决策者 | 实时查看状态、每日早报回顾 |
| **Clawdbots** | 被动同步（通过 progress.md），不直接交互 | 执行工作、汇报进度 |

---

## 3. 核心需求

### 3.1 功能需求

| 需求 | 优先级 | 说明 |
|------|--------|------|
| **统一任务 Dashboard** | P0 | 一个地方看到所有项目状态 |
| **任务状态追踪** | P0 | 状态和描述实时可见 |
| **资源投入可视化** | P0 | 我 + 各 bot 的分配情况 |
| **Apple Reminders 集成** | P0 | 双向同步 |
| **Bot 项目聚合** | P0 | 从各项目 progress.md 聚合 |
| **优先级决策支持** | P1 | 便于评估和分配资源 |
| **定时报告** | P1 | Telegram + iMessage 推送 |

### 3.2 数据需求

| 数据类型 | 来源 | 说明 |
|----------|------|------|
| **我的项目** | Apple Reminders | 列表 = 项目，任务 = 事项 |
| **Bot 项目** | progress.md | 从各 bot 项目同步 |
| **Bot 资源** | bots.yaml | 4 个 Agents 的元数据 |
| **项目元数据** | projects.yaml | 名称、描述、地址、参与 Agent |

---

## 4. 产品设计思路（进行中）

### 4.1 产品形态

**主控模式**：Clawd（主 Agent）作为统一入口

```
Neal ←──→ Clawd ←──→ Dashboard/Reports
            │
            ├──→ pd/Dev/Test（执行 Agent）
            └──→ Apple Reminders（双向同步）
```

### 4.2 核心模块

| 模块 | 说明 |
|------|------|
| **项目注册中心** | 管理所有项目元数据（Reminders 列表 + Bot 项目） |
| **状态聚合引擎** | 从 Reminders 和 progress.md 同步最新状态 |
| **Dashboard 视图** | 项目列表、进度、阻塞任务、即将到期 |
| **定时报告器** | Telegram + iMessage 推送 |

### 4.3 关键设计决策

| 决策 | 内容 |
|------|------|
| **项目定义** | Reminders 列表 = 项目；列表内任务 = 项目任务 |
| **优先级 scheme** | high/medium/low（与 Reminders 系统字段一致） |
| **Bot-项目关系** | 多对多：一个项目可有多个 Agent，一个 Agent 可参与多个项目 |
| **项目类型** | ① 专门项目（有始有终的大事情）② 日常运营（主题下的琐事） |
| **Dashboard 展示** | 显示所有项目，按优先级排序 |
| **明确不做** | 项目依赖关系、时间工时追踪、复杂度量指标 |

### 4.4 交互流程

> **重要约束**：所有交互通过**对话渠道**（Telegram）进行，Dashboard 以文本/表格形式输出，不是可视化界面。

**实时状态查询**：
1. 发送消息给 Clawd（如 "查看项目状态"）
2. Clawd 读取 Reminders + 各项目 progress.md
3. 聚合生成文本格式 Dashboard
4. 回复消息展示（支持摘要/详情模式）

**任务分配**：
1. 对话中告知 Clawd 新建项目（如 "登记新项目 xxx"）
2. Clawd 更新 projects.yaml
3. 对话中分配执行 Agent（如 "让 pd 负责需求分析"）
4. Clawd 通知执行 Agent
5. 执行 Agent 推进工作
6. 执行 Agent 汇报进度
7. Clawd 更新 progress.md
8. Portfolio 同步最新状态

**进度汇报与 Review**：
1. 执行 Agent 完成阶段性工作
2. 通过对话向 Clawd 汇报
3. Clawd 安排检查点 Review
4. Review 通过后，Clawd 更新状态

---

## 5. Dashboard 设计（文本格式）

### 5.1 布局原则

- **摘要模式**：项目数量统计 + 关键提醒（阻塞/到期）
- **详情模式**：完整项目列表，按优先级分组
- **消息友好**：考虑 Telegram 消息长度限制，支持分页

### 5.2 摘要模式示例

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

### 5.3 详情模式示例

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

### 5.4 信息字段

| 字段 | 说明 | 来源 |
|------|------|------|
| 项目名称 | 简短标识 | Reminders 列表名 / 项目登记 |
| 进度百分比 | 完成度 | progress.md / 任务完成率 |
| 状态 | 当前阶段 | progress.md |
| 负责 Agent | Emoji + 名称 | projects.yaml 分配 |
| 优先级 | 🔴/🟡/🟢 | Reminders / 项目登记 |
| 截止日期 | 到期提醒 | Reminders / 项目登记 |
| 下一步 | 待办事项 | progress.md 当前任务 |

---

## 6. 数据模型设计

### 6.1 核心实体

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
source_ref: string      # 来源引用（Reminders 任务 ID）
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

### 6.2 数据文件结构

```
output/
├── resources/
│   ├── bots/
│   │   └── bots.yaml        # Agent 列表
│   └── me.md               # 用户信息（可选）
├── projects/
│   ├── projects.yaml       # 项目注册表
│   └── {project-id}/
│       └── progress.md     # 项目进度（Bot 项目）
└── tasks/
    └── sync-state.yaml     # 同步状态记录
```

---

## 7. 同步机制设计

### 7.1 数据源与同步策略

| 数据源 | 同步方向 | 触发时机 | 冲突处理 |
|--------|----------|----------|----------|
| Apple Reminders | 双向 | 查询时实时同步 | 以 Reminders 为准 |
| Bot progress.md | 单向（读） | 查询时读取 | 以 progress.md 为准 |
| projects.yaml | 本地更新 | Clawd 操作后更新 | 手动编辑需谨慎 |

### 7.2 同步流程

```
Dashboard 查询
    │
    ├──→ 读取 projects.yaml（获取项目列表）
    │
    ├──→ 对于 Reminders 项目
    │     └──→ 调用 Reminders API 同步最新状态
    │
    ├──→ 对于 Bot 项目
    │     └──→ 读取 progress.md 解析状态
    │
    └──→ 聚合生成 Dashboard
```

---

## 8. 命令/指令设计

### 8.1 用户 → Clawd 指令

| 指令 | 说明 | 示例 |
|------|------|------|
| `状态` / `summary` | 查看摘要 Dashboard | "状态" |
| `详情` / `list` | 查看详情列表 | "详情" |
| `项目 {名称}` | 查看项目详情 | "项目 产品需求" |
| `新建项目 {名称}` | 登记新项目 | "新建项目 技术调研" |
| `分配 {项目} 给 {Agent}` | 分配负责人 | "分配 技术调研 给 Dev" |
| `设置优先级 {项目} {高/中/低}` | 修改优先级 | "设置优先级 技术调研 高" |

### 8.2 Clawd → 执行 Agent 指令

通过内部调用或对话渠道通知：

```
Clawd → pd: "你被分配至项目 '技术调研'，本地地址: ~/projects/tech-research/"
```

---

## 9. 成功标准

| 标准 | 验证方式 |
|------|----------|
| 在一个地方看到所有项目 | Dashboard 展示 Reminders 项目 + Bot 项目 |
| 清楚资源分配 | 每个项目显示参与的 Agent |
| 快速识别优先级 | high 优先级项目在前，有 🔴 标识 |
| 不遗漏阻塞任务 | Dashboard 高亮显示等待 Review/阻塞状态 |
| 对话交互顺畅 | 自然语言指令可被正确解析执行 |

---

## 10. 产品形态与架构

### 10.1 实现方案：Skill + CLI 混合架构

基于需求分析，确定采用 **Skill + CLI 混合架构**：

| 组件 | 职责 | 实现方式 | 位置 |
|------|------|----------|------|
| **Portfolio Skill** | 对话交互、任务分配、状态查询、配置定时任务 | OpenClaw Skill (`SKILL.md` + scripts) | `skills/portfolio/` |
| **Portfolio CLI** | 数据操作、Dashboard 生成、定时报告发送 | Python 脚本 | `cli/` 或 Skill 的 `scripts/` |
| **系统 Cron** | 定时触发报告 | `crontab` 或 OpenClaw cron | 系统配置 |

### 10.2 交互架构图

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
│  Apple        │   │   progress.md  │   │  Telegram/       │
│  Reminders    │   │   解析         │   │  iMessage 发送   │
└───────────────┘   └────────────────┘   └──────────────────┘
```

### 10.3 组件边界

**Portfolio Skill 职责**:
- ✅ 解析自然语言指令（"状态"、"分配 xxx 给 pd"）
- ✅ 协调其他 Agent（通知 pd/Dev 开始工作）
- ✅ 配置定时报告（设置时间、渠道）
- ✅ 调用 CLI 生成 Dashboard

**Portfolio CLI 职责**:
- ✅ 读取 Reminders API
- ✅ 解析 progress.md
- ✅ 生成文本 Dashboard
- ✅ 发送 Telegram/iMessage 报告

### 10.4 数据与代码分离

| 类型 | 位置 | 版本控制 |
|------|------|----------|
| **Skill 代码** | `skills/portfolio/` | GitHub |
| **CLI 脚本** | `cli/` 或 Skill 内 | GitHub |
| **业务数据** | `output/` | 不提交 Git（本地数据） |

**数据访问**: Skill 通过约定路径或配置文件访问 `output/` 数据

---

## 11. Schema 契约设计

### 11.1 问题背景

Portfolio 需要解析各项目的 progress.md，但 markdown 格式不统一会导致解析失败。需要从"事后容错"转向"事前预防"。

### 11.2 解决方案：双格式输出 + Schema 契约

**核心设计**:
- **人类可读**: `progress.md`（展示用）
- **机器可读**: `progress.json`（Portfolio 消费用）
- **Schema 约束**: 共享 schema 文件，保证格式一致

### 11.3 Schema 规范

**文件位置**: `output/schemas/progress-schema.v1.json`

**核心字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `project_id` | string | 项目唯一标识 |
| `project_name` | string | 项目名称 |
| `current_phase` | string | 当前阶段 |
| `progress_percentage` | integer | 进度百分比 (0-100) |
| `status` | enum | 项目状态: active/paused/blocked/completed |
| `tasks` | array | 任务列表 |
| `agents` | array | 参与 Agent 列表 |
| `blockers` | array | 阻塞项列表 |
| `updated_at` | datetime | 最后更新时间 |

**任务字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 任务 ID |
| `name` | string | 任务名称 |
| `status` | enum | todo/in_progress/review/done/blocked |
| `assignee` | string | 负责人 |
| `priority` | enum | high/medium/low |
| `due_date` | date | 截止日期 |

### 11.4 契约关系

```
Portfolio 项目（Schema 维护者）
├─ schemas/progress-schema.v1.json
└─ 发布到: 项目管理 Skill

项目管理 Skill（Schema 消费者）
├─ 复制 schema 到 skill 目录
├─ 写入时按 schema 校验
└─ 同时输出 progress.md + progress.json
```

### 11.5 写入流程（强制）

项目管理 Skill 更新进度时必须：

1. **构建数据对象** - 按 schema 构建 json
2. **Schema 校验** - 验证数据格式
3. **双写文件** - 同时写入 md 和 json
4. **失败回滚** - 校验失败不写入，提示修正

### 11.6 消费流程

Portfolio CLI 读取时：
1. 直接读取 `progress.json`
2. 按 schema 解析（无需容错）
3. 生成 Dashboard

---

## 12. 对项目管理 Skill 的修改需求

详见 `output/docs/skill-integration.md`，主要包括：

1. **文件结构**: 增加 `schemas/progress-schema.json`
2. **SKILL.md**: 增加"输出格式规范"章节
3. **新增脚本**: `validate-and-save-progress.py`（校验并双写）
4. **写入流程**: 强制双格式输出流程
5. **交付物要求**：产出一个给 AI agent 读的《项目管理 Skill 的修改需求》，让 AI agent 正确修改项目管理 Skill。

---

## 13. 下一步（产品设计阶段已完成）

当前状态：产品设计阶段 ✅ 完成，PRD 已输出到 `output_product_doc.md`

**下一阶段：技术架构设计与实现**

1. **技术架构设计**
   - CLI 模块架构设计
   - Skill 指令设计
   - 数据流详细设计

2. **MVP 实现**
   - CLI: Reminders API 集成
   - CLI: progress.json 解析
   - CLI: Dashboard 生成
   - Skill: 基础对话指令（"状态"）
   - 集成测试

---

## 附录：暂不实现（MVP 之后）

| 功能 | 原因 |
|------|------|
| 项目依赖关系 | 当前无此需求 |
| 时间工时追踪 | 避免过度设计 |
| 复杂度量指标 | 避免过度设计 |
| GitHub 集成 | MVP 后按需添加 |
| Web Dashboard | 当前对话渠道足够 |
| Agent 工作负载统计 | 当前规模小，人工可见 |

---

*此文档由 pd 基于需求澄清整理，后续产品设计更新将记录在此。*
