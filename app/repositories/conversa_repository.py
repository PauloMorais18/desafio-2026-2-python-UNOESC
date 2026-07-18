"""Persistence helpers for conversations and RF05 message history."""

from uuid import UUID

from sqlalchemy import func, select, update
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

    def message_count_for_student(self, conversation_key: UUID, student_code: str) -> int:
        """Count visible messages in one conversation owned by the student."""
        statement = select(func.count(HistoryMessage.id)).where(
            HistoryMessage.conversation_key == conversation_key,
            HistoryMessage.student_code == student_code,
            HistoryMessage.active.is_(True),
        )
        return int(self.session.scalar(statement) or 0)
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
    def deactivate_for_student(self, conversation_key: UUID, student_code: str) -> bool:
        """Soft-delete a conversation and all its visible messages for its owner."""
        conversation = self.get_for_student(conversation_key, student_code)
        if conversation is None:
            return False
        conversation.active = False
        self.session.execute(
            update(HistoryMessage)
            .where(
                HistoryMessage.conversation_key == conversation_key,
                HistoryMessage.student_code == student_code,
                HistoryMessage.active.is_(True),
            )
            .values(active=False)
        )
        self.session.commit()
        return True
