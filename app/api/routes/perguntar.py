"""Question-answering routes."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_student
from app.core.database import get_db_session
from app.schemas.pergunta import QuestionRequest
from app.schemas.resposta import AnswerResponse
from app.services.pergunta_service import QuestionService

router = APIRouter(tags=["questions"])


@router.post("/perguntar", response_model=AnswerResponse, status_code=status.HTTP_200_OK)
async def ask_question(
    payload: QuestionRequest,
    current_student: Annotated[str, Depends(get_current_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> AnswerResponse:
    """Accept an authenticated student's question and persist its audit log."""
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
    return QuestionService(session).answer(payload.student_code, payload.question, payload.search_mode)
