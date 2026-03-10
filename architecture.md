# Architecture

> **版本**: v2.0  
> **状态**: ✅ 已确认  
> **最后更新**: 2026-03-10

---

## 1. 架构概览

### 1.1 架构风格: Hexagonal Architecture (端口与适配器)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         接口层 (Interfaces)                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │  Skill Adapter  │  │   CLI Adapter   │  │  Future: Web API    │  │
│  │  (Telegram)     │  │  (Command Line) │  │                     │  │
│  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘  │
└───────────┼────────────────────┼─────────────────────┼─────────────┘
            │                    │                     │
            └────────────────────┼─────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      应用层 (Application Services)                   │
│                                                                      │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│   │ ProjectService  │  │ DashboardService│  │   AgentService      │  │
│   │                 │  │                 │  │                     │  │
│   │ • create()      │  │ • summary()     │  │ • assign()          │  │
│   │ • assign_agent()│  │ • detail()      │  │ • notify()          │  │
│   │ • list()        │  │ • report()      │  │ • workload()        │  │
│   └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘  │
└────────────┼────────────────────┼─────────────────────┼─────────────┘
             │                    │                     │
             └────────────────────┼─────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        领域层 (Domain)                               │
│                                                                      │
│   ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────┐     │
│   │   Project   │  │ ProjectProgress │  │       Task          │     │
│   │  (静态信息)  │  │  (运行时数据)    │  │                     │     │
│   │             │  │                 │  │                     │     │
│   │ id          │  │ project_id      │  │ id                  │     │
│   │ name        │  │ percentage      │  │ project_id          │     │
│   │ type        │  │ phase           │  │ title               │     │
│   │ status      │  │ blockers[]      │  │ status              │     │
│   │ source      │  │ next_steps[]    │  │ assignee_id         │     │
│   │ priority    │  │ updated_at      │  │ due_date            │     │
│   └─────────────┘  └─────────────────┘  └─────────────────────┘     │
│                                                                      │
│  NOTE: Project 只存静态配置，运行时数据统一由 ProjectProgress 管理   │
│  避免 projects.yaml 与 progress.json 之间的同步问题                  │
│                                                                      │
│   ┌─────────────┐  ┌─────────────────┐                               │
│   │    Agent    │  │    AgentRole    │  (Enum: product, developer)   │
│   │             │  │                 │                               │
│   │ id          │  └─────────────────┘                               │
│   │ name        │                                                    │
│   │ emoji       │                                                    │
│   │ role        │                                                    │
│   │ status      │                                                    │
│   └─────────────┘                                                    │
└────────────────────────────────────────┬─────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      适配器层 (Adapters)                             │
│                                                                      │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│   │RemindersAdapter │  │ ProgressAdapter │  │  ConfigAdapter      │  │
│   │                 │  │                 │  │                     │  │
│   │ fetch_projects()│  │ load_progress() │  │ load_projects()     │  │
│   │ fetch_tasks()   │  │                 │  │ load_agents()       │  │
│   └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
│                                                                      │
│   ┌─────────────────┐  ┌─────────────────┐                           │
│   │ TelegramAdapter │  │  IMessageAdapter│  (Output Adapters)        │
│   │                 │  │                 │                           │
│   │ send()          │  │ send()          │                           │
│   └─────────────────┘  └─────────────────┘                           │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心设计原则

| 原则 | 说明 |
|------|------|
| **依赖向内** | 外层依赖内层，Domain 不依赖任何外层 |
| **接口隔离** | Skill 和 CLI 都是一等公民，平等调用 Service |
| **可测试性** | Domain 和 Service 纯内存，可单元测试 |
| **可替换性** | 数据源/输出渠道通过适配器接口可替换 |

---

## 2. 目录结构

