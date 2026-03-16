from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:postgres@localhost/task_db"

engine = create_engine(DATABASE_URL)
