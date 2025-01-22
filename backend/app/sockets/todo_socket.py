from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from ..models.todo import TodoModel
import logging
import json
from datetime import datetime, timezone
import uuid
import sys
from .socket_instance import sio

# Setup logging to output to console
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        print('------------------------------------------Hmaaaaaaaaaaaa---')
        """Accept connection and add to active connections"""
        try:
            await websocket.accept()
            # Generate unique connection ID using UUID
            connection_id = str(uuid.uuid4())
            self.active_connections[connection_id] = websocket
            count = len(self.active_connections)
            logger.info(f"Client {connection_id} connected. Total connections: {count}")
            
            # Send connection confirmation
            await websocket.send_json({
                "type": "connection_status",
                "status": "connected",
                "connection_id": connection_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            logger.info("Sent connection confirmation")

            # Immediately send current user count to the new connection
            await websocket.send_json({
                "type": "user_count",
                "data": count
            })
            logger.info(f"Sent initial user count: {count}")
            
            # Then broadcast to all clients
            await self.broadcast_user_count()
            
            return connection_id
        except Exception as e:
            logger.error(f"Error during WebSocket connection: {str(e)}")
            raise

    async def disconnect(self, connection_id: str):
        """Remove connection from active connections"""
        try:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.close()
                except:
                    pass
                del self.active_connections[connection_id]
                logger.info(f"Client {connection_id} disconnected. Total connections: {len(self.active_connections)}")
                # Broadcast updated user count to all clients
                await self.broadcast_user_count()
        except Exception as e:
            logger.error(f"Error during WebSocket disconnection: {str(e)}")

    async def broadcast_todo_update(self, todo: TodoModel, action: str):
        """Broadcast todo updates to all connected clients"""
        try:
            # Map actions to specific event types
            event_type = {
                "create": "todo_created",
                "update": "todo_updated",
                "delete": "todo_deleted"
            }.get(action, "todo_update")

            message = {
                "type": event_type,
                "action": action,
                "data": todo.model_dump(by_alias=True),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Broadcasting todo update: {message}")
            # Emit with the specific event type
            await sio.emit(event_type, message)
            
        except Exception as e:
            logger.error(f"Error broadcasting todo update: {str(e)}")

    async def broadcast_user_count(self):
        count = len(self.active_connections)
        logger.info(f"Broadcasting user count: {count}")
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json({
                    "type": "user_count",
                    "data": count
                })
                logger.info(f"Sent user count to client {connection_id}")
            except Exception as e:
                logger.error(f"Error sending user count to client {connection_id}: {str(e)}")

# Create a global instance of the connection manager
socket_manager = ConnectionManager() 