```
portfolio-manager/
│
├── core/                          # 核心业务逻辑 (Hexagon)
│   ├── __init__.py
│   ├── domain/                    # 领域模型 (最内层)
│   │   ├── __init__.py
│   │   ├── project.py             # Project 实体
│   │   ├── progress.py            # ProjectProgress 实体
│   │   ├── task.py                # Task 实体
│   │   ├── agent.py               # Agent 实体
│   │   ├── agent_role.py          # AgentRole 枚举
│   │   └── enums.py               # 其他枚举 (Priority, Status...)
│   │
│   ├── services/                  # 应用服务 (用例编排)
│   │   ├── __init__.py
│   │   ├── project_service.py     # 项目管理用例
│   │   ├── dashboard_service.py   # Dashboard 生成用例
│   │   └── agent_service.py       # Agent 协调用例
│   │
│   └── adapters/                  # 端口适配器
│       ├── __init__.py
│       ├── base.py                # 适配器抽象基类
│       ├── reminders_adapter.py   # Apple Reminders 适配器
│       ├── progress_adapter.py    # progress.json 适配器
│       ├── config_adapter.py      # YAML 配置适配器
│       ├── telegram_adapter.py    # Telegram 输出适配器
│       └── imessage_adapter.py    # iMessage 输出适配器
│
├── interfaces/                    # 用户接口层
│   ├── skill/                     # OpenClaw Skill
│   │   ├── SKILL.md
│   │   ├── __init__.py
│   │   ├── handlers.py            # 指令处理器
│   │   └── coordinator.py         # Agent 协调器
│   │
│   └── cli/                       # 命令行接口
│       ├── __init__.py
│       ├── main.py                # 入口点
│       ├── commands/              # 子命令
│       │   ├── dashboard.py
│       │   ├── project.py
│       │   ├── sync.py
│       │   └── report.py
│       └── formatters/            # 输出格式化
│           └── text_formatter.py
│
├── data/                          # 数据存储 (file-based DB)
│   ├── projects.yaml              # 项目注册表 (静态)
│   ├── agents.yaml                # Agent 注册表
│   └── schemas/                   # Schema 定义
│       └── progress-schema.v1.json
│
├── config/                        # 配置
│   └── portfolio.yaml
│
├── tests/                         # 测试
│   ├── unit/                      # 单元测试 (domain, services)
│   ├── integration/               # 集成测试 (adapters)
│   └── e2e/                       # 端到端测试
│
├── pyproject.toml                 # Python 项目配置
└── README.md
```

---

## 3. 领域模型 (Domain)

### 3.1 Project (项目) - 静态信息

```python
@dataclass(frozen=True)
class Project:
    """项目静态信息 (不随时间变化)"""
    id: ProjectId                    # 唯一标识 (值对象)
    name: str                        # 显示名称
    type: ProjectType                # dedicated | operation
    source: DataSource               # reminders | bot_project
    priority: Priority               # high | medium | low
    status: ProjectStatus            # active | paused | completed | archived
    
    # 位置信息
    local_path: Optional[Path] = None
    github_url: Optional[str] = None
    
    # 关联 (只存 ID，不存对象)
    agent_ids: FrozenSet[AgentId] = field(default_factory=frozenset)
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # NOTE: 运行时数据 (进度、阻塞项等) 存储在 ProjectProgress 中
    # 避免与 progress.json / projects.yaml 产生同步问题
```

### 3.2 ProjectProgress (项目进度) - 运行时信息

```python
@dataclass
class ProjectProgress:
    """项目动态进度 (从不同数据源聚合)"""
    project_id: ProjectId
    
    # 进度信息
    percentage: int                  # 0-100
    phase: str                       # 当前阶段描述
    
    # 任务状态
    next_steps: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    
    # 统计
    tasks_total: int = 0
    tasks_completed: int = 0
    
    # 时间戳
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_blocked(self) -> bool:
        return len(self.blockers) > 0
```

### 3.3 Task (任务) - 纯净领域模型

