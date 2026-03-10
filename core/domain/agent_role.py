"""Portfolio Manager 领域模型 - Agent 角色枚举

本模块定义 Agent 的角色类型，支持未来扩展。
"""

from enum import Enum


class AgentRole(Enum):
    """Agent 角色枚举
    
    定义不同类型的 AI Agent 角色，可根据需要扩展。
    
    当前角色:
    - COORDINATOR: 主协调者 (如 Clawd)
    - PRODUCT: 产品经理 (如 pd)
    - DEVELOPER: 开发工程师 (如 Dev)
    - QA: 测试/验证工程师 (如 Test)
    
    未来可扩展:
    - DESIGN = "design"
    - RESEARCH = "research"
    - OPS = "ops"
    """
    COORDINATOR = "coordinator"
    PRODUCT = "product"
    DEVELOPER = "developer"
    QA = "qa"
    
    @property
    def display_name(self) -> str:
        """获取角色的显示名称"""
        return {
            AgentRole.COORDINATOR: "协调者",
            AgentRole.PRODUCT: "产品经理",
            AgentRole.DEVELOPER: "开发工程师",
            AgentRole.QA: "测试工程师",
        }.get(self, self.value)
