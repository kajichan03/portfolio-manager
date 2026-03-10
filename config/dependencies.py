"""Portfolio Manager 依赖注入配置

本模块实现 Service Container，用于依赖注入。
连接所有适配器和服务，供 CLI 和 Skill 使用。
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from core.domain import ProjectId
from core.adapters import (
    JsonProjectRepository,
    JsonAgentRepository,
    RemindersAdapter,
    ProgressAdapter,
    TelegramAdapter,
    IMessageAdapter,
)
from core.services import ProjectService, DashboardService, AgentService


class Config:
    """配置类
    
    从配置文件加载配置。
    """
    
    def __init__(self, config_path: Path):
        self._config = self._load_config(config_path)
    
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """加载配置文件"""
        if not config_path.exists():
            return self._default_config()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "data_dir": "./data",
            "projects_root": "~/projects",
            "remindctl_path": "remindctl",
            "telegram": {
                "bot_token": "${TELEGRAM_BOT_TOKEN}"
            }
        }
    
    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return Path(self._config.get("data_dir", "./data")).expanduser()
    
    @property
    def projects_root(self) -> Path:
        """项目根目录"""
        return Path(self._config.get("projects_root", "~/projects")).expanduser()
    
    @property
    def remindctl_path(self) -> str:
        """remindctl 路径"""
        return self._config.get("remindctl_path", "remindctl")
    
    @property
    def telegram_bot_token(self) -> str:
        """Telegram Bot Token"""
        token = self._config.get("telegram", {}).get("bot_token", "")
        # 支持环境变量
        if token.startswith("${") and token.endswith("}"):
            import os
            env_var = token[2:-1]
            token = os.environ.get(env_var, "")
        return token


class ServiceContainer:
    """服务容器
    
    负责创建和连接所有服务与适配器。
    供 CLI 和 Skill 使用。
    
    Attributes:
        project: ProjectService 实例
        dashboard: DashboardService 实例
        agent: AgentService 实例
    """
    
    def __init__(self, config: Config):
        """
        Args:
            config: 配置对象
        """
        self._config = config
        
        # 创建 Repositories
        self._project_repo = JsonProjectRepository(config.data_dir)
        self._agent_repo = JsonAgentRepository(config.data_dir)
        
        # 创建 Progress Sources
        self._progress_sources = [
            RemindersAdapter(config.remindctl_path),
            ProgressAdapter(config.projects_root),
        ]
        
        # 创建 Notification Adapters
        self._notification_adapters: Dict[str, Any] = {}
        
        # Telegram Adapter（如果有 token）
        telegram_token = config.telegram_bot_token
        if telegram_token:
            self._notification_adapters["telegram"] = TelegramAdapter(telegram_token)
        
        # iMessage Adapter（macOS 专用）
        self._notification_adapters["imessage"] = IMessageAdapter()
        
        # 创建 Services
        self.project = ProjectService(
            project_repo=self._project_repo,
            progress_source=None  # Progress 由 DashboardService 处理
        )
        
        self.dashboard = DashboardService(
            project_service=self.project,
            progress_sources=self._progress_sources
        )
        
        self.agent = AgentService(
            agent_repo=self._agent_repo,
            notification_adapters=self._notification_adapters
        )
    
    def get_project_with_progress(self, project_id: str):
        """获取项目及其进度（辅助方法）"""
        return self.project.get_project_with_progress(ProjectId(project_id))


def create_service_container(config_path: Optional[Path] = None) -> ServiceContainer:
    """创建服务容器
    
    工厂函数，用于创建配置好的 ServiceContainer。
    
    Args:
        config_path: 配置文件路径，默认使用 ./config/portfolio.json
        
    Returns:
        ServiceContainer 实例
    """
    if config_path is None:
        config_path = Path(__file__).parent / "portfolio.json"
    
    config = Config(config_path)
    return ServiceContainer(config)
