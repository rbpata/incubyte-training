from fastapi import (
    APIRouter,
    Depends,
    Response,
    Query,
    status,
    BackgroundTasks,
    HTTPException,
)
import logging

from app.db.base import TaskStatus
from app.schemas.task import TaskCreate, PaginatedTaskRead, TaskRead, TaskStatusUpdate
from app.services.task import TaskService
from app.services.repository import TaskRepository
from app.dependencies import (
    provide_service,
    provide_job_processor,
    get_session,
    get_current_user,
    get_current_admin,
    rate_limit_dependency,
)
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task import Task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def create_tasks_router() -> APIRouter:
    tasks_router = APIRouter()

    @tasks_router.post(
        "/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED
    )
    async def create_task(
        payload: TaskCreate,
        current_user: User = Depends(get_current_user),
        service: TaskService = Depends(provide_service),
        _: None = Depends(rate_limit_dependency),
    ) -> TaskRead:
        """Create task for current user."""
        task = await service.create_task(payload, user_id=current_user.id)
        return TaskRead.model_validate(task)

    @tasks_router.get("/tasks", response_model=PaginatedTaskRead)
    async def list_tasks(
        status_filter: TaskStatus | None = Query(None, alias="status"),
        search: str | None = Query(None, min_length=1),
        sort_by: str = Query(
            "created_at", pattern="^(created_at|run_at|status|priority)$"
        ),
        sort_order: str = Query("desc", pattern="^(asc|desc)$"),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        service: TaskService = Depends(provide_service),
        _: None = Depends(rate_limit_dependency),
    ) -> PaginatedTaskRead:
        """List tasks for current user."""
        tasks, total = await service.list_tasks(
            user_id=current_user.id,
            status_filter=status_filter,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            size=size,
        )
        pages = (total + size - 1) // size
        return PaginatedTaskRead(
            items=[TaskRead.model_validate(task) for task in tasks],
            total=total,
            page=page,
            size=size,
            pages=pages,
        )

    @tasks_router.get("/tasks/{task_id}", response_model=TaskRead)
    async def get_task(
        task_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
        _: None = Depends(rate_limit_dependency),
    ) -> TaskRead:
        """Get specific task (must own it)."""
        task = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        )
        task_obj = task.scalar_one_or_none()
        if not task_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return TaskRead.model_validate(task_obj)

    @tasks_router.patch("/tasks/{task_id}/status", response_model=TaskRead)
    async def update_task_status(
        task_id: int,
        payload: TaskStatusUpdate,
        current_user: User = Depends(get_current_user),
        service: TaskService = Depends(provide_service),
        session: AsyncSession = Depends(get_session),
        _: None = Depends(rate_limit_dependency),
    ) -> TaskRead:
        """Update task status (must own it)."""
        task = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        )
        task_obj = task.scalar_one_or_none()
        if not task_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        updated = await service.update_task_status(task_id, payload.status)
        return TaskRead.model_validate(updated)

    @tasks_router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_task(
        task_id: int,
        current_user: User = Depends(get_current_user),
        service: TaskService = Depends(provide_service),
        session: AsyncSession = Depends(get_session),
        _: None = Depends(rate_limit_dependency),
    ) -> Response:
        """Delete task (must own it)."""
        task = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        )
        task_obj = task.scalar_one_or_none()
        if not task_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        await service.delete_task(task_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @tasks_router.post(
        "/tasks/{task_id}/process",
        response_model=dict,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def process_task_background(
        task_id: int,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_user),
        processor=Depends(provide_job_processor),
        session: AsyncSession = Depends(get_session),
        _: None = Depends(rate_limit_dependency),
    ) -> dict:
        """Process task in background (must own it)."""
        task = await session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        )
        task_obj = task.scalar_one_or_none()
        if not task_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        background_tasks.add_task(processor.process_task, task_id, session)
        return {"status": "processing", "task_id": task_id}

    return tasks_router
