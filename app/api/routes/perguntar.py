"""Question-answering routes."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_student
from app.core.database import get_db_session
from app.schemas.pergunta import QuestionRequest
from app.schemas.resposta import AnswerResponse
from app.services.pergunta_service import ConversationNotFoundError, QuestionService

router = APIRouter(tags=["Perguntas"])


@router.post("/perguntar", response_model=AnswerResponse, status_code=status.HTTP_200_OK, summary="Enviar pergunta ao assistente")
async def ask_question(
    payload: QuestionRequest,
    current_student: Annotated[str, Depends(get_current_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> AnswerResponse:
    """Recebe a pergunta do aluno autenticado, busca contexto e registra o processamento."""
    if payload.student_code != current_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O código do aluno informado não corresponde ao token de acesso.",
        )

    received_payload = {
        "codigoAluno": int(payload.student_code)
        if payload.student_code.isdigit()
        else payload.student_code,
        "pergunta": payload.question,
    }
    print(json.dumps(received_payload, ensure_ascii=False), flush=True)
    try:
        return QuestionService(session).answer(
            payload.student_code,
            payload.question,
            payload.search_mode,
            payload.conversation_key,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
