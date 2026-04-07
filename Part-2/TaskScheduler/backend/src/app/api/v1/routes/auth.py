from fastapi import APIRouter, Depends, HTTPException, status
import logging

from app.services.auth import (
    AuthService,
    UserAlreadyExistsError,
    InvalidCredentialsError,
)
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    ApiKeyCreate,
    ApiKeyCreateResponse,
    ApiKeyResponse,
)
from app.dependencies import (
    provide_auth_service,
    get_current_user,
    rate_limit_dependency,
)
from app.models.user import User


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


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
        """Register new user."""
        try:
            user = await service.register_user(payload)
            await service.session.commit()
            return UserResponse.model_validate(user)
        except UserAlreadyExistsError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )

    @auth_router.post("/login", response_model=TokenResponse)
    async def login(
        payload: UserLogin,
        service: AuthService = Depends(provide_auth_service),
    ) -> TokenResponse:
        """Login user and return access/refresh tokens."""
        try:
            token_response = await service.login_user(payload)
            await service.session.commit()
            return token_response
        except InvalidCredentialsError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            )

    @auth_router.post("/refresh", response_model=TokenResponse)
    async def refresh_token(
        payload: RefreshTokenRequest,
        service: AuthService = Depends(provide_auth_service),
    ) -> TokenResponse:
        """Refresh access token using refresh token."""
        try:
            token_response = await service.refresh_access_token(payload)
            return token_response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            )

    @auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
    async def logout(
        payload: RefreshTokenRequest,
        service: AuthService = Depends(provide_auth_service),
    ) -> None:
        """Logout user by revoking refresh token."""
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
        """Get current user info."""
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
        """Create API key for external access."""
        plaintext_key, api_key_record = await service.create_api_key(
            current_user.id,
            payload.name,
        )
        await service.session.commit()

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
        """List user's API keys."""
        from sqlalchemy import select
        from app.models.api_key import ApiKey

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
