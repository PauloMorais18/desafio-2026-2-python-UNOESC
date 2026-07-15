"""RF06 statistics routes derived from the persisted question audit log."""

from datetime import date, timedelta
from typing import Annotated, Literal

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
StatisticsPeriod = Literal["hoje", "7dias", "30dias", "tudo"]


def _today_filter() -> object:
    """Build the PostgreSQL filter for records created on the current day."""
    return func.date(QuestionLog.created_at) == func.current_date()


def _period_filter(period: StatisticsPeriod) -> object | None:
    """Build the date filter shared by every dashboard indicator."""
    if period == "hoje":
        return _today_filter()
    if period == "7dias":
        return QuestionLog.created_at >= func.current_date() - timedelta(days=6)
    if period == "30dias":
        return QuestionLog.created_at >= func.current_date() - timedelta(days=29)
    return None


def _apply_period(statement: object, period: StatisticsPeriod) -> object:
    period_filter = _period_filter(period)
    return statement.where(period_filter) if period_filter is not None else statement


@router.get("/estatisticas", response_model=StatisticsResponse, status_code=status.HTTP_200_OK, summary="Consultar resumo das estatísticas")
def get_statistics(
    session: Annotated[Session, Depends(get_db_session)],
    periodo: StatisticsPeriod = "hoje",
) -> StatisticsResponse:
    """Retorna o resumo compacto de estatísticas mantido para compatibilidade."""
    statement = select(
            func.count(QuestionLog.id),
            func.count(QuestionLog.id).filter(QuestionLog.status == "respondida"),
            func.coalesce(func.avg(QuestionLog.processing_time_ms), 0),
        )
    total_questions, answered_questions, average_processing_time_ms = session.execute(
        _apply_period(statement, periodo)
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
def get_daily_questions(
    session: Annotated[Session, Depends(get_db_session)],
    periodo: StatisticsPeriod = "hoje",
) -> DailyQuestionsResponse:
    """Retorna o total de perguntas recebidas no período selecionado."""
    total = session.scalar(_apply_period(select(func.count(QuestionLog.id)), periodo)) or 0
    return DailyQuestionsResponse(date=date.today(), total_questions=int(total))


@router.get(
    "/estatisticas/perguntas-por-aluno",
    response_model=QuestionsByStudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar perguntas por aluno",
)
def get_questions_by_student(
    session: Annotated[Session, Depends(get_db_session)],
    periodo: StatisticsPeriod = "hoje",
) -> QuestionsByStudentResponse:
    """Retorna a quantidade de perguntas agrupada por código de aluno."""
    statement = (
        select(QuestionLog.student_code, func.count(QuestionLog.id).label("total"))
        .group_by(QuestionLog.student_code)
        .order_by(func.count(QuestionLog.id).desc(), QuestionLog.student_code.asc())
    )
    rows = session.execute(_apply_period(statement, periodo)).all()
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
    periodo: StatisticsPeriod = "hoje",
) -> DailyUnansweredOrErrorResponse:
    """Retorna registros sem resposta ou com erro no período selecionado."""
    statement = select(func.count(QuestionLog.id)).where(
        QuestionLog.status.in_(("sem_resposta", "erro"))
    )
    total = session.scalar(_apply_period(statement, periodo)) or 0
    return DailyUnansweredOrErrorResponse(date=date.today(), total=int(total))


@router.get(
    "/estatisticas/tempo-medio-resposta",
    response_model=AverageResponseTimeResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar tempo médio de resposta",
)
def get_average_response_time(
    session: Annotated[Session, Depends(get_db_session)],
    periodo: StatisticsPeriod = "hoje",
) -> AverageResponseTimeResponse:
    """Retorna o tempo médio de processamento no período selecionado."""
    statement = select(func.coalesce(func.avg(QuestionLog.processing_time_ms), 0)).where(
        QuestionLog.answer.is_not(None)
    )
    average = session.scalar(_apply_period(statement, periodo))
    return AverageResponseTimeResponse(average_processing_time_ms=round(float(average or 0), 2))
