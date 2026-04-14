import asyncio
import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)


class TaskEventType(StrEnum):
    CREATED = "task.created"
    STATUS_CHANGED = "task.status_changed"
    DELETED = "task.deleted"
    PROCESSING_STARTED = "task.processing_started"
    PROCESSING_COMPLETED = "task.processing_completed"
    PROCESSING_FAILED = "task.processing_failed"


@dataclass
class TaskEvent:
    event_type: TaskEventType
    task_id: int
    user_id: int
    metadata: dict = field(default_factory=dict)


EventHandler = Callable[[TaskEvent], Awaitable[None]]


class TaskEventBus:
    def __init__(self) -> None:
        self._handlers: dict[TaskEventType, list[EventHandler]] = {}
        self._queue: asyncio.Queue[TaskEvent] = asyncio.Queue()
        self._running = False

    def subscribe(self, event_type: TaskEventType, handler: EventHandler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, event: TaskEvent) -> None:
        await self._queue.put(event)

    async def run(self) -> None:
        self._running = True
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                for handler in self._handlers.get(event.event_type, []):
                    try:
                        await handler(event)
                    except Exception as exc:
                        logger.error(
                            "Event handler failed for %s: %s", event.event_type, exc
                        )
                self._queue.task_done()
            except asyncio.TimeoutError:
                continue

    def stop(self) -> None:
        self._running = False


task_event_bus = TaskEventBus()
