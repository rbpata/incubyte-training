import asyncio
import datetime

import httpx
import pytest
from asgi_lifespan import LifespanManager

from app.core.config import settings
from app.core.events import task_event_bus
from app.main import create_app

test_db_url = "sqlite+aiosqlite:///"


@pytest.fixture
async def app():
    task_event_bus._queue = asyncio.Queue()
    task_event_bus._running = False
    application = create_app(test_db_url)
    async with LifespanManager(application):
        yield application


@pytest.fixture
async def client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def valid_token():
    return _make_token(user_id=1, role="user")


@pytest.fixture
def admin_token():
    return _make_token(user_id=1, role="admin")


@pytest.fixture
def auth_headers(valid_token):
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def task_payload():
    run_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    return {
        "title": "Test Task",
        "description": "A test task description",
        "run_at": run_at.isoformat(),
        "priority": "medium",
        "max_retries": 3,
    }


def _make_token(user_id: int, role: str) -> str:
    import datetime as dt
    import jwt

    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
