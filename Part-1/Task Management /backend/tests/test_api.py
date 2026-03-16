import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from src.app.app import app
import pytest
from src.app.dependencies import get_task_service


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000") as ac:
        yield ac


@pytest.fixture
def mock_task_service(mocker):
    service = mocker.Mock()
    app.dependency_overrides[get_task_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_all_tasks(client, mock_task_service):
    task_id = str(uuid.uuid4())
    mock_task_service.list_tasks.return_value = [
        {
            "id": task_id,
            "title": "Test Task",
            "description": "Test Description",
            "is_completed": False,
        }
    ]
    response = await client.get("/tasks")
    assert response.status_code == 200
    data = response.json()

    assert data[0]["title"] == "Test Task"
    assert data[0]["id"] == task_id
    assert data[0]["is_completed"] is False


@pytest.mark.asyncio
async def test_post_create_task(client, mock_task_service):
    task_id = str(uuid.uuid4())
    mock_task_service.create_task.return_value = {
        "id": task_id,
        "title": "New Task",
        "description": "New Task Description",
        "is_completed": False,
    }
    response = await client.post(
        "/tasks",
        json={"title": "New Task", "description": "New Task Description"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == task_id
    assert data["is_completed"] is False


@pytest.mark.asyncio
async def test_post_create_task_rejects_id_from_user(client, mock_task_service):
    response = await client.post(
        "/tasks",
        json={
            "id": str(uuid.uuid4()),
            "title": "New Task",
            "description": "New Task Description",
        },
    )

    assert response.status_code == 422
    mock_task_service.create_task.assert_not_called()


@pytest.mark.asyncio
async def test_put_update_task(client, mock_task_service):
    task_id = str(uuid.uuid4())
    mock_task_service.update_task.return_value = {
        "id": task_id,
        "title": "Updated Task",
        "description": "Updated description",
        "is_completed": False,
    }
    response = await client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "description": "Updated description",
            "is_completed": False,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Updated Task"
    assert data["id"] == task_id
    assert data["is_completed"] is False


@pytest.mark.asyncio
async def test_delete_task(client, mock_task_service):
    task_id = str(uuid.uuid4())
    mock_task_service.delete_task.return_value = {
        "id": task_id,
        "title": "Test Task",
        "description": "Test Description",
        "is_completed": True,
    }
    response = await client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
