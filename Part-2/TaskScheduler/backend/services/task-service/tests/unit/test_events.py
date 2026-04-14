import asyncio

import pytest

from app.core.events import TaskEvent, TaskEventBus, TaskEventType


async def _make_bus_run_briefly(bus: TaskEventBus, timeout: float = 0.2) -> None:
    task = asyncio.create_task(bus.run())
    await asyncio.sleep(timeout)
    bus.stop()
    await task


@pytest.fixture
def bus():
    return TaskEventBus()


async def test_subscribe_and_publish_calls_handler(bus):
    received: list[TaskEvent] = []

    async def handler(event: TaskEvent) -> None:
        received.append(event)

    bus.subscribe(TaskEventType.CREATED, handler)
    event = TaskEvent(event_type=TaskEventType.CREATED, task_id=1, user_id=42)
    await bus.publish(event)
    await _make_bus_run_briefly(bus)

    assert len(received) == 1
    assert received[0].task_id == 1


async def test_publish_only_calls_matching_event_type_handler(bus):
    received: list[TaskEvent] = []

    async def handler(event: TaskEvent) -> None:
        received.append(event)

    bus.subscribe(TaskEventType.DELETED, handler)
    event = TaskEvent(event_type=TaskEventType.CREATED, task_id=2, user_id=1)
    await bus.publish(event)
    await _make_bus_run_briefly(bus)

    assert received == []


async def test_no_handlers_processes_event_without_error(bus):
    event = TaskEvent(event_type=TaskEventType.STATUS_CHANGED, task_id=3, user_id=1)
    await bus.publish(event)
    await _make_bus_run_briefly(bus)


async def test_handler_exception_does_not_stop_bus(bus):
    results: list[int] = []

    async def bad_handler(event: TaskEvent) -> None:
        raise RuntimeError("boom")

    async def good_handler(event: TaskEvent) -> None:
        results.append(event.task_id)

    bus.subscribe(TaskEventType.CREATED, bad_handler)
    bus.subscribe(TaskEventType.CREATED, good_handler)

    await bus.publish(TaskEvent(event_type=TaskEventType.CREATED, task_id=5, user_id=1))
    await _make_bus_run_briefly(bus)

    assert results == [5]


async def test_stop_ends_run_loop(bus):
    run_task = asyncio.create_task(bus.run())
    await asyncio.sleep(0.05)
    bus.stop()
    await asyncio.wait_for(run_task, timeout=2.0)


async def test_publish_puts_event_to_queue(bus):
    event = TaskEvent(event_type=TaskEventType.PROCESSING_STARTED, task_id=7, user_id=1)
    await bus.publish(event)
    assert bus._queue.qsize() == 1


async def test_multiple_subscribers_all_called(bus):
    calls: list[str] = []

    async def h1(event: TaskEvent) -> None:
        calls.append("h1")

    async def h2(event: TaskEvent) -> None:
        calls.append("h2")

    bus.subscribe(TaskEventType.CREATED, h1)
    bus.subscribe(TaskEventType.CREATED, h2)
    await bus.publish(TaskEvent(event_type=TaskEventType.CREATED, task_id=9, user_id=1))
    await _make_bus_run_briefly(bus)

    assert sorted(calls) == ["h1", "h2"]
