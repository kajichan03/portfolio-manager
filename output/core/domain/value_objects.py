"""Portfolio Manager 领域模型 - 值对象

本模块定义领域中的值对象（Value Objects）。
值对象是不可变的，通过属性相等性进行比较。
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProjectId:
    """项目 ID 值对象
    
    使用 slug 格式（小写字母、数字、连字符）
    示例: "portfolio-manager", "tech-research-2024"
    """
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("ProjectId cannot be empty")
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ProjectId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class AgentId:
    """Agent ID 值对象
    
    示例: "clawd", "pd", "dev", "test"
    """
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("AgentId cannot be empty")
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AgentId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class TaskId:
    """任务 ID 值对象"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("TaskId cannot be empty")
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TaskId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class CommunicationConfig:
    """通信配置值对象
    
    通用结构，不绑定具体通信渠道。
    
    示例:
    - Telegram: CommunicationConfig("telegram", {"chat_id": "123456"})
    - iMessage: CommunicationConfig("imessage", {"handle": "user@example.com"})
    """
    channel: str
    config: dict
    
    def __post_init__(self):
        if not self.channel:
            raise ValueError("channel cannot be empty")
        if self.config is None:
            object.__setattr__(self, 'config', {})
    
    def get(self, key: str, default=None):
        """获取配置项"""
        return self.config.get(key, default)
