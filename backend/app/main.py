from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import todo_routes
from .config.database import connect_to_mongo, close_mongo_connection
import logging
from contextlib import asynccontextmanager
from .sockets.socket_instance import sio
from socketio.asgi import ASGIApp

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

# Create the FastAPI app
fastapi_app = FastAPI(title="Todo App API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
fastapi_app.include_router(todo_routes.router)

@fastapi_app.get("/")
async def root():
    return {"status": "healthy", "message": "Todo API is running"}

# Create Socket.IO app
socket_app = ASGIApp(sio, fastapi_app)

# For compatibility with existing code
app = socket_app