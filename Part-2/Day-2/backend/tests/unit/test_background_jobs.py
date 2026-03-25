import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.background.jobs import TaskExecutor, RetryableTaskProcessor
from app.models.task import Task
from app.db.base import TaskStatus, TaskPriority
from app.services.repository import TaskRepository


@pytest.fixture
def sample_pending_task() -> Task:
    task = Task()
    task.id = 1
    task.title = "Test task"
    task.description = "Test description"
    task.run_at = datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc)
    task.status = TaskStatus.PENDING
    task.priority = TaskPriority.MEDIUM
    task.max_retries = 3
    task.retry_count = 0
    task.created_at = datetime.now(timezone.utc)
    task.updated_at = datetime.now(timezone.utc)
    return task


class TestTaskExecutor:
    async def test_process_task_marks_as_completed_when_successful(self, sample_pending_task: Task) -> None:
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        mock_repository = AsyncMock(spec=TaskRepository)
        mock_repository.get_by_id.return_value = sample_pending_task
        mock_repository.update_status = AsyncMock(return_value=sample_pending_task)
        
        executor = TaskExecutor(mock_repository)
        result = await executor.process_task(1, mock_session)
        
        assert result is True
        mock_repository.get_by_id.assert_called_once()

    async def test_process_task_returns_false_when_task_not_found(self) -> None:
        mock_session = AsyncMock()
        mock_repository = AsyncMock(spec=TaskRepository)
        mock_repository.get_by_id.return_value = None
        
        executor = TaskExecutor(mock_repository)
        result = await executor.process_task(999, mock_session)
        
        assert result is False

    async def test_process_task_returns_false_for_non_pending_task(self, sample_pending_task: Task) -> None:
        sample_pending_task.status = TaskStatus.COMPLETED
        mock_session = AsyncMock()
        mock_repository = AsyncMock(spec=TaskRepository)
        mock_repository.get_by_id.return_value = sample_pending_task
        
        executor = TaskExecutor(mock_repository)
        result = await executor.process_task(1, mock_session)
        
        assert result is False


class TestRetryableTaskProcessor:
    async def test_process_task_succeeds_on_first_attempt(self, sample_pending_task: Task) -> None:
        executor = AsyncMock(spec=TaskExecutor)
        executor.process_task.return_value = True
        processor = RetryableTaskProcessor(executor)
        mock_session = AsyncMock()
        
        result = await processor.process_task(1, mock_session)
        
        assert result is True
        assert executor.process_task.call_count == 1

    async def test_process_task_retries_on_failure(self) -> None:
        executor = AsyncMock(spec=TaskExecutor)
        executor.process_task.return_value = False
        processor = RetryableTaskProcessor(executor)
        mock_session = AsyncMock()
        
        result = await processor.process_task(1, mock_session)
        
        assert result is False
        assert executor.process_task.call_count == 3
