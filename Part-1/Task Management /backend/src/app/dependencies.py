from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.app.repositories.task_repository import TaskRepository
from src.app.repositories.user_repository import UserRepository
from src.app.security import decode_access_token
from src.app.services.task_service import TaskService
from src.app.services.user_service import UserService
from src.app.db.session import SessionLocal
from src.app.models.user import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_task_repository(db: Session = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db=db)


def get_task_service(
    task_repository: TaskRepository = Depends(get_task_repository),
) -> TaskService:
    return TaskService(task_repository=task_repository)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db=db)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository=user_repository)


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise _credentials_exception()

    username = payload.get("sub")
    if not username:
        raise _credentials_exception()

    user = user_service.get_by_username(username)
    if user is None:
        raise _credentials_exception()

    return user
