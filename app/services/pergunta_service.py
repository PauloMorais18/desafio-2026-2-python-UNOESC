"""Question-answering use case."""

from time import perf_counter

from sqlalchemy.orm import Session

from app.models.log_perguntas import QuestionLog
from app.repositories.log_repository import QuestionLogRepository
from app.schemas.resposta import AnswerResponse

INITIAL_RESPONSE = (
    "Recebi sua pergunta. A busca na base de conhecimento e a geração por IA "
    "serão integradas nas próximas etapas do projeto."
)


class QuestionService:
    """Persist questions while the RAG workflow is being integrated."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.logs = QuestionLogRepository(session)

    def answer(self, student_code: str, question: str) -> AnswerResponse:
        """Save the request log and return the current first-stage response."""
        started_at = perf_counter()
        answer = INITIAL_RESPONSE
        processing_time_ms = max(0, round((perf_counter() - started_at) * 1000))

        self.logs.create(
            QuestionLog(
                student_code=student_code,
                question=question,
                answer=answer,
                found=False,
                status="sem_resposta",
                processing_time_ms=processing_time_ms,
            )
        )
        self.session.commit()
        return AnswerResponse(answer=answer, found=False, processing_time_ms=processing_time_ms)
