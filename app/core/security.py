"""JWT and password-security helpers."""

from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Compare a plain-text password with its persisted hash."""
    return password_context.verify(plain_password, password_hash)


def hash_password(password: str) -> str:
    """Create a bcrypt hash for user provisioning utilities."""
    return password_context.hash(password)

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT whose subject is the authenticated student code."""
    settings = get_settings()
    expires_at = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    return jwt.encode(
        {"sub": subject, "exp": expires_at},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> str:
    """Return the student code in a valid JWT or raise PyJWT validation errors."""
    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise jwt.InvalidTokenError("Token sem código do aluno.")
    return subject
