"""Portfolio Manager CLI - 主入口

本模块是 CLI 的主入口点，使用 Click 框架。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import click

from interfaces.cli.commands.dashboard import dashboard_command
from interfaces.cli.commands.project import project_group


@click.group()
@click.pass_context
def cli(ctx):
    """Portfolio Manager CLI
    
    项目组合管理系统的命令行工具。
    
    示例:
        portfolio dashboard
        portfolio project list
        portfolio project create "My Project"
    """
    # 初始化服务容器
    # 注意：实际使用时需要加载配置并创建 ServiceContainer
    # 这里暂时使用 None，实际实现时需要替换
    ctx.obj = None


# 注册子命令
cli.add_command(dashboard_command)
cli.add_command(project_group)


if __name__ == '__main__':
    cli()
