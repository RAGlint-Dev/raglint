"""
Alerting module for RAGLint.
Handles sending notifications to external channels (e.g., Slack) when issues are detected.
"""

import asyncio
import logging
import os
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)

class AlertManager:
    """
    Manages system alerts and notifications.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
            cls._instance.enabled = bool(cls._instance.slack_webhook_url)
        return cls._instance

    async def send_alert(self, title: str, message: str, level: str = "info", details: Optional[dict[str, Any]] = None):
        """
        Send an alert to configured channels.
        """
        if not self.enabled:
            return

        if self.slack_webhook_url:
            await self._send_slack_alert(title, message, level, details)

    async def _send_slack_alert(self, title: str, message: str, level: str, details: Optional[dict[str, Any]]):
        """Send alert to Slack."""
        color = "#36a64f"  # Green (Info)
        if level == "warning":
            color = "#ffcc00"
        elif level == "error":
            color = "#ff0000"

        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"RAGLint Alert: {title}",
                    "text": message,
                    "fields": []
                }
            ]
        }

        if details:
            for k, v in details.items():
                payload["attachments"][0]["fields"].append({
                    "title": k,
                    "value": str(v),
                    "short": True
                })

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.slack_webhook_url, json=payload) as resp:
                    if resp.status != 200:
                        logger.error(f"Failed to send Slack alert: {await resp.text()}")
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")

    def send_alert_sync(self, title: str, message: str, level: str = "info", details: Optional[dict[str, Any]] = None):
        """Synchronous wrapper for sending alerts."""
        if not self.enabled:
            return

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we schedule it as a task
                loop.create_task(self.send_alert(title, message, level, details))
            else:
                loop.run_until_complete(self.send_alert(title, message, level, details))
        except Exception as e:
            # Fallback for when no loop is available or other issues
            # In a real app, might use 'requests' here for true sync fallback
            logger.warning(f"Could not send async alert from sync context: {e}")
