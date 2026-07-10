"""Question-audit persistence model placeholder."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class QuestionLog(Base):
    """Represent a future audit record for a question-answer interaction."""

    __tablename__ = "logs_perguntas"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_code: Mapped[str] = mapped_column(String(50), index=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    found: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_time_ms: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

