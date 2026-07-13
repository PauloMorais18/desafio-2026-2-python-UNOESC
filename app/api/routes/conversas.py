"""Persistent conversation-history routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_student
from app.core.database import get_db_session
from app.repositories.conversa_repository import ConversationRepository
from app.schemas.historico import ConversationResponse, HistoryMessageResponse

router = APIRouter(tags=["Conversas"])


@router.get("/conversas", response_model=list[ConversationResponse], status_code=status.HTTP_200_OK, summary="Listar conversas")
def list_conversations(
    current_student: Annotated[str, Depends(get_current_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[ConversationResponse]:
    """Retorna as conversas salvas do aluno autenticado."""
    conversations = ConversationRepository(session).list_for_student(current_student)
    return [
        ConversationResponse(
            conversation_key=conversation.key,
            title=conversation.title,
            created_at=conversation.created_at,
        )
        for conversation in conversations
    ]


@router.get(
    "/conversas/{conversation_key}/historico",
    response_model=list[HistoryMessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar histórico de uma conversa",
)
def get_conversation_history(
    conversation_key: UUID,
    current_student: Annotated[str, Depends(get_current_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[HistoryMessageResponse]:
    """Retorna as mensagens somente quando a conversa pertence ao aluno autenticado."""
    repository = ConversationRepository(session)
    if repository.get_for_student(conversation_key, current_student) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada.")

    return [
        HistoryMessageResponse(
            key=message.key,
            message_type=message.message_type,
            content=message.content,
            occurred_at=message.occurred_at,
            processing_time_ms=message.processing_time_ms,
        )
        for message in repository.messages_for_student(conversation_key, current_student)
    ]
