"""Shared FastAPI dependencies."""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.security import decode_access_token
from app.repositories.usuario_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_student(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_db_session)],
) -> str:
    """Validate the JWT and ensure its student is still active."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de autenticação ausente, inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized
    try:
        student_code = decode_access_token(credentials.credentials)
    except jwt.PyJWTError as error:
        raise unauthorized from error

    user = UserRepository(session).get_by_student_code(student_code)
    if user is None or not user.active:
        raise unauthorized
    return student_code
