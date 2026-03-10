"""Portfolio Manager Skill - 指令处理器

本模块实现 Skill 的指令处理器。
通过 Service Container 直接调用 Services，不经过 CLI。

关键约束：
- ✅ 不导入 CLI 任何模块
- ✅ 直接调用 Service（通过 Service Container）
- ✅ Skill 和 CLI 是平等的接口层
"""

import re
from typing import Dict, Type, Optional, Any

# 只导入 core 层，不导入 interfaces.cli
from output.core.services import ProjectService, DashboardService, AgentService
from output.core.services.commands import CreateProjectCommand
from output.core.domain import ProjectId, AgentId, Priority, ProjectType, DataSource


class SkillCommandBus:
    """Skill 指令总线
    
    负责解析用户输入并分派到对应的处理器。
    """
    
    def __init__(
        self,
        project_service: ProjectService,
        dashboard_service: DashboardService,
        agent_service: AgentService
    ):
        """
        Args:
            project_service: 项目服务
            dashboard_service: Dashboard 服务
            agent_service: Agent 服务
        """
        self._project = project_service
        self._dashboard = dashboard_service
        self._agent = agent_service
        
        # 注册指令处理器
        self._handlers = self._register_handlers()
    
    def _register_handlers(self) -> Dict[str, Any]:
        """注册指令处理器"""
        return {
            # 状态查询
            r"^(状态|summary|status)$": StatusHandler(self._dashboard),
            
            # 详情列表
            r"^(详情|list|projects)$": ListHandler(self._dashboard),
            
            # 项目详情
            r"^项目\s+(.+)$": ProjectDetailHandler(self._dashboard),
            
            # 新建项目
            r"^新建项目\s+(.+)$": CreateProjectHandler(self._project),
            
            # 分配 Agent
            r"^分配\s+(.+)\s+给\s+(.+)$": AssignHandler(self._project, self._agent),
            
            # 设置优先级
            r"^设置优先级\s+(.+)\s+(高|中|低)$": SetPriorityHandler(self._project),
        }
    
    def dispatch(self, message: str) -> str:
        """分派指令并返回响应
        
        Args:
            message: 用户输入消息
            
        Returns:
            响应文本
        """
        message = message.strip()
        
        for pattern, handler in self._handlers.items():
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                return handler.handle(*match.groups())
        
        return self._help_message()
    
    def _help_message(self) -> str:
        """帮助消息"""
        return """未知指令。可用指令:
• 状态 - 查看 Portfolio 摘要
• 详情 - 查看项目详情列表
• 项目 {名称} - 查看指定项目
• 新建项目 {名称} - 创建新项目
• 分配 {项目} 给 {Agent} - 分配 Agent
• 设置优先级 {项目} {高/中/低}"""


class StatusHandler:
    """状态查询处理器"""
    
    def __init__(self, dashboard_service: DashboardService):
        self._dashboard = dashboard_service
    
    def handle(self, *args) -> str:
        """处理状态查询"""
        try:
            summary = self._dashboard.generate_summary()
            return self._format_summary(summary)
        except Exception as e:
            return f"❌ 获取状态失败: {e}"
    
    def _format_summary(self, summary) -> str:
        """格式化摘要"""
        lines = [
            f"📊 Portfolio 状态摘要 ({summary.generated_at.strftime('%Y-%m-%d')})",
            "",
            f"项目总数: {summary.total}",
            f"├─ 🟢 进行中: {summary.active}",
            f"└─ 🔴 阻塞: {summary.blocked}",
        ]
        
        if summary.attention_needed:
            lines.append("")
            lines.append("⚠️ 需要关注:")
            for item in summary.attention_needed[:5]:
                priority = item.get('priority', 'low')
                emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
                reason = item.get('reason', '')
                reason_map = {"blocked": "被阻塞", "waiting_review": "等待 Review"}
                reason_text = reason_map.get(reason, reason)
                lines.append(f"• {emoji} {item.get('project_name')} - {reason_text}")
        
        lines.append("")
        lines.append("💬 回复 \"详情\" 查看完整列表")
        
        return "\n".join(lines)


class ListHandler:
    """详情列表处理器"""
    
    def __init__(self, dashboard_service: DashboardService):
        self._dashboard = dashboard_service
    
    def handle(self, *args) -> str:
        """处理详情查询"""
        try:
            detail = self._dashboard.generate_detail()
            return self._format_detail(detail)
        except Exception as e:
            return f"❌ 获取详情失败: {e}"
    
    def _format_detail(self, detail) -> str:
        """格式化详情"""
        lines = [
            f"📋 项目详情列表 ({detail.generated_at.strftime('%Y-%m-%d')})",
            ""
        ]
        
        # 高优先级
        if detail.high_priority:
            lines.append("🔴 HIGH 优先级")
            lines.append("─" * 20)
            for i, item in enumerate(detail.high_priority, 1):
                lines.extend(self._format_project_item(i, item))
            lines.append("")
        
        # 中优先级
        if detail.medium_priority:
            lines.append("🟡 MEDIUM 优先级")
            lines.append("─" * 20)
            for i, item in enumerate(detail.medium_priority, 1):
                lines.extend(self._format_project_item(
                    i + len(detail.high_priority), item
                ))
            lines.append("")
        
        # 低优先级
        if detail.low_priority:
            lines.append("🟢 LOW 优先级")
            lines.append("─" * 20)
            for i, item in enumerate(detail.low_priority, 1):
                lines.extend(self._format_project_item(
                    i + len(detail.high_priority) + len(detail.medium_priority),
                    item
                ))
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_project_item(self, num: int, item) -> list:
        """格式化单个项目"""
        project = item.project
        progress = item.progress
        
        lines = []
        status_emoji = "🔴" if progress and progress.is_blocked else "🟢"
        progress_str = f"{progress.percentage}%" if progress else "N/A"
        phase = progress.phase if progress else "未知"
        
        lines.append(f"{num}. [{project.name}]")
        lines.append(f"   进度: {progress_str} | 状态: {phase} {status_emoji}")
        
        if project.agent_ids:
            agents = ", ".join(str(a) for a in project.agent_ids)
            lines.append(f"   负责: {agents}")
        
        if progress and progress.next_steps:
            lines.append(f"   下一步: {progress.next_steps[0]}")
        
        lines.append("")
        return lines


