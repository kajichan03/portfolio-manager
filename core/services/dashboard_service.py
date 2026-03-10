"""Portfolio Manager 应用服务 - DashboardService

本模块实现 Dashboard 生成相关的应用服务。
负责聚合项目数据、生成摘要和详情视图。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from collections import defaultdict

from core.domain import (
    Project, ProjectId, ProjectProgress,
    Priority, ProjectStatus
)
from core.adapters.base import ProjectRepository, ProgressSource
from .project_service import ProjectService


@dataclass
class SummaryDashboard:
    """摘要 Dashboard 数据"""
    total: int = 0
    active: int = 0
    blocked: int = 0
    attention_needed: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProjectWithProgress:
    """项目及其进度数据"""
    project: Project
    progress: Optional[ProjectProgress]


@dataclass
class DetailDashboard:
    """详情 Dashboard 数据"""
    high_priority: List[ProjectWithProgress] = field(default_factory=list)
    medium_priority: List[ProjectWithProgress] = field(default_factory=list)
    low_priority: List[ProjectWithProgress] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


class DashboardService:
    """Dashboard 生成应用服务
    
    负责聚合多个数据源，生成 Dashboard 视图。
    支持摘要模式和详情模式。
    
    Attributes:
        _project_service: 项目管理服务
        _progress_sources: 进度数据源列表
    """
    
    def __init__(
        self,
        project_service: ProjectService,
        progress_sources: List[ProgressSource]
    ):
        self._project_service = project_service
        self._progress_sources = progress_sources
    
    def generate_summary(self) -> SummaryDashboard:
        """生成摘要 Dashboard
        
        统计项目总数、活跃数、阻塞数，
        并识别需要关注的项目。
        
        Returns:
            SummaryDashboard 数据对象
        """
        # 获取所有项目
        projects = self._project_service.list_projects()
        
        # 并行获取所有项目进度
        progresses = self._fetch_progresses([p.id for p in projects])
        
        # 统计
        total = len(projects)
        active = 0
        blocked = 0
        attention_needed = []
        
        for project in projects:
            progress = progresses.get(project.id)
            
            # 活跃项目：状态为 active 且未被阻塞
            if project.status == ProjectStatus.ACTIVE:
                if progress and progress.is_blocked:
                    blocked += 1
                else:
                    active += 1
            
            # 需要关注的项目
            attention_item = self._check_attention_needed(project, progress)
            if attention_item:
                attention_needed.append(attention_item)
        
        # 按优先级排序需要关注的项目
        attention_needed.sort(key=lambda x: self._priority_sort_key(x.get('priority', 'low')))
        
        return SummaryDashboard(
            total=total,
            active=active,
            blocked=blocked,
            attention_needed=attention_needed,
            generated_at=datetime.now()
        )
    
    def generate_detail(
        self,
        priority_filter: Optional[Priority] = None
    ) -> DetailDashboard:
        """生成详情 Dashboard
        
        按优先级分组展示所有项目及其进度。
        
        Args:
            priority_filter: 可选的优先级过滤
            
        Returns:
            DetailDashboard 数据对象
        """
        # 获取所有项目
        projects = self._project_service.list_projects()
        
        # 获取所有进度
        progresses = self._fetch_progresses([p.id for p in projects])
        
        # 按优先级分组
        by_priority: Dict[Priority, List[ProjectWithProgress]] = defaultdict(list)
        
        for project in projects:
            # 应用过滤器
            if priority_filter and project.priority != priority_filter:
                continue
            
            progress = progresses.get(project.id)
            by_priority[project.priority].append(
                ProjectWithProgress(project, progress)
            )
        
        # 排序：每个优先级内按名称排序
        for priority in by_priority:
            by_priority[priority].sort(key=lambda x: x.project.name)
        
        return DetailDashboard(
            high_priority=by_priority.get(Priority.HIGH, []),
            medium_priority=by_priority.get(Priority.MEDIUM, []),
            low_priority=by_priority.get(Priority.LOW, []),
            generated_at=datetime.now()
        )
    
    def get_project_detail(self, project_id: ProjectId) -> Optional[ProjectWithProgress]:
        """获取单个项目详情
        
        Args:
            project_id: 项目 ID
            
        Returns:
            ProjectWithProgress，项目不存在时返回 None
        """
        try:
            project, progress = self._project_service.get_project_with_progress(project_id)
            return ProjectWithProgress(project, progress)
        except Exception:
            return None
    
    def _fetch_progresses(
        self,
        project_ids: List[ProjectId]
    ) -> Dict[ProjectId, Optional[ProjectProgress]]:
        """从多个数据源获取进度
        
        按顺序尝试所有数据源，返回第一个成功的结果。
        
        Args:
            project_ids: 项目 ID 列表
            
        Returns:
            项目 ID 到进度的映射（进度可能为 None）
        """
        result = {}
        
        for pid in project_ids:
            progress = None
            
            # 按顺序尝试所有数据源
            for source in self._progress_sources:
                try:
                    if source.can_handle(pid):
                        progress = source.get_progress(pid)
                        if progress is not None:
                            break
                except Exception:
                    continue
            
            result[pid] = progress
        
        return result
    
    def _check_attention_needed(
        self,
        project: Project,
        progress: Optional[ProjectProgress]
    ) -> Optional[Dict[str, Any]]:
        """检查项目是否需要关注
        
        关注条件：
        - 被阻塞（有 blockers）
        - 等待 Review（phase 包含 "review"）
        - 今日到期（due_date 是今天）
        
        Returns:
            需要关注时返回字典，否则返回 None
        """
        if project.status != ProjectStatus.ACTIVE:
            return None
        
        reasons = []
        
        # 检查阻塞
        if progress and progress.is_blocked:
            reasons.append("blocked")
        
        # 检查等待 Review
        if progress and progress.phase and "review" in progress.phase.lower():
            reasons.append("waiting_review")
        
        # TODO: 检查今日到期（需要 Task 信息）
        
        if not reasons:
            return None
        
        # 获取负责人
        assignee = None
        if project.agent_ids:
            assignee = str(list(project.agent_ids)[0])
        
        return {
            "project_id": str(project.id),
            "project_name": project.name,
            "priority": project.priority.value,
            "reason": reasons[0],  # 主要理由
            "reasons": reasons,    # 所有理由
            "assignee": assignee,
            "phase": progress.phase if progress else ""
        }
    
    def _priority_sort_key(self, priority: str) -> int:
        """优先级排序键（高优先级返回小值）"""
        order = {"high": 0, "medium": 1, "low": 2}
        return order.get(priority, 3)
