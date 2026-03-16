import uuid

from src.app.models.tasks import Task as TaskModel
from src.app.schemas.task import Task as TaskSchema, TaskCreate


class TaskRepository:
    def __init__(self, db):
        self._db = db

    def list_tasks(self):
        tasks = self._db.query(TaskModel).all()
        return [TaskSchema.model_validate(task) for task in tasks]

    def create_task(self, task_data: TaskCreate) -> TaskSchema:
        task_id = uuid.uuid4()
        task = TaskModel(
            id=task_id,
            title=task_data.title,
            description=task_data.description,
            is_completed=False,
        )
        self._db.add(task)
        self._db.commit()
        self._db.refresh(task)
        return TaskSchema.model_validate(task)

    def update_task(
        self, task_id: uuid.UUID, task_data: TaskSchema
    ) -> TaskSchema | None:
        task = self._db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if task:
            task.title = task_data.title
            task.description = task_data.description
            task.is_completed = task_data.is_completed
            self._db.commit()
            self._db.refresh(task)
            return TaskSchema.model_validate(task)
        return None

    def delete_task(self, task_id: uuid.UUID) -> TaskSchema | None:
        task = self._db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if task:
            task_schema = TaskSchema.model_validate(task)
            self._db.delete(task)
            self._db.commit()
            return task_schema
        return None
