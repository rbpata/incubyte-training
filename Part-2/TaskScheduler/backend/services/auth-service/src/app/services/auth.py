import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import PasswordHasher, TokenManager
from app.models.api_key import ApiKey
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole
from app.schemas.auth import RefreshTokenRequest, TokenResponse, UserLogin, UserRegister


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_user(self, payload: UserRegister) -> User:
        existing = await self.session.execute(
            select(User).where(User.email == payload.email)
        )
        if existing.scalar_one_or_none():
            raise UserAlreadyExistsError(
                f"User with email {payload.email} already exists"
            )

        user = User(
            email=payload.email,
            password_hash=PasswordHasher.hash(payload.password),
            full_name=payload.full_name,
            role=UserRole.USER,
            is_active=True,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def login_user(self, payload: UserLogin) -> TokenResponse:
        result = await self.session.execute(
            select(User).where(User.email == payload.email)
        )
        user = result.scalar_one_or_none()

        if not user or not PasswordHasher.verify(payload.password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InvalidCredentialsError("User account is inactive")

        access_token = TokenManager.create_access_token(user.id, user.role)
        refresh_token = TokenManager.create_refresh_token(user.id)
        await self._store_refresh_token(user.id, refresh_token)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh_access_token(self, payload: RefreshTokenRequest) -> TokenResponse:
        try:
            user_id = TokenManager.extract_user_id(payload.refresh_token)
        except ValueError as e:
            raise InvalidRefreshTokenError(str(e))

        token_record = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token == payload.refresh_token,
                RefreshToken.user_id == user_id,
            )
        )
        if not token_record.scalar_one_or_none():
            raise InvalidRefreshTokenError("Refresh token not found or revoked")

        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise InvalidRefreshTokenError("User not found or inactive")

        access_token = TokenManager.create_access_token(user.id, user.role)
        return TokenResponse(
            access_token=access_token, refresh_token=payload.refresh_token
        )

    async def get_user_by_id(self, user_id: int) -> User:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    async def revoke_refresh_token(self, token: str) -> None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        token_obj = result.scalar_one_or_none()
        if token_obj:
            await self.session.delete(token_obj)
            await self.session.flush()

    async def create_api_key(self, user_id: int, name: str) -> tuple[str, ApiKey]:
        plaintext_key = f"sk_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(plaintext_key.encode()).hexdigest()

        api_key = ApiKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            is_active=True,
        )
        self.session.add(api_key)
        await self.session.flush()
        await self.session.refresh(api_key)
        return plaintext_key, api_key

    async def validate_api_key(self, key: str) -> int:
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        result = await self.session.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            raise ValueError("Invalid or inactive API key")

        api_key.last_used_at = datetime.now(timezone.utc)
        await self.session.flush()
        return api_key.user_id

    async def _store_refresh_token(self, user_id: int, token: str) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        self.session.add(
            RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        )
        await self.session.flush()
