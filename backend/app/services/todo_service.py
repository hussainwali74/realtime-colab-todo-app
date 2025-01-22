from typing import List
from bson import ObjectId
from ..config.database import get_database
from ..models.todo import TodoModel

class TodoService:
    def __init__(self):
        self.collection = get_database().todos

    async def create_todo(self, todo: TodoModel) -> TodoModel:
        """Create a new todo item."""
        # Convert the TodoModel instance to a dictionary, excluding the 'id' field
        todo_dict = todo.model_dump(exclude=["id"])
        result = await self.collection.insert_one(todo_dict)
        todo_dict["_id"] = result.inserted_id
        return TodoModel(**todo_dict)

    async def get_todos(self) -> List[TodoModel]:
        """Get all todos."""
        todos = []
        cursor = self.collection.find()
        async for document in cursor:
            todos.append(TodoModel(**document))
        return todos

    async def get_todo(self, todo_id: str) -> TodoModel:
        """Get a specific todo by ID."""
        todo = await self.collection.find_one({"_id": ObjectId(todo_id)})
        if todo:
            return TodoModel(**todo)
        return None

    async def update_todo(self, todo_id: str, todo_data: dict) -> TodoModel:
        """Update a todo item."""
        todo = await self.collection.find_one_and_update(
            {"_id": ObjectId(todo_id)},
            {"$set": todo_data},
            return_document=True
        )
        if todo:
            return TodoModel(**todo)
        return None

    async def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo item."""
        result = await self.collection.delete_one({"_id": ObjectId(todo_id)})
        return result.deleted_count > 0 