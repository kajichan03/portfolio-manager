# Portfolio Manager

集中度量、管理所有资源和任务

## 项目目标

建立一个中心化的项目组合管理系统，追踪：
- **资源**：我 (Neal) 和各种 Clawdbot
- **任务**：所有推进中的项目

## 核心原则

1. **单一真相源**：所有项目状态在此汇总
2. **资源可视化**：清楚知道谁/什么在做什么
3. **任务可追溯**：每个任务有归属、有状态、有进度

## 目录结构

```
portfolio-manager/
├── README.md              # 本文件
├── AGENTS.md              # AI 助手工作准则
├── architecture.md        # 架构设计文档
├── iteration-plan.md      # 迭代计划
├── progress.md            # 当前进度
├── decisions.md           # 决策记录
├── requirements.md        # 需求文档
└── output/                # 项目产出（可独立交付）
    ├── config/            # 配置文件
    │   ├── dependencies.py    # 依赖注入配置
    │   └── portfolio.json     # 主配置
    ├── core/              # 核心业务逻辑 (Hexagonal Architecture)
    │   ├── domain/        # 领域模型
    │   ├── adapters/      # 适配器接口和实现
    │   └── services/      # 应用服务
    ├── interfaces/        # 用户接口层
    │   ├── cli/           # 命令行接口
    │   └── skill/         # OpenClaw Skill 接口
    ├── data/              # 数据存储
    │   ├── projects.json  # 项目数据
    │   └── agents.json    # Agent 数据
    └── tests/             # 测试
        ├── unit/          # 单元测试
        └── integration/   # 集成测试
```

## 快速开始

### 1. 安装依赖

```bash
# 克隆仓库
git clone https://github.com/kajichan03/portfolio-manager.git
cd portfolio-manager

# 安装依赖 (可选，目前仅使用标准库)
# pip install pyyaml  # 如果需要 YAML 支持
```

### 2. 配置

编辑 `output/config/portfolio.json`：

```json
{
  "data_dir": "./data",
  "projects_root": "~/projects",
  "remindctl_path": "remindctl",
  "telegram": {
    "bot_token": "${TELEGRAM_BOT_TOKEN}"
  }
}
```

设置环境变量（可选）：

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
```

### 3. 初始化数据

数据文件已包含初始数据：
- `output/data/projects.json` - 项目列表
- `output/data/agents.json` - Agent 列表（clawd, pd, dev, test）

### 4. 主 Agent 部署

Portfolio Manager 作为主 Agent (Clawd) 的 Skill 运行：

```bash
# 1. 克隆代码
git clone https://github.com/kajichan03/portfolio-manager.git

# 2. 部署到主 Agent workspace
ln -s ~/projects/portfolio-manager/output ~/.openclaw/workspace/output

# 3. 创建标准 Skill 结构
mkdir -p ~/.openclaw/workspace/skills/portfolio
cp ~/projects/portfolio-manager/output/docs/SKILL.md ~/.openclaw/workspace/skills/portfolio/
cp ~/projects/portfolio-manager/output/docs/handlers.py ~/.openclaw/workspace/skills/portfolio/

# 4. 测试
# 现在可以在对话中说"状态"，OpenClaw 会自动调用 Portfolio Manager
```

### 5. 使用 CLI

```bash
cd ~/.openclaw/workspace

# 查看 Dashboard 摘要
python output/interfaces/cli/main.py dashboard

# 查看 Dashboard 详情
python output/interfaces/cli/main.py dashboard --format detail

# 列出所有项目
python output/interfaces/cli/main.py project list

# 创建新项目
python output/interfaces/cli/main.py project create "My New Project" --priority high

# 分配 Agent 到项目
python output/interfaces/cli/main.py project assign portfolio-manager dev
```

### 6. 使用 Skill

在 OpenClaw 中通过对话使用：

```
用户: 状态
Bot: 📊 Portfolio 状态摘要 (2026-03-11)
     项目总数: 1
     ├─ 🟢 进行中: 1
     └─ 🔴 阻塞: 0

用户: 详情
Bot: 📋 项目详情列表...

用户: 项目 portfolio-manager
Bot: 📁 Portfolio Manager
     ID: portfolio-manager
     进度: 95%
     ...

用户: 新建项目 "Tech Research"
Bot: ✅ 项目创建成功!
     ID: tech-research
     ...

用户: 分配 tech-research 给 dev
Bot: ✅ 分配成功!
```

### 7. 运行测试

```bash
cd ~/.openclaw/workspace

# 运行所有测试
python -m unittest discover output/tests

# 运行单元测试
python -m unittest output.tests.unit.test_domain
python -m unittest output.tests.unit.test_services

# 运行集成测试
python -m unittest output.tests.integration.test_repositories
```

## 架构说明

### Hexagonal Architecture (端口与适配器)

```
┌─────────────┐     ┌─────────────┐
│  CLI        │     │  Skill      │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 │
       ┌─────────▼─────────┐
       │  Services         │
       │  (Application)    │
       └─────────┬─────────┘
                 │
       ┌─────────▼─────────┐
       │  Domain           │
       │  (Business Logic) │
       └─────────┬─────────┘
                 │
       ┌─────────▼─────────┐
       │  Adapters         │
       │  (Infrastructure) │
       └───────────────────┘
```

### 关键设计决策

1. **Skill 直接调用 Service**（不经过 CLI）
2. **Project (静态) + ProjectProgress (运行时)** 分离
3. **依赖注入** 通过 ServiceContainer
4. **纯内存可测试** 的 Services

## 数据源

- **JSON Repository**: `output/data/projects.json`, `output/data/agents.json`
- **Reminders**: Apple Reminders 列表（通过 remindctl）
- **Progress**: Bot 项目的 `output/progress.json`

## 通知渠道

- **Telegram**: Bot API
- **iMessage**: macOS Messages.app（通过 AppleScript）

## 开发状态

- **当前迭代**: Iteration 1 - MVP ✅ 完成
- **整体进度**: 100%
- **测试**: 26 个测试全部通过

## 文档

- [architecture.md](architecture.md) - 架构设计文档
- [iteration-plan.md](iteration-plan.md) - 迭代计划
- [progress.md](progress.md) - 当前进度

---

*创建时间: 2026-03-10*  
*最后更新: 2026-03-11*
