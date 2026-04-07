from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from bcrypt import hashpw, gensalt, checkpw

from app.core.config import settings


class PasswordHasher:
    """Handles password hashing and verification with bcrypt."""

    @staticmethod
    def hash(password: str) -> str:
        """Hash password with bcrypt and salt."""
        salt = gensalt(rounds=settings.bcrypt_rounds)
        hashed = hashpw(password.encode(), salt)
        return hashed.decode()

    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return checkpw(password.encode(), hashed.encode())


class TokenManager:
    """Manages JWT creation and validation."""

    @staticmethod
    def create_access_token(user_id: int, role: str) -> str:
        """Create JWT access token."""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expire,
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
        """Create JWT refresh token."""
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
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
        """Decode and validate JWT token."""
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
        """Extract user ID from token."""
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
        """Extract role from access token."""
        payload = TokenManager.decode_token(token)
        token_type = payload.get("type")
        if token_type != "access":
            raise ValueError(f"Invalid token type: {token_type}. Expected 'access'")
        role = payload.get("role")
        if not role:
            raise ValueError("Invalid token: missing role")
        return role
