from src.app.models.user import User
from src.app.repositories.user_repository import UserRepository
from src.app.schemas.user import UserCreate
from src.app.security import hash_password, verify_password


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def create_user(self, user_data: UserCreate) -> User:
        existing_user = self._user_repository.get_by_username(user_data.username)
        if existing_user is not None:
            raise UserAlreadyExistsError("Username already exists")

        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )
        return self._user_repository.create(user)

    def authenticate_user(self, username: str, password: str) -> User:
        user = self._user_repository.get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid username or password")

        return user

    def get_by_username(self, username: str) -> User | None:
        return self._user_repository.get_by_username(username)