```python
@dataclass(frozen=True)
class Task:
    """任务领域模型 (与数据源解耦)"""
    id: TaskId
    project_id: ProjectId
    title: str
    status: TaskStatus               # todo | in_progress | review | done | blocked
    
    # 可选属性
    assignee_id: Optional[AgentId] = None
    due_date: Optional[date] = None
    priority: Priority = Priority.medium
```

### 3.4 Agent (执行代理)

```python
@dataclass(frozen=True)
class Agent:
    """Agent 领域模型"""
    id: AgentId
    name: str
    emoji: str
    role: AgentRole                  # product | developer | qa | coordinator | ...
    
    # 通信配置 (通用结构，不绑定具体渠道)
    communication: CommunicationConfig
    
    # 配置位置
    config_path: Optional[Path] = None
    
    status: AgentStatus = AgentStatus.active
```

### 3.5 AgentRole (枚举)

```python
class AgentRole(Enum):
    """Agent 角色枚举 (可扩展)"""
    COORDINATOR = "coordinator"      # 主协调者 (Clawd)
    PRODUCT = "product"              # 产品经理
    DEVELOPER = "developer"          # 开发工程师
    QA = "qa"                        # 测试/验证
    # 未来可扩展:
    # DESIGN = "design"
    # RESEARCH = "research"
    # OPS = "ops"
```

### 3.6 其他枚举

```python
class ProjectType(Enum):
    DEDICATED = "dedicated"          # 专门项目 (有开始有结束)
    OPERATION = "operation"          # 日常运营 (持续进行)

class DataSource(Enum):
    REMINDERS = "reminders"          # Apple Reminders
    BOT_PROJECT = "bot_project"      # Bot 本地项目

class Priority(Enum):
    HIGH = "high"                    # 🔴
    MEDIUM = "medium"                # 🟡
    LOW = "low"                      # 🟢

class ProjectStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

class AgentStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
```

### 3.7 值对象

```python
@dataclass(frozen=True)
class ProjectId:
    """项目 ID 值对象"""
    value: str
    
    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class AgentId:
    """Agent ID 值对象"""
    value: str
    
    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class TaskId:
    """任务 ID 值对象"""
    value: str

@dataclass
class CommunicationConfig:
    """通信配置 (通用结构)"""
    channel: str                     # "telegram" | "imessage" | ...
    config: Dict[str, Any] = field(default_factory=dict)
    # Telegram: {"chat_id": "..."}
    # iMessage: {"handle": "..."}
```

---

## 4. 应用服务 (Services)

### 4.1 ProjectService

```python
class ProjectService:
    """项目管理应用服务"""
    
    def __init__(
        self,
        project_repo: ProjectRepository,
        progress_repo: ProgressRepository,
        event_bus: Optional[EventBus] = None
    ):
        self._project_repo = project_repo
        self._progress_repo = progress_repo
        self._event_bus = event_bus
    
    def create_project(self, cmd: CreateProjectCommand) -> Project:
        """创建新项目"""
        project = Project(
            id=ProjectId(generate_slug(cmd.name)),
            name=cmd.name,
            type=cmd.type,
            source=cmd.source,
            priority=cmd.priority,
            status=ProjectStatus.ACTIVE,
            local_path=cmd.local_path,
            github_url=cmd.github_url,
        )
        self._project_repo.save(project)
        
        if self._event_bus:
            self._event_bus.publish(ProjectCreatedEvent(project.id))
        
        return project
    
    def assign_agent(self, project_id: ProjectId, agent_id: AgentId) -> Project:
        """分配 Agent 到项目"""
        project = self._project_repo.get(project_id)
        updated = project.with_agent(agent_id)
        self._project_repo.save(updated)
        return updated
    
    def list_projects(self, filter: Optional[ProjectFilter] = None) -> List[Project]:
        """列出项目 (不含进度)"""
        return self._project_repo.list(filter)
    
    def get_project_with_progress(self, project_id: ProjectId) -> Tuple[Project, Optional[ProjectProgress]]:
        """获取项目及其进度"""
        project = self._project_repo.get(project_id)
        progress = self._progress_repo.get(project_id)
        return project, progress
```

