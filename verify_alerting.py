"""
Verification script for RAGLint Alerting.
Mocks Slack webhook to verify alert triggering.
"""

import os
import sys
import asyncio
from unittest.mock import MagicMock, patch

# Mock dependencies
sys.modules["openai"] = MagicMock()
sys.modules["boto3"] = MagicMock()
sys.modules["sqlalchemy.ext.asyncio"] = MagicMock()
sys.modules["sqlalchemy.orm"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["chromadb"] = MagicMock()

# Add project root to path
sys.path.append(os.getcwd())

async def test_slack_alert():
    print("Testing Slack Alerting...")
    
    # Mock aiohttp
    with patch("aiohttp.ClientSession") as mock_session:
        mock_post = MagicMock()
        mock_post.__aenter__.return_value.status = 200
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_post
        
        from raglint.alerting import AlertManager
        
        # Enable alerting
        manager = AlertManager()
        manager.slack_webhook_url = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
        manager.enabled = True
        
        # Send alert
        await manager.send_alert("Test Alert", "This is a test", "info")
        
        # Verify call
        if mock_session.return_value.__aenter__.return_value.post.called:
            print("✅ AlertManager: Slack webhook called")
        else:
            print("❌ AlertManager: Slack webhook NOT called")

async def test_instrumentation_alert():
    print("\nTesting Instrumentation Alert Integration...")
    
    with patch("raglint.alerting.AlertManager.send_alert_sync") as mock_send:
        from raglint.instrumentation import Monitor
        
        monitor = Monitor()
        monitor.trace_file = "test_alert_events.jsonl"
        
        # Simulate error event
        monitor.log_event("end", {
            "operation": "test_op",
            "status": "error",
            "error": "Something went wrong",
            "trace_id": "123"
        })
        
        if mock_send.called:
            print("✅ Instrumentation: Alert triggered on error")
        else:
            print("❌ Instrumentation: Alert NOT triggered on error")
            
    if os.path.exists("test_alert_events.jsonl"):
        os.remove("test_alert_events.jsonl")

async def main():
    await test_slack_alert()
    await test_instrumentation_alert()

if __name__ == "__main__":
    asyncio.run(main())
