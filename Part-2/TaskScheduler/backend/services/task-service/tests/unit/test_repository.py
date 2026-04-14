import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base, TaskPriority, TaskStatus
from app.models.task import Task
from app.schemas.task import TaskCreate
from app.services.repository import TaskRepository

TEST_DB_URL = "sqlite+aiosqlite:///"


@pytest.fixture
async def session():
    engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def repo(session):
    return TaskRepository(session)


def _future_run_at(hours: int = 1) -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)


def _past_run_at(hours: int = 1) -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)


def _task_create(**kwargs) -> TaskCreate:
    defaults = {
        "title": "Test Task",
        "description": "desc",
        "run_at": _future_run_at(),
        "priority": TaskPriority.MEDIUM,
        "max_retries": 3,
    }
    defaults.update(kwargs)
    return TaskCreate(**defaults)


async def test_create_returns_task_with_pending_status(repo):
    task = await repo.create(_task_create(), user_id=1)

    assert task.id is not None
    assert task.status == TaskStatus.PENDING


async def test_create_stores_correct_user_id(repo):
    task = await repo.create(_task_create(), user_id=99)

    assert task.user_id == 99


async def test_get_by_id_returns_existing_task(repo):
    created = await repo.create(_task_create(), user_id=1)
    fetched = await repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id


async def test_get_by_id_returns_none_for_nonexistent_id(repo):
    result = await repo.get_by_id(99999)

    assert result is None


async def test_get_by_id_returns_none_for_soft_deleted_task(repo):
    task = await repo.create(_task_create(), user_id=1)
    await repo.delete(task)
    result = await repo.get_by_id(task.id)

    assert result is None


async def test_find_tasks_returns_only_requesting_users_tasks(repo):
    await repo.create(_task_create(title="User 1 Task"), user_id=1)
    await repo.create(_task_create(title="User 2 Task"), user_id=2)

    tasks, total = await repo.find_tasks(user_id=1)

    assert total == 1
    assert tasks[0].title == "User 1 Task"


async def test_find_tasks_filters_by_status(repo):
    task = await repo.create(_task_create(), user_id=1)
    await repo.update_status(task, TaskStatus.COMPLETED)
    await repo.create(_task_create(title="Pending Task"), user_id=1)

    tasks, total = await repo.find_tasks(user_id=1, status=TaskStatus.COMPLETED)

    assert total == 1
    assert tasks[0].status == TaskStatus.COMPLETED


async def test_find_tasks_searches_by_title(repo):
    await repo.create(_task_create(title="Alpha Task"), user_id=1)
    await repo.create(_task_create(title="Beta Task"), user_id=1)

    tasks, total = await repo.find_tasks(user_id=1, search="Alpha")

    assert total == 1
    assert tasks[0].title == "Alpha Task"


async def test_find_tasks_searches_by_description(repo):
    await repo.create(_task_create(title="T1", description="match me"), user_id=1)
    await repo.create(_task_create(title="T2", description="no match"), user_id=1)

    tasks, total = await repo.find_tasks(user_id=1, search="match me")

    assert total == 1
    assert tasks[0].description == "match me"


async def test_find_tasks_pagination_returns_correct_page(repo):
    for i in range(5):
        await repo.create(_task_create(title=f"Task {i}"), user_id=1)

    tasks, total = await repo.find_tasks(user_id=1, page=1, size=2)

    assert total == 5
    assert len(tasks) == 2


async def test_find_tasks_sort_order_asc_returns_oldest_first(repo):
    for i in range(3):
        await repo.create(_task_create(title=f"Task {i}"), user_id=1)

    tasks, _ = await repo.find_tasks(user_id=1, sort_by="created_at", sort_order="asc")

    assert tasks[0].title == "Task 0"


async def test_find_tasks_sort_order_desc_returns_newest_first(repo):
    for i in range(3):
        await repo.create(_task_create(title=f"Task {i}"), user_id=1)

    tasks, _ = await repo.find_tasks(user_id=1, sort_by="created_at", sort_order="desc")

    assert tasks[0].title == "Task 2"


async def test_update_status_changes_task_status(repo):
    task = await repo.create(_task_create(), user_id=1)
    updated = await repo.update_status(task, TaskStatus.RUNNING)

    assert updated.status == TaskStatus.RUNNING


async def test_delete_sets_deleted_at(repo):
    task = await repo.create(_task_create(), user_id=1)
    await repo.delete(task)

    assert task.deleted_at is not None
