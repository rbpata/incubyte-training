from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


class TestBackgroundTaskProcessing:
    @pytest.mark.anyio
    async def test_process_task_returns_202_accepted(self, async_test_client: AsyncClient) -> None:
        run_at = datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc).isoformat()
        
        create_response = await async_test_client.post(
            "/tasks",
            json={
                "title": "Test task for processing",
                "description": "Test",
                "run_at": run_at,
                "max_retries": 3,
            },
        )
        
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        process_response = await async_test_client.post(f"/tasks/{task_id}/process")
        
        assert process_response.status_code == 202
        data = process_response.json()
        assert data["status"] == "processing"
        assert data["task_id"] == task_id

    @pytest.mark.anyio
    async def test_process_nonexistent_task_returns_202(self, async_test_client: AsyncClient) -> None:
        response = await async_test_client.post("/tasks/99999/process")
        
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "processing"
