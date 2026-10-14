"""
ITBIS - Real-Time Alert & Threat Notification WebSocket Manager
Handles live connection pools and broadcasts real-time threat telemetry to SOC analysts.
"""

from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from typing import Any
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]):
        """Send JSON message to all active WebSocket connections."""
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

    def broadcast_sync(self, message: dict[str, Any]):
        """Non-blocking broadcast helper for synchronous request threads."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.broadcast(message))
            else:
                loop.run_until_complete(self.broadcast(message))
        except RuntimeError:
            # Fallback if no loop in current thread
            pass


ws_manager = ConnectionManager()


def create_notification_payload(
    title: str,
    message: str,
    severity: str = "medium",
    category: str = "alert",
    reference_id: str | None = None,
) -> dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "message": message,
        "severity": severity.lower(),
        "category": category,
        "reference_id": str(reference_id) if reference_id else None,
    }
