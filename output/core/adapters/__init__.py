"""Portfolio Manager 适配器层

本模块导出所有适配器实现，供服务层使用。
"""

# 抽象接口
from .base import (
    ProjectRepository,
    AgentRepository,
    ProgressSource,
    TaskSource,
    NotificationAdapter,
    ProjectFilter,
    AgentFilter,
    RepositoryError,
    ProjectNotFoundError,
    AgentNotFoundError,
    DuplicateProjectError,
    DuplicateAgentError,
    AdapterError,
    DataSourceError,
    NotificationError,
)

# 存储适配器
from .config_adapter import JsonProjectRepository, JsonAgentRepository

# 数据源适配器
from .reminders_adapter import RemindersAdapter
from .progress_adapter import ProgressAdapter

# 通知适配器
from .telegram_adapter import TelegramAdapter
from .imessage_adapter import IMessageAdapter

__all__ = [
    # 抽象接口
    "ProjectRepository",
    "AgentRepository",
    "ProgressSource",
    "TaskSource",
    "NotificationAdapter",
    "ProjectFilter",
    "AgentFilter",
    "RepositoryError",
    "ProjectNotFoundError",
    "AgentNotFoundError",
    "DuplicateProjectError",
    "DuplicateAgentError",
    "AdapterError",
    "DataSourceError",
    "NotificationError",
    # 存储适配器
    "JsonProjectRepository",
    "JsonAgentRepository",
    # 数据源适配器
    "RemindersAdapter",
    "ProgressAdapter",
    # 通知适配器
    "TelegramAdapter",
    "IMessageAdapter",
]
