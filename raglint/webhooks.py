"""
Generic Webhook System for RAGLint
Supports triggering webhooks on various events (not just Slack)
"""

import asyncio
import logging
from enum import Enum
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)

class WebhookEvent(str, Enum):
    """Types of events that can trigger webhooks"""
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"
    METRIC_THRESHOLD_BREACH = "metric.threshold_breach"
    HIGH_LATENCY = "trace.high_latency"
    ERROR_OCCURRED = "trace.error"
    DAILY_SUMMARY = "summary.daily"

class WebhookManager:
    """
    Manages generic webhook deliveries
    """

    def __init__(self):
        self.webhooks: list[dict[str, Any]] = []
        self.load_webhooks()

    def load_webhooks(self):
        """Load webhooks from config"""
        import json
        import os

        webhooks_config = os.getenv("RAGLINT_WEBHOOKS")
        if webhooks_config:
            try:
                self.webhooks = json.loads(webhooks_config)
            except:
                logger.warning("Failed to parse RAGLINT_WEBHOOKS")

    def register_webhook(self, url: str, events: list[WebhookEvent], headers: Optional[dict[str, str]] = None):
        """Register a new webhook"""
        webhook = {
            "url": url,
            "events": [e.value for e in events],
            "headers": headers or {},
            "enabled": True
        }
        self.webhooks.append(webhook)

    async def trigger(self, event: WebhookEvent, payload: dict[str, Any]):
        """
        Trigger webhooks for a specific event
        """
        matching_webhooks = [
            wh for wh in self.webhooks
            if wh["enabled"] and event.value in wh["events"]
        ]

        if not matching_webhooks:
            return

        # Prepare payload
        webhook_payload = {
            "event": event.value,
            "timestamp": payload.get("timestamp"),
            "data": payload
        }

        # Send to all matching webhooks
        tasks = []
        for webhook in matching_webhooks:
            tasks.append(self._send_webhook(webhook, webhook_payload))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_webhook(self, webhook: dict[str, Any], payload: dict[str, Any]):
        """Send a single webhook"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook["url"],
                    json=payload,
                    headers=webhook.get("headers", {}),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status >= 400:
                        logger.error(f"Webhook failed: {webhook['url']} - {resp.status}")
                    else:
                        logger.info(f"Webhook delivered: {webhook['url']}")
        except Exception as e:
            logger.error(f"Webhook error: {webhook['url']} - {e}")

# Global instance
webhook_manager = WebhookManager()

# Helper functions
async def trigger_run_completed(run_id: str, metrics: dict[str, float]):
    """Trigger webhook when a run completes"""
    await webhook_manager.trigger(
        WebhookEvent.RUN_COMPLETED,
        {
            "run_id": run_id,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

async def trigger_metric_breach(metric_name: str, value: float, threshold: float):
    """Trigger webhook when metric breaches threshold"""
    await webhook_manager.trigger(
        WebhookEvent.METRIC_THRESHOLD_BREACH,
        {
            "metric": metric_name,
            "value": value,
            "threshold": threshold,
            "severity": "high" if value < threshold * 0.8 else "medium",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

from datetime import datetime
