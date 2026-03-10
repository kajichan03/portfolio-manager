"""Portfolio Manager 应用服务 - 命令对象

本模块定义应用服务使用的命令和查询对象。
遵循 CQRS 思想，将写操作（Command）和读操作（Query）分离。
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from output.core.domain import ProjectType, DataSource, Priority, AgentId


# ============================================================================
# Project Commands
# ============================================================================

@dataclass
class CreateProjectCommand:
    """创建项目命令
    
    Attributes:
        name: 项目名称
        type: 项目类型
        source: 数据源类型
        priority: 优先级
        local_path: 本地路径（可选）
        github_url: GitHub 地址（可选）
    """
    name: str
    type: ProjectType
    source: DataSource
    priority: Priority = Priority.MEDIUM
    local_path: Optional[Path] = None
    github_url: Optional[str] = None


@dataclass
class UpdateProjectCommand:
    """更新项目命令"""
    project_id: str
    name: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[str] = None


@dataclass
class AssignAgentCommand:
    """分配 Agent 到项目命令"""
    project_id: str
    agent_id: str


@dataclass
class RemoveAgentCommand:
    """从项目移除 Agent 命令"""
    project_id: str
    agent_id: str


# ============================================================================
# Agent Commands
# ============================================================================

@dataclass
class CreateAgentCommand:
    """创建 Agent 命令"""
    id: str
    name: str
    emoji: str
    role: str
    channel: str
    channel_config: dict
    config_path: Optional[Path] = None


@dataclass
class UpdateAgentCommand:
    """更新 Agent 命令"""
    agent_id: str
    name: Optional[str] = None
    status: Optional[str] = None


# ============================================================================
# Dashboard Queries
# ============================================================================

@dataclass
class DashboardSummary:
    """Dashboard 摘要数据"""
    total: int
    active: int
    blocked: int
    attention_needed: list  # List[AttentionItem]
    generated_at: str


@dataclass
class AttentionItem:
    """需要关注的项目项"""
    project_id: str
    project_name: str
    priority: str
    reason: str  # "due_today", "blocked", "waiting_review"
    assignee: Optional[str]


@dataclass
class ProjectWithProgress:
    """项目及其进度数据"""
    project: 'Project'  # Forward reference
    progress: Optional['ProjectProgress']


@dataclass
class DetailDashboard:
    """详情 Dashboard 数据"""
    high_priority: list  # List[ProjectWithProgress]
    medium_priority: list
    low_priority: list
    generated_at: str
