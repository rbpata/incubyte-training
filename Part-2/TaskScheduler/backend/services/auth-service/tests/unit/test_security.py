from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import PasswordHasher, TokenManager


class TestPasswordHasher:
    def test_hash_returns_bcrypt_string(self):
        result = PasswordHasher.hash("mypassword")
        assert result.startswith("$2b$")

    def test_verify_returns_true_for_correct_password(self):
        hashed = PasswordHasher.hash("mypassword")
        assert PasswordHasher.verify("mypassword", hashed) is True

    def test_verify_returns_false_for_wrong_password(self):
        hashed = PasswordHasher.hash("mypassword")
        assert PasswordHasher.verify("wrongpassword", hashed) is False


class TestTokenManagerAccessToken:
    def test_create_access_token_contains_correct_sub(self):
        token = TokenManager.create_access_token(42, "user")
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "42"

    def test_create_access_token_contains_correct_role(self):
        token = TokenManager.create_access_token(42, "admin")
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["role"] == "admin"

    def test_create_access_token_type_is_access(self):
        token = TokenManager.create_access_token(42, "user")
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["type"] == "access"


class TestTokenManagerRefreshToken:
    def test_create_refresh_token_contains_correct_sub(self):
        token = TokenManager.create_refresh_token(42)
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "42"

    def test_create_refresh_token_type_is_refresh(self):
        token = TokenManager.create_refresh_token(42)
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["type"] == "refresh"


class TestDecodeToken:
    def test_decode_token_raises_for_empty_string(self):
        with pytest.raises(ValueError):
            TokenManager.decode_token("")

    def test_decode_token_raises_for_whitespace_string(self):
        with pytest.raises(ValueError):
            TokenManager.decode_token("   ")

    def test_decode_token_raises_for_expired_token(self):
        expired = jwt.encode(
            {
                "sub": "1",
                "exp": datetime.now(timezone.utc) - timedelta(seconds=10),
                "type": "access",
            },
            settings.secret_key,
            algorithm=settings.algorithm,
        )
        with pytest.raises(ValueError, match="expired"):
            TokenManager.decode_token(expired)

    def test_decode_token_raises_for_invalid_signature(self):
        token = jwt.encode(
            {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "wrong-secret",
            algorithm="HS256",
        )
        with pytest.raises(ValueError):
            TokenManager.decode_token(token)

    def test_decode_token_raises_for_garbage_string(self):
        with pytest.raises(ValueError):
            TokenManager.decode_token("garbage.not.a.jwt")

    def test_decode_token_returns_payload_for_valid_token(self):
        token = TokenManager.create_access_token(1, "user")
        payload = TokenManager.decode_token(token)
        assert payload["sub"] == "1"


class TestExtractUserIdAndRole:
    def test_extract_user_id_returns_correct_int(self):
        token = TokenManager.create_access_token(99, "user")
        assert TokenManager.extract_user_id(token) == 99

    def test_extract_role_returns_correct_role_for_access_token(self):
        token = TokenManager.create_access_token(1, "admin")
        assert TokenManager.extract_role(token) == "admin"

    def test_extract_role_raises_for_refresh_token(self):
        token = TokenManager.create_refresh_token(1)
        with pytest.raises(ValueError):
            TokenManager.extract_role(token)
