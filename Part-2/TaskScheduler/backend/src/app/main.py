from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.session import Database
from app.db.base import Base
from app.api.v1.routes.tasks import create_tasks_router
from app.dependencies import initialize_database


def create_app(database_url: str | None = None) -> FastAPI:
    database = Database(database_url)
    initialize_database(database)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        async with database.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        await database.engine.dispose()

    app = FastAPI(title="High-Performance Task Scheduler", lifespan=lifespan)
    app.include_router(create_tasks_router())
    return app


def main() -> None:
    pass


app = create_app()
