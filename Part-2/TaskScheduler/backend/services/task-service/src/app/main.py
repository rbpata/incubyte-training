import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.events import task_event_bus
from app.core.logging import configure_logging
from app.core.sentry import init_sentry
from app.db.session import Database
from app.db.base import Base
from app.api.v1.routes.tasks import create_tasks_router
from app.dependencies import initialize_database
from app.core.middleware import add_cors, add_correlation_id, add_metrics_middleware, add_request_logging, add_security_headers
from app.core.config import settings


def create_app(database_url: str | None = None) -> FastAPI:
    configure_logging(service_name="task-service", log_level=settings.log_level)
    init_sentry(sentry_dsn=settings.sentry_dsn, environment=settings.environment)
    database = Database(database_url)
    initialize_database(database)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        async with database.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        event_processor = asyncio.create_task(task_event_bus.run())
        yield
        task_event_bus.stop()
        await event_processor
        await database.engine.dispose()

    app = FastAPI(
        title="Task Service",
        description="Handles task CRUD operations and background processing",
        version="1.0.0",
        lifespan=lifespan,
    )

    add_cors(app)
    add_security_headers(app)
    add_correlation_id(app)
    add_request_logging(app)
    add_metrics_middleware(app)

    app.include_router(create_tasks_router(), prefix="/api/v1")

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "service": "task-service"}

    @app.get("/health/live", tags=["observability"])
    async def liveness() -> dict:
        """Liveness probe — service is running."""
        return {"status": "alive", "service": "task-service"}

    @app.get("/health/ready", tags=["observability"])
    async def readiness() -> dict:
        """Readiness probe — checks DB connectivity."""
        from fastapi import HTTPException as _HTTPException
        from sqlalchemy import text
        from app.dependencies import database_instance
        if database_instance is None:
            raise _HTTPException(status_code=503, detail="Database not initialized")
        try:
            async with database_instance.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return {"status": "ready", "service": "task-service", "db": "ok"}
        except Exception as exc:
            raise _HTTPException(status_code=503, detail=f"DB unavailable: {exc}")

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        from fastapi.responses import Response as FastAPIResponse
        from app.core.metrics import get_metrics
        data, content_type = get_metrics()
        return FastAPIResponse(content=data, media_type=content_type)

    def configure_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="Task Service",
            version="1.0.0",
            description="Handles task CRUD operations and background processing",
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT Bearer token. Obtain it from the auth-service /api/v1/auth/login",
            }
        }
        for path in openapi_schema.get("paths", {}).values():
            for operation in path.values():
                if isinstance(operation, dict) and "security" not in operation:
                    operation["security"] = [{"Bearer": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = configure_openapi

    return app


app = create_app()
