"""Question-log repository extension point."""

from app.models.log_perguntas import QuestionLog
from sqlalchemy.orm import Session


class QuestionLogRepository:
    """Encapsulate question-log persistence."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, question_log: QuestionLog) -> None:
        """Add a log record to the current transaction."""
        self.session.add(question_log)
