import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class TestContainer:
    def test_container(self, db_connection):
        assert db_connection is not None

    @pytest_asyncio.fixture(scope="session")
    async def async_engine(self, postgres_container):
        async_url = postgres_container.get_connection_url(driver="asyncpg")
        engine = create_async_engine(async_url)
        yield engine
        await engine.dispose()

    @pytest_asyncio.fixture
    async def async_session(self, async_engine):
        async_session_factory = async_sessionmaker(
            bind=async_engine, expire_on_commit=False
        )
        async with async_session_factory() as session:
            yield session

    @pytest.mark.asyncio
    async def test_async_db_connection(self, async_session):
        result = await async_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
