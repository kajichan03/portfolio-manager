"""Portfolio Manager iMessage 通知适配器

本模块实现通过 iMessage 发送通知的适配器。
通过调用 imsg CLI 工具或 AppleScript 实现。
"""

import subprocess
from typing import Dict, Any

from core.adapters.base import NotificationAdapter, NotificationError


class IMessageAdapter(NotificationAdapter):
    """iMessage 通知适配器
    
    通过 imsg CLI 工具或 osascript 发送 iMessage 消息。
    
    Attributes:
        _use_applescript: 是否使用 AppleScript（备用方案）
    """
    
    def __init__(self, use_applescript: bool = False):
        """
        Args:
            use_applescript: 是否使用 AppleScript 而非 imsg CLI
        """
        self._use_applescript = use_applescript
    
    def send(self, config: Dict[str, Any], message: str) -> bool:
        """发送 iMessage 消息
        
        Args:
            config: 配置字典，必须包含 handle（手机号或邮箱）
            message: 消息内容
            
        Returns:
            是否发送成功
            
        Raises:
            NotificationError: 发送失败
        """
        handle = config.get("handle")
        if not handle:
            raise NotificationError(
                "handle is required in config",
                channel="imessage"
            )
        
        if self._use_applescript:
            return self._send_via_applescript(handle, message)
        else:
            return self._send_via_imsg(handle, message)
    
    def _send_via_imsg(self, handle: str, message: str) -> bool:
        """通过 imsg CLI 发送
        
        使用 imsg 命令行工具发送消息。
        """
        try:
            result = subprocess.run(
                ["imsg", handle, message],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise NotificationError(
                    f"imsg error: {result.stderr}",
                    channel="imessage"
                )
            
            return True
            
        except FileNotFoundError:
            # imsg 未安装，尝试 AppleScript
            return self._send_via_applescript(handle, message)
        except subprocess.TimeoutExpired:
            raise NotificationError(
                "Timeout sending iMessage",
                channel="imessage"
            )
        except Exception as e:
            raise NotificationError(
                f"Failed to send iMessage: {e}",
                channel="imessage"
            ) from e
    
    def _send_via_applescript(self, handle: str, message: str) -> bool:
        """通过 AppleScript 发送
        
        使用 osascript 调用 Messages.app 发送消息。
        这是备用方案，当 imsg CLI 不可用时使用。
        """
        # 转义特殊字符
        escaped_handle = handle.replace('"', '\\"')
        escaped_message = message.replace('"', '\\"').replace("\\", "\\\\")
        
        script = f'''
        tell application "Messages"
            set targetService to 1st service whose service type = iMessage
            set targetBuddy to buddy "{escaped_handle}" of targetService
            send "{escaped_message}" to targetBuddy
        end tell
        '''
        
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise NotificationError(
                    f"AppleScript error: {result.stderr}",
                    channel="imessage"
                )
            
            return True
            
        except FileNotFoundError:
            raise NotificationError(
                "osascript not found. iMessage sending requires macOS.",
                channel="imessage"
            )
        except subprocess.TimeoutExpired:
            raise NotificationError(
                "Timeout sending iMessage via AppleScript",
                channel="imessage"
            )
        except Exception as e:
            raise NotificationError(
                f"Failed to send iMessage: {e}",
                channel="imessage"
            ) from e
    
    def get_channel_name(self) -> str:
        """获取渠道名称"""
        return "imessage"
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否有效
        
        检查必需的 handle（手机号或邮箱）是否存在。
        
        Args:
            config: 配置字典
            
        Returns:
            配置是否有效
        """
        if not isinstance(config, dict):
            return False
        
        handle = config.get("handle")
        if not handle:
            return False
        
        # 简单验证：手机号或邮箱格式
        handle = str(handle).strip()
        
        # 邮箱格式检查
        if "@" in handle:
            return True
        
        # 手机号格式检查（简单检查：数字和+号）
        if handle.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            return True
        
        return False
