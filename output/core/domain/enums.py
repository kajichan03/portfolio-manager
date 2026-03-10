"""Portfolio Manager 领域模型 - 枚举定义

本模块包含所有领域枚举类型。
"""

from enum import Enum, auto


class ProjectType(Enum):
    """项目类型
    
    - DEDICATED: 专门项目（有明确开始和结束的大型任务）
    - OPERATION: 日常运营（持续进行的维护性工作）
    """
    DEDICATED = "dedicated"
    OPERATION = "operation"


class DataSource(Enum):
    """项目数据源类型
    
    - REMINDERS: Apple Reminders 列表
    - BOT_PROJECT: Bot 本地项目（通过 progress.json 读取）
    """
    REMINDERS = "reminders"
    BOT_PROJECT = "bot_project"


class Priority(Enum):
    """优先级
    
    用于 Dashboard 排序和视觉标识：
    - HIGH: 🔴 高优先级
    - MEDIUM: 🟡 中优先级
    - LOW: 🟢 低优先级
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    
    @property
    def emoji(self) -> str:
        """获取优先级对应的 emoji"""
        return {
            Priority.HIGH: "🔴",
            Priority.MEDIUM: "🟡",
            Priority.LOW: "🟢",
        }[self]


class ProjectStatus(Enum):
    """项目状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskStatus(Enum):
    """任务状态"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class AgentStatus(Enum):
    """Agent 状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
