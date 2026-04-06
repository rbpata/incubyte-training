import asyncio
import time
import pytest
import pytest_asyncio
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock, call


# =============================================================================
# Domain — async service layer with external dependencies
# =============================================================================


@dataclass
class Task:
    title: str
    priority: str = "medium"
    is_completed: bool = False
    id: UUID = field(default_factory=uuid4)
    created_at: float = field(default_factory=time.time)


class TaskNotFoundError(Exception):
    pass


class ExternalAPIError(Exception):
    pass


# --- Interfaces (what the service depends on) --------------------------------


class TaskRepository:
    """Abstract: persist and retrieve tasks."""

    async def save(self, task: Task) -> Task: ...
    async def get(self, task_id: UUID) -> Optional[Task]: ...
    async def list_all(self) -> list[Task]: ...
    async def delete(self, task_id: UUID) -> bool: ...


class NotificationService:
    """Abstract: send notifications when tasks change."""

    async def notify_created(self, task: Task) -> None: ...
    async def notify_completed(self, task: Task) -> None: ...


class AnalyticsService:
    """Abstract: track events for analytics."""

    async def track(self, event: str, data: dict) -> None: ...


# --- Service under test ------------------------------------------------------


class TaskService:
    def __init__(
        self,
        repo: TaskRepository,
        notifications: NotificationService,
        analytics: AnalyticsService,
    ):
        self._repo = repo
        self._notifications = notifications
        self._analytics = analytics

    async def create(self, title: str, priority: str = "medium") -> Task:
        task = Task(title=title, priority=priority)
        saved = await self._repo.save(task)
        await self._notifications.notify_created(saved)
        await self._analytics.track(
            "task.created",
            {
                "task_id": str(saved.id),
                "priority": saved.priority,
            },
        )
        return saved

    async def get(self, task_id: UUID) -> Task:
        task = await self._repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task

    async def complete(self, task_id: UUID) -> Task:
        task = await self.get(task_id)
        task.is_completed = True
        saved = await self._repo.save(task)
        await self._notifications.notify_completed(saved)
        await self._analytics.track(
            "task.completed",
            {
                "task_id": str(saved.id),
            },
        )
        return saved

    async def list_all(self) -> list[Task]:
        return await self._repo.list_all()

    async def delete(self, task_id: UUID) -> None:
        task = await self.get(task_id)
        deleted = await self._repo.delete(task.id)
        if not deleted:
            raise TaskNotFoundError(f"Task {task_id} could not be deleted")


# =============================================================================
# TEST DOUBLE 1 — STUB
# Returns hardcoded values. No logic, no verification.
# Use when: the dependency must return something but behaviour doesn't matter.
# =============================================================================


class StubNotificationService:
    """Always succeeds. We don't care about notifications in these tests."""

    async def notify_created(self, task: Task) -> None:
        pass  # do nothing

    async def notify_completed(self, task: Task) -> None:
        pass


class StubAnalyticsService:
    """Silently discards all events."""

    async def track(self, event: str, data: dict) -> None:
        pass


# =============================================================================
# TEST DOUBLE 2 — FAKE
# Real implementation with fake infrastructure (dict instead of DB).
# Use when: you need real CRUD behaviour without a real database.
# =============================================================================


class FakeTaskRepository:
    """
    Fully functional in-memory repository.
    Behaves exactly like a real one — just stores in a dict.
    """

    def __init__(self):
        self._store: dict[UUID, Task] = {}

    async def save(self, task: Task) -> Task:
        self._store[task.id] = task
        return task

    async def get(self, task_id: UUID) -> Optional[Task]:
        return self._store.get(task_id)

    async def list_all(self) -> list[Task]:
        return list(self._store.values())

    async def delete(self, task_id: UUID) -> bool:
        if task_id in self._store:
            del self._store[task_id]
            return True
        return False

    @property
    def count(self) -> int:
        return len(self._store)


# =============================================================================
# TEST DOUBLE 3 — SPY
# Real behaviour + records every call that was made.
# Use when: you need real behaviour AND want to verify interactions.
# =============================================================================


class SpyNotificationService:
    """
    Records every notification sent.
    Can optionally delegate to a real service.
    """

    def __init__(self):
        self.created_notifications: list[Task] = []
        self.completed_notifications: list[Task] = []

    async def notify_created(self, task: Task) -> None:
        self.created_notifications.append(task)

    async def notify_completed(self, task: Task) -> None:
        self.completed_notifications.append(task)

    @property
    def total_notifications(self) -> int:
        return len(self.created_notifications) + len(self.completed_notifications)


