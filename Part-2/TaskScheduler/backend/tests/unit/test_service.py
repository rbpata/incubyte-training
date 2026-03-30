import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from fastapi import HTTPException

from app.services.task import TaskService
from app.services.repository import TaskRepository
from app.models.task import Task
from app.db.base import TaskStatus, TaskPriority
from app.schemas.task import TaskCreate


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=TaskRepository)


@pytest.fixture
def task_service(mock_repository: AsyncMock) -> TaskService:
    return TaskService(mock_repository)


@pytest.fixture
def sample_task() -> Task:
    task = Task()
    task.id = 1
    task.title = "Test task"
    task.description = "Test description"
    task.run_at = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc)
    task.status = TaskStatus.PENDING
    task.priority = TaskPriority.MEDIUM
    task.max_retries = 3
    task.retry_count = 0
    task.created_at = datetime.now(timezone.utc)
    task.updated_at = datetime.now(timezone.utc)
    return task


class TestTaskServiceCreate:
    async def test_create_task_returns_task(self, task_service: TaskService, mock_repository: AsyncMock, sample_task: Task) -> None:
        mock_repository.create.return_value = sample_task
        task_create = TaskCreate(
            title="Test task",
            description="Test description",
            run_at=datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc),
            priority=TaskPriority.MEDIUM,
            max_retries=3,
        )

        result = await task_service.create_task(task_create)

        assert result.id == 1
        assert result.title == "Test task"
        assert result.status == TaskStatus.PENDING
        mock_repository.create.assert_called_once_with(task_create)

    async def test_create_task_delegates_to_repository(self, task_service: TaskService, mock_repository: AsyncMock, sample_task: Task) -> None:
        mock_repository.create.return_value = sample_task
        task_create = TaskCreate(
            title="New task",
            description=None,
            run_at=datetime(2030, 6, 1, 10, 0, tzinfo=timezone.utc),
            max_retries=0,
        )

        await task_service.create_task(task_create)

        mock_repository.create.assert_called_once_with(task_create)


class TestTaskServiceGet:
    async def test_get_task_returns_task_when_exists(self, task_service: TaskService, mock_repository: AsyncMock, sample_task: Task) -> None:
        mock_repository.get_by_id.return_value = sample_task

        result = await task_service.get_task(1)

        assert result.id == 1
        assert result.title == "Test task"
        mock_repository.get_by_id.assert_called_once_with(1)

    async def test_get_task_raises_not_found_when_missing(self, task_service: TaskService, mock_repository: AsyncMock) -> None:
        mock_repository.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await task_service.get_task(999)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Task not found"


class TestTaskServiceList:
    async def test_list_tasks_returns_tasks_and_total(self, task_service: TaskService, mock_repository: AsyncMock, sample_task: Task) -> None:
        mock_repository.find_tasks.return_value = ([sample_task], 1)

        tasks, total = await task_service.list_tasks(page=1, size=10)

        assert len(tasks) == 1
        assert tasks[0].id == 1
        assert total == 1
        mock_repository.find_tasks.assert_called_once()

    async def test_list_tasks_forwards_filters(self, task_service: TaskService, mock_repository: AsyncMock, sample_task: Task) -> None:
        mock_repository.find_tasks.return_value = ([], 0)

        await task_service.list_tasks(
            status_filter=TaskStatus.COMPLETED,
            search="payment",
            sort_by="created_at",
            sort_order="desc",
            page=2,
            size=20,
        )

        mock_repository.find_tasks.assert_called_once_with(
            status=TaskStatus.COMPLETED,
            search="payment",
            sort_by="created_at",
            sort_order="desc",
            page=2,
            size=20,
        )


class TestTaskServiceUpdateStatus:
    async def test_update_task_status_updates_and_returns_task(self, task_service: TaskService, mock_repository: AsyncMock, sample_task: Task) -> None:
        updated_task = sample_task
        updated_task.status = TaskStatus.RUNNING
        mock_repository.get_by_id.return_value = sample_task
        mock_repository.update_status.return_value = updated_task

        result = await task_service.update_task_status(1, TaskStatus.RUNNING)

        assert result.status == TaskStatus.RUNNING
        mock_repository.update_status.assert_called_once()

    async def test_update_task_status_raises_not_found_when_missing(self, task_service: TaskService, mock_repository: AsyncMock) -> None:
        mock_repository.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await task_service.update_task_status(999, TaskStatus.RUNNING)

        assert exc_info.value.status_code == 404


class TestTaskServiceDelete:
    async def test_delete_task_calls_repository(self, task_service: TaskService, mock_repository: AsyncMock, sample_task: Task) -> None:
        mock_repository.get_by_id.return_value = sample_task

        await task_service.delete_task(1)

        mock_repository.delete.assert_called_once_with(sample_task)

    async def test_delete_task_raises_not_found_when_missing(self, task_service: TaskService, mock_repository: AsyncMock) -> None:
        mock_repository.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await task_service.delete_task(999)

        assert exc_info.value.status_code == 404
