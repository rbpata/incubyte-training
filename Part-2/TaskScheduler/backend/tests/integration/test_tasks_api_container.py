from contextlib import suppress
from datetime import datetime, timezone

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import create_app


pytestmark = pytest.mark.container


def _to_asyncpg_url(sync_url: str) -> str:
    if sync_url.startswith("postgresql+psycopg2://"):
        return sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if sync_url.startswith("postgresql://"):
        return sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return sync_url


@pytest.mark.anyio
async def test_create_task_against_real_postgres_container() -> None:
    postgres_module = pytest.importorskip("testcontainers.postgres")
    PostgresContainer = postgres_module.PostgresContainer

    try:
        container = PostgresContainer("postgres:16")
        container.start()
    except Exception as error:
        pytest.skip(f"Docker/testcontainers not available: {error}")

    try:
        database_url = _to_asyncpg_url(container.get_connection_url())
        app = create_app(database_url)

        async with LifespanManager(app):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://testserver",
            ) as client:
                response = await client.post(
                    "/tasks",
                    json={
                        "title": "container task",
                        "description": "postgres backed",
                        "run_at": datetime(
                            2030, 1, 1, 12, 0, tzinfo=timezone.utc
                        ).isoformat(),
                        "priority": "low",
                        "max_retries": 2,
                    },
                )

                assert response.status_code == 201
                assert response.json()["title"] == "container task"
    finally:
        with suppress(Exception):
            container.stop()
