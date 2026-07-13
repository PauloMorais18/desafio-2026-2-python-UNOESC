"""Schemas returned by the RF06 statistics endpoints."""

from datetime import date as Date

from pydantic import BaseModel, ConfigDict, Field


class StatisticsResponse(BaseModel):
    """Legacy summary retained for compatibility with existing consumers."""

    total_questions: int
    answered_questions: int
    average_processing_time_ms: float


class DailyQuestionsResponse(BaseModel):
    """Number of questions registered on the current database day."""

    model_config = ConfigDict(populate_by_name=True)

    date: Date = Field(serialization_alias="data")
    total_questions: int = Field(serialization_alias="totalPerguntas")


class StudentQuestionCount(BaseModel):
    """Question total for one student."""

    model_config = ConfigDict(populate_by_name=True)

    student_code: str = Field(serialization_alias="codigoAluno")
    total_questions: int = Field(serialization_alias="totalPerguntas")


class QuestionsByStudentResponse(BaseModel):
    """Aggregated question totals grouped by student code."""

    students: list[StudentQuestionCount] = Field(serialization_alias="alunos")


class DailyUnansweredOrErrorResponse(BaseModel):
    """Number of unanswered or errored questions registered today."""

    model_config = ConfigDict(populate_by_name=True)

    date: Date = Field(serialization_alias="data")
    total: int = Field(serialization_alias="totalSemRespostaOuErro")


class AverageResponseTimeResponse(BaseModel):
    """Average processing time across all persisted answers."""

    average_processing_time_ms: float = Field(serialization_alias="tempoMedioRespostaMs")
