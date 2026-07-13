"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.api.dependencies import get_current_student
from app.repositories.usuario_repository import UserRepository
from app.schemas.auth import LoginRequest, ProfileResponse, RegisterRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK, summary="Realizar login")
async def login(
    payload: LoginRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> TokenResponse:
    """Autentica um aluno por código e senha e retorna um token JWT."""
    token = AuthService(session).authenticate(payload.student_code, payload.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código do aluno ou senha inválidos.")
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/cadastro", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar aluno")
async def register(
    payload: RegisterRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> TokenResponse:
    """Cria uma conta de aluno usando código e senha."""
    if payload.password != payload.password_confirmation:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A confirmação de senha não confere.")
    token = AuthService(session).register(payload.student_code, payload.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um usuário com esse código de aluno.")
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/perfil", response_model=ProfileResponse, summary="Consultar perfil")
async def get_profile(
    student_code: Annotated[str, Depends(get_current_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> ProfileResponse:
    """Retorna o perfil do aluno autenticado."""
    user = UserRepository(session).get_by_student_code(student_code)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado.")
    return ProfileResponse(
        codigoAluno=user.student_code,
        nome=user.name,
        email=user.email,
        ativo=user.active,
        datahoracad=user.created_at,
    )
