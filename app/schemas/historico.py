"""Schemas for persistent conversations and RF05 message history."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConversationResponse(BaseModel):
    """A chat available in the authenticated student's history."""

    model_config = ConfigDict(populate_by_name=True)

    conversation_key: UUID = Field(serialization_alias="chaveConversa")
    title: str
    created_at: datetime = Field(serialization_alias="datahoracad")
    message_count: int = Field(default=0, serialization_alias="quantidadeMensagens")


class HistoryMessageResponse(BaseModel):
    """One persisted question or answer."""

    model_config = ConfigDict(populate_by_name=True)

    key: UUID = Field(serialization_alias="chave")
    message_type: int = Field(serialization_alias="tipo")
    content: str = Field(serialization_alias="conteudo")
    occurred_at: datetime = Field(serialization_alias="data")
    processing_time_ms: int | None = Field(default=None, serialization_alias="tempoProcessamentoMs")
