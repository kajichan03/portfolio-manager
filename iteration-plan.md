# Iteration Plan

> **版本**: v2.0  
> **状态**: 🟡 进行中  
> **迭代**: Iteration 1 - MVP  
> **时间**: 2026-03-10 至 2026-03-17 (预计)  
> **最后更新**: 2026-03-10

---

## 迭代目标

完成 Portfolio Manager 的 MVP 版本，遵循 Hexagonal Architecture 由内向外开发：
1. 领域层：Project, Task, Agent, Progress 实体定义
2. 适配器抽象：Repository/Adapter 接口
3. 应用层：ProjectService, DashboardService, AgentService
4. 适配器实现：YAML, Reminders, Progress, Telegram, iMessage
5. 接口层：CLI 和 Skill (平等调用 Service)

---

## 开发原则

**Hexagonal Architecture 由内向外开发顺序**:
```
Domain → Adapter Interfaces → Services → Adapter Impl → Interfaces (CLI/Skill)
```

**关键约束**:
- ✅ Skill 直接调用 Service，**不经过 CLI**
- ✅ CLI 直接调用 Service，**不依赖 Skill**
- ✅ 两者共享 core/ 层代码

---

## Phase 1: 领域层 (Domain Layer)

### I1-001: 领域模型定义
| 属性 | 值 |
|------|-----|
| **任务** | 创建 core/domain/ 目录，定义所有领域实体 |
| **工时** | 3h |
| **依赖** | - |
| **验收标准** | 所有领域实体可导入，类型注解完整 |

**子任务**:
- [ ] 创建 `core/domain/__init__.py`
- [ ] 定义值对象: `ProjectId`, `AgentId`, `TaskId`
- [ ] 定义枚举: `ProjectType`, `DataSource`, `Priority`, `ProjectStatus`, `TaskStatus`, `AgentStatus`, `AgentRole`
- [ ] 定义实体: `Project` (静态信息)
- [ ] 定义实体: `ProjectProgress` (运行时数据)
- [ ] 定义实体: `Task` (纯净领域模型)
- [ ] 定义实体: `Agent`, `CommunicationConfig`

**产出文件**:
- `core/domain/project.py`
- `core/domain/progress.py`
- `core/domain/task.py`
- `core/domain/agent.py`
- `core/domain/agent_role.py`
- `core/domain/enums.py`

---

## Phase 2: 适配器抽象层 (Adapter Interfaces)

### I1-002: 适配器抽象接口定义
| 属性 | 值 |
|------|-----|
| **任务** | 创建 core/adapters/base.py，定义所有抽象接口 |
| **工时** | 2h |
| **依赖** | I1-001 |
| **验收标准** | 接口定义完整，可被具体适配器实现 |

**子任务**:
- [ ] 创建 `core/adapters/__init__.py`
- [ ] 定义 `ProjectRepository` (项目存储抽象)
- [ ] 定义 `AgentRepository` (Agent 存储抽象)
- [ ] 定义 `ProgressSource` (进度数据源抽象)
- [ ] 定义 `NotificationAdapter` (通知渠道抽象)
- [ ] 定义异常类: `ProjectNotFoundError`, `AgentNotFoundError`

**产出文件**:
- `core/adapters/base.py`

---

## Phase 3: 应用层 (Application Layer)

### I1-003: 应用服务实现
| 属性 | 值 |
|------|-----|
| **任务** | 实现 core/services/ 所有应用服务 |
| **工时** | 5h |
| **依赖** | I1-001, I1-002 |
| **验收标准** | 所有服务可通过单元测试，纯内存可运行 |

**子任务**:
- [ ] 创建 `core/services/__init__.py`
- [ ] 实现 `ProjectService`
  - `create_project()`
  - `assign_agent()`
  - `list_projects()`
  - `get_project_with_progress()`
- [ ] 实现 `DashboardService`
  - `generate_summary()`
  - `generate_detail()`
  - `_fetch_progresses()` (并行获取)
- [ ] 实现 `AgentService`
  - `notify_assignment()`
  - `get_agent_workload()`
- [ ] 定义 Command/Query 对象 (CreateProjectCommand, ProjectFilter 等)

**产出文件**:
- `core/services/project_service.py`
- `core/services/dashboard_service.py`
- `core/services/agent_service.py`
- `core/services/commands.py`

---

## Phase 4: 适配器实现层 (Adapter Implementations)

### I1-004: 存储适配器实现 (YAML)
| 属性 | 值 |
|------|-----|
| **任务** | 实现 YAML 存储的 Repository |
| **工时** | 3h |
| **依赖** | I1-002, I1-003 |
| **验收标准** | 可读写 projects.yaml 和 agents.yaml |

**子任务**:
- [ ] 实现 `YamlProjectRepository`
- [ ] 实现 `YamlAgentRepository`
- [ ] 实现 YAML 序列化/反序列化
- [ ] 创建初始 `data/projects.yaml` 和 `data/agents.yaml`

**产出文件**:
- `core/adapters/config_adapter.py`
- `data/projects.yaml`
- `data/agents.yaml`

---

### I1-005: 数据源适配器实现 (Reminders + Progress)
| 属性 | 值 |
|------|-----|
| **任务** | 实现 RemindersAdapter 和 ProgressAdapter |
| **工时** | 4h |
| **依赖** | I1-002, I1-003 |
| **验收标准** | 可从两个数据源获取项目进度 |

**子任务**:
- [ ] 实现 `RemindersAdapter` (调用 remindctl)
- [ ] 实现 `ProgressAdapter` (读取 progress.json)
- [ ] 实现 Schema 验证
- [ ] 处理数据源不存在的情况

**产出文件**:
- `core/adapters/reminders_adapter.py`
- `core/adapters/progress_adapter.py`

