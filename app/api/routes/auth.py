"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(tags=["authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> TokenResponse:
    """Authenticate a student by code and password, returning a JWT."""
    token = AuthService(session).authenticate(payload.student_code, payload.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código do aluno ou senha inválidos.")
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/cadastro", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> TokenResponse:
    """Create a student account using only code and password."""
    if payload.password != payload.password_confirmation:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A confirmação de senha não confere.")
    token = AuthService(session).register(payload.student_code, payload.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um usuário com esse código de aluno.")
    return TokenResponse(access_token=token, token_type="bearer")