### 4.2 DashboardService

```python
class DashboardService:
    """Dashboard 生成应用服务"""
    
    def __init__(
        self,
        project_service: ProjectService,
        progress_sources: List[ProgressSource],
        formatter: DashboardFormatter
    ):
        self._project_service = project_service
        self._progress_sources = progress_sources
        self._formatter = formatter
    
    def generate_summary(self) -> SummaryDashboard:
        """生成摘要 Dashboard"""
        projects = self._project_service.list_projects()
        
        # 并行获取所有项目进度
        progresses = self._fetch_progresses([p.id for p in projects])
        
        # 统计
        total = len(projects)
        active = sum(1 for p in progresses.values() if p and not p.is_blocked)
        blocked = sum(1 for p in progresses.values() if p and p.is_blocked)
        
        # 需要关注的项目
        attention_needed = self._find_attention_needed(projects, progresses)
        
        return SummaryDashboard(
            total=total,
            active=active,
            blocked=blocked,
            attention_needed=attention_needed,
            generated_at=datetime.now()
        )
    
    def generate_detail(self, priority_filter: Optional[Priority] = None) -> DetailDashboard:
        """生成详情 Dashboard"""
        projects = self._project_service.list_projects()
        progresses = self._fetch_progresses([p.id for p in projects])
        
        # 按优先级分组
        by_priority: Dict[Priority, List[ProjectWithProgress]] = defaultdict(list)
        for project in projects:
            if priority_filter and project.priority != priority_filter:
                continue
            progress = progresses.get(project.id)
            by_priority[project.priority].append(
                ProjectWithProgress(project, progress)
            )
        
        return DetailDashboard(
            high_priority=by_priority[Priority.HIGH],
            medium_priority=by_priority[Priority.MEDIUM],
            low_priority=by_priority[Priority.LOW],
            generated_at=datetime.now()
        )
    
    def _fetch_progresses(self, project_ids: List[ProjectId]) -> Dict[ProjectId, Optional[ProjectProgress]]:
        """从多个数据源获取进度"""
        result = {}
        for pid in project_ids:
            for source in self._progress_sources:
                progress = source.get_progress(pid)
                if progress:
                    result[pid] = progress
                    break
            else:
                result[pid] = None
        return result
```

### 4.3 AgentService

```python
class AgentService:
    """Agent 协调应用服务"""
    
    def __init__(
        self,
        agent_repo: AgentRepository,
        notification_adapters: Dict[str, NotificationAdapter]
    ):
        self._agent_repo = agent_repo
        self._notification_adapters = notification_adapters
    
    def notify_assignment(self, agent_id: AgentId, project: Project) -> bool:
        """通知 Agent 被分配到项目"""
        agent = self._agent_repo.get(agent_id)
        
        message = self._format_assignment_message(agent, project)
        
        # 根据 Agent 配置的渠道发送通知
        adapter = self._notification_adapters.get(agent.communication.channel)
        if adapter:
            return adapter.send(agent.communication.config, message)
        return False
    
    def get_agent_workload(self, agent_id: AgentId) -> AgentWorkload:
        """获取 Agent 工作负载"""
        # 查询该 Agent 参与的所有活跃项目
        pass
```

---

## 5. 适配器层 (Adapters)

### 5.1 抽象基类

```python
# core/adapters/base.py

class ProjectRepository(ABC):
    """项目存储抽象"""
    
    @abstractmethod
    def get(self, project_id: ProjectId) -> Project:
        pass
    
    @abstractmethod
    def list(self, filter: Optional[ProjectFilter] = None) -> List[Project]:
        pass
    
    @abstractmethod
    def save(self, project: Project) -> None:
        pass

class ProgressSource(ABC):
    """进度数据源抽象"""
    
    @abstractmethod
    def get_progress(self, project_id: ProjectId) -> Optional[ProjectProgress]:
        """获取指定项目的进度"""
        pass

class NotificationAdapter(ABC):
    """通知渠道抽象"""
    
    @abstractmethod
    def send(self, config: Dict[str, Any], message: str) -> bool:
        pass
```

