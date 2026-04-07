from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict, field_validator
import json


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    database_url: str = Field(
        default="sqlite+aiosqlite:///./task_scheduler.db",
        description="Database URL - SQLite for dev, PostgreSQL for prod",
    )
    environment: str = Field(
        default="development", description="Environment: development or production"
    )
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Enable auto-reload in development")
    log_level: str = Field(default="INFO", description="Logging level")

    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT signing",
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=15, description="Access token expiry in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiry in days"
    )

    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(
        default=True, description="Allow credentials in CORS"
    )
    cors_allow_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        description="Allowed HTTP methods",
    )
    cors_allow_headers: list[str] = Field(
        default=["*"],
        description="Allowed headers",
    )

    rate_limit_calls: int = Field(
        default=100, description="Rate limit calls per window per user"
    )
    rate_limit_period: int = Field(
        default=60, description="Rate limit period in seconds"
    )

    bcrypt_rounds: int = Field(default=12, description="Bcrypt hashing rounds")

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
