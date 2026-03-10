"""Portfolio Manager progress.json 数据源适配器

本模块实现从 Bot 项目的 progress.json 文件读取进度的适配器。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from output.core.domain import ProjectId, ProjectProgress
from output.core.adapters.base import ProgressSource, DataSourceError


class ProgressAdapter(ProgressSource):
    """Bot 项目 progress.json 适配器
    
    从项目目录的 output/progress.json 文件读取进度数据。
    
    文件路径: {projects_root}/{project_id}/output/progress.json
    
    Attributes:
        _projects_root: 项目根目录
        _schema: 可选的 JSON Schema 用于验证
    """
    
    def __init__(self, projects_root: Path, schema: Optional[Dict] = None):
        """
        Args:
            projects_root: 项目根目录路径
            schema: 可选的 JSON Schema 用于验证
        """
        self._projects_root = Path(projects_root)
        self._schema = schema
    
    def get_progress(self, project_id: ProjectId) -> Optional[ProjectProgress]:
        """获取指定项目的进度
        
        从 progress.json 文件读取并转换为 ProjectProgress。
        
        Args:
            project_id: 项目 ID
            
        Returns:
            ProjectProgress 实体，文件不存在或无效返回 None
            
        Raises:
            DataSourceError: 文件读取或解析失败
        """
        progress_file = self._get_progress_file_path(project_id)
        
        if not progress_file.exists():
            return None
        
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataSourceError(
                f"Invalid JSON in {progress_file}: {e}",
                "progress.json"
            ) from e
        except Exception as e:
            raise DataSourceError(
                f"Failed to read {progress_file}: {e}",
                "progress.json"
            ) from e
        
        # 验证 Schema（如果提供）
        if self._schema:
            self._validate_schema(data)
        
        return self._parse_progress_data(project_id, data)
    
    def can_handle(self, project_id: ProjectId) -> bool:
        """检查是否能处理指定项目
        
        通过检查 progress.json 文件是否存在来判断。
        
        Args:
            project_id: 项目 ID
            
        Returns:
            是否能处理
        """
        progress_file = self._get_progress_file_path(project_id)
        return progress_file.exists()
    
    def _get_progress_file_path(self, project_id: ProjectId) -> Path:
        """获取 progress.json 文件路径
        
        Args:
            project_id: 项目 ID
            
        Returns:
            文件路径
        """
        return self._projects_root / str(project_id) / "output" / "progress.json"
    
    def _parse_progress_data(
        self, 
        project_id: ProjectId, 
        data: Dict[str, Any]
    ) -> ProjectProgress:
        """解析 progress.json 数据为 ProjectProgress
        
        Args:
            project_id: 项目 ID
            data: JSON 数据
            
        Returns:
            ProjectProgress 实体
        """
        # 解析进度百分比
        percentage = data.get("progress_percentage", 0)
        if not isinstance(percentage, int) or not 0 <= percentage <= 100:
            percentage = 0
        
        # 解析当前阶段
        phase = data.get("current_phase", "")
        
        # 解析下一步
        next_steps = data.get("next_steps", [])
        if not isinstance(next_steps, list):
            next_steps = []
        next_steps = [str(s) for s in next_steps if s]
        
        # 解析阻塞项
        blockers = []
        blockers_data = data.get("blockers", [])
        if isinstance(blockers_data, list):
            for b in blockers_data:
                if isinstance(b, dict):
                    desc = b.get("description", "")
                    if desc:
                        blockers.append(desc)
                elif isinstance(b, str):
                    blockers.append(b)
        
        # 解析任务统计
        tasks = data.get("tasks", [])
        tasks_total = len(tasks) if isinstance(tasks, list) else 0
        tasks_completed = sum(
            1 for t in tasks 
            if isinstance(t, dict) and t.get("status") == "done"
        )
        
        # 解析更新时间
        updated_at_str = data.get("updated_at", "")
        try:
            updated_at = datetime.fromisoformat(updated_at_str)
        except (ValueError, TypeError):
            updated_at = datetime.now()
        
        return ProjectProgress(
            project_id=project_id,
            percentage=percentage,
            phase=phase,
            next_steps=next_steps,
            blockers=blockers,
            tasks_total=tasks_total,
            tasks_completed=tasks_completed,
            updated_at=updated_at
        )
    
    def _validate_schema(self, data: Dict[str, Any]) -> None:
        """验证数据是否符合 Schema
        
        当前实现仅检查必需字段是否存在。
        完整 Schema 验证可使用 jsonschema 库。
        
        Args:
            data: 要验证的数据
            
        Raises:
            DataSourceError: 验证失败
        """
        required_fields = [
            "project_id",
            "project_name", 
            "current_phase",
            "progress_percentage",
            "status",
            "tasks",
            "agents",
            "updated_at"
        ]
        
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise DataSourceError(
                f"Missing required fields in progress.json: {missing}",
                "progress.json"
            )
    
    def load_schema(self, schema_path: Path) -> None:
        """从文件加载 JSON Schema
        
        Args:
            schema_path: Schema 文件路径
        """
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                self._schema = json.load(f)
        except Exception as e:
            raise DataSourceError(
                f"Failed to load schema from {schema_path}: {e}",
                "progress.json"
            ) from e
