import pytest
from greeting_service import GreetingService
from user_repository import UserRepository
from unittest.mock import Mock


@pytest.fixture
def user_repo_mock():
    return Mock()


@pytest.fixture
def greeting_service(user_repo_mock):
    return GreetingService(user_repo_mock)


class TestGreetingService:
    def test_should_return_personalized_greeting(
        self, user_repo_mock, greeting_service
    ):
        user_repo_mock.get_user.return_value = {"name": "Ram"}
        greeting = greeting_service.get_greeting(1)
        assert greeting == "Hello, Ram!"

    def test_should_return_generic_greeting_for_non_existent_user(
        self, user_repo_mock, greeting_service
    ):
        user_repo_mock.get_user.return_value = None
        greeting = greeting_service.get_greeting(999)
        assert greeting == "Hello, Guest!"
