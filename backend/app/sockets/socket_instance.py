import socketio
import logging

logger = logging.getLogger(__name__)

# Create Socket.IO server with CORS configuration
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://localhost", "http://localhost:4200", "http://localhost:80"],  
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1e8,
    allow_upgrades=True
)

connected_clients = set()

# Remove the @sio.on_error() decorator and use error_handler event instead
@sio.on('error')
async def error_handler(sid, error):
    logger.error(f"SocketIO error for {sid}: {str(error)}")

@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    connected_clients.add(sid)
    count = len(connected_clients)
    await sio.emit('user_count', count)

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")
    if sid in connected_clients:
        connected_clients.remove(sid)
        count = len(connected_clients)
        await sio.emit('user_count', count)

@sio.on('todo_created')
async def handle_todo_created(sid, data):
    await sio.emit('todo_created', data, skip_sid=sid)

@sio.on('todo_updated')
async def handle_todo_updated(sid, data):
    await sio.emit('todo_updated', data, skip_sid=sid)

@sio.on('todo_deleted')
async def handle_todo_deleted(sid, data):
    await sio.emit('todo_deleted', data, skip_sid=sid)   