class SpyAnalyticsService:
    """Records all tracked events."""

    def __init__(self):
        self.events: list[dict] = []

    async def track(self, event: str, data: dict) -> None:
        self.events.append({"event": event, "data": data})

    def events_of_type(self, event_type: str) -> list[dict]:
        return [e for e in self.events if e["event"] == event_type]


# =============================================================================
# FIXTURES — compose doubles into complete service instances
# =============================================================================


@pytest.fixture
def fake_repo():
    return FakeTaskRepository()


@pytest.fixture
def stub_notifications():
    return StubNotificationService()


@pytest.fixture
def stub_analytics():
    return StubAnalyticsService()


@pytest.fixture
def spy_notifications():
    return SpyNotificationService()


@pytest.fixture
def spy_analytics():
    return SpyAnalyticsService()


@pytest.fixture
def service(fake_repo, stub_notifications, stub_analytics):
    """Service with fake repo + stubs — use for CRUD behaviour tests."""
    return TaskService(
        repo=fake_repo,
        notifications=stub_notifications,
        analytics=stub_analytics,
    )


@pytest.fixture
def service_with_spies(fake_repo, spy_notifications, spy_analytics):
    """Service with fake repo + spies — use for interaction tests."""
    return TaskService(
        repo=fake_repo,
        notifications=spy_notifications,
        analytics=spy_analytics,
    )


# =============================================================================
# TESTS — using stubs and fakes (behaviour tests)
# =============================================================================


class TestTaskCreation:

    async def test_create_returns_task(self, service):
        task = await service.create("Buy groceries")
        assert task.title == "Buy groceries"
        assert task.id is not None
        assert task.is_completed is False

    async def test_create_with_priority(self, service):
        task = await service.create("Deploy", priority="high")
        assert task.priority == "high"

    async def test_created_task_is_persisted(self, service, fake_repo):
        task = await service.create("Persisted task")
        fetched = await fake_repo.get(task.id)
        assert fetched is not None
        assert fetched.title == "Persisted task"

    async def test_multiple_creates_are_independent(self, service):
        t1 = await service.create("Task one")
        t2 = await service.create("Task two")
        assert t1.id != t2.id

    async def test_list_returns_all_created(self, service):
        await service.create("A")
        await service.create("B")
        await service.create("C")
        tasks = await service.list_all()
        assert len(tasks) == 3


class TestTaskCompletion:

    async def test_complete_marks_done(self, service):
        task = await service.create("Finish me")
        completed = await service.complete(task.id)
        assert completed.is_completed is True

    async def test_complete_persists_change(self, service, fake_repo):
        task = await service.create("Finish me")
        await service.complete(task.id)
        stored = await fake_repo.get(task.id)
        assert stored.is_completed is True

    async def test_complete_nonexistent_raises(self, service):
        with pytest.raises(TaskNotFoundError):
            await service.complete(uuid4())


class TestTaskDeletion:

    async def test_delete_removes_from_store(self, service, fake_repo):
        task = await service.create("Delete me")
        await service.delete(task.id)
        assert await fake_repo.get(task.id) is None

    async def test_delete_nonexistent_raises(self, service):
        with pytest.raises(TaskNotFoundError):
            await service.delete(uuid4())


# =============================================================================
# TESTS — using spies (interaction / side-effect tests)
# =============================================================================


class TestNotificationsViaSpy:

    async def test_create_sends_notification(
        self, service_with_spies, spy_notifications
    ):
        task = await service_with_spies.create("Notify me")
        assert len(spy_notifications.created_notifications) == 1
        assert spy_notifications.created_notifications[0].id == task.id

    async def test_complete_sends_notification(
        self, service_with_spies, spy_notifications
    ):
        task = await service_with_spies.create("Complete me")
        await service_with_spies.complete(task.id)
        assert len(spy_notifications.completed_notifications) == 1
        notified_task = spy_notifications.completed_notifications[0]
        assert notified_task.is_completed is True

    async def test_no_notification_on_list(self, service_with_spies, spy_notifications):
        await service_with_spies.create("Task")
        spy_notifications.created_notifications.clear()  # reset
        await service_with_spies.list_all()
        assert spy_notifications.total_notifications == 0


