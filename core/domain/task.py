"""Portfolio Manager 领域模型 - Task 实体

本模块定义 Task 实体，表示项目中的具体任务。

注意：Task 是纯净的领域模型，不包含数据源特定的字段
（如 reminders_task_id）。数据源适配器负责映射。
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from .value_objects import TaskId, ProjectId, AgentId
from .enums import TaskStatus, Priority


@dataclass(frozen=True)
class Task:
    """任务实体 - 纯净领域模型
    
    Task 与数据源解耦，不包含特定数据源的标识字段。
    适配器层负责将外部数据（如 Reminders 任务）映射为 Task。
    
    属性:
        id: 任务唯一标识
        project_id: 所属项目 ID
        title: 任务标题
        status: 任务状态
        assignee_id: 负责人 Agent ID（可选）
        due_date: 截止日期（可选）
        priority: 优先级
    """
    id: TaskId
    project_id: ProjectId
    title: str
    status: TaskStatus
    
    # 可选属性
    assignee_id: Optional[AgentId] = None
    due_date: Optional[date] = None
    priority: Priority = Priority.MEDIUM
    
    def __post_init__(self):
        if not self.title:
            raise ValueError("Task title cannot be empty")
    
    def with_status(self, status: TaskStatus) -> "Task":
        """返回更新状态后的新任务实例"""
        return Task(
            id=self.id,
            project_id=self.project_id,
            title=self.title,
            status=status,
            assignee_id=self.assignee_id,
            due_date=self.due_date,
            priority=self.priority
        )
    
    def with_assignee(self, assignee_id: Optional[AgentId]) -> "Task":
        """返回更新负责人后的新任务实例"""
        return Task(
            id=self.id,
            project_id=self.project_id,
            title=self.title,
            status=self.status,
            assignee_id=assignee_id,
            due_date=self.due_date,
            priority=self.priority
        )
    
    def with_priority(self, priority: Priority) -> "Task":
        """返回更新优先级后的新任务实例"""
        return Task(
            id=self.id,
            project_id=self.project_id,
            title=self.title,
            status=self.status,
            assignee_id=self.assignee_id,
            due_date=self.due_date,
            priority=priority
        )
    
    @property
    def is_done(self) -> bool:
        """任务是否已完成"""
        return self.status == TaskStatus.DONE
    
    @property
    def is_blocked(self) -> bool:
        """任务是否被阻塞"""
        return self.status == TaskStatus.BLOCKED
    
    @property
    def is_in_progress(self) -> bool:
        """任务是否进行中"""
        return self.status == TaskStatus.IN_PROGRESS
