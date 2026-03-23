from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID

from src.app.dependencies import get_current_user, get_task_service, get_user_service
from src.app.schemas.task import Task, TaskCreate, TaskUpdate
from src.app.schemas.user import Token, User, UserCreate
from src.app.security import create_access_token
from src.app.services.task_service import TaskNotFoundError, TaskService
from src.app.services.user_service import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserService,
)


app = FastAPI(
    title="Task Management API",
    description="A simple task management API",
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users", response_model=User, status_code=201, summary="Create a new user")
def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    try:
        return user_service.create_user(user_data)
    except UserAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@app.post("/token", response_model=Token, summary="Get an access token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    try:
        user = user_service.authenticate_user(
            form_data.username,
            form_data.password,
        )
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    access_token = create_access_token(subject=user.username)
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me", response_model=User, summary="Get current user")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/tasks", response_model=list[Task], summary="Get all tasks")
def get_tasks(
    _current_user: User = Depends(get_current_user),
    filter_by: str | None = Query(default=None),
    order: str = Query(default="asc"),
    limit: int | None = Query(default=None),
    offset: int | None = Query(default=None),
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.list_tasks(
        filter_by=filter_by, order=order, limit=limit, offset=offset
    )


@app.post("/tasks", response_model=Task, summary="Create a new task")
def create_task(
    task_data: TaskCreate,
    _current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.create_task(task_data)


@app.put("/tasks/{task_id}", response_model=Task, summary="Update an existing task")
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    _current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    try:
        return task_service.update_task(task_id=task_id, task_data=task_data)
    except TaskNotFoundError as error:
        raise HTTPException(status_code=404, detail="Task not found") from error


@app.delete("/tasks/{task_id}", response_model=Task, summary="Delete a task")
def delete_task(
    task_id: UUID,
    _current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    try:
        return task_service.delete_task(task_id=task_id)
    except TaskNotFoundError as error:
        raise HTTPException(status_code=404, detail="Task not found") from error
