import socketio
import logging
from ..models.todo import TodoModel
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class SocketServer:
    def __init__(self):
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins=["http://localhost", "http://localhost:4200", "http://localhost:80"],  
            logger=True,
            engineio_logger=True,
            ping_timeout=60,
            ping_interval=25,
            max_http_buffer_size=1e8,
            allow_upgrades=True
        )
        self.connected_clients = set()
        self.register_events()

    def register_events(self):
        self.sio.on('error', self.error_handler)
        self.sio.event(self.connect)
        self.sio.event(self.disconnect)
        self.sio.on('todo_created', self.handle_todo_created)
        self.sio.on('todo_updated', self.handle_todo_updated)
        self.sio.on('todo_deleted', self.handle_todo_deleted)

    async def error_handler(self, sid, error):
        logger.error(f"SocketIO error for {sid}: {str(error)}")

    async def connect(self, sid, environ=None):
        logger.info(f"Client connected: {sid}")
        self.connected_clients.add(sid)
        count = len(self.connected_clients)
        await self.sio.emit('user_count', count)

    async def disconnect(self, sid):
        logger.info(f"Client disconnected: {sid}")
        if sid in self.connected_clients:
            self.connected_clients.remove(sid)
            count = len(self.connected_clients)
            await self.sio.emit('user_count', count)

    async def handle_todo_created(self, sid, data):
        await self.sio.emit('todo_created', data, skip_sid=sid)

    async def handle_todo_updated(self, sid, data):
        await self.sio.emit('todo_updated', data, skip_sid=sid)

    async def handle_todo_deleted(self, sid, data):
        await self.sio.emit('todo_deleted', data, skip_sid=sid)

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
            await self.sio.emit(event_type, message)
            
        except Exception as e:
            print(f"Error broadcasting todo update: {str(e)}")
            logger.error(f"Error broadcasting todo update: {str(e)}")

# Create an instance of the SocketServer
socket_server = SocketServer()
sio = socket_server.sio
