from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
import logging

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import Database
from app.services.repository import TaskRepository
from app.services.task import TaskService
from app.services.auth import AuthService
from app.background.jobs import TaskExecutor, RetryableTaskProcessor
from app.core.security import TokenManager
from app.models.user import User, UserRole
from app.core.config import settings


logger = logging.getLogger(__name__)

database_instance: Database | None = None

user_request_timestamps_and_counts: dict[int, list[tuple[float, int]]] = {}


def initialize_database(database: Database) -> None:
    global database_instance
    database_instance = database


async def get_session() -> AsyncIterator[AsyncSession]:
    if database_instance is None:
        raise RuntimeError(
            "Database not initialized. Call initialize_database() first."
        )
    async for session in database_instance.get_session():
        yield session


async def provide_repository(
    session: AsyncSession = Depends(get_session),
) -> TaskRepository:
    return TaskRepository(session)


async def provide_service(
    repository: TaskRepository = Depends(provide_repository),
) -> TaskService:
    return TaskService(repository)


async def provide_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(session)


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
    session: AsyncSession = Depends(get_session),
) -> User:
    """Extract and validate JWT token, return current user."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    authorization_scheme_and_token = authorization.split()

    if len(authorization_scheme_and_token) != 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
        )

    scheme, token = authorization_scheme_and_token

    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Use 'Bearer' scheme",
        )

    if not token or token.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is empty",
        )

    try:
        user_id = TokenManager.extract_user_id(token)
    except ValueError as e:
        logger.warning(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )

    try:
        user = await session.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        current_user = user.scalar_one_or_none()

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return current_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database lookup failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to retrieve user",
        )


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify current user is admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user


def check_rate_limit(user_id: int) -> None:
    """Check if user has exceeded rate limit.

    Raises HTTPException if rate limit exceeded.
    """
    current_time_seconds = datetime.now(timezone.utc).timestamp()
    rate_limit_window_start = current_time_seconds - settings.rate_limit_period

    if user_id not in user_request_timestamps_and_counts:
        user_request_timestamps_and_counts[user_id] = []

    requests_within_valid_time_window = [
        (timestamp, count)
        for timestamp, count in user_request_timestamps_and_counts[user_id]
        if timestamp > rate_limit_window_start
    ]
    user_request_timestamps_and_counts[user_id] = requests_within_valid_time_window

    total_request_count_in_window = sum(
        count for _, count in user_request_timestamps_and_counts[user_id]
    )

    if total_request_count_in_window >= settings.rate_limit_calls:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    last_request_entry = (
        user_request_timestamps_and_counts[user_id][-1]
        if user_request_timestamps_and_counts[user_id]
        else None
    )
    last_request_timestamp = last_request_entry[0] if last_request_entry else None

    if last_request_timestamp == current_time_seconds:
        timestamp, count = user_request_timestamps_and_counts[user_id][-1]
        user_request_timestamps_and_counts[user_id][-1] = (timestamp, count + 1)
    else:
        user_request_timestamps_and_counts[user_id].append((current_time_seconds, 1))


async def rate_limit_dependency(current_user: User = Depends(get_current_user)) -> None:
    """Dependency for rate limiting. Use in route decorators."""
    check_rate_limit(current_user.id)
