"""Add soft delete support and task indexes

Revision ID: 002
Revises: 001
Create Date: 2026-03-30 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tasks", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)
    )

    op.create_index("ix_tasks_status", "tasks", ["status"], unique=False)
    op.create_index("ix_tasks_priority", "tasks", ["priority"], unique=False)
    op.create_index("ix_tasks_run_at", "tasks", ["run_at"], unique=False)
    op.create_index("ix_tasks_created_at", "tasks", ["created_at"], unique=False)
    op.create_index("ix_tasks_deleted_at", "tasks", ["deleted_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tasks_deleted_at", table_name="tasks")
    op.drop_index("ix_tasks_created_at", table_name="tasks")
    op.drop_index("ix_tasks_run_at", table_name="tasks")
    op.drop_index("ix_tasks_priority", table_name="tasks")
    op.drop_index("ix_tasks_status", table_name="tasks")

    op.drop_column("tasks", "deleted_at")
