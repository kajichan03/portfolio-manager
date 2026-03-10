"""Portfolio Manager 领域模型 - Agent 实体

本模块定义 Agent 实体，表示 AI 执行代理。
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .value_objects import AgentId, CommunicationConfig
from .agent_role import AgentRole
from .enums import AgentStatus


@dataclass(frozen=True)
class Agent:
    """Agent 实体 - AI 执行代理
    
    属性:
        id: Agent 唯一标识
        name: 显示名称
        emoji: 可视化标识（如 ☎️, 🎯, 📟）
        role: Agent 角色（coordinator/product/developer/qa）
        communication: 通信配置（渠道、地址等）
        config_path: 配置文件本地路径（可选）
        status: Agent 状态
    """
    id: AgentId
    name: str
    emoji: str
    role: AgentRole
    
    # 通信配置（通用结构，不绑定具体渠道）
    communication: CommunicationConfig
    
    # 配置位置
    config_path: Optional[Path] = None
    
    # 状态
    status: AgentStatus = AgentStatus.ACTIVE
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Agent name cannot be empty")
        if not self.emoji:
            raise ValueError("Agent emoji cannot be empty")
    
    def with_status(self, status: AgentStatus) -> "Agent":
        """返回更新状态后的新 Agent 实例"""
        return Agent(
            id=self.id,
            name=self.name,
            emoji=self.emoji,
            role=self.role,
            communication=self.communication,
            config_path=self.config_path,
            status=status
        )
    
    def with_communication(self, communication: CommunicationConfig) -> "Agent":
        """返回更新通信配置后的新 Agent 实例"""
        return Agent(
            id=self.id,
            name=self.name,
            emoji=self.emoji,
            role=self.role,
            communication=communication,
            config_path=self.config_path,
            status=self.status
        )
    
    @property
    def display_name(self) -> str:
        """获取带 emoji 的显示名称"""
        return f"{self.emoji} {self.name}"
    
    @property
    def is_active(self) -> bool:
        """Agent 是否活跃"""
        return self.status == AgentStatus.ACTIVE
    
    @property
    def channel(self) -> str:
        """获取通信渠道"""
        return self.communication.channel
