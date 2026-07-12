"""Authentication use case."""

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.usuario import User
from app.repositories.usuario_repository import UserRepository


class AuthService:
    """Validate student credentials and issue an access token."""

    def __init__(self, session: Session) -> None:
        self.users = UserRepository(session)

    def authenticate(self, student_code: str, password: str) -> str | None:
        """Return a JWT when an active student's credentials are valid."""
        user = self.users.get_by_student_code(student_code)
        if user is None or not user.active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return create_access_token(user.student_code)

    def register(self, student_code: str, password: str) -> str | None:
        """Create an active student account and return its first JWT."""
        if self.users.get_by_student_code(student_code) is not None:
            return None
        user = User(
            student_code=student_code,
            name=f"Aluno {student_code}",
            login=f"aluno-{student_code}",
            password_hash=hash_password(password),
            active=True,
        )
        self.users.session.add(user)
        self.users.session.commit()
        return create_access_token(user.student_code)
