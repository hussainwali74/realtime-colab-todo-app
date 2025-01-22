from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import todo_routes
from .config.database import connect_to_mongo, close_mongo_connection
import logging
from contextlib import asynccontextmanager
import socketio
from .sockets.socket_instance import sio

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(title="Todo App API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todo_routes.router)

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Todo API is running"}

socket_app = socketio.ASGIApp(sio, app)