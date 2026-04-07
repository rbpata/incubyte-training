from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.db.session import Database
from app.db.base import Base
from app.api.v1.routes.tasks import create_tasks_router
from app.api.v1.routes.auth import create_auth_router
from app.dependencies import initialize_database
from app.core.middleware import add_cors, add_security_headers


def create_app(database_url: str | None = None) -> FastAPI:
    database = Database(database_url)
    initialize_database(database)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        async with database.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        await database.engine.dispose()

    app = FastAPI(
        title="High-Performance Task Scheduler",
        description="Secure task scheduling API with JWT authentication, RBAC, and rate limiting",
        version="1.0.0",
        lifespan=lifespan,
    )

    add_cors(app)
    add_security_headers(app)

    app.include_router(create_auth_router(), prefix="/api/v1")
    app.include_router(create_tasks_router(), prefix="/api/v1")

    def configure_openapi_with_jwt_bearer_security():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="High-Performance Task Scheduler",
            version="1.0.0",
            description="Secure task scheduling API with JWT authentication, RBAC, and rate limiting",
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT Bearer token. Get it from /api/v1/auth/login",
            }
        }

        for path in openapi_schema.get("paths", {}).values():
            for operation in path.values():
                if isinstance(operation, dict):
                    operation_id = operation.get("operationId", "")
                    is_public_endpoint = any(
                        endpoint in operation_id for endpoint in ["register", "login"]
                    )

                    if not is_public_endpoint and "security" not in operation:
                        operation["security"] = [{"Bearer": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = configure_openapi_with_jwt_bearer_security

    return app


def main() -> None:
    pass


app = create_app()
