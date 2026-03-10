"""Portfolio Manager Reminders 数据源适配器

本模块实现从 Apple Reminders 获取项目进度的适配器。
通过调用 remindctl 命令行工具获取数据。
"""

import json
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any

from output.core.domain import ProjectId, ProjectProgress, ProjectType, Project, DataSource, Priority, ProjectStatus, AgentId
from output.core.adapters.base import ProgressSource, DataSourceError
from typing import List


class RemindersAdapter(ProgressSource):
    """Apple Reminders 数据源适配器
    
    通过 remindctl CLI 获取 Reminders 列表作为项目进度数据。
    
    映射规则:
    - Reminders 列表名 = 项目 ID
    - 列表中的任务 = 项目任务
    - 任务完成率 = 进度百分比
    - 未完成任务 = next_steps
    
    Attributes:
        _remindctl_path: remindctl 命令路径
    """
    
    def __init__(self, remindctl_path: str = "remindctl"):
        """
        Args:
            remindctl_path: remindctl 命令路径，默认为 "remindctl"
        """
        self._remindctl_path = remindctl_path
    
    def get_progress(self, project_id: ProjectId) -> Optional[ProjectProgress]:
        """获取指定项目的进度
        
        从 Reminders 获取列表数据，转换为 ProjectProgress。
        
        Args:
            project_id: 项目 ID（对应 Reminders 列表名）
            
        Returns:
            ProjectProgress 实体，如果列表不存在返回 None
            
        Raises:
            DataSourceError: 调用 remindctl 失败
        """
        try:
            list_data = self._fetch_list(str(project_id))
        except DataSourceError:
            return None
        
        if not list_data:
            return None
        
        # 解析任务
        tasks = list_data.get("tasks", [])
        total = len(tasks)
        completed = sum(1 for t in tasks if t.get("completed", False))
        
        # 计算进度百分比
        percentage = int(completed / total * 100) if total > 0 else 0
        
        # 确定阶段
        list_type = list_data.get("type", "")
        if list_type == "operation":
            phase = "运营中"
        elif percentage == 0:
            phase = "未开始"
        elif percentage == 100:
            phase = "已完成"
        else:
            phase = "进行中"
        
        # 未完成任务作为 next_steps
        next_steps = [
            t.get("title", "") 
            for t in tasks 
            if not t.get("completed", False)
        ][:5]  # 只取前 5 个
        
        return ProjectProgress(
            project_id=project_id,
            percentage=percentage,
            phase=phase,
            next_steps=next_steps,
            tasks_total=total,
            tasks_completed=completed,
            updated_at=datetime.now()
        )
    
    def can_handle(self, project_id: ProjectId) -> bool:
        """检查是否能处理指定项目
        
        通过检查 Reminders 中是否存在同名列表来判断。
        
        Args:
            project_id: 项目 ID
            
        Returns:
            是否能处理
        """
        try:
            result = self._fetch_list(str(project_id))
            return result is not None
        except DataSourceError:
            return False
    
    def _fetch_list(self, list_name: str) -> Optional[Dict[str, Any]]:
        """调用 remindctl 获取列表数据
        
        Args:
            list_name: 列表名称
            
        Returns:
            列表数据字典，不存在返回 None
            
        Raises:
            DataSourceError: 命令执行失败
        """
        try:
            result = subprocess.run(
                [self._remindctl_path, "list", list_name, "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )
        except subprocess.TimeoutExpired:
            raise DataSourceError(f"Timeout fetching list: {list_name}", "reminders")
        except FileNotFoundError:
            raise DataSourceError(
                f"remindctl not found at: {self._remindctl_path}", 
                "reminders"
            )
        
        if result.returncode != 0:
            # 列表不存在或其他错误
            if "not found" in result.stderr.lower():
                return None
            raise DataSourceError(
                f"remindctl error: {result.stderr}", 
                "reminders"
            )
        
        if not result.stdout.strip():
            return None
        
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise DataSourceError(
                f"Invalid JSON from remindctl: {e}", 
                "reminders"
            ) from e
    
    def list_available_lists(self) -> list:
        """获取所有可用的 Reminders 列表
        
        Returns:
            列表名称列表
            
        Raises:
            DataSourceError: 获取失败
        """
        try:
            result = subprocess.run(
                [self._remindctl_path, "lists", "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception as e:
            raise DataSourceError(f"Failed to list reminders: {e}", "reminders")
        
        if result.returncode != 0:
            raise DataSourceError(
                f"remindctl error: {result.stderr}", 
                "reminders"
            )
        
        try:
            lists = json.loads(result.stdout)
            return [l.get("name", "") for l in lists if l.get("name")]
        except json.JSONDecodeError:
            return []
    
    def list_projects(self) -> List[Project]:
        """从 Reminders 获取所有列表作为项目
        
        将每个 Reminders 列表转换为一个 Project 对象，
        用于 Dashboard 自动发现。
        
        Returns:
            Project 列表
        """
        lists = self._fetch_all_lists()
        projects = []
        
        for list_data in lists:
            list_name = list_data.get("title", "")
            if not list_name:
                continue
            
            # 生成项目 ID（slug 格式）
            project_id = self._generate_slug(list_name)
            
            # 创建 Project 对象
            project = Project(
                id=ProjectId(project_id),
                name=list_name,
                type=ProjectType.OPERATION,  # Reminders 列表默认为运营项目
                source=DataSource.REMINDERS,
                priority=Priority.MEDIUM,  # 默认中优先级
                status=ProjectStatus.ACTIVE,
                agent_ids=frozenset([AgentId("neal")]),  # 用户的项目
            )
            projects.append(project)
        
        return projects
    
    def _fetch_all_lists(self) -> List[Dict[str, Any]]:
        """获取所有 Reminders 列表数据
        
        Returns:
            列表数据字典列表
        """
        try:
            result = subprocess.run(
                [self._remindctl_path, "lists", "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception as e:
            raise DataSourceError(f"Failed to fetch lists: {e}", "reminders")
        
        if result.returncode != 0:
            raise DataSourceError(
                f"remindctl error: {result.stderr}",
                "reminders"
            )
        
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return []
    
    def _generate_slug(self, name: str) -> str:
        """将名称转换为 slug 格式
        
        示例: "My Project" -> "my-project"
        对于非 ASCII 字符（如中文），使用原始名称的哈希或转义
        """
        import re
        import hashlib
        
        # 尝试提取 ASCII 字符
        slug = name.lower()
        ascii_slug = re.sub(r'[^a-z0-9]+', '-', slug)
        ascii_slug = ascii_slug.strip('-')
        
        # 如果结果为空（全是非 ASCII 字符），使用哈希
        if not ascii_slug:
            # 使用名称的前 8 个字符的哈希
            hash_obj = hashlib.md5(name.encode('utf-8'))
            ascii_slug = hash_obj.hexdigest()[:8]
        
        return ascii_slug
