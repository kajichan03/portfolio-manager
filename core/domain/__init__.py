"""Portfolio Manager 领域模型

本模块导出所有领域实体、值对象和枚举，供其他层使用。

使用示例:
    from core.domain import Project, ProjectId, ProjectType
    from core.domain import Agent, AgentId, AgentRole
    from core.domain import Task, TaskId, TaskStatus
    from core.domain import ProjectProgress
    from core.domain import Priority, DataSource
"""

# 实体
from .project import Project
from .progress import ProjectProgress
from .task import Task
from .agent import Agent

# 值对象
from .value_objects import ProjectId, AgentId, TaskId, CommunicationConfig

# 枚举
from .enums import (
    ProjectType,
    DataSource,
    Priority,
    ProjectStatus,
    TaskStatus,
    AgentStatus,
)
from .agent_role import AgentRole

__all__ = [
    # 实体
    "Project",
    "ProjectProgress",
    "Task",
    "Agent",
    # 值对象
    "ProjectId",
    "AgentId",
    "TaskId",
    "CommunicationConfig",
    # 枚举
    "ProjectType",
    "DataSource",
    "Priority",
    "ProjectStatus",
    "TaskStatus",
    "AgentStatus",
    "AgentRole",
]
