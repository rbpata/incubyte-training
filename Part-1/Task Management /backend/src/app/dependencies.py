from fastapi import Depends

from src.app.repositories.task_repository import TaskRepository
from src.app.schemas.task import Task
from src.app.services.task_service import TaskService


default_task_repository = TaskRepository(
    initial_tasks=[
        Task(
            id="1",
            title="Task 1",
            description="Description for Task 1",
            is_completed=False,
        )
    ]
)


def get_task_repository() -> TaskRepository:
    return default_task_repository


def get_task_service(
    task_repository: TaskRepository = Depends(get_task_repository),
) -> TaskService:
    return TaskService(task_repository=task_repository)
