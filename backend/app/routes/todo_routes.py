from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..models.todo import TodoModel, TodoResponse
from ..services.todo_service import TodoService
from ..sockets.socket_instance import socket_server
import logging
import sys

# Setup logging to output to console
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/todos", tags=["Tstodos"])

def get_todo_service():
    """Dependency to get TodoService instance."""
    return TodoService()

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoModel, todo_service: TodoService = Depends(get_todo_service)):
    """Create a new todo item."""
    try:
        created_todo = await todo_service.create_todo(todo)
        # Add logging to debug broadcast
        logger.info(f"Broadcasting new todo: {created_todo}")
        # Broadcast the creation
        await socket_server.broadcast_todo_update(created_todo, "create")
        return TodoResponse(data=created_todo)
        
    except Exception as e:
        logger.error(f"Error creating todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[TodoModel])
async def get_todos(todo_service: TodoService = Depends(get_todo_service)):
    """Get all todos."""
    try:
        return await todo_service.get_todos()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{todo_id}", response_model=TodoModel)
async def get_todo(todo_id: str, todo_service: TodoService = Depends(get_todo_service)):
    """Get a specific todo by ID."""
    try:
        todo = await todo_service.get_todo(todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with ID {todo_id} not found"
            )
        return todo
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{todo_id}", response_model=TodoModel)
async def update_todo(todo_id: str, todo_update: dict, todo_service: TodoService = Depends(get_todo_service)):
    """Update a todo item."""
    try:
        # Convert the incoming data to a dict and remove None values
        update_data = {k: v for k, v in todo_update.items() if v is not None}
        
        updated_todo = await todo_service.update_todo(todo_id, update_data)
        
        if not updated_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with ID {todo_id} not found"
            )
        # Broadcast the update
        await socket_server.broadcast_todo_update(updated_todo, "update")
        return updated_todo
    except Exception as e:
        logger.error(f"Error updating todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: str, todo_service: TodoService = Depends(get_todo_service)):
    """Delete a todo item."""
    try:
        todo = await todo_service.get_todo(todo_id)  # Get todo before deletion for broadcasting
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with ID {todo_id} not found"
            )
        deleted = await todo_service.delete_todo(todo_id)
        if deleted:
            # Broadcast the deletion
            await socket_server.broadcast_todo_update(todo, "delete")
    except Exception as e:
        print(f"Error deleting todo: {str(e)}")
        logger.error(f"Error deleting todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 