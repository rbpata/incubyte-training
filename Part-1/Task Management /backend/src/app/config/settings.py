import os

from dotenv import load_dotenv


load_dotenv()


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"{name} is not set")


SECRET_KEY = _get_required_env("SECRET_KEY")
DATABASE_URL = _get_required_env("DATABASE_URL")
