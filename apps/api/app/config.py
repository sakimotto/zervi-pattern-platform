"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    app_name: str = "Zervi Pattern Platform API"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    database_url: str = "postgresql+psycopg://zervi:zervi_dev@localhost:5432/zervi_pattern"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
