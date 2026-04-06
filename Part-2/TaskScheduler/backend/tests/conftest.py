import os
from datetime import datetime, timedelta, timezone

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import create_app
from app.db.base import Base


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest.fixture
def task_payload_factory():
    def make_payload(**overrides):
        base_payload = {
            "title": "Generated task",
            "description": "Generated description",
            "run_at": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            "priority": "medium",
            "max_retries": 1,
        }
        base_payload.update(overrides)
        return base_payload

    return make_payload


@pytest.fixture
async def isolated_test_database(test_database_url: str):
    engine = create_async_engine(test_database_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def async_test_client(isolated_test_database, test_database_url: str):
    app = create_app(test_database_url)

    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as async_client:
            yield async_client
