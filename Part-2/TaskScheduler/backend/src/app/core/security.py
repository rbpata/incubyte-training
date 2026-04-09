from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from bcrypt import hashpw, gensalt, checkpw

from app.core.config import settings


class PasswordHasher:
    """Handles password hashing and verification using bcrypt."""

    @staticmethod
    def hash(password: str) -> str:
        salt = gensalt(rounds=settings.bcrypt_rounds)
        hashed = hashpw(password.encode(), salt)
        return hashed.decode()

    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        return checkpw(password.encode(), hashed.encode())


class TokenManager:
    """Manages JWT token creation and validation."""

    @staticmethod
    def create_access_token(user_id: int, role: str) -> str:
        expiration_time = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expiration_time,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }
        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.algorithm,
        )

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        expiration_time = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        payload = {
            "sub": str(user_id),
            "exp": expiration_time,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }
        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.algorithm,
        )

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        """Decodes and validates JWT token, raising ValueError on invalid tokens."""
        if not token or not token.strip():
            raise ValueError("Token is empty")

        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidSignatureError:
            raise ValueError(
                "Invalid token signature - possibly using wrong secret key"
            )
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
        token_type = payload.get("type")
        if token_type != "access":
            raise ValueError(f"Invalid token type: {token_type}. Expected 'access'")
        role = payload.get("role")
        if not role:
            raise ValueError("Invalid token: missing role")
        return role
