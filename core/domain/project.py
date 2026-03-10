"""Portfolio Manager 领域模型 - Project 实体

本模块定义 Project 实体，存储项目的静态配置信息。

注意：运行时数据（进度、阻塞项等）存储在 ProjectProgress 中，
避免与 progress.json / projects.yaml 产生同步问题。
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, FrozenSet

from .value_objects import ProjectId, AgentId
from .enums import ProjectType, DataSource, Priority, ProjectStatus


@dataclass(frozen=True)
class Project:
    """项目实体 - 静态配置信息
    
    Project 只存储不随时间变化的配置信息。
    运行时数据（进度百分比、当前阶段、阻塞项等）
    由 ProjectProgress 实体管理。
    
    这种分离避免了 projects.yaml 与 progress.json 之间的同步问题。
    
    属性:
        id: 项目唯一标识
        name: 显示名称
        type: 项目类型（专门项目/日常运营）
        source: 数据源类型（Reminders/Bot项目）
        priority: 优先级（high/medium/low）
        status: 项目状态（active/paused/completed/archived）
        local_path: 本地路径（可选）
        github_url: GitHub 地址（可选）
        agent_ids: 参与的 Agent ID 集合
        created_at: 创建时间
        updated_at: 最后更新时间
    """
    id: ProjectId
    name: str
    type: ProjectType
    source: DataSource
    priority: Priority
    status: ProjectStatus
    
    # 位置信息（可选）
    local_path: Optional[Path] = None
    github_url: Optional[str] = None
    
    # 关联（只存 ID，不存对象）
    agent_ids: FrozenSet[AgentId] = field(default_factory=frozenset)
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Project name cannot be empty")
    
    def with_agent(self, agent_id: AgentId) -> "Project":
        """返回添加 Agent 后的新项目实例
        
        由于 Project 是不可变的，此方法返回新实例。
        """
        new_agents = set(self.agent_ids)
        new_agents.add(agent_id)
        return Project(
            id=self.id,
            name=self.name,
            type=self.type,
            source=self.source,
            priority=self.priority,
            status=self.status,
            local_path=self.local_path,
            github_url=self.github_url,
            agent_ids=frozenset(new_agents),
            created_at=self.created_at,
            updated_at=datetime.now()
        )
    
    def without_agent(self, agent_id: AgentId) -> "Project":
        """返回移除 Agent 后的新项目实例"""
        new_agents = set(self.agent_ids)
        new_agents.discard(agent_id)
        return Project(
            id=self.id,
            name=self.name,
            type=self.type,
            source=self.source,
            priority=self.priority,
            status=self.status,
            local_path=self.local_path,
            github_url=self.github_url,
            agent_ids=frozenset(new_agents),
            created_at=self.created_at,
            updated_at=datetime.now()
        )
    
    def with_status(self, status: ProjectStatus) -> "Project":
        """返回更新状态后的新项目实例"""
        return Project(
            id=self.id,
            name=self.name,
            type=self.type,
            source=self.source,
            priority=self.priority,
            status=status,
            local_path=self.local_path,
            github_url=self.github_url,
            agent_ids=self.agent_ids,
            created_at=self.created_at,
            updated_at=datetime.now()
        )
    
    def with_priority(self, priority: Priority) -> "Project":
        """返回更新优先级后的新项目实例"""
        return Project(
            id=self.id,
            name=self.name,
            type=self.type,
            source=self.source,
            priority=priority,
            status=self.status,
            local_path=self.local_path,
            github_url=self.github_url,
            agent_ids=self.agent_ids,
            created_at=self.created_at,
            updated_at=datetime.now()
        )
