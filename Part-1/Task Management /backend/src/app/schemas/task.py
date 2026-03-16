from pydantic import BaseModel, Field
from typing import Optional


class Task(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    is_completed: bool = Field(default=False)
