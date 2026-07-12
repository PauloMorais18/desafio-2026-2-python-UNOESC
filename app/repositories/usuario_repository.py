"""User repository extension point."""

from app.models.usuario import User
from sqlalchemy import select
from sqlalchemy.orm import Session


class UserRepository:
    """Encapsulate user lookups."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_student_code(self, student_code: str) -> User | None:
        """Find an active or inactive user by their institutional code."""
        statement = select(User).where(User.student_code == student_code)
        return self.session.scalar(statement)
