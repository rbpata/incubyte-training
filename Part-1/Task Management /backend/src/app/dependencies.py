from fastapi import Depends
from sqlalchemy.orm import Session

from src.app.repositories.task_repository import TaskRepository
from src.app.services.task_service import TaskService
from src.app.db.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_task_repository(db: Session = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db=db)


def get_task_service(
    task_repository: TaskRepository = Depends(get_task_repository),
) -> TaskService:
    return TaskService(task_repository=task_repository)
