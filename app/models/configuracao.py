"""Runtime configuration persisted in PostgreSQL."""

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ApplicationSetting(Base):
    """Represent one editable global application option."""

    __tablename__ = "configuracoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column("chave", String(100), unique=True, index=True)
    value: Mapped[str] = mapped_column("valor", Text)
    description: Mapped[str] = mapped_column("descricao", String(255))
    updated_at: Mapped[datetime] = mapped_column(
        "datahoraalt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
