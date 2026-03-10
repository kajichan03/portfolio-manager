"""Portfolio Manager Skill

本模块是 OpenClaw Skill 的实现。
通过 Service Container 直接调用 Services，不经过 CLI。

关键约束：
- ✅ 不导入 CLI 任何模块
- ✅ 直接调用 Service（通过 Service Container）
- ✅ Skill 和 CLI 是平等的接口层
"""

# 只导入 core 层和 config，不导入 interfaces.cli
from output.config.dependencies import create_service_container
from output.interfaces.skill.handlers import SkillCommandBus

# 创建 Service Container（单例）
_service_container = None
_command_bus = None


def _get_command_bus():
    """获取 Command Bus（懒加载）"""
    global _service_container, _command_bus
    
    if _command_bus is None:
        _service_container = create_service_container()
        _command_bus = SkillCommandBus(
            project_service=_service_container.project,
            dashboard_service=_service_container.dashboard,
            agent_service=_service_container.agent
        )
    
    return _command_bus


def handle_message(message: str) -> str:
    """处理用户消息
    
    这是 Skill 的主入口点，由 OpenClaw 调用。
    
    Args:
        message: 用户输入的消息
        
    Returns:
        响应文本
    """
    command_bus = _get_command_bus()
    return command_bus.dispatch(message)


# 为了兼容 OpenClaw Skill API，可以定义一个类
class PortfolioSkill:
    """Portfolio Manager Skill
    
    OpenClaw Skill 实现。
    """
    
    def __init__(self):
        self._command_bus = _get_command_bus()
    
    def process(self, message: str) -> str:
        """处理消息"""
        return self._command_bus.dispatch(message)
    
    def status(self) -> str:
        """获取状态摘要"""
        return self._command_bus.dispatch("状态")
    
    def list_projects(self) -> str:
        """获取项目列表"""
        return self._command_bus.dispatch("详情")
