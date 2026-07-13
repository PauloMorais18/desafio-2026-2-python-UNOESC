"""Message history model required by RF05."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, SmallInteger, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HistoryMessage(Base):
    """Store a single user question or assistant response."""

    __tablename__ = "historico"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[UUID] = mapped_column("chave", Uuid, default=uuid4, unique=True)
    active: Mapped[bool] = mapped_column("ativo", Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        "datahoraalt", DateTime(timezone=True), server_default=func.now()
    )
    conversation_key: Mapped[UUID] = mapped_column("chaveconversa", Uuid, index=True)
    student_code: Mapped[str] = mapped_column("codigo_aluno", String(50), index=True)
    message_type: Mapped[int] = mapped_column("tipo", SmallInteger)
    content: Mapped[str] = mapped_column("conteudo", Text)
    occurred_at: Mapped[datetime] = mapped_column("data", DateTime(timezone=True), server_default=func.now())
    processing_time_ms: Mapped[int | None] = mapped_column("tempo_processamento_ms", Integer)
