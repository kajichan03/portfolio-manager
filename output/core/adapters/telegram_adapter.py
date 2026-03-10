"""Portfolio Manager Telegram 通知适配器

本模块实现通过 Telegram Bot API 发送通知的适配器。
"""

import json
from typing import Dict, Any, Optional
from urllib import request, error

from output.core.adapters.base import NotificationAdapter, NotificationError


class TelegramAdapter(NotificationAdapter):
    """Telegram 通知适配器
    
    通过 Telegram Bot API 发送消息。
    
    Attributes:
        _bot_token: Telegram Bot Token
        _base_url: API 基础 URL
    """
    
    def __init__(self, bot_token: str):
        """
        Args:
            bot_token: Telegram Bot Token
        """
        self._bot_token = bot_token
        self._base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send(self, config: Dict[str, Any], message: str) -> bool:
        """发送 Telegram 消息
        
        Args:
            config: 配置字典，必须包含 chat_id
            message: 消息内容（支持 Markdown）
            
        Returns:
            是否发送成功
            
        Raises:
            NotificationError: 发送失败
        """
        chat_id = config.get("chat_id")
        if not chat_id:
            raise NotificationError(
                "chat_id is required in config",
                channel="telegram"
            )
        
        url = f"{self._base_url}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        try:
            req = request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if not result.get("ok"):
                    raise NotificationError(
                        f"Telegram API error: {result.get('description', 'Unknown error')}",
                        channel="telegram"
                    )
                
                return True
                
        except error.HTTPError as e:
            raise NotificationError(
                f"HTTP {e.code}: {e.reason}",
                channel="telegram"
            ) from e
        except error.URLError as e:
            raise NotificationError(
                f"Connection error: {e.reason}",
                channel="telegram"
            ) from e
        except Exception as e:
            raise NotificationError(
                f"Failed to send message: {e}",
                channel="telegram"
            ) from e
    
    def get_channel_name(self) -> str:
        """获取渠道名称"""
        return "telegram"
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否有效
        
        检查必需的 chat_id 是否存在。
        
        Args:
            config: 配置字典
            
        Returns:
            配置是否有效
        """
        if not isinstance(config, dict):
            return False
        return "chat_id" in config and config["chat_id"]
    
    def get_me(self) -> Dict[str, Any]:
        """获取 Bot 信息
        
        用于验证 Bot Token 是否有效。
        
        Returns:
            Bot 信息
            
        Raises:
            NotificationError: 请求失败
        """
        url = f"{self._base_url}/getMe"
        
        try:
            with request.urlopen(url, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                if result.get("ok"):
                    return result.get("result", {})
                else:
                    raise NotificationError(
                        f"Telegram API error: {result.get('description')}",
                        channel="telegram"
                    )
        except Exception as e:
            raise NotificationError(
                f"Failed to get bot info: {e}",
                channel="telegram"
            ) from e
