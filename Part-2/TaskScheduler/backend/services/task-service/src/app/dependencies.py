from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timezone
import logging

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.background.jobs import RetryableTaskProcessor, TaskExecutor
from app.core.config import settings
from app.core.events import task_event_bus
from app.core.security import TokenManager
from app.db.session import Database
from app.services.repository import TaskRepository
from app.services.task import TaskService

logger = logging.getLogger(__name__)

database_instance: Database | None = None
_user_request_log: dict[int, list[tuple[float, int]]] = {}


@dataclass
class CurrentUser:
    id: int
    role: str


def initialize_database(database: Database) -> None:
    global database_instance
    database_instance = database


async def get_session() -> AsyncIterator[AsyncSession]:
    if database_instance is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    async for session in database_instance.get_session():
        yield session


async def provide_repository(
    session: AsyncSession = Depends(get_session),
) -> TaskRepository:
    return TaskRepository(session)


async def provide_service(
    repository: TaskRepository = Depends(provide_repository),
) -> TaskService:
    return TaskService(repository, task_event_bus)


async def provide_task_executor(
    repository: TaskRepository = Depends(provide_repository),
) -> TaskExecutor:
    return TaskExecutor(repository)


async def provide_job_processor(
    executor: TaskExecutor = Depends(provide_task_executor),
) -> RetryableTaskProcessor:
    return RetryableTaskProcessor(executor)


async def get_current_user(
    authorization: str | None = Header(None),
) -> CurrentUser:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
        )

    token = parts[1]
    if not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is empty",
        )

    try:
        user_id = TokenManager.extract_user_id(token)
        role = TokenManager.extract_role(token)
    except ValueError as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )

    return CurrentUser(id=user_id, role=role)


async def get_current_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user


def _check_rate_limit(user_id: int) -> None:
    now = datetime.now(timezone.utc).timestamp()
    window_start = now - settings.rate_limit_period

    if user_id not in _user_request_log:
        _user_request_log[user_id] = []

    _user_request_log[user_id] = [
        (ts, cnt) for ts, cnt in _user_request_log[user_id] if ts > window_start
    ]

    total = sum(cnt for _, cnt in _user_request_log[user_id])
    if total >= settings.rate_limit_calls:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    last = _user_request_log[user_id][-1] if _user_request_log[user_id] else None
    if last and last[0] == now:
        ts, cnt = _user_request_log[user_id][-1]
        _user_request_log[user_id][-1] = (ts, cnt + 1)
    else:
        _user_request_log[user_id].append((now, 1))


async def rate_limit_dependency(
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    _check_rate_limit(current_user.id)
