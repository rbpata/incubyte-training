from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Database
from app.services.repository import TaskRepository
from app.services.task import TaskService
from app.background.jobs import TaskExecutor, RetryableTaskProcessor


database_instance: Database | None = None


def initialize_database(database: Database) -> None:
    global database_instance
    database_instance = database


async def get_session() -> AsyncIterator[AsyncSession]:
    if database_instance is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    async for session in database_instance.get_session():
        yield session


async def provide_repository(session: AsyncSession = Depends(get_session)) -> TaskRepository:
    return TaskRepository(session)


async def provide_service(
    repository: TaskRepository = Depends(provide_repository),
) -> TaskService:
    return TaskService(repository)


async def provide_task_executor(repository: TaskRepository = Depends(provide_repository)) -> TaskExecutor:
    return TaskExecutor(repository)


async def provide_job_processor(executor: TaskExecutor = Depends(provide_task_executor)) -> RetryableTaskProcessor:
    return RetryableTaskProcessor(executor)
