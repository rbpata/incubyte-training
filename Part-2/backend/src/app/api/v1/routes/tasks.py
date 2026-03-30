from fastapi import APIRouter, Depends, Response, Query, status, BackgroundTasks
import logging

from app.db.base import TaskStatus
from app.schemas.task import TaskCreate, PaginatedTaskRead, TaskRead, TaskStatusUpdate
from app.services.task import TaskService
from app.dependencies import provide_service, provide_job_processor, get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def create_tasks_router() -> APIRouter:
    tasks_router = APIRouter()

    @tasks_router.post(
        "/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED
    )
    async def create_task(
        payload: TaskCreate,
        service: TaskService = Depends(provide_service),
    ) -> TaskRead:
        task = await service.create_task(payload)
        return TaskRead.model_validate(task)

    @tasks_router.get("/tasks", response_model=PaginatedTaskRead)
    async def list_tasks(
        status: TaskStatus | None = None,
        search: str | None = Query(None, min_length=1),
        sort_by: str = Query(
            "created_at", pattern="^(created_at|run_at|status|priority)$"
        ),
        sort_order: str = Query("desc", pattern="^(asc|desc)$"),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        service: TaskService = Depends(provide_service),
    ) -> PaginatedTaskRead:
        tasks, total = await service.list_tasks(
            status_filter=status,
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
        service: TaskService = Depends(provide_service),
    ) -> TaskRead:
        task = await service.get_task(task_id)
        return TaskRead.model_validate(task)

    @tasks_router.patch("/tasks/{task_id}/status", response_model=TaskRead)
    async def update_task_status(
        task_id: int,
        payload: TaskStatusUpdate,
        service: TaskService = Depends(provide_service),
    ) -> TaskRead:
        task = await service.update_task_status(task_id, payload.status)
        return TaskRead.model_validate(task)

    @tasks_router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_task(
        task_id: int,
        service: TaskService = Depends(provide_service),
    ) -> Response:
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
        processor=Depends(provide_job_processor),
        session=Depends(get_session),
    ) -> dict:
        background_tasks.add_task(processor.process_task, task_id, session)
        return {"status": "processing", "task_id": task_id}

    return tasks_router
