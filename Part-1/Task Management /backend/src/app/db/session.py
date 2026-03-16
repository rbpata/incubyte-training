from sqlalchemy.orm import sessionmaker
from src.app.config.database import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
