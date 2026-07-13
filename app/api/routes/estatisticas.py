"""RF06 statistics routes derived from the persisted question audit log."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.log_perguntas import QuestionLog
from app.schemas.estatisticas import (
    AverageResponseTimeResponse,
    DailyQuestionsResponse,
    DailyUnansweredOrErrorResponse,
    QuestionsByStudentResponse,
    StatisticsResponse,
    StudentQuestionCount,
)

router = APIRouter(tags=["Estatísticas"])


def _today_filter() -> object:
    """Build the PostgreSQL filter for records created on the current day."""
    return func.date(QuestionLog.created_at) == func.current_date()


@router.get("/estatisticas", response_model=StatisticsResponse, status_code=status.HTTP_200_OK, summary="Consultar resumo das estatísticas")
def get_statistics(session: Annotated[Session, Depends(get_db_session)]) -> StatisticsResponse:
    """Retorna o resumo compacto de estatísticas mantido para compatibilidade."""
    total_questions, answered_questions, average_processing_time_ms = session.execute(
        select(
            func.count(QuestionLog.id),
            func.count(QuestionLog.id).filter(QuestionLog.status == "respondida"),
            func.coalesce(func.avg(QuestionLog.processing_time_ms), 0),
        )
    ).one()
    return StatisticsResponse(
        total_questions=int(total_questions),
        answered_questions=int(answered_questions),
        average_processing_time_ms=round(float(average_processing_time_ms), 2),
    )


@router.get(
    "/estatisticas/perguntas-do-dia",
    response_model=DailyQuestionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar perguntas realizadas no dia",
)
def get_daily_questions(session: Annotated[Session, Depends(get_db_session)]) -> DailyQuestionsResponse:
    """Retorna o total de perguntas recebidas no dia atual."""
    total = session.scalar(select(func.count(QuestionLog.id)).where(_today_filter())) or 0
    return DailyQuestionsResponse(date=date.today(), total_questions=int(total))


@router.get(
    "/estatisticas/perguntas-por-aluno",
    response_model=QuestionsByStudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar perguntas por aluno",
)
def get_questions_by_student(
    session: Annotated[Session, Depends(get_db_session)],
) -> QuestionsByStudentResponse:
    """Retorna a quantidade de perguntas agrupada por código de aluno."""
    rows = session.execute(
        select(QuestionLog.student_code, func.count(QuestionLog.id).label("total"))
        .group_by(QuestionLog.student_code)
        .order_by(func.count(QuestionLog.id).desc(), QuestionLog.student_code.asc())
    ).all()
    return QuestionsByStudentResponse(
        students=[StudentQuestionCount(student_code=code, total_questions=int(total)) for code, total in rows]
    )


@router.get(
    "/estatisticas/sem-resposta-ou-erro-do-dia",
    response_model=DailyUnansweredOrErrorResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar perguntas sem resposta ou com erro no dia",
)
def get_daily_unanswered_or_error(
    session: Annotated[Session, Depends(get_db_session)],
) -> DailyUnansweredOrErrorResponse:
    """Retorna os registros do dia marcados como sem resposta ou com erro."""
    total = session.scalar(
        select(func.count(QuestionLog.id)).where(
            _today_filter(),
            QuestionLog.status.in_(("sem_resposta", "erro")),
        )
    ) or 0
    return DailyUnansweredOrErrorResponse(date=date.today(), total=int(total))


@router.get(
    "/estatisticas/tempo-medio-resposta",
    response_model=AverageResponseTimeResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar tempo médio de resposta",
)
def get_average_response_time(
    session: Annotated[Session, Depends(get_db_session)],
) -> AverageResponseTimeResponse:
    """Retorna o tempo médio de processamento de todas as respostas armazenadas."""
    average = session.scalar(
        select(func.coalesce(func.avg(QuestionLog.processing_time_ms), 0)).where(
            QuestionLog.answer.is_not(None)
        )
    )
    return AverageResponseTimeResponse(average_processing_time_ms=round(float(average or 0), 2))
