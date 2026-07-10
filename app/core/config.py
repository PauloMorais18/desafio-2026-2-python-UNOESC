"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed configuration contract for all deployment environments."""

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/academic_assistant"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    ollama_url: str = "http://localhost:11434"
    model_name: str = "replace-with-local-model"
    app_name: str = "Academic Assistant API"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings to keep configuration consistent per process."""
    return Settings()

