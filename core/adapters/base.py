"""Portfolio Manager 适配器抽象接口

本模块定义所有适配器的抽象基类（端口）。
遵循 Hexagonal Architecture，这些接口位于领域层外围，
由具体适配器实现。

关键约束：
- 接口只依赖 core/domain/，不依赖任何具体实现
- 所有方法必须定义完整的类型注解
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from core.domain import Project, ProjectId, ProjectProgress
from core.domain import Agent, AgentId


# ============================================================================
# 异常类
# ============================================================================

class RepositoryError(Exception):
    """仓储操作异常基类"""
    pass


class ProjectNotFoundError(RepositoryError):
    """项目不存在异常
    
    当尝试获取、更新或删除不存在的项目时抛出。
    
    Attributes:
        project_id: 找不到的项目 ID
    """
    
    def __init__(self, project_id: ProjectId):
        self.project_id = project_id
        super().__init__(f"Project not found: {project_id}")


class AgentNotFoundError(RepositoryError):
    """Agent 不存在异常
    
    当尝试获取、更新或删除不存在的 Agent 时抛出。
    
    Attributes:
        agent_id: 找不到的 Agent ID
    """
    
    def __init__(self, agent_id: AgentId):
        self.agent_id = agent_id
        super().__init__(f"Agent not found: {agent_id}")


class DuplicateProjectError(RepositoryError):
    """项目重复异常
    
    当尝试创建已存在的项目时抛出。
    """
    
    def __init__(self, project_id: ProjectId):
        self.project_id = project_id
        super().__init__(f"Project already exists: {project_id}")


class DuplicateAgentError(RepositoryError):
    """Agent 重复异常
    
    当尝试创建已存在的 Agent 时抛出。
    """
    
    def __init__(self, agent_id: AgentId):
        self.agent_id = agent_id
        super().__init__(f"Agent already exists: {agent_id}")


class AdapterError(Exception):
    """适配器操作异常基类"""
    pass


class DataSourceError(AdapterError):
    """数据源访问异常
    
    当访问外部数据源（如 Reminders API、文件系统）失败时抛出。
    """
    
    def __init__(self, message: str, source: str = ""):
        self.source = source
        super().__init__(f"Data source error{' [' + source + ']' if source else ''}: {message}")


class NotificationError(AdapterError):
    """通知发送异常
    
    当发送通知（Telegram/iMessage）失败时抛出。
    """
    
    def __init__(self, message: str, channel: str = ""):
        self.channel = channel
        super().__init__(f"Notification error{' [' + channel + ']' if channel else ''}: {message}")


# ============================================================================
# 过滤器对象
# ============================================================================

@dataclass
class ProjectFilter:
    """项目查询过滤器
    
    用于 ProjectRepository.list() 的过滤条件。
    所有条件都是可选的，多个条件之间是 AND 关系。
    
    Attributes:
        status: 按状态过滤
        source: 按数据源过滤
        priority: 按优先级过滤
        agent_id: 按参与的 Agent 过滤
        type: 按项目类型过滤
    """
    status: Optional[str] = None
    source: Optional[str] = None
    priority: Optional[str] = None
    agent_id: Optional[AgentId] = None
    type: Optional[str] = None
    
    def is_empty(self) -> bool:
        """检查过滤器是否为空（即无过滤条件）"""
        return all(
            v is None
            for v in [self.status, self.source, self.priority, self.agent_id, self.type]
        )


@dataclass
class AgentFilter:
    """Agent 查询过滤器"""
    status: Optional[str] = None
    role: Optional[str] = None
    
    def is_empty(self) -> bool:
        return all(v is None for v in [self.status, self.role])


# ============================================================================
# Repository 接口
# ============================================================================

class ProjectRepository(ABC):
    """项目仓储抽象接口
    
    负责 Project 实体的持久化操作。
    具体实现可以是 YAML、SQLite、或其他存储后端。
    
    注意：此接口只操作 Project（静态配置），
    不操作 ProjectProgress（运行时数据）。
    """
    
    @abstractmethod
    def get(self, project_id: ProjectId) -> Project:
        """根据 ID 获取项目
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Project 实体
            
        Raises:
            ProjectNotFoundError: 项目不存在
        """
        pass
    
    @abstractmethod
    def list(self, filter: Optional[ProjectFilter] = None) -> List[Project]:
        """获取项目列表
        
        Args:
            filter: 可选的过滤条件
            
        Returns:
            符合条件的 Project 列表（不包含运行时数据）
        """
        pass
    
    @abstractmethod
    def save(self, project: Project) -> None:
        """保存项目
        
        如果项目已存在则更新，不存在则创建。
        
        Args:
            project: 要保存的 Project 实体
        """
        pass
    
    @abstractmethod
    def delete(self, project_id: ProjectId) -> None:
        """删除项目
        
        Args:
            project_id: 要删除的项目 ID
            
        Raises:
            ProjectNotFoundError: 项目不存在
        """
        pass
    
    @abstractmethod
    def exists(self, project_id: ProjectId) -> bool:
        """检查项目是否存在
        
        Args:
            project_id: 项目 ID
            
        Returns:
            是否存在
        """
        pass


class AgentRepository(ABC):
    """Agent 仓储抽象接口
    
    负责 Agent 实体的持久化操作。
    """
    
    @abstractmethod
    def get(self, agent_id: AgentId) -> Agent:
        """根据 ID 获取 Agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent 实体
            
        Raises:
            AgentNotFoundError: Agent 不存在
        """
        pass
    
    @abstractmethod
    def list(self, filter: Optional[AgentFilter] = None) -> List[Agent]:
        """获取 Agent 列表
        
        Args:
            filter: 可选的过滤条件
            
        Returns:
            符合条件的 Agent 列表
        """
        pass
    
    @abstractmethod
    def save(self, agent: Agent) -> None:
        """保存 Agent
        
        Args:
            agent: 要保存的 Agent 实体
        """
        pass
    
    @abstractmethod
    def delete(self, agent_id: AgentId) -> None:
        """删除 Agent
        
        Args:
            agent_id: 要删除的 Agent ID
            
        Raises:
            AgentNotFoundError: Agent 不存在
        """
        pass
    
    @abstractmethod
    def exists(self, agent_id: AgentId) -> bool:
        """检查 Agent 是否存在"""
        pass


# ============================================================================
# 数据源适配器接口
# ============================================================================

class ProgressSource(ABC):
    """进度数据源抽象接口
    
    负责从外部数据源获取项目的运行时进度数据。
    具体实现：RemindersAdapter, ProgressAdapter
    """
    
    @abstractmethod
    def get_progress(self, project_id: ProjectId) -> Optional[ProjectProgress]:
        """获取指定项目的进度
        
        如果数据源中没有该项目的进度信息，返回 None。
        
        Args:
            project_id: 项目 ID
            
        Returns:
            ProjectProgress 实体，或 None
            
        Raises:
            DataSourceError: 访问数据源失败
        """
        pass
    
    @abstractmethod
    def can_handle(self, project_id: ProjectId) -> bool:
        """检查此数据源是否能处理指定项目
        
        用于多数据源场景下的路由选择。
        
        Args:
            project_id: 项目 ID
            
        Returns:
            是否能处理
        """
        pass


class TaskSource(ABC):
    """任务数据源抽象接口
    
    负责从外部数据源获取项目的任务列表。
    例如：从 Reminders 列表获取任务。
    """
    
    @abstractmethod
    def get_tasks(self, project_id: ProjectId) -> List[Any]:
        """获取项目的任务列表
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Task 实体列表
            
        Raises:
            DataSourceError: 访问数据源失败
        """
        pass


# ============================================================================
# 通知适配器接口
# ============================================================================

class NotificationAdapter(ABC):
    """通知渠道抽象接口
    
    负责向用户或 Agent 发送通知。
    具体实现：TelegramAdapter, IMessageAdapter
    """
    
    @abstractmethod
    def send(self, config: Dict[str, Any], message: str) -> bool:
        """发送通知
        
        Args:
            config: 渠道特定的配置（如 chat_id, handle）
            message: 消息内容
            
        Returns:
            是否发送成功
            
        Raises:
            NotificationError: 发送失败
        """
        pass
    
    @abstractmethod
    def get_channel_name(self) -> str:
        """获取渠道名称
        
        Returns:
            渠道标识符（如 "telegram", "imessage"）
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否有效
        
        Args:
            config: 配置字典
            
        Returns:
            配置是否有效
        """
        pass


# ============================================================================
# 复合适配器（用于聚合多个数据源）
# ============================================================================

class CompositeProgressSource(ProgressSource):
    """组合多个 ProgressSource 的复合适配器
    
    按优先级顺序尝试多个数据源，返回第一个成功的结果。
    """
    
    def __init__(self, sources: List[ProgressSource]):
        self._sources = sources
    
    def get_progress(self, project_id: ProjectId) -> Optional[ProjectProgress]:
        """按顺序尝试所有数据源"""
        for source in self._sources:
            try:
                progress = source.get_progress(project_id)
                if progress is not None:
                    return progress
            except DataSourceError:
                continue
        return None
    
    def can_handle(self, project_id: ProjectId) -> bool:
        """只要有一个数据源能处理就返回 True"""
        return any(source.can_handle(project_id) for source in self._sources)
