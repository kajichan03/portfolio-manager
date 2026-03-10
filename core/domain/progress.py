"""Portfolio Manager 领域模型 - ProjectProgress 实体

本模块定义 ProjectProgress 实体，存储项目的运行时动态数据。

与 Project 实体分离，避免数据同步问题：
- Project: 存储在 projects.yaml（静态配置）
- ProjectProgress: 存储在 progress.json（运行时数据）
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .value_objects import ProjectId


@dataclass
class ProjectProgress:
    """项目进度实体 - 运行时动态数据
    
    存储项目的实时进度信息，包括：
    - 完成百分比
    - 当前阶段
    - 任务统计
    - 阻塞项
    - 下一步计划
    
    此实体是可变的，因为运行时数据会频繁更新。
    
    属性:
        project_id: 关联的项目 ID
        percentage: 完成百分比 (0-100)
        phase: 当前阶段描述
        next_steps: 下一步计划列表
        blockers: 阻塞项列表
        tasks_total: 任务总数
        tasks_completed: 已完成任务数
        updated_at: 最后更新时间
    """
    project_id: ProjectId
    
    # 进度信息
    percentage: int = 0
    phase: str = ""
    
    # 任务状态
    next_steps: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    
    # 统计
    tasks_total: int = 0
    tasks_completed: int = 0
    
    # 时间戳
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not 0 <= self.percentage <= 100:
            raise ValueError(f"percentage must be 0-100: {self.percentage}")
    
    @property
    def is_blocked(self) -> bool:
        """项目是否被阻塞"""
        return len(self.blockers) > 0
    
    @property
    def completion_rate(self) -> float:
        """任务完成率 (0.0 - 1.0)"""
        if self.tasks_total == 0:
            return 0.0
        return self.tasks_completed / self.tasks_total
    
    def update_progress(self, percentage: int, phase: str) -> None:
        """更新进度信息"""
        if not 0 <= percentage <= 100:
            raise ValueError(f"percentage must be 0-100: {percentage}")
        self.percentage = percentage
        self.phase = phase
        self.updated_at = datetime.now()
    
    def add_blocker(self, blocker: str) -> None:
        """添加阻塞项"""
        if blocker not in self.blockers:
            self.blockers.append(blocker)
            self.updated_at = datetime.now()
    
    def remove_blocker(self, blocker: str) -> None:
        """移除阻塞项"""
        if blocker in self.blockers:
            self.blockers.remove(blocker)
            self.updated_at = datetime.now()
    
    def set_next_steps(self, steps: List[str]) -> None:
        """设置下一步计划"""
        self.next_steps = list(steps)
        self.updated_at = datetime.now()
    
    def update_task_stats(self, total: int, completed: int) -> None:
        """更新任务统计"""
        if completed > total:
            raise ValueError(f"completed ({completed}) cannot exceed total ({total})")
        self.tasks_total = total
        self.tasks_completed = completed
        self.updated_at = datetime.now()
