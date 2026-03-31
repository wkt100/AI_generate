import asyncio
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[task_id] = websocket
        logger.info(f"[WS] Client connected for task {task_id}")

    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]
            logger.info(f"[WS] Client disconnected for task {task_id}")

    async def send_message(self, task_id: str, message: dict):
        if task_id in self.active_connections:
            await self.active_connections[task_id].send_json(message)
            logger.info(f"[WS] Sent message to {task_id}: {message}")


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket 端点: ws://host/ws/tasks/{task_id}"""
    await manager.connect(task_id, websocket)
    try:
        while True:
            # 保持连接，等待后端推送消息
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(task_id)


async def broadcast_task_update(task_id: str, status: str, current_state: str, step_info: dict = None):
    """FSM 引擎调用此方法推送状态更新"""
    message = {
        "type": "task_update",
        "task_id": task_id,
        "status": status,
        "current_state": current_state,
    }
    if step_info:
        message["step"] = step_info

    await manager.send_message(task_id, message)