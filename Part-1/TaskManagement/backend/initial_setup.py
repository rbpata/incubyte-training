from src.app.config.database import engine
from src.app.db.base import Base
from src.app.db.session import SessionLocal
from src.app.models.tasks import Task
from src.app.models.user import User  # Import User to register it with Base


def create_tables():
    """
    Create all database tables based on SQLAlchemy models.
    """
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")


def seed_data():
    """
    Insert initial seed data into the database.
    """
    db = SessionLocal()

    try:
        existing_tasks = db.query(Task).count()

        if existing_tasks > 0:
            print("Seed data already exists. Skipping...")
            return

        tasks = [
            Task(
                title="Learn FastAPI",
                description="Build a REST API with FastAPI",
                is_completed=False,
            ),
            Task(
                title="Learn SQLAlchemy",
                description="Understand ORM concepts",
                is_completed=False,
            ),
            Task(
                title="Write API tests",
                description="Use pytest and httpx",
                is_completed=False,
            ),
        ]

        db.add_all(tasks)
        db.commit()

        print("Initial seed data inserted successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error inserting seed data: {e}")

    finally:
        db.close()


def main():
    create_tables()
    seed_data()


if __name__ == "__main__":
    main()
