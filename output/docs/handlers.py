"""Portfolio Manager Skill Handlers

OpenClaw 通过此模块调用 Portfolio Manager。
复制到 ~/.openclaw/workspace/skills/portfolio/handlers.py
"""

import sys
from pathlib import Path

# 添加 workspace 根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from output.interfaces.skill import handle_message


def process(text: str) -> str:
    """处理用户消息
    
    这是 OpenClaw 调用的主入口。
    
    Args:
        text: 用户输入的消息
        
    Returns:
        响应文本
    """
    return handle_message(text)
