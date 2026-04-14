from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import settings


class TokenManager:
    """Validates JWT tokens issued by the auth-service.

    The task-service only needs to *verify* tokens, not create them.
    Token creation lives exclusively in the auth-service.
    """

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        if not token or not token.strip():
            raise ValueError("Token is empty")
        try:
            return jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidSignatureError:
            raise ValueError("Invalid token signature")
        except jwt.DecodeError:
            raise ValueError("Failed to decode token")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")

    @staticmethod
    def extract_user_id(token: str) -> int:
        payload = TokenManager.decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token: missing user ID")
        try:
            return int(user_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid user ID in token: {user_id}")

    @staticmethod
    def extract_role(token: str) -> str:
        payload = TokenManager.decode_token(token)
        if payload.get("type") != "access":
            raise ValueError(f"Invalid token type: {payload.get('type')}")
        role = payload.get("role")
        if not role:
            raise ValueError("Invalid token: missing role")
        return role
