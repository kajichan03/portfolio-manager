"""Portfolio Manager CLI - 文本格式化器

本模块提供 Dashboard 和消息的文本格式化功能。
"""

from datetime import datetime
from typing import List, Optional

from core.services import SummaryDashboard, DetailDashboard, ProjectWithProgress
from core.domain import Priority


class TextFormatter:
    """文本格式化器
    
    将 Dashboard 数据格式化为适合终端或聊天界面显示的文本。
    """
    
    def format_summary(self, summary: SummaryDashboard) -> str:
        """格式化摘要 Dashboard
        
        Args:
            summary: 摘要数据
            
        Returns:
            格式化后的文本
        """
        lines = [
            f"📊 Portfolio 状态摘要 ({summary.generated_at.strftime('%Y-%m-%d')})",
            "",
            f"项目总数: {summary.total}",
            f"├─ 🟢 进行中: {summary.active}",
            f"└─ 🔴 阻塞: {summary.blocked}",
        ]
        
        # 需要关注的项目
        if summary.attention_needed:
            lines.append("")
            lines.append("⚠️ 需要关注:")
            for item in summary.attention_needed[:5]:  # 最多显示 5 个
                priority_emoji = self._get_priority_emoji(item.get('priority', 'low'))
                reason = self._format_reason(item.get('reason', ''))
                assignee = item.get('assignee', '未分配')
                lines.append(f"• {priority_emoji} {item.get('project_name', 'Unknown')} - {reason} ({assignee})")
        
        lines.append("")
        lines.append("💬 回复 \"详情\" 查看完整列表")
        
        return "\n".join(lines)
    
    def format_detail(self, detail: DetailDashboard) -> str:
        """格式化详情 Dashboard
        
        Args:
            detail: 详情数据
            
        Returns:
            格式化后的文本
        """
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
                lines.extend(self._format_project_item(i, item, len(detail.high_priority)))
            lines.append("")
        
        # 低优先级
        if detail.low_priority:
            lines.append("🟢 LOW 优先级")
            lines.append("─" * 20)
            for i, item in enumerate(detail.low_priority, 1):
                lines.extend(self._format_project_item(
                    i, item, 
                    len(detail.high_priority) + len(detail.medium_priority)
                ))
            lines.append("")
        
        return "\n".join(lines)
    
    def format_project_item(
        self, 
        index: int, 
        item: ProjectWithProgress,
        offset: int = 0
    ) -> List[str]:
        """格式化单个项目项
        
        Args:
            index: 序号
            item: 项目及其进度
            offset: 序号偏移量
            
        Returns:
            格式化后的文本行列表
        """
        project = item.project
        progress = item.progress
        
        lines = []
        num = offset + index
        
        # 基本信息
        status_emoji = "🔴" if progress and progress.is_blocked else "🟢"
        progress_str = f"{progress.percentage}%" if progress else "N/A"
        phase = progress.phase if progress else "未知"
        
        lines.append(f"{num}. [{project.name}]")
        lines.append(f"   进度: {progress_str} | 状态: {phase} {status_emoji}")
        
        # Agent 信息
        if project.agent_ids:
            agents = ", ".join(str(a) for a in project.agent_ids)
            lines.append(f"   负责: {agents}")
        
        # 下一步
        if progress and progress.next_steps:
            next_step = progress.next_steps[0]
            lines.append(f"   下一步: {next_step}")
        
        # 阻塞项
        if progress and progress.blockers:
            lines.append(f"   ⚠️ 阻塞: {progress.blockers[0]}")
        
        lines.append("")
        
        return lines
    
    def _get_priority_emoji(self, priority: str) -> str:
        """获取优先级 emoji"""
        return {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(priority, "⚪")
    
    def _format_reason(self, reason: str) -> str:
        """格式化原因"""
        reason_map = {
            "blocked": "被阻塞",
            "waiting_review": "等待 Review",
            "due_today": "今日到期"
        }
        return reason_map.get(reason, reason)
