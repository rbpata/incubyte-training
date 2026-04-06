from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.background.jobs import TaskExecutor
from app.db.base import TaskPriority, TaskStatus
from app.models.task import Task
from app.schemas.task import TaskCreate
from app.services.task import TaskService


class FakeRepository:
    def __init__(self) -> None:
        self.tasks: dict[int, Task] = {}
        self.deleted_ids: list[int] = []

    async def create(self, task_data: TaskCreate) -> Task:
        task = Task()
        task.id = len(self.tasks) + 1
        task.title = task_data.title
        task.description = task_data.description
        task.run_at = task_data.run_at
        task.status = TaskStatus.PENDING
        task.priority = task_data.priority
        task.max_retries = task_data.max_retries
        task.retry_count = 0
        task.created_at = datetime.now(timezone.utc)
        task.updated_at = datetime.now(timezone.utc)
        self.tasks[task.id] = task
        return task

    async def get_by_id(self, task_id: int) -> Task | None:
        return self.tasks.get(task_id)

    async def find_tasks(self, **_kwargs):
        all_tasks = list(self.tasks.values())
        return all_tasks, len(all_tasks)

    async def update_status(self, task: Task, status_value: TaskStatus) -> Task:
        task.status = status_value
        return task

    async def delete(self, task: Task) -> None:
        self.deleted_ids.append(task.id)


class TestWithTestDoubles:
    @pytest.mark.anyio
    async def test_fake_repository_can_drive_service_without_db(self) -> None:
        fake_repository = FakeRepository()
        service = TaskService(fake_repository)
        payload = TaskCreate(
            title="from fake",
            description="no db",
            run_at=datetime(2031, 1, 1, tzinfo=timezone.utc),
            priority=TaskPriority.MEDIUM,
            max_retries=1,
        )

        created = await service.create_task(payload)
        fetched = await service.get_task(created.id)

        assert fetched.id == created.id
        assert fetched.title == "from fake"

    @pytest.mark.anyio
    async def test_stubbed_execute_task_forces_retry_flow(self) -> None:
        task = Task()
        task.id = 1
        task.title = "future"
        task.description = None
        task.run_at = datetime(2031, 1, 1, tzinfo=timezone.utc)
        task.status = TaskStatus.PENDING
        task.priority = TaskPriority.MEDIUM
        task.max_retries = 3
        task.retry_count = 0

        repository = AsyncMock()
        repository.get_by_id.return_value = task

        executor = TaskExecutor(repository)
        executor._execute_task = AsyncMock(side_effect=RuntimeError("forced"))
        session = AsyncMock()

        result = await executor.process_task(task.id, session)

        assert result is False
        assert task.retry_count == 1
        session.commit.assert_called_once()

    @pytest.mark.anyio
    async def test_spy_like_assertion_on_update_status_calls(self) -> None:
        task = Task()
        task.id = 99
        task.title = "ready"
        task.description = None
        task.run_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
        task.status = TaskStatus.PENDING
        task.priority = TaskPriority.HIGH
        task.max_retries = 1
        task.retry_count = 0

        repository = AsyncMock()
        repository.get_by_id.return_value = task
        repository.update_status.return_value = task

        executor = TaskExecutor(repository)
        session = AsyncMock()

        result = await executor.process_task(task.id, session)

        assert result is True
        repository.update_status.assert_awaited_once_with(task, TaskStatus.COMPLETED)

    @pytest.mark.anyio
    async def test_mock_can_assert_not_found_error_path(self) -> None:
        repository = AsyncMock()
        repository.get_by_id.return_value = None
        service = TaskService(repository)

        with pytest.raises(HTTPException) as exc:
            await service.get_task(404)

        assert exc.value.status_code == 404
