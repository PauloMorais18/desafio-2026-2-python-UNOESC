"""User persistence model placeholder."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    """Represent a future authenticated application user."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_code: Mapped[str] = mapped_column("codigo_aluno", String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column("nome", String(150))
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    login: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column("senha_hash", String(255))
    active: Mapped[bool] = mapped_column("ativo", Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
