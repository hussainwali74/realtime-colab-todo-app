# Todo App Backend

A FastAPI-based backend for a real-time collaborative todo application.

## Current Setup

### Project Structure
```
backend/
├── app/
│   ├── config/      # Configuration files
│   ├── models/      # Pydantic models
│   ├── routes/      # API endpoints
│   ├── services/    # Business logic
│   ├── sockets/     # WebSocket handlers
│   └── main.py      # FastAPI application entry point
├── .env             # Environment variables
└── requirements.txt # Project dependencies
```

### Dependencies
- FastAPI (0.115.0) - Web framework
- Python-SocketIO (5.12.1) - WebSocket support
- Motor (3.6.1) - Async MongoDB driver
- Other dependencies in requirements.txt

### Prerequisites
- Python 3.10+
- MongoDB running locally (or accessible MongoDB instance)

### Setup Instructions
1. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env`:
   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=todo_db
   ```

4. Run the server:
   ```bash
   uvicorn app.main:socket_app --reload
   ```

### API Endpoints
- `GET /` - Health check endpoint
- `GET /todos` - List all todos
- `GET /todos/{todo_id}` - Get a specific todo
- `POST /todos` - Create a new todo
- `PUT /todos/{todo_id}` - Update a todo
- `DELETE /todos/{todo_id}` - Delete a todo

### WebSocket Integration

#### Connection
Connect to the WebSocket endpoint at: `ws://localhost:8000/ws/todos`

#### Message Format
The server sends JSON messages in the following format:

1. Connection Status Message:
```json
{
    "type": "connection_status",
    "status": "connected",
    "connection_id": "connection_1",
    "timestamp": "2024-01-20T12:00:00.000Z"
}
```

2. Todo Update Messages:
```json
{
    "type": "todo_update",
    "action": "create|update|delete",
    "todo": {
        "_id": "...",
        "title": "...",
        "description": "...",
        "completed": false,
        "created_at": "2024-01-20T12:00:00.000Z",
        "updated_at": "2024-01-20T12:00:00.000Z"
    },
    "timestamp": "2024-01-20T12:00:00.000Z"
}
```

#### Real-time Updates
The WebSocket connection will automatically receive updates when:
- A new todo is created
- An existing todo is updated
- A todo is deleted

Each update includes the complete todo object and the type of action performed.

### Error Handling
- WebSocket connections are automatically cleaned up on disconnection
- Failed message deliveries are handled gracefully
- Connection errors are logged for debugging
- Automatic reconnection should be implemented on the client side

### Current Features
- FastAPI application setup
- CORS configuration
- MongoDB connection setup
- Basic Socket.IO integration 