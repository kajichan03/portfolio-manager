"""Portfolio Manager 应用服务 - ProjectService

本模块实现项目管理相关的应用服务。
负责项目生命周期管理、Agent 分配等用例。
"""

import re
from datetime import datetime
from typing import List, Optional, Tuple

from output.core.domain import (
    Project, ProjectId, ProjectProgress,
    AgentId, Priority, ProjectStatus
)
from output.core.adapters.base import (
    ProjectRepository, ProgressSource,
    ProjectNotFoundError, AgentNotFoundError, DuplicateProjectError
)
from .commands import CreateProjectCommand, UpdateProjectCommand


class ProjectService:
    """项目管理应用服务
    
    负责项目的创建、更新、查询和 Agent 分配。
    通过构造函数注入 Repository 接口，支持纯内存测试。
    
    Attributes:
        _project_repo: 项目仓储接口
        _progress_source: 进度数据源接口（可选）
    """
    
    def __init__(
        self,
        project_repo: ProjectRepository,
        progress_source: Optional[ProgressSource] = None
    ):
        self._project_repo = project_repo
        self._progress_source = progress_source
    
    def create_project(self, cmd: CreateProjectCommand) -> Project:
        """创建新项目
        
        Args:
            cmd: 创建项目命令
            
        Returns:
            创建的 Project 实体
            
        Raises:
            DuplicateProjectError: 项目 ID 已存在
            ValueError: 参数无效
        """
        # 验证名称
        if not cmd.name or not cmd.name.strip():
            raise ValueError("Project name cannot be empty")
        
        # 生成项目 ID（slug 格式）
        project_id = ProjectId(self._generate_slug(cmd.name))
        
        # 检查是否已存在
        if self._project_repo.exists(project_id):
            raise DuplicateProjectError(project_id)
        
        # 创建项目实体
        project = Project(
            id=project_id,
            name=cmd.name.strip(),
            type=cmd.type,
            source=cmd.source,
            priority=cmd.priority,
            status=ProjectStatus.ACTIVE,
            local_path=cmd.local_path,
            github_url=cmd.github_url,
        )
        
        # 保存
        self._project_repo.save(project)
        
        return project
    
    def assign_agent(self, project_id: ProjectId, agent_id: AgentId) -> Project:
        """分配 Agent 到项目
        
        Args:
            project_id: 项目 ID
            agent_id: Agent ID
            
        Returns:
            更新后的 Project 实体
            
        Raises:
            ProjectNotFoundError: 项目不存在
        """
        project = self._project_repo.get(project_id)
        updated = project.with_agent(agent_id)
        self._project_repo.save(updated)
        return updated
    
    def remove_agent(self, project_id: ProjectId, agent_id: AgentId) -> Project:
        """从项目移除 Agent
        
        Args:
            project_id: 项目 ID
            agent_id: Agent ID
            
        Returns:
            更新后的 Project 实体
            
        Raises:
            ProjectNotFoundError: 项目不存在
        """
        project = self._project_repo.get(project_id)
        updated = project.without_agent(agent_id)
        self._project_repo.save(updated)
        return updated
    
    def list_projects(
        self,
        status: Optional[ProjectStatus] = None,
        source: Optional[str] = None,
        priority: Optional[Priority] = None
    ) -> List[Project]:
        """列出项目
        
        Args:
            status: 按状态过滤
            source: 按数据源过滤
            priority: 按优先级过滤
            
        Returns:
            符合条件的 Project 列表（不含运行时数据）
        """
        from output.core.adapters.base import ProjectFilter
        
        filter = ProjectFilter(
            status=status.value if status else None,
            source=source,
            priority=priority.value if priority else None
        )
        
        return self._project_repo.list(filter if not filter.is_empty() else None)
    
    def get_project(self, project_id: ProjectId) -> Project:
        """获取项目（不含进度）
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Project 实体
            
        Raises:
            ProjectNotFoundError: 项目不存在
        """
        return self._project_repo.get(project_id)
    
    def get_project_with_progress(
        self,
        project_id: ProjectId
    ) -> Tuple[Project, Optional[ProjectProgress]]:
        """获取项目及其进度
        
        Args:
            project_id: 项目 ID
            
        Returns:
            (Project, ProjectProgress) 元组，进度可能为 None
            
        Raises:
            ProjectNotFoundError: 项目不存在
        """
        project = self._project_repo.get(project_id)
        
        progress = None
        if self._progress_source:
            progress = self._progress_source.get_progress(project_id)
        
        return project, progress
    
    def update_project_status(
        self,
        project_id: ProjectId,
        status: ProjectStatus
    ) -> Project:
        """更新项目状态
        
        Args:
            project_id: 项目 ID
            status: 新状态
            
        Returns:
            更新后的 Project 实体
        """
        project = self._project_repo.get(project_id)
        updated = project.with_status(status)
        self._project_repo.save(updated)
        return updated
    
    def update_project_priority(
        self,
        project_id: ProjectId,
        priority: Priority
    ) -> Project:
        """更新项目优先级
        
        Args:
            project_id: 项目 ID
            priority: 新优先级
            
        Returns:
            更新后的 Project 实体
        """
        project = self._project_repo.get(project_id)
        updated = project.with_priority(priority)
        self._project_repo.save(updated)
        return updated
    
    def delete_project(self, project_id: ProjectId) -> None:
        """删除项目
        
        Args:
            project_id: 项目 ID
            
        Raises:
            ProjectNotFoundError: 项目不存在
        """
        self._project_repo.delete(project_id)
    
    def _generate_slug(self, name: str) -> str:
        """将名称转换为 slug 格式
        
        示例: "Portfolio Manager" -> "portfolio-manager"
        """
        # 转换为小写
        slug = name.lower()
        # 替换非字母数字字符为连字符
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        # 移除首尾连字符
        slug = slug.strip('-')
        return slug
