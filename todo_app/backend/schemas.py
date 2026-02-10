from typing import Optional
from enum import IntEnum, Enum
from pydantic import BaseModel, Field

class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Status(str, Enum):
    TODO = 'to-do'
    IN_PROGRESS = 'in-progress'
    DONE = 'done'

class TodoBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=512, description='Name of the task')
    description: str = Field(...,  description='Description of the task')
    priority: Priority = Field(default=Priority.LOW, description='Priority of the task')
    status: Status = Field(default=Status.TODO, description="Status of the task")

class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: int = Field(..., description='Unique identifier of the task')