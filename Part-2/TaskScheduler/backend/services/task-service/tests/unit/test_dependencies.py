import datetime

import jwt
import pytest

from app.core.config import settings


def _make_token(**overrides) -> str:
    payload = {
        "sub": "1",
        "role": "user",
        "type": "access",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    }
    payload.update(overrides)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


async def test_missing_auth_header_returns_401(client):
    response = await client.get("/api/v1/tasks")

    assert response.status_code == 401
    assert "Missing" in response.json()["detail"]


async def test_malformed_auth_header_returns_401(client):
    response = await client.get("/api/v1/tasks", headers={"Authorization": "BadFormat"})

    assert response.status_code == 401


async def test_empty_bearer_token_returns_401(client):
    response = await client.get("/api/v1/tasks", headers={"Authorization": "Bearer  "})

    assert response.status_code == 401


async def test_expired_token_returns_401(client):
    expired = jwt.encode(
        {"sub": "1", "role": "user", "type": "access", "exp": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    response = await client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401


async def test_token_missing_sub_returns_401(client):
    token = jwt.encode(
        {"role": "user", "type": "access", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    response = await client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


async def test_token_missing_role_returns_401(client):
    token = jwt.encode(
        {"sub": "1", "type": "access", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    response = await client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


async def test_refresh_token_type_returns_401(client):
    token = jwt.encode(
        {"sub": "1", "role": "user", "type": "refresh", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    response = await client.get("/api/v1/tasks", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
