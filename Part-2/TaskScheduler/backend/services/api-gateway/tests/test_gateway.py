from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

import main as gateway_module
from main import CircuitState, auth_circuit_breaker, task_circuit_breaker


async def test_gateway_health_returns_200(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api-gateway"}


async def test_correlation_id_middleware_adds_header_to_response(client):
    response = await client.get("/health")

    assert "x-correlation-id" in response.headers


async def test_correlation_id_middleware_uses_provided_header_value(client):
    custom_id = "my-test-correlation-id-12345"
    response = await client.get("/health", headers={"X-Correlation-ID": custom_id})

    assert response.headers.get("x-correlation-id") == custom_id


async def test_correlation_id_middleware_generates_id_when_not_provided(client):
    response = await client.get("/health")

    assert response.headers.get("x-correlation-id") != ""


async def test_proxy_auth_returns_503_when_circuit_breaker_is_open(client):
    original_state = auth_circuit_breaker.state
    auth_circuit_breaker.state = CircuitState.OPEN
    auth_circuit_breaker.last_failure_time = 9999999999.0

    try:
        response = await client.post("/api/v1/auth/login", json={})
        assert response.status_code == 503
    finally:
        auth_circuit_breaker.state = original_state
        auth_circuit_breaker.failure_count = 0


async def test_proxy_tasks_returns_503_when_circuit_breaker_is_open(client):
    original_state = task_circuit_breaker.state
    task_circuit_breaker.state = CircuitState.OPEN
    task_circuit_breaker.last_failure_time = 9999999999.0

    try:
        response = await client.get("/api/v1/tasks")
        assert response.status_code == 503
    finally:
        task_circuit_breaker.state = original_state
        task_circuit_breaker.failure_count = 0


async def test_proxy_auth_returns_upstream_response(client):
    mock_response = httpx.Response(200, json={"access_token": "tok"})
    mock_client = AsyncMock()
    mock_client.request = AsyncMock(return_value=mock_response)

    auth_circuit_breaker.state = CircuitState.CLOSED
    auth_circuit_breaker.failure_count = 0

    with patch.object(gateway_module, "http_client", mock_client):
        response = await client.post("/api/v1/auth/login", json={"username": "u", "password": "p"})

    assert response.status_code == 200


async def test_proxy_returns_502_on_connect_error(client):
    mock_client = AsyncMock()
    mock_client.request = AsyncMock(side_effect=httpx.ConnectError("refused"))

    auth_circuit_breaker.state = CircuitState.CLOSED
    auth_circuit_breaker.failure_count = 0

    with patch.object(gateway_module, "http_client", mock_client):
        response = await client.post("/api/v1/auth/login", json={})

    assert response.status_code == 502


async def test_proxy_records_failure_on_connect_error(client):
    mock_client = AsyncMock()
    mock_client.request = AsyncMock(side_effect=httpx.ConnectError("refused"))

    auth_circuit_breaker.state = CircuitState.CLOSED
    original_count = auth_circuit_breaker.failure_count
    auth_circuit_breaker.failure_count = 0

    try:
        with patch.object(gateway_module, "http_client", mock_client):
            await client.post("/api/v1/auth/login", json={})

        assert auth_circuit_breaker.failure_count == 1
    finally:
        auth_circuit_breaker.failure_count = original_count


async def test_health_services_returns_service_statuses(client):
    mock_auth_response = httpx.Response(200, json={"status": "ok"})
    mock_task_response = httpx.Response(200, json={"status": "ok"})
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=[mock_auth_response, mock_task_response])

    with patch.object(gateway_module, "http_client", mock_client):
        response = await client.get("/health/services")

    assert response.status_code == 200
    body = response.json()
    assert "services" in body
    assert "auth-service" in body["services"]
    assert "task-service" in body["services"]


async def test_health_services_marks_unreachable_when_upstream_fails(client):
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))

    with patch.object(gateway_module, "http_client", mock_client):
        response = await client.get("/health/services")

    assert response.status_code == 200
    body = response.json()
    assert body["services"]["auth-service"]["reachable"] is False
    assert body["services"]["task-service"]["reachable"] is False


async def test_health_services_includes_circuit_state(client):
    mock_auth_response = httpx.Response(200, json={"status": "ok"})
    mock_task_response = httpx.Response(200, json={"status": "ok"})
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=[mock_auth_response, mock_task_response])

    with patch.object(gateway_module, "http_client", mock_client):
        response = await client.get("/health/services")

    body = response.json()
    assert "circuit_state" in body["services"]["auth-service"]
    assert "circuit_state" in body["services"]["task-service"]
