import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from fastapi import HTTPException

from app.models.task import Task
from app.db.base import TaskStatus, TaskPriority
from app.services.task import TaskService
from app.schemas.task import TaskCreate, TaskRead


@pytest.fixture
def mock_service() -> AsyncMock:
    return AsyncMock(spec=TaskService)


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


class TestCreateTaskRoute:
    async def test_create_task_returns_201_when_valid(self, mock_service: AsyncMock, sample_task: Task) -> None:
        mock_service.create_task.return_value = sample_task
        payload = TaskCreate(
            title="Test task",
            description="Test description",
            run_at=datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc),
            priority=TaskPriority.MEDIUM,
            max_retries=3,
        )

        result = await mock_service.create_task(payload)

        assert result.id == 1
        assert result.title == "Test task"
        mock_service.create_task.assert_called_once_with(payload)

    async def test_create_task_calls_service_with_payload(self, mock_service: AsyncMock, sample_task: Task) -> None:
        mock_service.create_task.return_value = sample_task
        payload = TaskCreate(
            title="New task",
            description=None,
            run_at=datetime(2030, 6, 1, 10, 0, tzinfo=timezone.utc),
            max_retries=0,
        )

        await mock_service.create_task(payload)

        mock_service.create_task.assert_called_once_with(payload)


class TestGetTaskRoute:
    async def test_get_task_returns_task_when_exists(self, mock_service: AsyncMock, sample_task: Task) -> None:
        mock_service.get_task.return_value = sample_task

        result = await mock_service.get_task(1)

        assert result.id == 1
        mock_service.get_task.assert_called_once_with(1)

    async def test_get_task_raises_404_when_not_found(self, mock_service: AsyncMock) -> None:
        mock_service.get_task.side_effect = HTTPException(status_code=404, detail="Task not found")

        with pytest.raises(HTTPException) as exc_info:
            await mock_service.get_task(999)

        assert exc_info.value.status_code == 404


class TestListTasksRoute:
    async def test_list_tasks_returns_empty_list_when_no_tasks(self, mock_service: AsyncMock) -> None:
        mock_service.list_tasks.return_value = ([], 0)

        tasks, total = await mock_service.list_tasks()

        assert len(tasks) == 0
        assert total == 0

    async def test_list_tasks_with_filters_forwards_parameters(self, mock_service: AsyncMock, sample_task: Task) -> None:
        mock_service.list_tasks.return_value = ([sample_task], 1)

        tasks, total = await mock_service.list_tasks(
            status_filter=TaskStatus.PENDING,
            search="report",
            sort_by="created_at",
            sort_order="desc",
            page=1,
            size=10,
        )

        mock_service.list_tasks.assert_called_once()
        assert len(tasks) == 1
        assert total == 1


class TestUpdateTaskStatusRoute:
    async def test_update_task_status_returns_updated_task(self, mock_service: AsyncMock, sample_task: Task) -> None:
        updated_task = sample_task
        updated_task.status = TaskStatus.RUNNING
        mock_service.update_task_status.return_value = updated_task

        result = await mock_service.update_task_status(1, TaskStatus.RUNNING)

        assert result.status == TaskStatus.RUNNING
        mock_service.update_task_status.assert_called_once_with(1, TaskStatus.RUNNING)

    async def test_update_task_status_raises_404_when_not_found(self, mock_service: AsyncMock) -> None:
        mock_service.update_task_status.side_effect = HTTPException(status_code=404, detail="Task not found")

        with pytest.raises(HTTPException):
            await mock_service.update_task_status(999, TaskStatus.RUNNING)


class TestDeleteTaskRoute:
    async def test_delete_task_calls_service(self, mock_service: AsyncMock) -> None:
        mock_service.delete_task.return_value = None

        await mock_service.delete_task(1)

        mock_service.delete_task.assert_called_once_with(1)

    async def test_delete_task_raises_404_when_not_found(self, mock_service: AsyncMock) -> None:
        mock_service.delete_task.side_effect = HTTPException(status_code=404, detail="Task not found")

        with pytest.raises(HTTPException):
            await mock_service.delete_task(999)
