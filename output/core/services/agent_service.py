"""Portfolio Manager 应用服务 - AgentService

本模块实现 Agent 协调相关的应用服务。
负责 Agent 管理、任务分配通知、工作负载查询等。
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from output.core.domain import Agent, AgentId, Project, ProjectStatus
from output.core.adapters.base import (
    AgentRepository, NotificationAdapter,
    AgentNotFoundError, DuplicateAgentError, NotificationError
)


@dataclass
class AgentWorkload:
    """Agent 工作负载数据"""
    agent_id: str
    agent_name: str
    total_projects: int
    active_projects: int
    blocked_projects: int
    projects: List[Dict[str, Any]]  # 项目简要信息


class AgentService:
    """Agent 协调应用服务
    
    负责 Agent 的生命周期管理、通知发送、工作负载查询。
    
    Attributes:
        _agent_repo: Agent 仓储接口
        _notification_adapters: 通知渠道适配器字典
    """
    
    def __init__(
        self,
        agent_repo: AgentRepository,
        notification_adapters: Dict[str, NotificationAdapter]
    ):
        self._agent_repo = agent_repo
        self._notification_adapters = notification_adapters
    
    def get_agent(self, agent_id: AgentId) -> Agent:
        """获取 Agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent 实体
            
        Raises:
            AgentNotFoundError: Agent 不存在
        """
        return self._agent_repo.get(agent_id)
    
    def list_agents(self, status: Optional[str] = None) -> List[Agent]:
        """列出 Agent
        
        Args:
            status: 按状态过滤
            
        Returns:
            Agent 列表
        """
        from output.core.adapters.base import AgentFilter
        
        filter = AgentFilter(status=status) if status else None
        return self._agent_repo.list(filter)
    
    def notify_assignment(self, agent_id: AgentId, project: Project) -> bool:
        """通知 Agent 被分配到项目
        
        根据 Agent 配置的通信渠道发送通知。
        
        Args:
            agent_id: Agent ID
            project: 被分配的项目
            
        Returns:
            通知是否发送成功
            
        Raises:
            AgentNotFoundError: Agent 不存在
            NotificationError: 发送失败
        """
        agent = self._agent_repo.get(agent_id)
        
        # 构建通知消息
        message = self._format_assignment_message(agent, project)
        
        # 获取对应渠道的适配器
        channel = agent.communication.channel
        adapter = self._notification_adapters.get(channel)
        
        if not adapter:
            raise NotificationError(
                f"No adapter found for channel: {channel}",
                channel=channel
            )
        
        # 发送通知
        try:
            return adapter.send(agent.communication.config, message)
        except Exception as e:
            raise NotificationError(
                str(e),
                channel=channel
            ) from e
    
    def notify_project_update(
        self,
        agent_id: AgentId,
        project: Project,
        update_type: str,
        details: str
    ) -> bool:
        """通知 Agent 项目更新
        
        Args:
            agent_id: Agent ID
            project: 更新的项目
            update_type: 更新类型（如 "status_changed", "blocked"）
            details: 更新详情
            
        Returns:
            通知是否发送成功
        """
        agent = self._agent_repo.get(agent_id)
        
        message = self._format_update_message(agent, project, update_type, details)
        
        channel = agent.communication.channel
        adapter = self._notification_adapters.get(channel)
        
        if not adapter:
            return False
        
        try:
            return adapter.send(agent.communication.config, message)
        except Exception:
            return False
    
    def get_agent_workload(
        self,
        agent_id: AgentId,
        project_service: Any  # ProjectService
    ) -> AgentWorkload:
        """获取 Agent 工作负载
        
        查询该 Agent 参与的所有项目及其状态。
        
        Args:
            agent_id: Agent ID
            project_service: 项目服务（用于查询项目）
            
        Returns:
            AgentWorkload 数据
            
        Raises:
            AgentNotFoundError: Agent 不存在
        """
        agent = self._agent_repo.get(agent_id)
        
        # 获取该 Agent 参与的所有项目
        all_projects = project_service.list_projects()
        agent_projects = [
            p for p in all_projects
            if agent_id in p.agent_ids
        ]
        
        # 统计
        total = len(agent_projects)
        active = sum(1 for p in agent_projects if p.status == ProjectStatus.ACTIVE)
        
        # 获取阻塞项目数（需要进度信息）
        blocked = 0
        project_infos = []
        
        for project in agent_projects:
            _, progress = project_service.get_project_with_progress(project.id)
            
            if progress and progress.is_blocked:
                blocked += 1
            
            project_infos.append({
                "id": str(project.id),
                "name": project.name,
                "status": project.status.value,
                "priority": project.priority.value,
                "progress": progress.percentage if progress else 0,
                "phase": progress.phase if progress else ""
            })
        
        return AgentWorkload(
            agent_id=str(agent.id),
            agent_name=agent.name,
            total_projects=total,
            active_projects=active,
            blocked_projects=blocked,
            projects=project_infos
        )
    
    def validate_notification_config(self, channel: str, config: Dict[str, Any]) -> bool:
        """验证通知配置是否有效
        
        Args:
            channel: 渠道名称
            config: 配置字典
            
        Returns:
            配置是否有效
        """
        adapter = self._notification_adapters.get(channel)
        if not adapter:
            return False
        return adapter.validate_config(config)
    
    def _format_assignment_message(self, agent: Agent, project: Project) -> str:
        """格式化分配通知消息"""
        lines = [
            f"🎯 项目分配通知",
            f"",
            f"你已被分配至项目: **{project.name}**",
            f"项目 ID: `{project.id}`",
            f"优先级: {project.priority.emoji} {project.priority.value}",
            f"类型: {project.type.value}",
        ]
        
        if project.local_path:
            lines.append(f"本地路径: `{project.local_path}`")
        
        if project.github_url:
            lines.append(f"GitHub: {project.github_url}")
        
        lines.append("")
        lines.append("请开始跟进此项目，并及时更新进度。")
        
        return "\n".join(lines)
    
    def _format_update_message(
        self,
        agent: Agent,
        project: Project,
        update_type: str,
        details: str
    ) -> str:
        """格式化更新通知消息"""
        type_labels = {
            "status_changed": "📊 状态变更",
            "blocked": "🚫 项目阻塞",
            "unblocked": "✅ 阻塞解除",
            "completed": "🎉 项目完成",
            "priority_changed": "⚡ 优先级变更",
        }
        
        label = type_labels.get(update_type, "📋 项目更新")
        
        return f"""{label}

项目: **{project.name}**
更新: {details}

请及时查看并处理。"""
