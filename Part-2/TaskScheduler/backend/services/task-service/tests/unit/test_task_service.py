import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.core.events import TaskEvent, TaskEventType
from app.db.base import TaskPriority, TaskStatus
from app.models.task import Task
from app.schemas.task import TaskCreate
from app.services.task import TaskService


def _make_task(task_id: int = 1, user_id: int = 1, status: TaskStatus = TaskStatus.PENDING) -> Task:
    task = Task()
    task.id = task_id
    task.user_id = user_id
    task.title = "Task"
    task.description = "desc"
    task.run_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    task.status = status
    task.priority = TaskPriority.MEDIUM
    task.max_retries = 3
    task.retry_count = 0
    task.created_at = datetime.datetime.now(datetime.timezone.utc)
    task.updated_at = datetime.datetime.now(datetime.timezone.utc)
    task.deleted_at = None
    return task


def _task_create() -> TaskCreate:
    return TaskCreate(
        title="Task",
        description="desc",
        run_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
        priority=TaskPriority.MEDIUM,
        max_retries=3,
    )


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.find_tasks = AsyncMock()
    repo.update_status = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_bus():
    bus = MagicMock()
    bus.publish = AsyncMock()
    return bus


@pytest.fixture
def service(mock_repo, mock_bus):
    return TaskService(repository=mock_repo, event_bus=mock_bus)


async def test_create_task_calls_repository_create(service, mock_repo, mock_bus):
    task = _make_task()
    mock_repo.create.return_value = task

    result = await service.create_task(_task_create(), user_id=1)

    mock_repo.create.assert_called_once()
    assert result is task


async def test_create_task_publishes_created_event(service, mock_repo, mock_bus):
    task = _make_task(task_id=5, user_id=1)
    mock_repo.create.return_value = task

    await service.create_task(_task_create(), user_id=1)

    mock_bus.publish.assert_called_once()
    event: TaskEvent = mock_bus.publish.call_args[0][0]
    assert event.event_type == TaskEventType.CREATED
    assert event.task_id == 5


async def test_get_task_returns_task_when_found(service, mock_repo):
    task = _make_task()
    mock_repo.get_by_id.return_value = task

    result = await service.get_task(1)

    assert result is task


async def test_get_task_raises_404_when_not_found(service, mock_repo):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_task(999)

    assert exc_info.value.status_code == 404


async def test_list_tasks_delegates_to_repository(service, mock_repo):
    mock_repo.find_tasks.return_value = ([], 0)

    tasks, total = await service.list_tasks(user_id=1)

    mock_repo.find_tasks.assert_called_once()
    assert total == 0


async def test_update_task_status_calls_update_status_on_repo(service, mock_repo, mock_bus):
    task = _make_task()
    updated = _make_task(status=TaskStatus.COMPLETED)
    mock_repo.get_by_id.return_value = task
    mock_repo.update_status.return_value = updated

    result = await service.update_task_status(1, TaskStatus.COMPLETED)

    mock_repo.update_status.assert_called_once_with(task, TaskStatus.COMPLETED)
    assert result.status == TaskStatus.COMPLETED


async def test_update_task_status_publishes_status_changed_event(service, mock_repo, mock_bus):
    task = _make_task(task_id=3, user_id=7)
    mock_repo.get_by_id.return_value = task
    mock_repo.update_status.return_value = task

    await service.update_task_status(3, TaskStatus.RUNNING)

    event: TaskEvent = mock_bus.publish.call_args[0][0]
    assert event.event_type == TaskEventType.STATUS_CHANGED
    assert event.task_id == 3
    assert event.metadata["new_status"] == TaskStatus.RUNNING


async def test_delete_task_publishes_deleted_event(service, mock_repo, mock_bus):
    task = _make_task(task_id=10, user_id=2)
    mock_repo.get_by_id.return_value = task

    await service.delete_task(10)

    event: TaskEvent = mock_bus.publish.call_args[0][0]
    assert event.event_type == TaskEventType.DELETED
    assert event.task_id == 10


async def test_delete_task_calls_repository_delete(service, mock_repo, mock_bus):
    task = _make_task()
    mock_repo.get_by_id.return_value = task

    await service.delete_task(1)

    mock_repo.delete.assert_called_once_with(task)
