import pytest
import httpx
from asgi_lifespan import LifespanManager

from app.core.config import settings
from app.main import create_app

settings.bcrypt_rounds = 4

REGISTER_PAYLOAD = {
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User",
}


@pytest.fixture
async def app():
    application = create_app("sqlite+aiosqlite:///:memory:")
    async with LifespanManager(application) as manager:
        yield manager.app


@pytest.fixture
async def client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def registered_user(client):
    response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    return response.json()


@pytest.fixture
async def auth_headers(client, registered_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def access_token(client, registered_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    return response.json()["access_token"]
