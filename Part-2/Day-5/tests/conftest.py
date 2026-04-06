from testcontainers.postgres import PostgresContainer
import pytest


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:latest") as postgres:
        yield postgres


@pytest.fixture
def db_connection(postgres_container):
    # testcontainers exposes connection URLs, not raw DB connection objects
    connection_url = postgres_container.get_connection_url()
    yield connection_url
