import time

import pytest
from asgi_lifespan import LifespanManager
import httpx

from main import app, CircuitBreaker, CircuitState


@pytest.fixture
async def gateway_app():
    async with LifespanManager(app):
        yield app


@pytest.fixture
async def client(gateway_app):
    transport = httpx.ASGITransport(app=gateway_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
