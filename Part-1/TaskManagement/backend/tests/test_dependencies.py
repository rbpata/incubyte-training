import pytest
from src.app.repositories.task_repository import TaskRepository
from src.app.dependencies import get_db, get_task_repository, get_task_service
from src.app.services.task_service import TaskService


def test_get_db(mocker):
    mock_session = mocker.Mock()
    mock_session.close = mocker.Mock()

    mocker.patch("src.app.dependencies.SessionLocal", return_value=mock_session)

    generator = get_db()
    db = next(generator)

    assert db == mock_session

    mock_session.close.assert_not_called()

    try:
        next(generator)
    except StopIteration:
        pass

    mock_session.close.assert_called_once()


def test_get_task_repository(mocker):
    mock_db = mocker.Mock()

    repository = get_task_repository(mock_db)

    assert isinstance(repository, TaskRepository)
    assert repository._db == mock_db


def test_get_task_service(mocker):
    mock_repo = mocker.Mock()

    service = get_task_service(task_repository=mock_repo)

    assert isinstance(service, TaskService)
    assert service._task_repository == mock_repo
