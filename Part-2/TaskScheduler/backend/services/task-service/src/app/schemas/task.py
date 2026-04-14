from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.base import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    run_at: datetime
    priority: TaskPriority = TaskPriority.MEDIUM
    max_retries: int = Field(ge=0, le=10)

    @field_validator("run_at")
    @classmethod
    def validate_run_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("run_at must have timezone information")
        return value


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None
    run_at: datetime
    status: TaskStatus
    priority: TaskPriority
    max_retries: int
    retry_count: int
    created_at: datetime
    updated_at: datetime


class PaginatedTaskRead(BaseModel):
    items: list[TaskRead]
    total: int
    page: int
    size: int
    pages: int
