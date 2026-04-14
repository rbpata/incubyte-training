import enum
import logging
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field
from pydantic_settings import BaseSettings
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class GatewaySettings(BaseSettings):
    auth_service_url: str = Field(default="http://auth-service:8001")
    task_service_url: str = Field(default="http://task-service:8002")
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:8000",
        ]
    )
    circuit_breaker_failure_threshold: int = Field(default=5)
    circuit_breaker_recovery_timeout_seconds: float = Field(default=30.0)

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = GatewaySettings()


class CircuitState(enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    failure_threshold: int
    recovery_timeout_seconds: float
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = field(default_factory=float)

    def is_request_allowed(self) -> bool:
        if self.state == CircuitState.OPEN:
            if time.monotonic() - self.last_failure_time >= self.recovery_timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN


http_client: httpx.AsyncClient | None = None

auth_circuit_breaker = CircuitBreaker(
    failure_threshold=settings.circuit_breaker_failure_threshold,
    recovery_timeout_seconds=settings.circuit_breaker_recovery_timeout_seconds,
)
task_circuit_breaker = CircuitBreaker(
    failure_threshold=settings.circuit_breaker_failure_threshold,
    recovery_timeout_seconds=settings.circuit_breaker_recovery_timeout_seconds,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info(
        "API Gateway started. auth=%s tasks=%s",
        settings.auth_service_url,
        settings.task_service_url,
    )
    yield
    await http_client.aclose()


app = FastAPI(
    title="API Gateway",
    description="Routes /api/v1/auth/** to auth-service and /api/v1/tasks/** to task-service",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


app.add_middleware(CorrelationIdMiddleware)


_HOP_BY_HOP_HEADERS = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "content-encoding",
    }
)


def _build_upstream_headers(request: Request) -> dict[str, str]:
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP_HEADERS
    }
    headers["X-Correlation-ID"] = getattr(
        request.state, "correlation_id", str(uuid.uuid4())
    )
    return headers


def _build_response_headers(upstream: httpx.Response) -> dict[str, str]:
    skip = _HOP_BY_HOP_HEADERS | {"server", "content-length"}
    return {k: v for k, v in upstream.headers.items() if k.lower() not in skip}


async def _proxy(
    request: Request, upstream_base_url: str, circuit_breaker: CircuitBreaker
) -> Response:
    assert http_client is not None, "HTTP client not initialised"

    if not circuit_breaker.is_request_allowed():
        return Response(
            content=b'{"detail":"Service temporarily unavailable"}',
            status_code=503,
            media_type="application/json",
        )

    upstream_url = httpx.URL(
        upstream_base_url.rstrip("/") + str(request.url.path),
        params=dict(request.query_params),
    )
    body = await request.body()

    try:
        upstream_response = await http_client.request(
            method=request.method,
            url=upstream_url,
            headers=_build_upstream_headers(request),
            content=body,
        )
        circuit_breaker.record_success()
        return Response(
            content=upstream_response.content,
            status_code=upstream_response.status_code,
            headers=_build_response_headers(upstream_response),
            media_type=upstream_response.headers.get("content-type"),
        )
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        circuit_breaker.record_failure()
        logger.error("Upstream request failed: %s", exc)
        return Response(
            content=b'{"detail":"Upstream service error"}',
            status_code=502,
            media_type="application/json",
        )


@app.api_route(
    "/api/v1/auth",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
@app.api_route(
    "/api/v1/auth/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
async def proxy_auth_requests(request: Request) -> Response:
    return await _proxy(request, settings.auth_service_url, auth_circuit_breaker)


@app.api_route(
    "/api/v1/tasks",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
@app.api_route(
    "/api/v1/tasks/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
async def proxy_task_requests(request: Request) -> Response:
    return await _proxy(request, settings.task_service_url, task_circuit_breaker)


@app.get("/health")
async def gateway_health() -> dict:
    return {"status": "ok", "service": "api-gateway"}


@app.get("/health/services")
async def upstream_services_health() -> dict:
    assert http_client is not None, "HTTP client not initialised"

    async def probe_upstream(url: str, breaker: CircuitBreaker) -> dict:
        try:
            response = await http_client.get(f"{url}/health", timeout=5.0)
            reachable = response.status_code == 200
        except Exception:
            reachable = False
        return {
            "reachable": reachable,
            "circuit_state": breaker.state.value,
        }

    auth_status = await probe_upstream(settings.auth_service_url, auth_circuit_breaker)
    task_status = await probe_upstream(settings.task_service_url, task_circuit_breaker)

    return {
        "services": {
            "auth-service": auth_status,
            "task-service": task_status,
        }
    }
