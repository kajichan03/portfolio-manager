"""Portfolio Manager CLI - Dashboard 命令

本模块实现 dashboard 子命令。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

import click
from typing import Optional

from output.core.domain import Priority
from output.core.services import DashboardService, SummaryDashboard, DetailDashboard
from output.interfaces.cli.formatters.text_formatter import TextFormatter


@click.command(name='dashboard')
@click.option(
    '--format', 'fmt',
    type=click.Choice(['summary', 'detail'], case_sensitive=False),
    default='summary',
    help='Dashboard 格式: summary 或 detail'
)
@click.option(
    '--priority',
    type=click.Choice(['high', 'medium', 'low'], case_sensitive=False),
    default=None,
    help='按优先级过滤 (仅 detail 格式有效)'
)
@click.pass_context
def dashboard_command(ctx, fmt: str, priority: Optional[str]):
    """生成 Dashboard
    
    示例:
        portfolio dashboard
        portfolio dashboard --format detail
        portfolio dashboard --format detail --priority high
    """
    # 获取服务（从 context 中的 service container）
    services = ctx.obj
    if not services:
        click.echo("错误: 服务未初始化", err=True)
        sys.exit(1)
    
    dashboard_service: DashboardService = services.dashboard
    formatter = TextFormatter()
    
    try:
        if fmt == 'summary':
            result = dashboard_service.generate_summary()
            output = formatter.format_summary(result)
        else:
            priority_enum = Priority(priority) if priority else None
            result = dashboard_service.generate_detail(priority_enum)
            output = formatter.format_detail(result)
        
        click.echo(output)
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
