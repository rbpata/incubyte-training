from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import TaskStatus
from app.models.task import Task
from app.schemas.task import TaskCreate


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, task_data: TaskCreate, user_id: int) -> Task:
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            run_at=task_data.run_at,
            status=TaskStatus.PENDING,
            priority=task_data.priority,
            max_retries=task_data.max_retries,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_by_id(self, task_id: int) -> Task | None:
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def find_tasks(
        self,
        user_id: int,
        status: TaskStatus | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Task], int]:
        base_filter = [Task.deleted_at.is_(None), Task.user_id == user_id]
        if status is not None:
            base_filter.append(Task.status == status)
        if search:
            pattern = f"%{search}%"
            base_filter.append(
                (Task.title.ilike(pattern)) | (Task.description.ilike(pattern))
            )

        count_query = (
            select(func.count()).select_from(Task).where(*base_filter)
        )
        total = await self.session.scalar(count_query)

        query = select(Task).where(*base_filter)
        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc(), Task.id.desc())
        else:
            query = query.order_by(sort_column.asc(), Task.id.asc())

        query = query.offset((page - 1) * size).limit(size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total or 0

    async def update_status(self, task: Task, status: TaskStatus) -> Task:
        task.status = status
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        task.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
