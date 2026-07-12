"""Persistence model linking answers to their knowledge sources."""

from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class QuestionKnowledgeLog(Base):
    """Keep the knowledge records used to answer a question."""

    __tablename__ = "logs_perguntas_conhecimento"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_log_id: Mapped[int] = mapped_column("log_pergunta_id", BigInteger, ForeignKey("logs_perguntas.id"))
    knowledge_id: Mapped[int] = mapped_column("conhecimento_id", BigInteger, ForeignKey("conhecimento.id"))
    relevance: Mapped[Decimal | None] = mapped_column("relevancia", Numeric(5, 4), nullable=True)
