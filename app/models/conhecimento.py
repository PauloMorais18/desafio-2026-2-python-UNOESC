"""Knowledge-base persistence model placeholder."""

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Knowledge(Base):
    """Represent a document fragment available to future retrieval flows."""

    __tablename__ = "conhecimento"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

