import json

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    database_url: str = Field(
        default="sqlite+aiosqlite:///./task_service.db",
        description="Database URL for the task service",
    )
    environment: str = Field(default="development")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8002)
    log_level: str = Field(default="INFO")

    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT secret key – must match auth-service value",
    )
    algorithm: str = Field(default="HS256")

    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:8000",
        ]
    )
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )
    cors_allow_headers: list[str] = Field(default=["*"])

    rate_limit_calls: int = Field(default=100)
    rate_limit_period: int = Field(default=60)

    sentry_dsn: str | None = Field(default=None, description="Sentry DSN for error tracking. Leave unset to disable.")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                return [x.strip() for x in v.split(",")]
        return v


settings = Settings()
