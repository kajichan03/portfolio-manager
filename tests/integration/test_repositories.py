"""集成测试 - Repository 适配器

测试 Repository 与真实文件系统的交互。
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import unittest

from core.domain import (
    Project, ProjectId, ProjectType, DataSource, Priority, ProjectStatus,
    Agent, AgentId, AgentRole, AgentStatus, CommunicationConfig
)
from core.adapters import JsonProjectRepository, JsonAgentRepository
from core.adapters.base import ProjectNotFoundError, AgentNotFoundError


class TestJsonProjectRepository(unittest.TestCase):
    """测试 JsonProjectRepository"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.repo = JsonProjectRepository(self.temp_dir)
    
    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_get(self):
        """测试保存和读取项目"""
        project = Project(
            id=ProjectId("test-project"),
            name="Test Project",
            type=ProjectType.DEDICATED,
            source=DataSource.BOT_PROJECT,
            priority=Priority.HIGH,
            status=ProjectStatus.ACTIVE
        )
        
        # 保存
        self.repo.save(project)
        
        # 读取
        loaded = self.repo.get(ProjectId("test-project"))
        self.assertEqual(loaded.name, "Test Project")
        self.assertEqual(loaded.priority, Priority.HIGH)
    
    def test_get_not_found_raises(self):
        """测试读取不存在的项目应抛出异常"""
        with self.assertRaises(ProjectNotFoundError):
            self.repo.get(ProjectId("non-existent"))
    
    def test_list(self):
        """测试列出项目"""
        # 创建多个项目
        for i in range(3):
            project = Project(
                id=ProjectId(f"project-{i}"),
                name=f"Project {i}",
                type=ProjectType.DEDICATED,
                source=DataSource.BOT_PROJECT,
                priority=Priority.MEDIUM,
                status=ProjectStatus.ACTIVE
            )
            self.repo.save(project)
        
        # 列出
        projects = self.repo.list()
        self.assertEqual(len(projects), 3)
    
    def test_delete(self):
        """测试删除项目"""
        project = Project(
            id=ProjectId("to-delete"),
            name="To Delete",
            type=ProjectType.DEDICATED,
            source=DataSource.BOT_PROJECT,
            priority=Priority.MEDIUM,
            status=ProjectStatus.ACTIVE
        )
        self.repo.save(project)
        
        # 删除
        self.repo.delete(ProjectId("to-delete"))
        
        # 验证
        self.assertFalse(self.repo.exists(ProjectId("to-delete")))
    
    def test_exists(self):
        """测试存在性检查"""
        project = Project(
            id=ProjectId("exists"),
            name="Exists",
            type=ProjectType.DEDICATED,
            source=DataSource.BOT_PROJECT,
            priority=Priority.MEDIUM,
            status=ProjectStatus.ACTIVE
        )
        self.repo.save(project)
        
        self.assertTrue(self.repo.exists(ProjectId("exists")))
        self.assertFalse(self.repo.exists(ProjectId("not-exists")))


class TestJsonAgentRepository(unittest.TestCase):
    """测试 JsonAgentRepository"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.repo = JsonAgentRepository(self.temp_dir)
    
    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_get(self):
        """测试保存和读取 Agent"""
        agent = Agent(
            id=AgentId("test-agent"),
            name="Test Agent",
            emoji="🤖",
            role=AgentRole.DEVELOPER,
            communication=CommunicationConfig("telegram", {"chat_id": "123"})
        )
        
        # 保存
        self.repo.save(agent)
        
        # 读取
        loaded = self.repo.get(AgentId("test-agent"))
        self.assertEqual(loaded.name, "Test Agent")
        self.assertEqual(loaded.role, AgentRole.DEVELOPER)
    
    def test_get_not_found_raises(self):
        """测试读取不存在的 Agent 应抛出异常"""
        with self.assertRaises(AgentNotFoundError):
            self.repo.get(AgentId("non-existent"))


if __name__ == '__main__':
    unittest.main()
