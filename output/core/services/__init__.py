"""Portfolio Manager 应用服务

本模块导出所有应用服务，供接口层使用。
"""

from .project_service import ProjectService
from .dashboard_service import DashboardService, SummaryDashboard, DetailDashboard, ProjectWithProgress
from .agent_service import AgentService, AgentWorkload
from .commands import (
    CreateProjectCommand,
    UpdateProjectCommand,
    AssignAgentCommand,
    RemoveAgentCommand,
    CreateAgentCommand,
    UpdateAgentCommand,
)

__all__ = [
    # 服务
    "ProjectService",
    "DashboardService",
    "AgentService",
    # 数据对象
    "SummaryDashboard",
    "DetailDashboard",
    "ProjectWithProgress",
    "AgentWorkload",
    # 命令
    "CreateProjectCommand",
    "UpdateProjectCommand",
    "AssignAgentCommand",
    "RemoveAgentCommand",
    "CreateAgentCommand",
    "UpdateAgentCommand",
]
