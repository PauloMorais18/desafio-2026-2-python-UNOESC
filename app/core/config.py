"""Application settings loaded from environment variables."""

from functools import lru_cache
from urllib.parse import quote

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed configuration contract for all deployment environments."""

    database_url: str | None = None
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "CHATIA"
    db_user: str = "postgres"
    db_password: str = ""
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    ollama_url: str = "http://localhost:11434"
    model_name: str = "qwen2.5:3b"
    app_name: str = "UNOIA"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        """Build the SQLAlchemy URL from the explicit PostgreSQL settings."""
        if not self.database_url:
            password = quote(self.db_password, safe="")
            self.database_url = (
                f"postgresql+psycopg://{self.db_user}:{password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached settings to keep configuration consistent per process."""
    return Settings()
