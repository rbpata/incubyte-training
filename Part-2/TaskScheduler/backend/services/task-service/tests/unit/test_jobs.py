import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.background.jobs import RetryableTaskProcessor, TaskExecutor
from app.db.base import Base, TaskPriority, TaskStatus
from app.models.task import Task
from app.services.repository import TaskRepository

TEST_DB_URL = "sqlite+aiosqlite:///"


@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def repo(db_session):
    return TaskRepository(db_session)


@pytest.fixture
def executor(repo):
    return TaskExecutor(repo)


@pytest.fixture
def retryable(executor):
    return RetryableTaskProcessor(executor)


async def _create_task(
    repo: TaskRepository,
    *,
    user_id: int = 1,
    run_at: datetime.datetime | None = None,
    max_retries: int = 3,
    retry_count: int = 0,
    status: TaskStatus = TaskStatus.PENDING,
) -> Task:
    from app.schemas.task import TaskCreate

    if run_at is None:
        run_at = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)

    task_data = TaskCreate(
        title="Test",
        description=None,
        run_at=run_at,
        priority=TaskPriority.MEDIUM,
        max_retries=max_retries,
    )
    task = await repo.create(task_data, user_id=user_id)
    if retry_count > 0 or status != TaskStatus.PENDING:
        task.retry_count = retry_count
        task.status = status
        await repo.session.commit()
        await repo.session.refresh(task)
    return task


async def test_process_task_returns_false_when_task_not_found(executor, db_session):
    result = await executor.process_task(99999, db_session)

    assert result is False


async def test_process_task_returns_false_for_non_pending_task(executor, repo, db_session):
    task = await _create_task(repo, status=TaskStatus.COMPLETED)

    result = await executor.process_task(task.id, db_session)

    assert result is False


async def test_process_task_increments_retry_count_for_future_task(executor, repo, db_session):
    future_run_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
    task = await _create_task(repo, run_at=future_run_at, max_retries=5)

    with patch("app.core.events.task_event_bus.publish", new_callable=AsyncMock):
        await executor.process_task(task.id, db_session)

    refreshed = await repo.get_by_id(task.id)
    assert refreshed is not None
    assert refreshed.retry_count == 1


async def test_process_task_marks_failed_when_retry_count_reaches_max_retries(
    executor, repo, db_session
):
    future_run_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
    task = await _create_task(repo, run_at=future_run_at, max_retries=1, retry_count=0)

    with patch("app.core.events.task_event_bus.publish", new_callable=AsyncMock):
        result = await executor.process_task(task.id, db_session)

    assert result is False
    refreshed = await repo.get_by_id(task.id)
    assert refreshed is not None
    assert refreshed.status == TaskStatus.FAILED


async def test_process_task_returns_true_for_past_task(executor, repo, db_session):
    past_run_at = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
    task = await _create_task(repo, run_at=past_run_at)

    with patch("app.core.events.task_event_bus.publish", new_callable=AsyncMock):
        result = await executor.process_task(task.id, db_session)

    assert result is True


async def test_process_task_marks_completed_for_past_task(executor, repo, db_session):
    past_run_at = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
    task = await _create_task(repo, run_at=past_run_at)

    with patch("app.core.events.task_event_bus.publish", new_callable=AsyncMock):
        await executor.process_task(task.id, db_session)

    refreshed = await repo.get_by_id(task.id)
    assert refreshed is not None
    assert refreshed.status == TaskStatus.COMPLETED


async def test_retryable_processor_returns_true_on_first_success(retryable, repo, db_session):
    past_run_at = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
    task = await _create_task(repo, run_at=past_run_at)

    with patch("app.core.events.task_event_bus.publish", new_callable=AsyncMock):
        result = await retryable.process_task(task.id, db_session)

    assert result is True


async def test_retryable_processor_returns_false_after_all_attempts_fail(db_session):
    mock_executor = MagicMock()
    mock_executor.process_task = AsyncMock(return_value=False)
    processor = RetryableTaskProcessor(mock_executor)

    result = await processor.process_task(1, db_session)

    assert result is False
    assert mock_executor.process_task.call_count == 3


async def test_retryable_processor_stops_retrying_after_first_success(db_session):
    mock_executor = MagicMock()
    mock_executor.process_task = AsyncMock(side_effect=[False, True, False])
    processor = RetryableTaskProcessor(mock_executor)

    result = await processor.process_task(1, db_session)

    assert result is True
    assert mock_executor.process_task.call_count == 2
