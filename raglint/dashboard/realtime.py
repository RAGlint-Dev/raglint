"""
Real-time metrics dashboard with WebSocket support
"""

import asyncio
from datetime import datetime
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]):
        """Send message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Connection closed, will be cleaned up
                pass

# Global manager instance
manager = ConnectionManager()

async def send_metric_update(metric_name: str, value: float, metadata: dict[str, Any] = None):
    """
    Send a metric update to all connected dashboards
    """
    message = {
        "type": "metric_update",
        "metric": metric_name,
        "value": value,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": metadata or {}
    }

    await manager.broadcast(message)

async def send_trace_event(event: dict[str, Any]):
    """
    Send a trace event to all connected dashboards
    """
    message = {
        "type": "trace_event",
        "event": event,
        "timestamp": datetime.utcnow().isoformat()
    }

    await manager.broadcast(message)

async def stream_metrics(websocket: WebSocket):
    """
    Stream metrics to a connected client
    """
    await manager.connect(websocket)

    try:
        # Send initial state
        await websocket.send_json({
            "type": "connected",
            "message": "Real-time metrics stream started"
        })

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for any messages from client (optional ping/pong)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)

                if data == "ping":
                    await websocket.send_json({"type": "pong"})

            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({"type": "keepalive"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
