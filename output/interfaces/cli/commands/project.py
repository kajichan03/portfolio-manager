"""Portfolio Manager CLI - Project 命令

本模块实现 project 子命令。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

import click
from typing import Optional

from output.core.domain import ProjectId, AgentId, Priority, ProjectType, DataSource
from output.core.services import ProjectService
from output.core.services.commands import CreateProjectCommand


@click.group(name='project')
def project_group():
    """项目管理命令"""
    pass


@project_group.command(name='list')
@click.option('--status', default=None, help='按状态过滤')
@click.option('--priority', default=None, help='按优先级过滤')
@click.pass_context
def project_list(ctx, status: Optional[str], priority: Optional[str]):
    """列出所有项目"""
    services = ctx.obj
    if not services:
        click.echo("错误: 服务未初始化", err=True)
        sys.exit(1)
    
    project_service: ProjectService = services.project
    
    try:
        priority_enum = Priority(priority) if priority else None
        projects = project_service.list_projects(priority=priority_enum)
        
        if not projects:
            click.echo("暂无项目")
            return
        
        click.echo(f"项目列表 ({len(projects)} 个):\n")
        
        for i, project in enumerate(projects, 1):
            priority_emoji = project.priority.emoji
            click.echo(f"{i}. {priority_emoji} {project.name}")
            click.echo(f"   ID: {project.id}")
            click.echo(f"   类型: {project.type.value}")
            click.echo(f"   状态: {project.status.value}")
            if project.agent_ids:
                agents = ", ".join(str(a) for a in project.agent_ids)
                click.echo(f"   Agent: {agents}")
            click.echo("")
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@project_group.command(name='create')
@click.argument('name')
@click.option('--type', 'project_type', default='dedicated', 
              type=click.Choice(['dedicated', 'operation']))
@click.option('--source', default='bot_project',
              type=click.Choice(['reminders', 'bot_project']))
@click.option('--priority', default='medium',
              type=click.Choice(['high', 'medium', 'low']))
@click.option('--local-path', default=None, help='本地路径')
@click.option('--github-url', default=None, help='GitHub URL')
@click.pass_context
def project_create(
    ctx,
    name: str,
    project_type: str,
    source: str,
    priority: str,
    local_path: Optional[str],
    github_url: Optional[str]
):
    """创建新项目
    
    示例:
        portfolio project create "My Project" --type dedicated --priority high
    """
    services = ctx.obj
    if not services:
        click.echo("错误: 服务未初始化", err=True)
        sys.exit(1)
    
    project_service: ProjectService = services.project
    
    try:
        cmd = CreateProjectCommand(
            name=name,
            type=ProjectType(project_type),
            source=DataSource(source),
            priority=Priority(priority),
            local_path=Path(local_path) if local_path else None,
            github_url=github_url
        )
        
        project = project_service.create_project(cmd)
        
        click.echo(f"✅ 项目创建成功!")
        click.echo(f"   ID: {project.id}")
        click.echo(f"   名称: {project.name}")
        click.echo(f"   类型: {project.type.value}")
        click.echo(f"   优先级: {project.priority.emoji} {project.priority.value}")
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@project_group.command(name='assign')
@click.argument('project_id')
@click.argument('agent_id')
@click.pass_context
def project_assign(ctx, project_id: str, agent_id: str):
    """分配 Agent 到项目
    
    示例:
        portfolio project assign portfolio-manager dev
    """
    services = ctx.obj
    if not services:
        click.echo("错误: 服务未初始化", err=True)
        sys.exit(1)
    
    project_service: ProjectService = services.project
    
    try:
        project = project_service.assign_agent(
            ProjectId(project_id),
            AgentId(agent_id)
        )
        
        click.echo(f"✅ 已分配 Agent '{agent_id}' 到项目 '{project.name}'")
        click.echo(f"   当前 Agent: {', '.join(str(a) for a in project.agent_ids)}")
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
