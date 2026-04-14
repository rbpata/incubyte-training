import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import TokenManager
from app.db.base import Base
from app.schemas.auth import RefreshTokenRequest, UserLogin, UserRegister
from app.services.auth import (
    AuthService,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

REGISTER_PAYLOAD = UserRegister(
    email="user@example.com",
    password="securepassword123",
    full_name="Test User",
)


@pytest.fixture
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest.fixture
async def auth_service(db_session):
    return AuthService(db_session)


@pytest.fixture
async def registered_user(auth_service, db_session):
    user = await auth_service.register_user(REGISTER_PAYLOAD)
    await db_session.commit()
    return user


class TestRegisterUser:
    async def test_creates_user_with_correct_email(self, auth_service, db_session):
        user = await auth_service.register_user(REGISTER_PAYLOAD)
        await db_session.commit()
        assert user.email == REGISTER_PAYLOAD.email

    async def test_creates_user_with_correct_full_name(self, auth_service, db_session):
        user = await auth_service.register_user(REGISTER_PAYLOAD)
        await db_session.commit()
        assert user.full_name == REGISTER_PAYLOAD.full_name

    async def test_creates_user_with_hashed_password(self, auth_service, db_session):
        user = await auth_service.register_user(REGISTER_PAYLOAD)
        await db_session.commit()
        assert user.password_hash != REGISTER_PAYLOAD.password

    async def test_raises_on_duplicate_email(self, auth_service, db_session):
        await auth_service.register_user(REGISTER_PAYLOAD)
        await db_session.commit()
        with pytest.raises(UserAlreadyExistsError):
            await auth_service.register_user(REGISTER_PAYLOAD)


class TestLoginUser:
    async def test_returns_token_response_with_tokens(
        self, auth_service, db_session, registered_user
    ):
        payload = UserLogin(
            email=REGISTER_PAYLOAD.email, password=REGISTER_PAYLOAD.password
        )
        result = await auth_service.login_user(payload)
        await db_session.commit()
        assert result.access_token
        assert result.refresh_token

    async def test_raises_for_wrong_password(self, auth_service, registered_user):
        payload = UserLogin(email=REGISTER_PAYLOAD.email, password="wrongpassword")
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login_user(payload)

    async def test_raises_for_unknown_email(self, auth_service):
        payload = UserLogin(email="unknown@example.com", password="password123")
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login_user(payload)

    async def test_raises_for_inactive_user(
        self, auth_service, db_session, registered_user
    ):
        registered_user.is_active = False
        await db_session.flush()
        payload = UserLogin(
            email=REGISTER_PAYLOAD.email, password=REGISTER_PAYLOAD.password
        )
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login_user(payload)


class TestRefreshAccessToken:
    async def test_returns_new_access_token(
        self, auth_service, db_session, registered_user
    ):
        login_payload = UserLogin(
            email=REGISTER_PAYLOAD.email, password=REGISTER_PAYLOAD.password
        )
        token_response = await auth_service.login_user(login_payload)
        await db_session.commit()

        refresh_payload = RefreshTokenRequest(
            refresh_token=token_response.refresh_token
        )
        result = await auth_service.refresh_access_token(refresh_payload)
        assert result.access_token

    async def test_raises_for_malformed_token(self, auth_service):
        payload = RefreshTokenRequest(refresh_token="invalid_token")
        with pytest.raises(InvalidRefreshTokenError):
            await auth_service.refresh_access_token(payload)

    async def test_raises_for_valid_token_not_stored_in_db(self, auth_service):
        valid_token = TokenManager.create_refresh_token(999)
        payload = RefreshTokenRequest(refresh_token=valid_token)
        with pytest.raises(InvalidRefreshTokenError):
            await auth_service.refresh_access_token(payload)


class TestGetUserById:
    async def test_returns_user_for_valid_id(self, auth_service, registered_user):
        user = await auth_service.get_user_by_id(registered_user.id)
        assert user.id == registered_user.id

    async def test_raises_for_nonexistent_id(self, auth_service):
        with pytest.raises(UserNotFoundError):
            await auth_service.get_user_by_id(999999)


class TestRevokeRefreshToken:
    async def test_removes_token_so_it_cannot_be_refreshed(
        self, auth_service, db_session, registered_user
    ):
        login_payload = UserLogin(
            email=REGISTER_PAYLOAD.email, password=REGISTER_PAYLOAD.password
        )
        token_response = await auth_service.login_user(login_payload)
        await db_session.commit()

        await auth_service.revoke_refresh_token(token_response.refresh_token)
        await db_session.commit()

        refresh_payload = RefreshTokenRequest(
            refresh_token=token_response.refresh_token
        )
        with pytest.raises(InvalidRefreshTokenError):
            await auth_service.refresh_access_token(refresh_payload)


class TestCreateApiKey:
    async def test_returns_plaintext_key_starting_with_sk(
        self, auth_service, db_session, registered_user
    ):
        plaintext_key, _ = await auth_service.create_api_key(
            registered_user.id, "test-key"
        )
        await db_session.commit()
        assert plaintext_key.startswith("sk_")

    async def test_returns_api_key_record_with_correct_name(
        self, auth_service, db_session, registered_user
    ):
        _, api_key = await auth_service.create_api_key(registered_user.id, "test-key")
        await db_session.commit()
        assert api_key.name == "test-key"

    async def test_returns_api_key_record_linked_to_user(
        self, auth_service, db_session, registered_user
    ):
        _, api_key = await auth_service.create_api_key(registered_user.id, "test-key")
        await db_session.commit()
        assert api_key.user_id == registered_user.id


class TestValidateApiKey:
    async def test_returns_user_id_for_valid_key(
        self, auth_service, db_session, registered_user
    ):
        plaintext_key, _ = await auth_service.create_api_key(
            registered_user.id, "test-key"
        )
        await db_session.commit()

        user_id = await auth_service.validate_api_key(plaintext_key)
        assert user_id == registered_user.id

    async def test_raises_for_invalid_key(self, auth_service):
        with pytest.raises(ValueError):
            await auth_service.validate_api_key("sk_invalid_key_that_does_not_exist")


class TestRefreshAccessTokenInactiveUser:
    async def test_raises_when_user_is_inactive_at_refresh_time(
        self, auth_service, db_session, registered_user
    ):
        login_payload = UserLogin(
            email=REGISTER_PAYLOAD.email, password=REGISTER_PAYLOAD.password
        )
        token_response = await auth_service.login_user(login_payload)
        await db_session.commit()

        registered_user.is_active = False
        await db_session.flush()

        refresh_payload = RefreshTokenRequest(
            refresh_token=token_response.refresh_token
        )
        with pytest.raises(InvalidRefreshTokenError):
            await auth_service.refresh_access_token(refresh_payload)
