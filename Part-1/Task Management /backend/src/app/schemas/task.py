from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=200)


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    is_completed: bool = Field(default=False)
