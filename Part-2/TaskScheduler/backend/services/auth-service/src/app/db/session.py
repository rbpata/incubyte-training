from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


class Database:
    def __init__(self, database_url: str | None = None) -> None:
        url = database_url or settings.database_url
        engine_kwargs: dict = {"echo": False}
        if "sqlite" in url:
            engine_kwargs["connect_args"] = {"check_same_thread": False}

        self.engine: AsyncEngine = create_async_engine(url, **engine_kwargs)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            yield session
