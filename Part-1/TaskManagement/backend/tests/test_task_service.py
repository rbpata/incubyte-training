import pytest
import uuid
from src.app.schemas.task import Task, TaskCreate
from src.app.services.task_service import TaskNotFoundError, TaskService


@pytest.fixture
def mock_task_repository(mocker):
    return mocker.Mock()


@pytest.fixture
def task_service_instance(mock_task_repository):
    return TaskService(task_repository=mock_task_repository)


def test_task_service_initialization(task_service_instance):
    assert task_service_instance is not None


def test_task_service_list_tasks(task_service_instance, mock_task_repository):
    mock_tasks = [
        Task(id=uuid.uuid4(), title="Task 1", description="D1", is_completed=False),
        Task(id=uuid.uuid4(), title="Task 2", description="D2", is_completed=True),
    ]
    mock_task_repository.list_tasks.return_value = mock_tasks

    result = task_service_instance.list_tasks()

    assert result == mock_tasks
    mock_task_repository.list_tasks.assert_called_once()


def test_task_service_create_task(task_service_instance, mock_task_repository):
    task_data = TaskCreate(
        title="Task 3",
        description="Description for Task 3",
    )
    created_task = Task(
        id=uuid.uuid4(),
        title="Task 3",
        description="Description for Task 3",
        is_completed=False,
    )
    mock_task_repository.create_task.return_value = created_task

    result = task_service_instance.create_task(task_data)

    assert result == created_task
    mock_task_repository.create_task.assert_called_once_with(task_data)


def test_task_service_update_task(task_service_instance, mock_task_repository):
    task_id = uuid.uuid4()
    updated_data = Task(
        title="Updated Task 1",
        description="Updated description",
        is_completed=True,
    )
    updated_task = Task(
        id=task_id,
        title="Updated Task 1",
        description="Updated description",
        is_completed=True,
    )
    mock_task_repository.update_task.return_value = updated_task

    result = task_service_instance.update_task(task_id, updated_data)

    assert result == updated_task
    mock_task_repository.update_task.assert_called_once_with(
        task_id=task_id,
        task_data=updated_data,
    )


def test_task_service_update_task_not_found(
    task_service_instance, mock_task_repository
):
    task_id = uuid.uuid4()
    updated_data = Task(
        title="Missing",
        description="Does not exist",
        is_completed=False,
    )
    mock_task_repository.update_task.return_value = None

    with pytest.raises(TaskNotFoundError):
        task_service_instance.update_task(task_id, updated_data)

    mock_task_repository.update_task.assert_called_once_with(
        task_id=task_id,
        task_data=updated_data,
    )


def test_task_service_delete_task(task_service_instance, mock_task_repository):
    task_id = uuid.uuid4()
    deleted_task = Task(
        id=task_id,
        title="Task 1",
        description="Description for Task 1",
        is_completed=False,
    )
    mock_task_repository.delete_task.return_value = deleted_task

    result = task_service_instance.delete_task(task_id)

    assert result == deleted_task
    mock_task_repository.delete_task.assert_called_once_with(task_id=task_id)


def test_task_service_delete_task_not_found(
    task_service_instance, mock_task_repository
):
    task_id = uuid.uuid4()
    mock_task_repository.delete_task.return_value = None

    with pytest.raises(TaskNotFoundError):
        task_service_instance.delete_task(task_id)

    mock_task_repository.delete_task.assert_called_once_with(task_id=task_id)


def test_task_service_update_task_not_found(
    task_service_instance, mock_task_repository
):
    task_id = uuid.uuid4()
    updated_data = Task(
        title="Missing",
        description="Does not exist",
        is_completed=False,
    )
    mock_task_repository.update_task.return_value = None

    with pytest.raises(TaskNotFoundError):
        task_service_instance.update_task(task_id, updated_data)

    mock_task_repository.update_task.assert_called_once_with(
        task_id=task_id,
        task_data=updated_data,
    )
