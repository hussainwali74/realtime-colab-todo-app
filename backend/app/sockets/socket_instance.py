import socketio

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:4200','*'],
    logger=True,
    engineio_logger=True
)

connected_clients = set()

@sio.on('connect')
async def handle_connect(sid, environ):
    connected_clients.add(sid)
    count = len(connected_clients)
    await sio.emit('user_count', count)

@sio.on('disconnect')
async def handle_disconnect(sid):
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