from src.app.repositories.task_repository import TaskRepository
from src.app.schemas.task import Task, TaskCreate, TaskUpdate
from uuid import UUID


class TaskNotFoundError(Exception):
    pass


class TaskService:
    def __init__(self, task_repository: TaskRepository) -> None:
        self._task_repository = task_repository

    def list_tasks(self, filter_by=None, order="asc", limit=None, offset=None):
        return self._task_repository.list_tasks(
            filter_by=filter_by, order=order, limit=limit, offset=offset
        )

    def create_task(self, task_data: TaskCreate) -> Task:
        return self._task_repository.create_task(task_data)

    def update_task(self, task_id: UUID, task_data: TaskUpdate) -> Task:
        updated_task = self._task_repository.update_task(
            task_id=task_id, task_data=task_data
        )
        if updated_task is None:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return updated_task

    def delete_task(self, task_id: UUID) -> Task:
        deleted_task = self._task_repository.delete_task(task_id=task_id)
        if deleted_task is None:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return deleted_task
