from fastapi import Depends, FastAPI, HTTPException

from src.app.dependencies import get_task_service
from src.app.schemas.task import Task
from src.app.services.task_service import TaskNotFoundError, TaskService


app = FastAPI(
    title="Task Management API",
    description="A simple task management API",
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
)

@app.get("/tasks", response_model=list[Task], summary="Get all tasks")
def get_tasks(task_service: TaskService = Depends(get_task_service)):
    return task_service.list_tasks()


@app.post("/tasks", response_model=Task, summary="Create a new task")
def create_task(task_data: Task, task_service: TaskService = Depends(get_task_service)):
    return task_service.create_task(task_data)


@app.put("/tasks/{task_id}", response_model=Task, summary="Update an existing task")
def update_task(
    task_id: str,
    task_data: Task,
    task_service: TaskService = Depends(get_task_service),
):
    try:
        return task_service.update_task(task_id=task_id, task_data=task_data)
    except TaskNotFoundError as error:
        raise HTTPException(status_code=404, detail="Task not found") from error


@app.delete("/tasks/{task_id}", response_model=Task, summary="Delete a task")
def delete_task(task_id: str, task_service: TaskService = Depends(get_task_service)):
    try:
        return task_service.delete_task(task_id=task_id)
    except TaskNotFoundError as error:
        raise HTTPException(status_code=404, detail="Task not found") from error
