from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


def parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class TestCreateTaskIntegration:
    @pytest.mark.anyio
    async def test_create_task_returns_201_when_valid(
        self, async_test_client: AsyncClient
    ) -> None:
        run_at = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc).isoformat()

        response = await async_test_client.post(
            "/tasks",
            json={
                "title": "Send weekly report",
                "description": "Generate and email report",
                "run_at": run_at,
                "priority": "medium",
                "max_retries": 2,
            },
        )

        assert response.status_code == 201
        task = response.json()
        assert task["id"] > 0
        assert task["title"] == "Send weekly report"
        assert task["status"] == "pending"
        assert task["priority"] == "medium"
        assert task["max_retries"] == 2
        assert task["retry_count"] == 0

    @pytest.mark.anyio
    async def test_create_task_sets_default_priority(
        self, async_test_client: AsyncClient
    ) -> None:
        run_at = datetime(2030, 2, 1, 10, 0, tzinfo=timezone.utc).isoformat()

        response = await async_test_client.post(
            "/tasks",
            json={
                "title": "Task without priority",
                "description": None,
                "run_at": run_at,
                "max_retries": 0,
            },
        )

        assert response.status_code == 201
        task = response.json()
        assert task["priority"] == "medium"

    @pytest.mark.anyio
    async def test_create_task_rejects_missing_timezone(
        self, async_test_client: AsyncClient
    ) -> None:
        response = await async_test_client.post(
            "/tasks",
            json={
                "title": "Task without timezone",
                "description": None,
                "run_at": "2030-01-01T12:00:00",
                "max_retries": 0,
            },
        )

        assert response.status_code == 422


class TestGetTaskIntegration:
    @pytest.mark.anyio
    async def test_get_task_returns_200_when_exists(
        self, async_test_client: AsyncClient
    ) -> None:
        run_at = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc).isoformat()
        create_response = await async_test_client.post(
            "/tasks",
            json={
                "title": "Test task",
                "description": "Test",
                "run_at": run_at,
                "max_retries": 1,
            },
        )
        task_id = create_response.json()["id"]

        get_response = await async_test_client.get(f"/tasks/{task_id}")

        assert get_response.status_code == 200
        task = get_response.json()
        assert task["id"] == task_id
        assert task["title"] == "Test task"

    @pytest.mark.anyio
    async def test_get_task_returns_404_when_missing(
        self, async_test_client: AsyncClient
    ) -> None:
        response = await async_test_client.get("/tasks/99999")

        assert response.status_code == 404


class TestListTasksIntegration:
    @pytest.mark.anyio
    async def test_list_tasks_returns_empty_when_no_tasks(
        self, async_test_client: AsyncClient
    ) -> None:
        response = await async_test_client.get("/tasks")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["pages"] == 0

    @pytest.mark.anyio
    async def test_list_tasks_with_pagination(
        self, async_test_client: AsyncClient
    ) -> None:
        run_at = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc).isoformat()

        for i in range(15):
            await async_test_client.post(
                "/tasks",
                json={
                    "title": f"Task {i}",
                    "description": None,
                    "run_at": run_at,
                    "max_retries": 0,
                },
            )

        first_page = await async_test_client.get("/tasks?page=1&size=10")
        assert first_page.status_code == 200
        first_data = first_page.json()
        assert len(first_data["items"]) == 10
        assert first_data["total"] == 15
        assert first_data["pages"] == 2

        second_page = await async_test_client.get("/tasks?page=2&size=10")
        second_data = second_page.json()
        assert len(second_data["items"]) == 5

    @pytest.mark.anyio
    async def test_list_tasks_with_search(self, async_test_client: AsyncClient) -> None:
        run_at = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc).isoformat()

        await async_test_client.post(
            "/tasks",
            json={
                "title": "Send email report",
                "description": "Weekly email",
                "run_at": run_at,
                "max_retries": 0,
            },
        )
        await async_test_client.post(
            "/tasks",
            json={
                "title": "Database backup",
                "description": "Daily backup task",
                "run_at": run_at,
                "max_retries": 0,
            },
        )

        response = await async_test_client.get("/tasks?search=email")
        data = response.json()

        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert "email" in data["items"][0]["title"].lower()

    @pytest.mark.anyio
    async def test_list_tasks_with_status_filter(
        self, async_test_client: AsyncClient
    ) -> None:
        run_at = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc).isoformat()

        response1 = await async_test_client.post(
            "/tasks",
            json={
                "title": "First task",
                "description": None,
                "run_at": run_at,
                "max_retries": 0,
            },
        )
        response2 = await async_test_client.post(
            "/tasks",
            json={
                "title": "Second task",
                "description": None,
                "run_at": run_at,
                "max_retries": 0,
            },
        )

        task_id = response2.json()["id"]
        await async_test_client.patch(
            f"/tasks/{task_id}/status", json={"status": "completed"}
        )

        response = await async_test_client.get("/tasks?status=completed")
        data = response.json()

        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "completed"

    @pytest.mark.anyio
    async def test_list_tasks_with_sorting(
        self, async_test_client: AsyncClient
    ) -> None:
        run_at1 = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc).isoformat()
        run_at2 = datetime(2030, 6, 1, 12, 0, tzinfo=timezone.utc).isoformat()

        await async_test_client.post(
            "/tasks",
            json={
                "title": "Early task",
                "description": None,
                "run_at": run_at1,
                "max_retries": 0,
            },
        )
        await async_test_client.post(
            "/tasks",
            json={
                "title": "Later task",
                "description": None,
                "run_at": run_at2,
                "max_retries": 0,
            },
        )

        response = await async_test_client.get("/tasks?sort_by=run_at&sort_order=asc")
        data = response.json()

        assert len(data["items"]) == 2
        assert parse_iso_datetime(data["items"][0]["run_at"]) < parse_iso_datetime(
            data["items"][1]["run_at"]
        )


class TestUpdateTaskStatusIntegration:
    @pytest.mark.anyio
    async def test_update_task_status_returns_200_when_valid(
        self, async_test_client: AsyncClient
    ) -> None:
        run_at = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc).isoformat()
        create_response = await async_test_client.post(
            "/tasks",
            json={
                "title": "Test task",
                "description": None,
                "run_at": run_at,
                "max_retries": 0,
            },
        )
        task_id = create_response.json()["id"]

        response = await async_test_client.patch(
            f"/tasks/{task_id}/status",
            json={"status": "running"},
        )

        assert response.status_code == 200
        task = response.json()
        assert task["status"] == "running"

    @pytest.mark.anyio
    async def test_update_task_status_returns_404_when_missing(
        self, async_test_client: AsyncClient
    ) -> None:
        response = await async_test_client.patch(
            "/tasks/99999/status",
            json={"status": "running"},
        )

        assert response.status_code == 404


class TestDeleteTaskIntegration:
    @pytest.mark.anyio
    async def test_delete_task_returns_204_when_exists(
        self, async_test_client: AsyncClient
    ) -> None:
        run_at = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc).isoformat()
        create_response = await async_test_client.post(
            "/tasks",
            json={
                "title": "Task to delete",
                "description": None,
                "run_at": run_at,
                "max_retries": 0,
            },
        )
        task_id = create_response.json()["id"]

        response = await async_test_client.delete(f"/tasks/{task_id}")

        assert response.status_code == 204

        get_response = await async_test_client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404

    @pytest.mark.anyio
    async def test_delete_task_returns_404_when_missing(
        self, async_test_client: AsyncClient
    ) -> None:
        response = await async_test_client.delete("/tasks/99999")

        assert response.status_code == 404
