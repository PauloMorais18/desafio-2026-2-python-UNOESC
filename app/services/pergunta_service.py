"""Question-answering use case."""

from time import perf_counter

from sqlalchemy.orm import Session

from app.models.log_perguntas import QuestionLog
from app.models.log_perguntas_conhecimento import QuestionKnowledgeLog
from app.repositories.conhecimento_repository import KnowledgeRepository
from app.repositories.log_repository import QuestionLogRepository
from app.schemas.resposta import AnswerResponse, KnowledgeSourceResponse

NO_KNOWLEDGE_RESPONSE = "Não encontrei informações sobre essa pergunta na base de conhecimento institucional."


class QuestionService:
    """Search the knowledge base and persist the complete audit trail."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.logs = QuestionLogRepository(session)
        self.knowledge = KnowledgeRepository(session)

    def answer(self, student_code: str, question: str, search_mode: str = "like") -> AnswerResponse:
        """Search the knowledge base before returning a grounded response."""
        started_at = perf_counter()
        matches = self.knowledge.search(question, search_mode)
        found = bool(matches)
        sources = [
            KnowledgeSourceResponse(
                id=knowledge.id,
                title=knowledge.title,
                category=knowledge.category,
                relevance=round(relevance, 4),
            )
            for knowledge, relevance in matches
        ]
        if found:
            excerpts = "\n\n".join(f"{knowledge.title}:\n{knowledge.content}" for knowledge, _ in matches)
            answer = excerpts
            status = "respondida"
        else:
            answer = NO_KNOWLEDGE_RESPONSE
            status = "sem_resposta"
        processing_time_ms = max(0, round((perf_counter() - started_at) * 1000))

        question_log = QuestionLog(
            student_code=student_code,
            question=question,
            answer=answer,
            found=found,
            status=status,
            processing_time_ms=processing_time_ms,
        )
        self.logs.create(question_log)
        self.session.flush()
        for knowledge, relevance in matches:
            self.session.add(
                QuestionKnowledgeLog(
                    question_log_id=question_log.id,
                    knowledge_id=knowledge.id,
                    relevance=round(relevance, 4),
                )
            )
        self.session.commit()
        return AnswerResponse(answer=answer, found=found, processing_time_ms=processing_time_ms, sources=sources)
