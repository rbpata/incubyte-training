import pytest


@pytest.fixture()
def created_task(client, auth_headers):
    resp = client.post(
        "/tasks",
        json={"title": "Buy milk", "description": "Whole milk"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    return resp.json()


def test_create_task(client, auth_headers):
    resp = client.post(
        "/tasks",
        json={
            "title": "Write tests",
            "description": "Write tests for the task management API",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Write tests"
    assert resp.json()["description"] == "Write tests for the task management API"


def test_get_tasks_returns_list(client, auth_headers, created_task):
    resp = client.get("/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert any(t["id"] == created_task["id"] for t in resp.json())


def test_get_tasks_requires_auth(client):
    resp = client.get("/tasks")
    assert resp.status_code == 401


def test_update_task(client, auth_headers, created_task):
    updated = {**created_task, "title": "Buy oat milk", "description": "Oat milk"}
    resp = client.put(
        f"/tasks/{created_task['id']}",
        json=updated,
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Buy oat milk"
    assert data["description"] == "Oat milk"
    assert data["is_completed"] is False


def test_update_nonexistent_task(client, auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"

    resp = client.put(
        f"/tasks/{fake_id}",
        json={"id": fake_id, "title": "Ghost", "description": "Ghost task"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_delete_task(client, auth_headers, created_task):
    resp = client.delete(f"/tasks/{created_task['id']}", headers=auth_headers)
    assert resp.status_code == 200

    # Confirm it's gone
    all_tasks = client.get("/tasks", headers=auth_headers).json()
    assert all(t["id"] != created_task["id"] for t in all_tasks)


def test_delete_nonexistent_task(client, auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.delete(f"/tasks/{fake_id}", headers=auth_headers)
    assert resp.status_code == 404