class ProjectDetailHandler:
    """项目详情处理器"""
    
    def __init__(self, dashboard_service: DashboardService):
        self._dashboard = dashboard_service
    
    def handle(self, project_name: str) -> str:
        """处理项目详情查询"""
        try:
            # 先查找项目 ID
            projects = self._dashboard._project_service.list_projects()
            target_project = None
            for p in projects:
                if p.name.lower() == project_name.lower() or str(p.id) == project_name:
                    target_project = p
                    break
            
            if not target_project:
                return f"❌ 项目未找到: {project_name}"
            
            item = self._dashboard.get_project_detail(target_project.id)
            if not item:
                return f"❌ 无法获取项目详情: {project_name}"
            
            return self._format_project_detail(item)
            
        except Exception as e:
            return f"❌ 获取项目详情失败: {e}"
    
    def _format_project_detail(self, item) -> str:
        """格式化项目详情"""
        project = item.project
        progress = item.progress
        
        lines = [
            f"📁 {project.name}",
            f"ID: {project.id}",
            f"类型: {project.type.value}",
            f"优先级: {project.priority.emoji} {project.priority.value}",
            f"状态: {project.status.value}",
        ]
        
        if progress:
            lines.append(f"进度: {progress.percentage}%")
            lines.append(f"阶段: {progress.phase}")
            
            if progress.next_steps:
                lines.append("下一步:")
                for step in progress.next_steps[:3]:
                    lines.append(f"  • {step}")
            
            if progress.blockers:
                lines.append("阻塞项:")
                for blocker in progress.blockers:
                    lines.append(f"  ⚠️ {blocker}")
        
        if project.agent_ids:
            lines.append(f"负责 Agent: {', '.join(str(a) for a in project.agent_ids)}")
        
        if project.local_path:
            lines.append(f"本地路径: {project.local_path}")
        
        if project.github_url:
            lines.append(f"GitHub: {project.github_url}")
        
        return "\n".join(lines)


class CreateProjectHandler:
    """创建项目处理器"""
    
    def __init__(self, project_service: ProjectService):
        self._project = project_service
    
    def handle(self, project_name: str) -> str:
        """处理创建项目"""
        try:
            cmd = CreateProjectCommand(
                name=project_name,
                type=ProjectType.DEDICATED,
                source=DataSource.BOT_PROJECT,
                priority=Priority.MEDIUM
            )
            
            project = self._project.create_project(cmd)
            
            return f"""✅ 项目创建成功!

名称: {project.name}
ID: {project.id}
类型: {project.type.value}
优先级: {project.priority.emoji} {project.priority.value}"""
            
        except Exception as e:
            return f"❌ 创建项目失败: {e}"


class AssignHandler:
    """分配 Agent 处理器"""
    
    def __init__(
        self,
        project_service: ProjectService,
        agent_service: AgentService
    ):
        self._project = project_service
        self._agent = agent_service
    
    def handle(self, project_name: str, agent_name: str) -> str:
        """处理分配 Agent"""
        try:
            # 查找项目
            projects = self._project.list_projects()
            target_project = None
            for p in projects:
                if p.name.lower() == project_name.lower() or str(p.id) == project_name:
                    target_project = p
                    break
            
            if not target_project:
                return f"❌ 项目未找到: {project_name}"
            
            # 分配 Agent
            updated = self._project.assign_agent(
                target_project.id,
                AgentId(agent_name.lower())
            )
            
            # 发送通知
            try:
                self._agent.notify_assignment(AgentId(agent_name.lower()), updated)
                notification = "已发送通知给 Agent。"
            except Exception:
                notification = "通知发送失败。"
            
            return f"""✅ 分配成功!

项目: {updated.name}
Agent: {agent_name}
当前 Agent: {', '.join(str(a) for a in updated.agent_ids)}

{notification}"""
            
        except Exception as e:
            return f"❌ 分配失败: {e}"


class SetPriorityHandler:
    """设置优先级处理器"""
    
    def __init__(self, project_service: ProjectService):
        self._project = project_service
    
    def handle(self, project_name: str, priority_str: str) -> str:
        """处理设置优先级"""
        try:
            # 映射优先级
            priority_map = {"高": Priority.HIGH, "中": Priority.MEDIUM, "低": Priority.LOW}
            priority = priority_map.get(priority_str, Priority.MEDIUM)
            
            # 查找项目
            projects = self._project.list_projects()
            target_project = None
            for p in projects:
                if p.name.lower() == project_name.lower() or str(p.id) == project_name:
                    target_project = p
                    break
            
            if not target_project:
                return f"❌ 项目未找到: {project_name}"
            
            # 更新优先级
            updated = self._project.update_project_priority(target_project.id, priority)
            
            return f"""✅ 优先级更新成功!

项目: {updated.name}
新优先级: {updated.priority.emoji} {updated.priority.value}"""
            
        except Exception as e:
            return f"❌ 更新优先级失败: {e}"
