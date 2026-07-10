"""SQLAlchemy database integration placeholders."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for future SQLAlchemy ORM models."""


engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Generator[Session, None, None]:
    """Yield a database session; transaction policies will be defined later."""
    # TODO: Add managed commit/rollback policy with repositories.
    with SessionLocal() as session:
        yield session

