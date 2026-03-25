import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.repository import TaskRepository
from app.models.task import Task
from app.db.base import TaskStatus, TaskPriority
from app.schemas.task import TaskCreate


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def task_repository(mock_session: AsyncMock) -> TaskRepository:
    return TaskRepository(mock_session)


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


class TestTaskRepositoryCreate:
    async def test_create_task_inserts_and_returns_task(self, task_repository: TaskRepository, mock_session: AsyncMock, sample_task: Task) -> None:
        task_create = TaskCreate(
            title="Test task",
            description="Test description",
            run_at=datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc),
            priority=TaskPriority.MEDIUM,
            max_retries=3,
        )
        mock_session.refresh = AsyncMock()

        result = await task_repository.create(task_create)

        assert result.title == task_create.title
        assert result.status == TaskStatus.PENDING
        assert result.priority == TaskPriority.MEDIUM
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()


class TestTaskRepositoryGetById:
    async def test_get_by_id_returns_task_when_exists(self, task_repository: TaskRepository, mock_session: AsyncMock, sample_task: Task) -> None:
        mock_session.get.return_value = sample_task

        result = await task_repository.get_by_id(1)

        assert result.id == 1
        mock_session.get.assert_called_once_with(Task, 1)

    async def test_get_by_id_returns_none_when_missing(self, task_repository: TaskRepository, mock_session: AsyncMock) -> None:
        mock_session.get.return_value = None

        result = await task_repository.get_by_id(999)

        assert result is None


class TestTaskRepositoryUpdateStatus:
    async def test_update_status_modifies_and_returns_task(self, task_repository: TaskRepository, mock_session: AsyncMock, sample_task: Task) -> None:
        mock_session.refresh = AsyncMock()

        result = await task_repository.update_status(sample_task, TaskStatus.RUNNING)

        assert result.status == TaskStatus.RUNNING
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()


class TestTaskRepositoryDelete:
    async def test_delete_removes_task(self, task_repository: TaskRepository, mock_session: AsyncMock, sample_task: Task) -> None:
        await task_repository.delete(sample_task)

        mock_session.delete.assert_called_once_with(sample_task)
        mock_session.commit.assert_called_once()
