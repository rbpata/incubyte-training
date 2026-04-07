from fastapi import HTTPException, status

from app.models.task import Task
from app.db.base import TaskStatus
from app.services.repository import TaskRepository
from app.schemas.task import TaskCreate


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
    ) -> None:
        self.repository = repository

    async def create_task(self, task_data: TaskCreate, user_id: int) -> Task:
        task = await self.repository.create(task_data, user_id)
        return task

    async def get_task(self, task_id: int) -> Task:
        task = await self.repository.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task

    async def list_tasks(
        self,
        user_id: int,
        status_filter: TaskStatus | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Task], int]:
        return await self.repository.find_tasks(
            user_id=user_id,
            status=status_filter,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            size=size,
        )

    async def update_task_status(self, task_id: int, status_value: TaskStatus) -> Task:
        task = await self.get_task(task_id)
        updated_task = await self.repository.update_status(task, status_value)
        return updated_task

    async def delete_task(self, task_id: int) -> None:
        task = await self.get_task(task_id)
        await self.repository.delete(task)
