"""Portfolio Manager YAML 存储适配器

本模块实现基于 YAML 文件的 Repository。
用于持久化 Project 和 Agent 实体。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.domain import (
    Project, ProjectId, ProjectProgress,
    Agent, AgentId,
    ProjectType, DataSource, Priority, ProjectStatus,
    AgentStatus, AgentRole, CommunicationConfig
)
from core.adapters.base import (
    ProjectRepository, AgentRepository,
    ProjectFilter, AgentFilter,
    ProjectNotFoundError, AgentNotFoundError,
    DuplicateProjectError, DuplicateAgentError
)


class JsonProjectRepository(ProjectRepository):
    """基于 JSON 文件的项目仓储
    
    数据存储在 data/projects.json 文件中。
    
    YAML 结构:
        version: "1.0"
        projects:
          - id: "portfolio-manager"
            name: "Portfolio Manager"
            type: "dedicated"
            source: "bot_project"
            priority: "high"
            status: "active"
            local_path: "~/projects/portfolio-manager"
            github_url: "https://github.com/..."
            agent_ids: ["pd", "dev"]
            created_at: "2026-03-10T00:00:00Z"
            updated_at: "2026-03-10T00:00:00Z"
    """
    
    def __init__(self, data_dir: Path):
        """
        Args:
            data_dir: 数据目录路径（包含 projects.yaml）
        """
        self._data_dir = Path(data_dir)
        self._projects_file = self._data_dir / "projects.json"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """确保数据文件存在"""
        self._data_dir.mkdir(parents=True, exist_ok=True)
        if not self._projects_file.exists():
            self._save_data({"version": "1.0", "projects": []})
    
    def get(self, project_id: ProjectId) -> Project:
        """根据 ID 获取项目"""
        projects = self._load_projects()
        for project in projects:
            if project.id == project_id:
                return project
        raise ProjectNotFoundError(project_id)
    
    def list(self, filter: Optional[ProjectFilter] = None) -> List[Project]:
        """获取项目列表"""
        projects = self._load_projects()
        
        if not filter or filter.is_empty():
            return projects
        
        # 应用过滤器
        result = []
        for project in projects:
            if filter.status and project.status.value != filter.status:
                continue
            if filter.source and project.source.value != filter.source:
                continue
            if filter.priority and project.priority.value != filter.priority:
                continue
            if filter.agent_id and filter.agent_id not in project.agent_ids:
                continue
            if filter.type and project.type.value != filter.type:
                continue
            result.append(project)
        
        return result
    
    def save(self, project: Project) -> None:
        """保存项目（更新或创建）"""
        data = self._load_data()
        projects_data = data.get("projects", [])
        
        # 查找现有项目
        existing_index = None
        for i, p in enumerate(projects_data):
            if p.get("id") == str(project.id):
                existing_index = i
                break
        
        # 序列化项目
        project_data = self._serialize_project(project)
        
        if existing_index is not None:
            # 更新
            projects_data[existing_index] = project_data
        else:
            # 创建
            projects_data.append(project_data)
        
        data["projects"] = projects_data
        self._save_data(data)
    
    def delete(self, project_id: ProjectId) -> None:
        """删除项目"""
        data = self._load_data()
        projects_data = data.get("projects", [])
        
        original_len = len(projects_data)
        projects_data = [p for p in projects_data if p.get("id") != str(project_id)]
        
        if len(projects_data) == original_len:
            raise ProjectNotFoundError(project_id)
        
        data["projects"] = projects_data
        self._save_data(data)
    
    def exists(self, project_id: ProjectId) -> bool:
        """检查项目是否存在"""
        try:
            self.get(project_id)
            return True
        except ProjectNotFoundError:
            return False
    
    def _load_data(self) -> Dict[str, Any]:
        """加载原始 YAML 数据"""
        if not self._projects_file.exists():
            return {"version": "1.0", "projects": []}
        
        with open(self._projects_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_data(self, data: Dict[str, Any]) -> None:
        """保存原始 YAML 数据"""
        with open(self._projects_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_projects(self) -> List[Project]:
        """加载所有项目实体"""
        data = self._load_data()
        projects_data = data.get("projects", [])
        return [self._deserialize_project(p) for p in projects_data]
    
    def _serialize_project(self, project: Project) -> Dict[str, Any]:
        """将 Project 实体序列化为字典"""
        return {
            "id": str(project.id),
            "name": project.name,
            "type": project.type.value,
            "source": project.source.value,
            "priority": project.priority.value,
            "status": project.status.value,
            "local_path": str(project.local_path) if project.local_path else None,
            "github_url": project.github_url,
            "agent_ids": [str(aid) for aid in project.agent_ids],
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }
    
    def _deserialize_project(self, data: Dict[str, Any]) -> Project:
        """将字典反序列化为 Project 实体"""
        from dataclasses import field
        from typing import FrozenSet
        
        # 解析 agent_ids
        agent_ids = frozenset(AgentId(aid) for aid in data.get("agent_ids", []))
        
        # 解析路径
        local_path = data.get("local_path")
        if local_path:
            local_path = Path(local_path).expanduser()
        
        # 解析时间
        created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        updated_at = datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        
        return Project(
            id=ProjectId(data["id"]),
            name=data["name"],
            type=ProjectType(data["type"]),
            source=DataSource(data["source"]),
            priority=Priority(data["priority"]),
            status=ProjectStatus(data["status"]),
            local_path=local_path,
            github_url=data.get("github_url"),
            agent_ids=agent_ids,
            created_at=created_at,
            updated_at=updated_at,
        )


class JsonAgentRepository(AgentRepository):
    """基于 JSON 文件的 Agent 仓储
    
    数据存储在 data/agents.json 文件中。
    
    YAML 结构:
        version: "1.0"
        agents:
          - id: "clawd"
            name: "Clawd"
            emoji: "☎️"
            role: "coordinator"
            communication:
              channel: "telegram"
              config:
                chat_id: "123456"
            config_path: "~/.openclaw/workspace-dev"
            status: "active"
    """
    
    def __init__(self, data_dir: Path):
        self._data_dir = Path(data_dir)
        self._agents_file = self._data_dir / "agents.json"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """确保数据文件存在"""
        self._data_dir.mkdir(parents=True, exist_ok=True)
        if not self._agents_file.exists():
            self._save_data({"version": "1.0", "agents": []})
    
    def get(self, agent_id: AgentId) -> Agent:
        """根据 ID 获取 Agent"""
        agents = self._load_agents()
        for agent in agents:
            if agent.id == agent_id:
                return agent
        raise AgentNotFoundError(agent_id)
    
    def list(self, filter: Optional[AgentFilter] = None) -> List[Agent]:
        """获取 Agent 列表"""
        agents = self._load_agents()
        
        if not filter or filter.is_empty():
            return agents
        
        result = []
        for agent in agents:
            if filter.status and agent.status.value != filter.status:
                continue
            if filter.role and agent.role.value != filter.role:
                continue
            result.append(agent)
        
        return result
    
    def save(self, agent: Agent) -> None:
        """保存 Agent"""
        data = self._load_data()
        agents_data = data.get("agents", [])
        
        # 查找现有 Agent
        existing_index = None
        for i, a in enumerate(agents_data):
            if a.get("id") == str(agent.id):
                existing_index = i
                break
        
        # 序列化
        agent_data = self._serialize_agent(agent)
        
        if existing_index is not None:
            agents_data[existing_index] = agent_data
        else:
            agents_data.append(agent_data)
        
        data["agents"] = agents_data
        self._save_data(data)
    
    def delete(self, agent_id: AgentId) -> None:
        """删除 Agent"""
        data = self._load_data()
        agents_data = data.get("agents", [])
        
        original_len = len(agents_data)
        agents_data = [a for a in agents_data if a.get("id") != str(agent_id)]
        
        if len(agents_data) == original_len:
            raise AgentNotFoundError(agent_id)
        
        data["agents"] = agents_data
        self._save_data(data)
    
    def exists(self, agent_id: AgentId) -> bool:
        """检查 Agent 是否存在"""
        try:
            self.get(agent_id)
            return True
        except AgentNotFoundError:
            return False
    
    def _load_data(self) -> Dict[str, Any]:
        """加载原始 YAML 数据"""
        if not self._agents_file.exists():
            return {"version": "1.0", "agents": []}
        
        with open(self._agents_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_data(self, data: Dict[str, Any]) -> None:
        """保存原始 YAML 数据"""
        with open(self._agents_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_agents(self) -> List[Agent]:
        """加载所有 Agent 实体"""
        data = self._load_data()
        agents_data = data.get("agents", [])
        return [self._deserialize_agent(a) for a in agents_data]
    
    def _serialize_agent(self, agent: Agent) -> Dict[str, Any]:
        """将 Agent 实体序列化为字典"""
        return {
            "id": str(agent.id),
            "name": agent.name,
            "emoji": agent.emoji,
            "role": agent.role.value,
            "communication": {
                "channel": agent.communication.channel,
                "config": agent.communication.config,
            },
            "config_path": str(agent.config_path) if agent.config_path else None,
            "status": agent.status.value,
        }
    
    def _deserialize_agent(self, data: Dict[str, Any]) -> Agent:
        """将字典反序列化为 Agent 实体"""
        comm_data = data.get("communication", {})
        
        # 解析路径
        config_path = data.get("config_path")
        if config_path:
            config_path = Path(config_path).expanduser()
        
        return Agent(
            id=AgentId(data["id"]),
            name=data["name"],
            emoji=data["emoji"],
            role=AgentRole(data["role"]),
            communication=CommunicationConfig(
                channel=comm_data.get("channel", ""),
                config=comm_data.get("config", {})
            ),
            config_path=config_path,
            status=AgentStatus(data.get("status", "active")),
        )
