from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8, max_length=72)


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
