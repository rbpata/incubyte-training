import uuid

from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session
from src.app.models.tasks import Task as TaskModel
from src.app.schemas.task import Task as TaskSchema, TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, db: Session):
        self._db = db

    def list_tasks(
        self,
        filter_by: str | None = None,
        order: str = "asc",
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[TaskSchema]:
        stmt = select(TaskModel)

        if filter_by == "completed":
            stmt = stmt.where(TaskModel.is_completed.is_(True))
        elif filter_by == "pending":
            stmt = stmt.where(TaskModel.is_completed.is_(False))

        if order == "desc":
            stmt = stmt.order_by(desc(TaskModel.created_at))
        else:
            stmt = stmt.order_by(asc(TaskModel.created_at))

        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        tasks = self._db.execute(stmt).scalars().all()

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
        self, task_id: uuid.UUID, task_data: TaskUpdate
    ) -> TaskSchema | None:
        task = self._db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if task is None:
            return None

        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.completed is not None:
            task.is_completed = task_data.completed

        self._db.commit()
        self._db.refresh(task)
        return TaskSchema.model_validate(task)

    def delete_task(self, task_id: uuid.UUID) -> TaskSchema | None:
        task = self._db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if task:
            task_schema = TaskSchema.model_validate(task)
            self._db.delete(task)
            self._db.commit()
            return task_schema
        return None
