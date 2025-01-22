from pydantic import BaseModel, Field, ConfigDict, json_schema
from typing import Optional, Any, Dict, Annotated
from datetime import datetime, timezone
from bson import ObjectId

from typing import Any

from bson import ObjectId
from pydantic_core import core_schema

# for swagger UI mapping 
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")

        return ObjectId(value)


# Todo Model
class TodoModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    # id: Optional[ObjectId] = Field(alias="_id", default=None)
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "title": "Write a python file",
                "description": "Write code in python to do something.",
                "completed": False
            }
        }
    )

    def model_dump(self, **kwargs):
        """Custom model_dump to handle datetime serialization"""
        data = super().model_dump(**kwargs)
        # Convert datetime objects to ISO format strings
        if 'created_at' in data:
            data['created_at'] = data['created_at'].isoformat()
        if 'updated_at' in data:
            data['updated_at'] = data['updated_at'].isoformat()
        return data
class TodoResponse(BaseModel):
    data: TodoModel

# Explanation of the last three lines:
# 1. `populate_by_name = True`: This allows Pydantic to populate fields using their alias names. 
#    In this model, the `id` field is aliased as `_id`, which is commonly used in MongoDB documents.
# 2. `arbitrary_types_allowed = True`: This setting permits the use of custom types, such as `PyObjectId`, 
#    within the Pydantic model. It is necessary here because `PyObjectId` is not a standard Python type.
# 3. `json_encoders = {ObjectId: str}`: This specifies how to encode custom types when converting the model to JSON. 
#    Here, it converts `ObjectId` instances to strings, which is essential for JSON serialization since `ObjectId` 
#    is not natively serializable to JSON.