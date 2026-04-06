import pytest
from httpx import AsyncClient


class TestFixtureFactoryUsage:
    @pytest.mark.anyio
    async def test_factory_builds_custom_payloads(
        self,
        async_test_client: AsyncClient,
        task_payload_factory,
    ) -> None:
        payload = task_payload_factory(
            title="factory title", priority="high", max_retries=3
        )

        response = await async_test_client.post("/tasks", json=payload)

        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "factory title"
        assert body["priority"] == "high"
        assert body["max_retries"] == 3

    @pytest.mark.anyio
    async def test_factory_can_generate_many_tasks(
        self,
        async_test_client: AsyncClient,
        task_payload_factory,
    ) -> None:
        for index in range(3):
            payload = task_payload_factory(title=f"factory-{index}")
            response = await async_test_client.post("/tasks", json=payload)
            assert response.status_code == 201

        response = await async_test_client.get("/tasks?page=1&size=10")
        assert response.status_code == 200
        assert response.json()["total"] == 3
