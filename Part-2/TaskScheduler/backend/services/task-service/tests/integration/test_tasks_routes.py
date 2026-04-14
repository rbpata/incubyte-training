import datetime

import pytest


def _future_run_at(hours: int = 1) -> str:
    dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)
    return dt.isoformat()


def _past_run_at(hours: int = 1) -> str:
    dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
    return dt.isoformat()


async def test_health_endpoint_returns_200(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "task-service"}


async def test_list_tasks_without_auth_returns_401(client):
    response = await client.get("/api/v1/tasks")

    assert response.status_code == 401


async def test_create_task_returns_201(client, auth_headers, task_payload):
    response = await client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)

    assert response.status_code == 201


async def test_create_task_returns_correct_fields(client, auth_headers, task_payload):
    response = await client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    body = response.json()

    assert body["title"] == task_payload["title"]
    assert body["status"] == "pending"
    assert "id" in body


async def test_create_task_without_run_at_timezone_returns_422(client, auth_headers):
    payload = {
        "title": "No TZ Task",
        "run_at": "2099-01-01T12:00:00",
        "max_retries": 1,
    }
    response = await client.post("/api/v1/tasks", json=payload, headers=auth_headers)

    assert response.status_code == 422


async def test_list_tasks_returns_200_paginated(client, auth_headers, task_payload):
    await client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    response = await client.get("/api/v1/tasks", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body


async def test_list_tasks_status_filter_returns_only_matching(client, auth_headers, task_payload):
    await client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    response = await client.get("/api/v1/tasks?status=pending", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert all(item["status"] == "pending" for item in body["items"])


async def test_list_tasks_search_filter_returns_only_matching(client, auth_headers):
    payload_a = {
        "title": "UniqueAlphaTitleXYZ",
        "run_at": _future_run_at(),
        "max_retries": 0,
    }
    payload_b = {
        "title": "CompletedlyDifferentTask",
        "run_at": _future_run_at(),
        "max_retries": 0,
    }
    await client.post("/api/v1/tasks", json=payload_a, headers=auth_headers)
    await client.post("/api/v1/tasks", json=payload_b, headers=auth_headers)

    response = await client.get("/api/v1/tasks?search=UniqueAlpha", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "UniqueAlphaTitleXYZ"


async def test_get_task_by_id_returns_200(client, auth_headers, task_payload):
    created = await client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    task_id = created.json()["id"]

    response = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == task_id


async def test_get_task_by_id_for_different_user_returns_404(client, task_payload):
    import datetime as dt
    import jwt
    from app.core.config import settings

    payload_user1 = {
        "sub": "1",
        "role": "user",
        "type": "access",
        "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
    }
    payload_user2 = {
        "sub": "2",
        "role": "user",
        "type": "access",
        "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
    }
    token1 = jwt.encode(payload_user1, settings.secret_key, algorithm=settings.algorithm)
    token2 = jwt.encode(payload_user2, settings.secret_key, algorithm=settings.algorithm)

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    created = await client.post("/api/v1/tasks", json=task_payload, headers=headers1)
    task_id = created.json()["id"]

    response = await client.get(f"/api/v1/tasks/{task_id}", headers=headers2)

    assert response.status_code == 404


async def test_get_task_nonexistent_id_returns_404(client, auth_headers):
    response = await client.get("/api/v1/tasks/99999", headers=auth_headers)

    assert response.status_code == 404


async def test_update_task_status_returns_200_with_updated_status(
    client, auth_headers, task_payload
):
    created = await client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    task_id = created.json()["id"]

    response = await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "running"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "running"


async def test_delete_task_returns_204(client, auth_headers, task_payload):
    created = await client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    task_id = created.json()["id"]

    response = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)

    assert response.status_code == 204


async def test_delete_nonexistent_task_returns_404(client, auth_headers):
    response = await client.delete("/api/v1/tasks/99999", headers=auth_headers)

    assert response.status_code == 404


async def test_process_task_endpoint_returns_202(client, auth_headers, task_payload):
    created = await client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    task_id = created.json()["id"]

    response = await client.post(f"/api/v1/tasks/{task_id}/process", headers=auth_headers)

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "processing"
    assert body["task_id"] == task_id


async def test_process_task_nonexistent_id_returns_404(client, auth_headers):
    response = await client.post("/api/v1/tasks/99999/process", headers=auth_headers)

    assert response.status_code == 404


async def test_create_task_missing_title_returns_422(client, auth_headers):
    payload = {"run_at": _future_run_at(), "max_retries": 0}
    response = await client.post("/api/v1/tasks", json=payload, headers=auth_headers)

    assert response.status_code == 422


async def test_create_task_invalid_bearer_format_returns_401(client):
    headers = {"Authorization": "Token some-random-token"}
    response = await client.get("/api/v1/tasks", headers=headers)

    assert response.status_code == 401


async def test_list_tasks_shows_only_own_tasks(client, task_payload):
    import datetime as dt
    import jwt
    from app.core.config import settings

    def make_token(user_id: int) -> str:
        p = {
            "sub": str(user_id),
            "role": "user",
            "type": "access",
            "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
        }
        return jwt.encode(p, settings.secret_key, algorithm=settings.algorithm)

    h1 = {"Authorization": f"Bearer {make_token(10)}"}
    h2 = {"Authorization": f"Bearer {make_token(20)}"}

    await client.post("/api/v1/tasks", json=task_payload, headers=h1)
    await client.post("/api/v1/tasks", json=task_payload, headers=h2)

    r1 = await client.get("/api/v1/tasks", headers=h1)
    r2 = await client.get("/api/v1/tasks", headers=h2)

    assert r1.json()["total"] == 1
    assert r2.json()["total"] == 1
