from datetime import datetime, timezone

import pytest
from httpx import AsyncClient

from app.main import create_app


def parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@pytest.mark.anyio
async def test_create_and_get_task(async_test_client: AsyncClient) -> None:
    run_at = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc).isoformat()

    create_response = await async_test_client.post(
        "/tasks",
        json={
            "title": "Send weekly report",
            "description": "Generate and email report",
            "run_at": run_at,
            "priority": "medium",
            "max_retries": 2,
        },
    )

    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["id"] > 0
    assert created_task["status"] == "pending"
    assert created_task["title"] == "Send weekly report"
    assert created_task["priority"] == "medium"
    assert created_task["max_retries"] == 2

    get_response = await async_test_client.get(f"/tasks/{created_task['id']}")
    assert get_response.status_code == 200
    fetched_task = get_response.json()
    assert fetched_task["id"] == created_task["id"]
    assert parse_iso_datetime(fetched_task["run_at"]) == parse_iso_datetime(run_at)


@pytest.mark.anyio
async def test_list_and_filter_tasks(async_test_client: AsyncClient) -> None:
    run_at = datetime(2031, 5, 10, 9, 30, tzinfo=timezone.utc).isoformat()

    first = await async_test_client.post(
        "/tasks",
        json={"title": "T1", "description": None, "run_at": run_at, "priority": "medium", "max_retries": 1},
    )
    second = await async_test_client.post(
        "/tasks",
        json={"title": "T2", "description": None, "run_at": run_at, "priority": "low", "max_retries": 0},
    )

    assert first.status_code == 201
    assert second.status_code == 201

    second_id = second.json()["id"]
    update_status = await async_test_client.patch(f"/tasks/{second_id}/status", json={"status": "completed"})
    assert update_status.status_code == 200

    list_all = await async_test_client.get("/tasks?page=1&size=10")
    assert list_all.status_code == 200
    assert len(list_all.json()["items"]) == 2

    list_completed = await async_test_client.get("/tasks?status=completed&page=1&size=10")
    assert list_completed.status_code == 200
    completed_data = list_completed.json()
    assert len(completed_data["items"]) == 1
    assert completed_data["items"][0]["id"] == second_id


@pytest.mark.anyio
async def test_update_status_and_delete_task(async_test_client: AsyncClient) -> None:
    run_at = datetime(2032, 8, 20, 15, 0, tzinfo=timezone.utc).isoformat()
    created = await async_test_client.post(
        "/tasks",
        json={"title": "Cleanup", "description": "Purge temp files", "run_at": run_at, "priority": "high", "max_retries": 5},
    )

    task_id = created.json()["id"]

    status_response = await async_test_client.patch(f"/tasks/{task_id}/status", json={"status": "running"})
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "running"

    delete_response = await async_test_client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    get_deleted = await async_test_client.get(f"/tasks/{task_id}")
    assert get_deleted.status_code == 404


@pytest.mark.anyio
async def test_returns_not_found_for_missing_task(async_test_client: AsyncClient) -> None:
    response = await async_test_client.get("/tasks/99999")
    assert response.status_code == 404
