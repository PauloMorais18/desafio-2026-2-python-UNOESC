"""Question-log repository extension point."""

from app.models.log_perguntas import QuestionLog


class QuestionLogRepository:
    """Encapsulate future persistence and aggregation of question logs."""

    def create(self, question_log: QuestionLog) -> None:
        """Persist an audit record once transaction handling is implemented."""
        # TODO: Insert the record using an injected SQLAlchemy session.
        _ = question_log

