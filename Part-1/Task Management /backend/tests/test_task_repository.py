import pytest
import uuid

from pytest_mock import mocker
from src.app.repositories.task_repository import TaskRepository
from src.app.schemas.task import Task, TaskCreate


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock()


@pytest.fixture
def repo(mock_db):
    return TaskRepository(db=mock_db)


def test_task_repository_initialization(repo, mock_db):
    assert repo._db == mock_db


def test_list_tasks(repo, mock_db, mocker):
    mock_task = mocker.Mock(
        id=uuid.uuid4(), title="Test Task", description="desc", is_completed=False
    )
    mock_db.query.return_value.all.return_value = [mock_task]
    mock_execute = mock_db.execute.return_value
    mock_scalars = mock_execute.scalars.return_value
    mock_scalars.all.return_value = [mock_task]

    result = repo.list_tasks()
    assert len(result) == 1
    assert result[0].title == "Test Task"


def test_create_task(repo, mock_db, mocker):
    mock_task = mocker.Mock(
        id=uuid.uuid4(), title="Test Task", description="desc", is_completed=False
    )
    mock_db.add.return_value = mock_task
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    task_data = TaskCreate(title="Test Task", description="desc")

    result = repo.create_task(task_data)
    assert result.title == "Test Task"
    mock_db.add.assert_called_once
    mock_db.commit.assert_called_once
    mock_db.refresh.assert_called_once


def test_update_task_success(repo, mock_db, mocker):
    task_id = uuid.uuid4()

    mock_task = mocker.Mock(
        id=task_id,
        title="Old",
        description="Old Desc",
        is_completed=False,
    )

    mock_db.query.return_value.filter.return_value.first.return_value = mock_task

    updated_data = mocker.Mock(
        title="Updated",
        description="Updated Desc",
        is_completed=True,
    )

    result = repo.update_task(task_id, updated_data)

    assert result.title == "Updated"
    assert result.is_completed is True

    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_update_task_not_found(repo, mock_db, mocker):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = repo.update_task(uuid.uuid4(), mocker.Mock())

    assert result is None


def test_delete_task_success(repo, mock_db, mocker):
    task_id = uuid.uuid4()

    mock_task = mocker.Mock(
        id=task_id,
        title="Task",
        description="Desc",
        is_completed=False,
    )

    mock_db.query.return_value.filter.return_value.first.return_value = mock_task

    result = repo.delete_task(task_id)

    mock_db.delete.assert_called_once_with(mock_task)
    mock_db.commit.assert_called_once()

    assert result.title == "Task"


def test_delete_task_not_found(repo, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = repo.delete_task(uuid.uuid4())

    assert result is None