### 5.2 ConfigAdapter (YAML 存储)

```python
class YamlProjectRepository(ProjectRepository):
    """基于 YAML 的项目存储"""
    
    def __init__(self, data_dir: Path):
        self._projects_file = data_dir / "projects.yaml"
        self._agents_file = data_dir / "agents.yaml"
    
    def get(self, project_id: ProjectId) -> Project:
        projects = self._load_projects()
        for p in projects:
            if p.id == project_id:
                return p
        raise ProjectNotFoundError(project_id)
    
    def list(self, filter: Optional[ProjectFilter] = None) -> List[Project]:
        projects = self._load_projects()
        if filter:
            projects = [p for p in projects if self._matches_filter(p, filter)]
        return projects
    
    def save(self, project: Project) -> None:
        projects = self._load_projects()
        # 更新或追加
        existing = [i for i, p in enumerate(projects) if p.id == project.id]
        if existing:
            projects[existing[0]] = project
        else:
            projects.append(project)
        self._save_projects(projects)
    
    def _load_projects(self) -> List[Project]:
        if not self._projects_file.exists():
            return []
        with open(self._projects_file) as f:
            data = yaml.safe_load(f)
        return [self._deserialize_project(p) for p in data.get("projects", [])]
```

### 5.3 RemindersAdapter

```python
class RemindersAdapter(ProgressSource):
    """Apple Reminders 数据源适配器"""
    
    def __init__(self, remindctl_path: str = "remindctl"):
        self._remindctl = remindctl_path
    
    def get_progress(self, project_id: ProjectId) -> Optional[ProjectProgress]:
        """
        Reminders 列表映射为项目进度:
        - 列表名 = 项目名
        - 任务完成率 = 进度百分比
        - 未完成任务 = next_steps
        """
        list_data = self._fetch_list(str(project_id))
        if not list_data:
            return None
        
        tasks = list_data.get("tasks", [])
        total = len(tasks)
        completed = sum(1 for t in tasks if t.get("completed"))
        
        percentage = int(completed / total * 100) if total > 0 else 0
        
        return ProjectProgress(
            project_id=project_id,
            percentage=percentage,
            phase="运营中" if list_data.get("type") == "operation" else "进行中",
            next_steps=[t["title"] for t in tasks if not t.get("completed")][:5],
            tasks_total=total,
            tasks_completed=completed,
            updated_at=datetime.now()
        )
    
    def _fetch_list(self, list_name: str) -> Optional[Dict]:
        """调用 remindctl 获取列表数据"""
        result = subprocess.run(
            [self._remindctl, "list", list_name, "--json"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
```

### 5.4 ProgressAdapter

```python
class ProgressAdapter(ProgressSource):
    """Bot 项目 progress.json 适配器"""
    
    def __init__(self, projects_root: Path):
        self._projects_root = projects_root
    
    def get_progress(self, project_id: ProjectId) -> Optional[ProjectProgress]:
        """
        从项目目录读取 progress.json
        路径: {projects_root}/{project_id}/output/progress.json
        """
        progress_file = self._projects_root / str(project_id) / "output" / "progress.json"
        
        if not progress_file.exists():
            return None
        
        with open(progress_file) as f:
            data = json.load(f)
        
        # 验证 Schema
        self._validate_schema(data)
        
        return ProjectProgress(
            project_id=project_id,
            percentage=data["progress_percentage"],
            phase=data["current_phase"],
            next_steps=data.get("next_steps", []),
            blockers=data.get("blockers", []),
            tasks_total=len(data.get("tasks", [])),
            tasks_completed=sum(1 for t in data.get("tasks", []) 
                              if t.get("status") == "done"),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
```

### 5.5 TelegramAdapter

