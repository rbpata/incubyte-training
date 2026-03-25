from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)
    
    database_url: str = Field(
        default="sqlite+aiosqlite:///./task_scheduler.db",
        description="Database URL - SQLite for dev, PostgreSQL for prod",
    )
    environment: str = Field(default="development", description="Environment: development or production")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Enable auto-reload in development")
    log_level: str = Field(default="INFO", description="Logging level")


settings = Settings()