---

### I1-006: 通知适配器实现 (Telegram + iMessage)
| 属性 | 值 |
|------|-----|
| **任务** | 实现通知渠道适配器 |
| **工时** | 2h |
| **依赖** | I1-002 |
| **验收标准** | 可通过两个渠道发送通知 |

**子任务**:
- [ ] 实现 `TelegramAdapter`
- [ ] 实现 `IMessageAdapter` (复用现有 skill)
- [ ] 配置管理 (bot token, chat_id)

**产出文件**:
- `core/adapters/telegram_adapter.py`
- `core/adapters/imessage_adapter.py`

---

## Phase 5: 接口层 (Interface Layer)

### I1-007: CLI 命令实现
| 属性 | 值 |
|------|-----|
| **任务** | 实现 interfaces/cli/ 命令行接口 |
| **工时** | 3h |
| **依赖** | I1-003, I1-004, I1-005, I1-006 |
| **验收标准** | 命令行可正常执行所有子命令 |

**子任务**:
- [ ] 创建 `interfaces/cli/__init__.py`
- [ ] 实现 `main.py` 入口 (Click)
- [ ] 实现 `dashboard` 命令 (summary/detail)
- [ ] 实现 `project` 命令 (list, create, assign)
- [ ] 实现 `sync` 命令
- [ ] 实现 `report` 命令
- [ ] 实现输出格式化 (`TextFormatter`)

**产出文件**:
- `interfaces/cli/main.py`
- `interfaces/cli/commands/dashboard.py`
- `interfaces/cli/commands/project.py`
- `interfaces/cli/commands/sync.py`
- `interfaces/cli/commands/report.py`
- `interfaces/cli/formatters/text_formatter.py`

---

### I1-008: Skill 指令实现 ⚠️ 关键：直接调用 Service
| 属性 | 值 |
|------|-----|
| **任务** | 实现 interfaces/skill/ 指令处理器 |
| **工时** | 3h |
| **依赖** | I1-003, I1-004, I1-005, I1-006 |
| **验收标准** | Telegram 对话可触发 Dashboard 查询 |

**⚠️ 架构约束**: Skill **直接调用 Service**，**不经过 CLI**

**子任务**:
- [ ] 创建 `interfaces/skill/SKILL.md`
- [ ] 实现 `SkillCommandBus` (指令路由)
- [ ] 实现 `StatusHandler` → 调用 `DashboardService.generate_summary()`
- [ ] 实现 `ListHandler` → 调用 `DashboardService.generate_detail()`
- [ ] 实现 `ProjectDetailHandler` → 调用 `ProjectService`
- [ ] 实现 `CreateProjectHandler` → 调用 `ProjectService`
- [ ] 实现 `AssignHandler` → 调用 `ProjectService` + `AgentService`

**产出文件**:
- `interfaces/skill/SKILL.md`
- `interfaces/skill/__init__.py`
- `interfaces/skill/handlers.py`
- `interfaces/skill/coordinator.py`

---

## Phase 6: 集成与配置

### I1-009: 依赖注入与集成测试
| 属性 | 值 |
|------|-----|
| **任务** | 实现依赖注入配置，编写集成测试 |
| **工时** | 3h |
| **依赖** | I1-007, I1-008 |
| **验收标准** | 完整功能通过测试，可独立部署 |

**子任务**:
- [ ] 实现 `ServiceContainer` (依赖注入)
- [ ] 实现配置加载 (`config/portfolio.yaml`)
- [ ] 编写单元测试 (domain, services)
- [ ] 编写集成测试 (adapters)
- [ ] 编写 `pyproject.toml`
- [ ] 更新 README.md

**产出文件**:
- `config/dependencies.py`
- `config/portfolio.yaml`
- `pyproject.toml`
- `tests/unit/`
- `tests/integration/`

---

## 任务总览

| 任务 | 阶段 | 工时 | 产出 |
|------|------|------|------|
| I1-001 | Phase 1 | 3h | core/domain/ |
| I1-002 | Phase 2 | 2h | core/adapters/base.py |
| I1-003 | Phase 3 | 5h | core/services/ |
| I1-004 | Phase 4 | 3h | YAML Repository |
| I1-005 | Phase 4 | 4h | Reminders/Progress Adapter |
| I1-006 | Phase 4 | 2h | Telegram/iMessage Adapter |
| I1-007 | Phase 5 | 3h | CLI |
| I1-008 | Phase 5 | 3h | Skill |
| I1-009 | Phase 6 | 3h | DI + Tests |
| **总计** | | **28h** | **9 个任务** |

---

## 关键检查点

### 架构合规检查
- [ ] I1-001 完成后：Domain 模型无外部依赖
- [ ] I1-002 完成后：适配器接口可 mock
- [ ] I1-003 完成后：Services 可单元测试（纯内存）
- [ ] I1-008 完成后：Skill **不导入 CLI 任何模块**

### 数据流验证
```
Skill ──┐
        ├──→ Services ──→ Domain ──→ Adapters
CLI ────┘
```

---

## 迭代完成标准

- [ ] 所有 9 个任务完成并通过测试
- [ ] Dashboard 可正常显示 Reminders 和 Bot 项目
- [ ] Telegram 对话可查询状态 (Skill → Service，不经过 CLI)
- [ ] CLI 可独立运行 (CLI → Service，不依赖 Skill)
- [ ] 定时报告可正常发送
- [ ] 文档完整，可独立部署

---

## 迭代后回顾 (完成后填写)

> **实际完成时间**: _待填写_  
> **原计划**: 9 个任务，预计 28 小时  
> **实际完成**: _待填写_  
> **偏差分析**: _待填写_

---

*本文档由 clawdbot: Dev 根据架构 v2.0 修订 (v2.0)*
