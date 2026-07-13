"""Persistent chat-conversation model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Conversation(Base):
    """Group the messages exchanged by one student in a chat."""

    __tablename__ = "conversas"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[UUID] = mapped_column("chave", Uuid, default=uuid4, unique=True)
    active: Mapped[bool] = mapped_column("ativo", Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        "datahoraalt", DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        "datahoracad", DateTime(timezone=True), server_default=func.now()
    )
    student_code: Mapped[str] = mapped_column("codigo_aluno", String(50), index=True)
    title: Mapped[str] = mapped_column("titulo", String(255))
