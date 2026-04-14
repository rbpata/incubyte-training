from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import TaskEvent, TaskEventType, task_event_bus
from app.db.base import TaskStatus
from app.services.repository import TaskRepository


class TaskExecutor:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    async def process_task(self, task_id: int, session: AsyncSession) -> bool:
        task = await self.repository.get_by_id(task_id)

        if task is None:
            return False

        if task.status != TaskStatus.PENDING:
            return False

        await task_event_bus.publish(
            TaskEvent(
                event_type=TaskEventType.PROCESSING_STARTED,
                task_id=task_id,
                user_id=task.user_id,
            )
        )

        try:
            await self._execute_task_work(task)
            await self.repository.update_status(task, TaskStatus.COMPLETED)
            await task_event_bus.publish(
                TaskEvent(
                    event_type=TaskEventType.PROCESSING_COMPLETED,
                    task_id=task_id,
                    user_id=task.user_id,
                )
            )
            return True
        except Exception:
            task.retry_count += 1
            if task.retry_count >= task.max_retries:
                await self.repository.update_status(task, TaskStatus.FAILED)
                await task_event_bus.publish(
                    TaskEvent(
                        event_type=TaskEventType.PROCESSING_FAILED,
                        task_id=task_id,
                        user_id=task.user_id,
                    )
                )
                return False
            await session.commit()
            return False

    async def _execute_task_work(self, task) -> None:
        if task.run_at > datetime.now(timezone.utc):
            raise RuntimeError(f"Task {task.id} scheduled for future execution")


class RetryableTaskProcessor:
    def __init__(self, executor: TaskExecutor) -> None:
        self.executor = executor
        self.max_attempts = 3

    async def process_task(self, task_id: int, session: AsyncSession) -> bool:
        for attempt in range(self.max_attempts):
            try:
                success = await self.executor.process_task(task_id, session)
                if success:
                    return True
            except Exception:
                if attempt == self.max_attempts - 1:
                    raise
        return False
