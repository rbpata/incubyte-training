from sqlalchemy import create_engine

from src.app.config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True, echo_pool=True)
