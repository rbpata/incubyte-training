from src.app.schemas.task import Task


class TaskRepository:
    def __init__(self, initial_tasks: list[Task] | None = None) -> None:
        self._tasks: list[Task] = list(initial_tasks or [])

    def list_tasks(self) -> list[Task]:
        return self._tasks

    def create_task(self, task_data: Task) -> Task:
        task_to_save = task_data
        if task_to_save.id is None:
            task_to_save = task_data.model_copy(
                update={"id": str(len(self._tasks) + 1)}
            )
        self._tasks.append(task_to_save)
        return task_to_save

    def update_task(self, task_id: str, task_data: Task) -> Task | None:
        for index, current_task in enumerate(self._tasks):
            if current_task.id == task_id:
                updated_task = task_data.model_copy(update={"id": task_id})
                self._tasks[index] = updated_task
                return updated_task
        return None

    def delete_task(self, task_id: str) -> Task | None:
        for index, current_task in enumerate(self._tasks):
            if current_task.id == task_id:
                return self._tasks.pop(index)
        return None
