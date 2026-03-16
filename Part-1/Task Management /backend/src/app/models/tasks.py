from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from src.app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String)
    is_completed = Column("completed", Boolean, default=False)
    created_at = Column("created_at", DateTime, default=datetime.datetime.utcnow)