```python
class TelegramAdapter(NotificationAdapter):
    """Telegram 通知适配器"""
    
    def __init__(self, bot_token: str):
        self._bot_token = bot_token
        self._base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send(self, config: Dict[str, Any], message: str) -> bool:
        chat_id = config.get("chat_id")
        if not chat_id:
            return False
        
        response = requests.post(
            f"{self._base_url}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        )
        return response.status_code == 200
```

---

## 6. 接口层 (Interfaces)

### 6.1 Skill 指令映射

```python
# interfaces/skill/handlers.py

class SkillCommandBus:
    """Skill 指令总线"""
    
    def __init__(self, services: ServiceContainer):
        self._services = services
        self._handlers = {
            r"^(状态|summary|status)$": StatusHandler(services.dashboard),
            r"^(详情|list|projects)$": ListHandler(services.dashboard),
            r"^项目\s+(.+)$": ProjectDetailHandler(services.project, services.dashboard),
            r"^新建项目\s+(.+)$": CreateProjectHandler(services.project),
            r"^分配\s+(.+)\s+给\s+(.+)$": AssignHandler(services.project, services.agent),
            r"^设置优先级\s+(.+)\s+(高|中|低)$": SetPriorityHandler(services.project),
        }
    
    def dispatch(self, message: str) -> str:
        """分派指令并返回响应"""
        for pattern, handler in self._handlers.items():
            match = re.match(pattern, message.strip())
            if match:
                return handler.handle(*match.groups())
        return "未知指令。可用: 状态、详情、项目 {名称}、新建项目 {名称}、分配 {项目} 给 {Agent}"

class StatusHandler:
    """状态查询处理器"""
    
    def __init__(self, dashboard_service: DashboardService):
        self._dashboard = dashboard_service
    
    def handle(self) -> str:
        summary = self._dashboard.generate_summary()
        return self._format_summary(summary)
    
    def _format_summary(self, summary: SummaryDashboard) -> str:
        return f"""📊 Portfolio 状态摘要 ({summary.generated_at.strftime('%Y-%m-%d')})

项目总数: {summary.total}
├─ 🟢 进行中: {summary.active}
└─ 🔴 阻塞: {summary.blocked}

⚠️ 需要关注:
{self._format_attention(summary.attention_needed)}

💬 回复 "详情" 查看完整列表"""
```

### 6.2 CLI 命令

```python
# interfaces/cli/commands/dashboard.py

import click
from core.services.dashboard_service import DashboardService

@click.group()
def cli():
    """Portfolio Manager CLI"""
    pass

@cli.command()
@click.option('--format', 'fmt', type=click.Choice(['summary', 'detail']), default='summary')
@click.option('--priority', type=click.Choice(['high', 'medium', 'low']), default=None)
def dashboard(fmt: str, priority: Optional[str]):
    """生成 Dashboard"""
    services = create_service_container()
    
    if fmt == 'summary':
        result = services.dashboard.generate_summary()
        click.echo(format_summary(result))
    else:
        priority_enum = Priority(priority) if priority else None
        result = services.dashboard.generate_detail(priority_enum)
        click.echo(format_detail(result))

@cli.command()
@click.argument('project_name')
@click.argument('agent_name')
def assign(project_name: str, agent_name: str):
    """分配 Agent 到项目"""
    services = create_service_container()
    
    project = services.project.assign_agent(
        ProjectId(project_name),
        AgentId(agent_name)
    )
    
    # 发送通知
    services.agent.notify_assignment(AgentId(agent_name), project)
    
    click.echo(f"✅ 已将项目 '{project_name}' 分配给 {agent_name}")
```

---

## 7. 依赖注入配置

