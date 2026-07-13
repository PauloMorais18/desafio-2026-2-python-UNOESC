"""Question-answering use case backed by the local Ollama model."""

from time import perf_counter

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.log_perguntas import QuestionLog
from app.models.log_perguntas_conhecimento import QuestionKnowledgeLog
from app.repositories.conhecimento_repository import KnowledgeRepository
from app.repositories.log_repository import QuestionLogRepository
from app.schemas.resposta import AnswerResponse, KnowledgeSourceResponse

OLLAMA_UNAVAILABLE_RESPONSE = (
    "Não foi possível gerar uma resposta agora. Verifique se o Ollama está em execução e tente novamente."
)
SYSTEM_PROMPT = """Você é o Assistente Acadêmico da instituição.
Responda em português do Brasil, de forma objetiva e cordial.
Responda naturalmente a cumprimentos, despedidas e conversas gerais, mesmo quando não houver contexto institucional.
Para perguntas sobre a instituição, use exclusivamente o contexto institucional recebido. Não invente dados, regras, prazos ou procedimentos.
Quando uma pergunta institucional não possuir contexto suficiente, explique que não há informação suficiente na base e sugira que o aluno detalhe a dúvida ou consulte a instituição."""


class QuestionService:
    """Search the knowledge base, call the LLM, and persist the audit trail."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.logs = QuestionLogRepository(session)
        self.knowledge = KnowledgeRepository(session)

    @staticmethod
    def _generate_answer(question: str, context: str) -> tuple[str, str | None]:
        """Generate an answer grounded exclusively in institutional context."""
        settings = get_settings()
        try:
            chat = ChatOllama(
                model=settings.model_name,
                base_url=settings.ollama_url,
                temperature=0,
            )
            response = chat.invoke(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(
                        content=(
                            f"Contexto institucional:\n{context}\n\n"
                            f"Pergunta do aluno: {question}"
                        )
                    ),
                ]
            )
            content = response.content
            answer = content.strip() if isinstance(content, str) else str(content).strip()
            if not answer:
                raise ValueError("O modelo retornou uma resposta vazia.")
            return answer, None
        except Exception as exc:
            return OLLAMA_UNAVAILABLE_RESPONSE, f"{type(exc).__name__}: {exc}"

    def answer(self, student_code: str, question: str, search_mode: str = "like") -> AnswerResponse:
        """Search before generating a response, then save the interaction."""
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

        context = (
            "\n\n".join(f"{knowledge.title}:\n{knowledge.content}" for knowledge, _ in matches)
            if found
            else "Nenhum contexto institucional relevante foi encontrado para esta pergunta."
        )
        answer, error_detail = self._generate_answer(question, context)
        status = "erro" if error_detail else "respondida"

        processing_time_ms = max(0, round((perf_counter() - started_at) * 1000))
        question_log = QuestionLog(
            student_code=student_code,
            question=question,
            answer=answer,
            found=found,
            status=status,
            error_detail=error_detail,
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

        return AnswerResponse(
            answer=answer,
            found=found,
            processing_time_ms=processing_time_ms,
            sources=sources,
        )
