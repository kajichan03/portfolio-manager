"""Portfolio Manager Reminders 数据源适配器

本模块实现从 Apple Reminders 获取项目进度的适配器。
通过调用 remindctl 命令行工具获取数据。
"""

import json
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any, List, Union

from output.core.domain import ProjectId, ProjectProgress, ProjectType, Project, DataSource, Priority, ProjectStatus, AgentId
from output.core.adapters.base import ProgressSource, DataSourceError


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
            tasks = self._fetch_list(str(project_id))
        except DataSourceError:
            return None
        
        if tasks is None:
            return None
        
        # tasks 是任务列表（数组）
        total = len(tasks)
        completed = sum(1 for t in tasks if t.get("isCompleted", False))
        
        # 计算进度百分比
        percentage = int(completed / total * 100) if total > 0 else 0
        
        # 确定阶段
        if percentage == 0:
            phase = "未开始"
        elif percentage == 100:
            phase = "已完成"
        else:
            phase = "进行中"
        
        # 未完成任务作为 next_steps
        next_steps = [
            t.get("title", "") 
            for t in tasks 
            if not t.get("isCompleted", False)
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
    
    def _fetch_list(self, list_name: str) -> Optional[List[Dict[str, Any]]]:
        """调用 remindctl 获取列表数据
        
        Args:
            list_name: 列表名称
            
        Returns:
            任务列表，不存在返回 None
            
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
            return [l.get("title", "") for l in lists if l.get("title")]
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
            
            # 使用原始列表名作为项目 ID（以便 get_progress 能正确调用 remindctl）
            # 同时保存 slug 作为备用标识
            
            # 创建 Project 对象
            project = Project(
                id=ProjectId(list_name),  # 使用原始名称作为 ID
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
        
        使用 remindctl list --plain 获取所有列表名称，
        然后动态获取每个列表的任务。
        """
        # 获取所有列表名称
        list_names = self._fetch_list_names()
        
        lists = []
        for list_name in list_names:
            try:
                # 获取列表任务
                tasks = self._fetch_list(list_name)
                if tasks is not None:
                    lists.append({"title": list_name, "tasks": tasks})
            except Exception:
                pass
        
        return lists
    
    def _fetch_list_names(self) -> List[str]:
        """获取所有 Reminders 列表名称
        
        使用 remindctl list --plain 获取列表名称。
        格式: 列表名\t任务数\t逾期数
        
        Returns:
            列表名称列表
        """
        try:
            result = subprocess.run(
                [self._remindctl_path, "list", "--plain"],
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception as e:
            raise DataSourceError(f"Failed to fetch list names: {e}", "reminders")
        
        if result.returncode != 0:
            raise DataSourceError(
                f"remindctl error: {result.stderr}",
                "reminders"
            )
        
        names = []
        for line in result.stdout.strip().split("\n"):
            if line and "\t" in line:
                # 格式: 列表名\t任务数\t逾期数
                parts = line.split("\t")
                if parts[0]:
                    names.append(parts[0])
        
        return names
    
    def _generate_slug(self, name: str) -> str:
        """将名称转换为 slug 格式
        
        示例: "My Project" -> "my-project"
        对于非 ASCII 字符（如中文），保留原始字符
        """
        import re
        
        # 转换为小写，替换空格和特殊字符为连字符
        # 保留中文字符和其他非 ASCII 字符
        slug = re.sub(r'[\s]+', '-', name.lower())
        slug = re.sub(r'[^\w\u4e00-\u9fff-]', '-', slug)
        slug = slug.strip('-')
        
        # 确保不为空
        if not slug:
            import hashlib
            hash_obj = hashlib.md5(name.encode('utf-8'))
            slug = hash_obj.hexdigest()[:8]
        
        return slug
