import datetime

import jwt
import pytest

from app.core.config import settings
from app.core.security import TokenManager


def _make_token(**payload_overrides) -> str:
    payload = {
        "sub": "1",
        "role": "user",
        "type": "access",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    }
    payload.update(payload_overrides)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def test_decode_token_raises_for_empty_string():
    with pytest.raises(ValueError, match="Token is empty"):
        TokenManager.decode_token("")


def test_decode_token_raises_for_whitespace_string():
    with pytest.raises(ValueError, match="Token is empty"):
        TokenManager.decode_token("   ")


def test_decode_token_raises_for_expired_token():
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    with pytest.raises(ValueError, match="Token has expired"):
        TokenManager.decode_token(expired)


def test_decode_token_raises_for_invalid_signature():
    token = _make_token()
    with pytest.raises(ValueError, match="Invalid token signature"):
        TokenManager.decode_token(token + "tampered")


def test_decode_token_raises_for_garbage_token():
    with pytest.raises(ValueError, match="Failed to decode token"):
        TokenManager.decode_token("not.a.jwt")


def test_decode_token_returns_payload_for_valid_token():
    token = _make_token()
    payload = TokenManager.decode_token(token)

    assert payload["sub"] == "1"


def test_extract_user_id_returns_integer_from_valid_token():
    token = _make_token(sub="42")
    result = TokenManager.extract_user_id(token)

    assert result == 42


def test_extract_user_id_raises_when_sub_missing():
    token = jwt.encode(
        {"role": "user", "type": "access", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    with pytest.raises(ValueError, match="missing user ID"):
        TokenManager.extract_user_id(token)


def test_extract_user_id_raises_for_non_integer_sub():
    token = jwt.encode(
        {"sub": "not-an-int", "type": "access", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    with pytest.raises(ValueError, match="Invalid user ID"):
        TokenManager.extract_user_id(token)


def test_extract_role_returns_role_for_valid_token():
    token = _make_token(role="admin")
    result = TokenManager.extract_role(token)

    assert result == "admin"


def test_extract_role_raises_for_non_access_token_type():
    token = jwt.encode(
        {"sub": "1", "role": "user", "type": "refresh", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    with pytest.raises(ValueError, match="Invalid token type"):
        TokenManager.extract_role(token)


def test_extract_role_raises_when_role_missing():
    token = jwt.encode(
        {"sub": "1", "type": "access", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    with pytest.raises(ValueError, match="missing role"):
        TokenManager.extract_role(token)