```python
# config/dependencies.py

from core.adapters.config_adapter import YamlProjectRepository, YamlAgentRepository
from core.adapters.reminders_adapter import RemindersAdapter
from core.adapters.progress_adapter import ProgressAdapter
from core.adapters.telegram_adapter import TelegramAdapter
from core.services.project_service import ProjectService
from core.services.dashboard_service import DashboardService
from core.services.agent_service import AgentService

class ServiceContainer:
    """服务容器 (依赖注入)"""
    
    def __init__(self, config: Config):
        # Repositories
        self.project_repo = YamlProjectRepository(config.data_dir)
        self.agent_repo = YamlAgentRepository(config.data_dir)
        
        # Progress Sources
        self.progress_sources = [
            RemindersAdapter(config.remindctl_path),
            ProgressAdapter(config.projects_root),
        ]
        
        # Notification Adapters
        self.notification_adapters = {
            "telegram": TelegramAdapter(config.telegram_bot_token),
            "imessage": IMessageAdapter(),  # 复用现有 skill
        }
        
        # Services
        self.project = ProjectService(self.project_repo)
        self.dashboard = DashboardService(
            self.project,
            self.progress_sources,
            TextFormatter()
        )
        self.agent = AgentService(
            self.agent_repo,
            self.notification_adapters
        )

def create_service_container() -> ServiceContainer:
    config = load_config()
    return ServiceContainer(config)
```

---

## 8. 数据流 (修正后)

### 8.1 Skill 查询 Dashboard

```
用户: "状态"
  │
  ▼
┌─────────────────────────┐
│  interfaces/skill/      │  解析指令 → 调用 Service
│  StatusHandler          │  (不经过 CLI!)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  core/services/         │  DashboardService.generate_summary()
│  DashboardService       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  core/adapters/         │  并行调用 Progress Sources
│  RemindersAdapter       │  ProgressAdapter
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  返回 SummaryDashboard  │
│  → Skill 格式化为消息   │
└─────────────────────────┘
```

### 8.2 CLI 查询 Dashboard

```
$ portfolio dashboard --format summary
  │
  ▼
┌─────────────────────────┐
│  interfaces/cli/        │  解析参数 → 调用 Service
│  dashboard command      │  (与 Skill 同路径!)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  core/services/         │  DashboardService.generate_summary()
│  DashboardService       │  (与 Skill 同路径!)
└───────────┬─────────────┘
            │
            │ (同上，复用所有逻辑)
            ▼
```

---

## 9. 关键改进总结

| 问题 | v1.0 | v2.0 (修正后) |
|------|------|---------------|
| **Skill → CLI** | ❌ 反模式，性能差 | ✅ Skill 直接调用 Service |
| **目录结构** | cli/ 包含所有逻辑 | ✅ core/ + interfaces/ 分离 |
| **Project 模型** | 太胖，包含运行时数据 | ✅ Project + ProjectProgress 分离 |
| **数据同步** | Project 和 Progress 重复 | ✅ Project 纯静态，Progress 管运行时 |
| **Task 耦合** | reminders_task_id 污染 Domain | ✅ 纯净 Task，Adapter 负责映射 |
| **Agent 角色** | 简单字符串 | ✅ AgentRole 枚举，可扩展 |
| **可测试性** | CLI 难以测试 | ✅ Service/Domain 纯内存可测 |

### 数据存储边界

| 文件 | 存储内容 | 写入方 |
|------|----------|--------|
| `projects.yaml` | Project (静态配置) | ProjectService |
| `progress.json` | ProjectProgress (运行时) | Bot Skill / RemindersAdapter |
| `agents.yaml` | Agent (静态配置) | AgentService |

---

## 10. 待决策事项

| 事项 | 选项 | 建议 |
|------|------|------|
| **Repository 实现** | A) 纯 YAML<br>B) SQLite + YAML 元数据 | **A** MVP 保持简单 |
| **并发策略** | A) asyncio<br>B) 多线程<br>C) 同步 | **A** 适配器 IO 为主 |
| **缓存层** | A) 无缓存<br>B) 内存缓存<br>C) 文件缓存 | **A** 实时查询优先 |

---

*本文档由 clawdbot: Dev 根据 Review 反馈修订 (v2.0)*
