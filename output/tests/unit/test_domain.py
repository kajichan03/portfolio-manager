"""单元测试 - Domain 领域模型

测试领域模型的创建、不可变性和业务规则。
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import unittest
from datetime import datetime
from pathlib import Path as FilePath

from output.core.domain import (
    Project, ProjectId, ProjectType, DataSource, Priority, ProjectStatus,
    ProjectProgress,
    Task, TaskId, TaskStatus,
    Agent, AgentId, AgentRole, AgentStatus, CommunicationConfig
)


class TestProjectId(unittest.TestCase):
    """测试 ProjectId 值对象"""
    
    def test_valid_slug(self):
        """测试有效的 slug 格式"""
        pid = ProjectId("portfolio-manager")
        self.assertEqual(pid.value, "portfolio-manager")
    
    def test_invalid_slug_raises(self):
        """测试无效的 slug 格式应抛出异常"""
        with self.assertRaises(ValueError):
            ProjectId("invalid slug with spaces!")
    
    def test_empty_raises(self):
        """测试空 ID 应抛出异常"""
        with self.assertRaises(ValueError):
            ProjectId("")
    
    def test_equality(self):
        """测试值对象相等性"""
        pid1 = ProjectId("test")
        pid2 = ProjectId("test")
        self.assertEqual(pid1, pid2)
        self.assertEqual(hash(pid1), hash(pid2))


class TestProject(unittest.TestCase):
    """测试 Project 实体"""
    
    def setUp(self):
        self.project = Project(
            id=ProjectId("test-project"),
            name="Test Project",
            type=ProjectType.DEDICATED,
            source=DataSource.BOT_PROJECT,
            priority=Priority.HIGH,
            status=ProjectStatus.ACTIVE
        )
    
    def test_creation(self):
        """测试项目创建"""
        self.assertEqual(str(self.project.id), "test-project")
        self.assertEqual(self.project.name, "Test Project")
        self.assertEqual(self.project.priority, Priority.HIGH)
    
    def test_immutable(self):
        """测试项目不可变性"""
        with self.assertRaises(Exception):  # FrozenInstanceError
            self.project.name = "New Name"
    
    def test_with_agent(self):
        """测试添加 Agent 返回新实例"""
        updated = self.project.with_agent(AgentId("dev"))
        self.assertIn(AgentId("dev"), updated.agent_ids)
        self.assertNotIn(AgentId("dev"), self.project.agent_ids)  # 原实例不变
    
    def test_empty_name_raises(self):
        """测试空名称应抛出异常"""
        with self.assertRaises(ValueError):
            Project(
                id=ProjectId("test"),
                name="",
                type=ProjectType.DEDICATED,
                source=DataSource.BOT_PROJECT,
                priority=Priority.MEDIUM,
                status=ProjectStatus.ACTIVE
            )


class TestProjectProgress(unittest.TestCase):
    """测试 ProjectProgress 实体"""
    
    def setUp(self):
        self.progress = ProjectProgress(
            project_id=ProjectId("test"),
            percentage=50,
            phase="开发中"
        )
    
    def test_creation(self):
        """测试进度创建"""
        self.assertEqual(self.progress.percentage, 50)
        self.assertEqual(self.progress.phase, "开发中")
    
    def test_mutable(self):
        """测试进度可变性"""
        self.progress.percentage = 75
        self.assertEqual(self.progress.percentage, 75)
    
    def test_is_blocked(self):
        """测试阻塞检测"""
        self.assertFalse(self.progress.is_blocked)
        self.progress.blockers = ["问题1"]
        self.assertTrue(self.progress.is_blocked)
    
    def test_invalid_percentage_raises(self):
        """测试无效百分比应抛出异常"""
        with self.assertRaises(ValueError):
            ProjectProgress(
                project_id=ProjectId("test"),
                percentage=150  # 超过 100
            )


class TestTask(unittest.TestCase):
    """测试 Task 实体"""
    
    def test_creation(self):
        """测试任务创建"""
        task = Task(
            id=TaskId("task-1"),
            project_id=ProjectId("project-1"),
            title="Test Task",
            status=TaskStatus.TODO
        )
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, TaskStatus.TODO)
    
    def test_empty_title_raises(self):
        """测试空标题应抛出异常"""
        with self.assertRaises(ValueError):
            Task(
                id=TaskId("task-1"),
                project_id=ProjectId("project-1"),
                title="",
                status=TaskStatus.TODO
            )


class TestAgent(unittest.TestCase):
    """测试 Agent 实体"""
    
    def setUp(self):
        self.agent = Agent(
            id=AgentId("dev"),
            name="Dev",
            emoji="📟",
            role=AgentRole.DEVELOPER,
            communication=CommunicationConfig("telegram", {"chat_id": "123"})
        )
    
    def test_creation(self):
        """测试 Agent 创建"""
        self.assertEqual(str(self.agent.id), "dev")
        self.assertEqual(self.agent.name, "Dev")
        self.assertEqual(self.agent.role, AgentRole.DEVELOPER)
    
    def test_display_name(self):
        """测试显示名称包含 emoji"""
        self.assertEqual(self.agent.display_name, "📟 Dev")
    
    def test_role_display_name(self):
        """测试角色显示名称"""
        self.assertEqual(self.agent.role.display_name, "开发工程师")


class TestAgentRole(unittest.TestCase):
    """测试 AgentRole 枚举"""
    
    def test_roles(self):
        """测试所有角色"""
        self.assertEqual(AgentRole.COORDINATOR.value, "coordinator")
        self.assertEqual(AgentRole.PRODUCT.value, "product")
        self.assertEqual(AgentRole.DEVELOPER.value, "developer")
        self.assertEqual(AgentRole.QA.value, "qa")


class TestPriority(unittest.TestCase):
    """测试 Priority 枚举"""
    
    def test_emojis(self):
        """测试优先级 emoji"""
        self.assertEqual(Priority.HIGH.emoji, "🔴")
        self.assertEqual(Priority.MEDIUM.emoji, "🟡")
        self.assertEqual(Priority.LOW.emoji, "🟢")


if __name__ == '__main__':
    unittest.main()
