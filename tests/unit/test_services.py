"""单元测试 - Services 应用服务

测试应用服务的业务逻辑，使用 Mock Repository。
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import unittest
from unittest.mock import Mock, MagicMock
from typing import List

from core.domain import (
    Project, ProjectId, ProjectType, DataSource, Priority, ProjectStatus,
    AgentId
)
from core.services import ProjectService, DashboardService
from core.services.commands import CreateProjectCommand
from core.adapters.base import ProjectFilter


class TestProjectService(unittest.TestCase):
    """测试 ProjectService"""
    
    def setUp(self):
        """设置 Mock Repository"""
        self.mock_repo = Mock()
        self.service = ProjectService(project_repo=self.mock_repo)
    
    def test_create_project(self):
        """测试创建项目"""
        # 配置 Mock
        self.mock_repo.exists.return_value = False
        
        # 执行
        cmd = CreateProjectCommand(
            name="Test Project",
            type=ProjectType.DEDICATED,
            source=DataSource.BOT_PROJECT,
            priority=Priority.HIGH
        )
        project = self.service.create_project(cmd)
        
        # 验证
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.priority, Priority.HIGH)
        self.mock_repo.save.assert_called_once()
    
    def test_create_project_duplicate_raises(self):
        """测试重复项目应抛出异常"""
        from core.adapters.base import DuplicateProjectError
        
        self.mock_repo.exists.return_value = True
        
        cmd = CreateProjectCommand(
            name="Test Project",
            type=ProjectType.DEDICATED,
            source=DataSource.BOT_PROJECT
        )
        
        with self.assertRaises(DuplicateProjectError):
            self.service.create_project(cmd)
    
    def test_assign_agent(self):
        """测试分配 Agent"""
        # 准备测试数据
        project = Project(
            id=ProjectId("test"),
            name="Test",
            type=ProjectType.DEDICATED,
            source=DataSource.BOT_PROJECT,
            priority=Priority.MEDIUM,
            status=ProjectStatus.ACTIVE
        )
        self.mock_repo.get.return_value = project
        
        # 执行
        updated = self.service.assign_agent(ProjectId("test"), AgentId("dev"))
        
        # 验证
        self.assertIn(AgentId("dev"), updated.agent_ids)
        self.mock_repo.save.assert_called_once()
    
    def test_list_projects(self):
        """测试列出项目"""
        # 准备测试数据
        projects = [
            Project(
                id=ProjectId("p1"),
                name="Project 1",
                type=ProjectType.DEDICATED,
                source=DataSource.BOT_PROJECT,
                priority=Priority.HIGH,
                status=ProjectStatus.ACTIVE
            ),
            Project(
                id=ProjectId("p2"),
                name="Project 2",
                type=ProjectType.DEDICATED,
                source=DataSource.BOT_PROJECT,
                priority=Priority.LOW,
                status=ProjectStatus.ACTIVE
            )
        ]
        self.mock_repo.list.return_value = projects
        
        # 执行
        result = self.service.list_projects()
        
        # 验证
        self.assertEqual(len(result), 2)


class TestDashboardService(unittest.TestCase):
    """测试 DashboardService"""
    
    def setUp(self):
        """设置 Mock"""
        self.mock_project_service = Mock()
        self.mock_progress_source = Mock()
        
        self.service = DashboardService(
            project_service=self.mock_project_service,
            progress_sources=[self.mock_progress_source]
        )
    
    def test_generate_summary(self):
        """测试生成摘要"""
        # 准备测试数据
        from core.domain import ProjectProgress
        
        projects = [
            Project(
                id=ProjectId("p1"),
                name="Project 1",
                type=ProjectType.DEDICATED,
                source=DataSource.BOT_PROJECT,
                priority=Priority.HIGH,
                status=ProjectStatus.ACTIVE
            )
        ]
        self.mock_project_service.list_projects.return_value = projects
        
        progress = ProjectProgress(
            project_id=ProjectId("p1"),
            percentage=50,
            phase="开发中"
        )
        self.mock_progress_source.can_handle.return_value = True
        self.mock_progress_source.get_progress.return_value = progress
        
        # 执行
        summary = self.service.generate_summary()
        
        # 验证
        self.assertEqual(summary.total, 1)
        self.assertEqual(summary.active, 1)


if __name__ == '__main__':
    unittest.main()
