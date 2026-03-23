from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=200)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    completed: Optional[bool] = Field(None, alias="is_completed")


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: Optional[UUID] = None
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    completed: bool = Field(default=False, alias="is_completed")
