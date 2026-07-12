"""Knowledge-base persistence model placeholder."""

from datetime import datetime

from sqlalchemy import Boolean, Computed, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TSVECTOR

from app.core.database import Base


class Knowledge(Base):
    """Represent a document fragment available to future retrieval flows."""

    __tablename__ = "conhecimento"

    id: Mapped[int] = mapped_column(primary_key=True)
    active: Mapped[bool] = mapped_column("ativo", Boolean, default=True)
    title: Mapped[str] = mapped_column("titulo", String(255), index=True)
    content: Mapped[str] = mapped_column("conteudo", Text)
    category: Mapped[str] = mapped_column("categoria", String(100), index=True)
    search_document: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('portuguese', coalesce(titulo, '') || ' ' || coalesce(categoria, '') || ' ' || coalesce(conteudo, ''))",
            persisted=True,
        ),
    )
