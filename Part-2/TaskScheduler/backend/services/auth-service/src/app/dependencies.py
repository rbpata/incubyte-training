from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
import logging

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import TokenManager
from app.db.session import Database
from app.models.user import User, UserRole
from app.services.auth import AuthService

logger = logging.getLogger(__name__)

database_instance: Database | None = None
_user_request_log: dict[int, list[tuple[float, int]]] = {}


def initialize_database(database: Database) -> None:
    global database_instance
    database_instance = database


async def get_session() -> AsyncIterator[AsyncSession]:
    if database_instance is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    async for session in database_instance.get_session():
        yield session


async def provide_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(session)


async def get_current_user(
    authorization: str | None = Header(None),
    session: AsyncSession = Depends(get_session),
) -> User:
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
    except ValueError as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )

    try:
        result = await session.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        return current_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database lookup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to retrieve user",
        )


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
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
        (ts, cnt)
        for ts, cnt in _user_request_log[user_id]
        if ts > window_start
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
    current_user: User = Depends(get_current_user),
) -> None:
    _check_rate_limit(current_user.id)
