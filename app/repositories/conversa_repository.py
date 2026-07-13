"""Persistence helpers for conversations and RF05 message history."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversa import Conversation
from app.models.historico import HistoryMessage


class ConversationRepository:
    """Encapsulate ownership-aware conversation queries."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_for_student(self, conversation_key: UUID, student_code: str) -> Conversation | None:
        """Return an active conversation only when it belongs to the student."""
        statement = select(Conversation).where(
            Conversation.key == conversation_key,
            Conversation.student_code == student_code,
            Conversation.active.is_(True),
        )
        return self.session.scalar(statement)

    def list_for_student(self, student_code: str) -> list[Conversation]:
        """List the student's conversations from newest to oldest."""
        statement = (
            select(Conversation)
            .where(Conversation.student_code == student_code, Conversation.active.is_(True))
            .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
        )
        return list(self.session.scalars(statement))

    def messages_for_student(self, conversation_key: UUID, student_code: str) -> list[HistoryMessage]:
        """List one conversation's messages in chronological order."""
        statement = (
            select(HistoryMessage)
            .where(
                HistoryMessage.conversation_key == conversation_key,
                HistoryMessage.student_code == student_code,
                HistoryMessage.active.is_(True),
            )
            .order_by(HistoryMessage.occurred_at.asc(), HistoryMessage.id.asc())
        )
        return list(self.session.scalars(statement))