class TestAnalyticsViaSpy:

    async def test_create_tracks_event(self, service_with_spies, spy_analytics):
        task = await service_with_spies.create("Track me", priority="high")
        events = spy_analytics.events_of_type("task.created")
        assert len(events) == 1
        assert events[0]["data"]["priority"] == "high"
        assert events[0]["data"]["task_id"] == str(task.id)

    async def test_complete_tracks_event(self, service_with_spies, spy_analytics):
        task = await service_with_spies.create("Complete me")
        await service_with_spies.complete(task.id)
        events = spy_analytics.events_of_type("task.completed")
        assert len(events) == 1
        assert events[0]["data"]["task_id"] == str(task.id)

    async def test_create_and_complete_track_separately(
        self, service_with_spies, spy_analytics
    ):
        task = await service_with_spies.create("Full lifecycle")
        await service_with_spies.complete(task.id)
        assert len(spy_analytics.events_of_type("task.created")) == 1
        assert len(spy_analytics.events_of_type("task.completed")) == 1
        assert len(spy_analytics.events) == 2


# =============================================================================
# TESTS — using AsyncMock (mock / verify exact calls)
# =============================================================================


class TestWithAsyncMock:

    async def test_repo_called_correctly_on_create(self):
        """AsyncMock verifies exact arguments passed to the repository."""
        mock_repo = AsyncMock()
        mock_repo.save.return_value = Task(title="Mocked")

        service = TaskService(
            repo=mock_repo,
            notifications=StubNotificationService(),
            analytics=StubAnalyticsService(),
        )

        await service.create("Mocked")

        # Verify save was called exactly once with a Task
        mock_repo.save.assert_called_once()
        saved_arg = mock_repo.save.call_args[0][0]
        assert isinstance(saved_arg, Task)
        assert saved_arg.title == "Mocked"

    async def test_notification_called_with_correct_task(self):
        """Verify the notification received the exact task that was saved."""
        task = Task(title="Test", id=uuid4())

        mock_repo = AsyncMock()
        mock_repo.save.return_value = task

        mock_notifications = AsyncMock(spec=NotificationService)
        mock_analytics = AsyncMock(spec=AnalyticsService)

        service = TaskService(
            repo=mock_repo,
            notifications=mock_notifications,
            analytics=mock_analytics,
        )

        await service.create("Test")

        mock_notifications.notify_created.assert_called_once_with(task)

    async def test_analytics_not_called_when_repo_fails(self):
        """If saving fails, analytics should never receive the event."""
        mock_repo = AsyncMock()
        mock_repo.save.side_effect = RuntimeError("DB connection lost")
        mock_analytics = AsyncMock(spec=AnalyticsService)

        service = TaskService(
            repo=mock_repo,
            notifications=StubNotificationService(),
            analytics=mock_analytics,
        )

        with pytest.raises(RuntimeError):
            await service.create("Will fail")

        mock_analytics.track.assert_not_called()

    async def test_complete_calls_operations_in_order(self):
        """Verify the sequence: get → save → notify → track."""
        task = Task(title="Order test")
        call_order = []

        mock_repo = AsyncMock()
        mock_repo.get.return_value = task
        mock_repo.save.side_effect = lambda t: (call_order.append("save"), t)[1]

        mock_notifications = AsyncMock()
        mock_notifications.notify_completed.side_effect = lambda t: call_order.append(
            "notify"
        )

        mock_analytics = AsyncMock()
        mock_analytics.track.side_effect = lambda e, d: call_order.append("track")

        service = TaskService(
            repo=mock_repo,
            notifications=mock_notifications,
            analytics=mock_analytics,
        )

        await service.complete(task.id)

        assert call_order == ["save", "notify", "track"]


# =============================================================================
# ASYNC BEHAVIOUR — concurrency and timing tests
# =============================================================================


class TestAsyncBehaviour:

    async def test_multiple_creates_run_concurrently(self, fake_repo):
        """Concurrent creates should all persist independently."""
        stub_n = StubNotificationService()
        stub_a = StubAnalyticsService()
        service = TaskService(repo=fake_repo, notifications=stub_n, analytics=stub_a)

        tasks = await asyncio.gather(
            service.create("Task A"),
            service.create("Task B"),
            service.create("Task C"),
        )

        assert len(tasks) == 3
        assert len(await fake_repo.list_all()) == 3
        # All IDs are unique
        assert len({t.id for t in tasks}) == 3

    async def test_service_handles_notification_failure_gracefully(self, fake_repo):
        """If notifications fail, the task is still created."""
        failing_notifications = AsyncMock(spec=NotificationService)
        failing_notifications.notify_created.side_effect = ExternalAPIError(
            "Push service down"
        )

        service = TaskService(
            repo=fake_repo,
            notifications=failing_notifications,
            analytics=StubAnalyticsService(),
        )

        with pytest.raises(ExternalAPIError):
            await service.create("Task")

        # Task WAS saved before notification failed
        all_tasks = await fake_repo.list_all()
        assert len(all_tasks) == 1