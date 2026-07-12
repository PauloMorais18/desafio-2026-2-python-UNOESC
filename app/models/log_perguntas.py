"""Question-audit persistence model placeholder."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class QuestionLog(Base):
    """Represent a future audit record for a question-answer interaction."""

    __tablename__ = "logs_perguntas"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_code: Mapped[str] = mapped_column("codigo_aluno", String(50), index=True)
    question: Mapped[str] = mapped_column("pergunta", Text)
    answer: Mapped[str | None] = mapped_column("resposta", Text, nullable=True)
    found: Mapped[bool] = mapped_column("encontrada", Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="respondida")
    error_detail: Mapped[str | None] = mapped_column("erro_detalhe", Text, nullable=True)
    processing_time_ms: Mapped[int] = mapped_column("tempo_processamento_ms", Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
