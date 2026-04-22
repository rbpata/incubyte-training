import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.metrics import AUTH_LOGIN_ATTEMPTS_TOTAL, AUTH_REGISTRATIONS_TOTAL, AUTH_TOKEN_REFRESHES_TOTAL, API_KEYS_CREATED_TOTAL
from app.models.api_key import ApiKey
from app.models.user import User
from app.schemas.auth import (
    ApiKeyCreate,
    ApiKeyCreateResponse,
    ApiKeyResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth import (
    AuthService,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.dependencies import (
    get_current_user,
    provide_auth_service,
    rate_limit_dependency,
)

logger = logging.getLogger(__name__)


def create_auth_router() -> APIRouter:
    auth_router = APIRouter(prefix="/auth", tags=["auth"])

    @auth_router.post(
        "/register",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def register(
        payload: UserRegister,
        service: AuthService = Depends(provide_auth_service),
    ) -> UserResponse:
        try:
            user = await service.register_user(payload)
            await service.session.commit()
            AUTH_REGISTRATIONS_TOTAL.inc()
            return UserResponse.model_validate(user)
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    @auth_router.post("/login", response_model=TokenResponse)
    async def login(
        payload: UserLogin,
        service: AuthService = Depends(provide_auth_service),
    ) -> TokenResponse:
        try:
            token_response = await service.login_user(payload)
            await service.session.commit()
            AUTH_LOGIN_ATTEMPTS_TOTAL.labels(result="success").inc()
            return token_response
        except InvalidCredentialsError as e:
            AUTH_LOGIN_ATTEMPTS_TOTAL.labels(result="failure").inc()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
            )

    @auth_router.post("/refresh", response_model=TokenResponse)
    async def refresh_token(
        payload: RefreshTokenRequest,
        service: AuthService = Depends(provide_auth_service),
    ) -> TokenResponse:
        try:
            result = await service.refresh_access_token(payload)
            AUTH_TOKEN_REFRESHES_TOTAL.labels(result="success").inc()
            return result
        except Exception as e:
            AUTH_TOKEN_REFRESHES_TOTAL.labels(result="failure").inc()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
            )

    @auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
    async def logout(
        payload: RefreshTokenRequest,
        service: AuthService = Depends(provide_auth_service),
    ) -> None:
        try:
            await service.revoke_refresh_token(payload.refresh_token)
            await service.session.commit()
        except Exception as e:
            logger.warning(f"Logout error: {e}")

    @auth_router.get("/me", response_model=UserResponse)
    async def get_current_user_info(
        current_user: User = Depends(get_current_user),
        _: None = Depends(rate_limit_dependency),
    ) -> UserResponse:
        return UserResponse.model_validate(current_user)

    @auth_router.post(
        "/api-keys",
        response_model=ApiKeyCreateResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_api_key(
        payload: ApiKeyCreate,
        current_user: User = Depends(get_current_user),
        service: AuthService = Depends(provide_auth_service),
        _: None = Depends(rate_limit_dependency),
    ) -> ApiKeyCreateResponse:
        plaintext_key, api_key_record = await service.create_api_key(
            current_user.id, payload.name
        )
        await service.session.commit()
        API_KEYS_CREATED_TOTAL.inc()
        return ApiKeyCreateResponse(
            id=api_key_record.id,
            name=api_key_record.name,
            plaintext_key=plaintext_key,
            created_at=api_key_record.created_at.isoformat(),
        )

    @auth_router.get("/api-keys", response_model=list[ApiKeyResponse])
    async def list_api_keys(
        current_user: User = Depends(get_current_user),
        service: AuthService = Depends(provide_auth_service),
        _: None = Depends(rate_limit_dependency),
    ) -> list[ApiKeyResponse]:
        result = await service.session.execute(
            select(ApiKey).where(ApiKey.user_id == current_user.id)
        )
        api_keys = result.scalars().all()
        return [
            ApiKeyResponse(
                id=key.id,
                name=key.name,
                is_active=key.is_active,
                created_at=key.created_at.isoformat(),
            )
            for key in api_keys
        ]

    return auth_router
