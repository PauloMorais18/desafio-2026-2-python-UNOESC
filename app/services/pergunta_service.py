"""Question-answering use case backed by the local Ollama model."""

from datetime import UTC, datetime
from time import perf_counter
from uuid import UUID

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.conversa import Conversation
from app.models.historico import HistoryMessage
from app.models.log_perguntas import QuestionLog
from app.models.log_perguntas_conhecimento import QuestionKnowledgeLog
from app.repositories.conhecimento_repository import KnowledgeRepository
from app.repositories.conversa_repository import ConversationRepository
from app.repositories.log_repository import QuestionLogRepository
from app.schemas.resposta import AnswerResponse, KnowledgeSourceResponse
from app.services.configuration_service import ConfigurationService, DEFAULT_SETTINGS

OLLAMA_UNAVAILABLE_RESPONSE = (
    "Não foi possível gerar uma resposta agora. Verifique se o Ollama está em execução e tente novamente."
)
OUT_OF_SCOPE_RESPONSE = (
    DEFAULT_SETTINGS["mensagem_fora_escopo"].replace(
        "{telefone}", DEFAULT_SETTINGS["telefone_suporte_whatsapp"]
    )
)
SYSTEM_PROMPT = """Você é o Assistente Acadêmico da instituição.
Responda em português do Brasil, de forma objetiva e cordial.
Use exclusivamente o contexto institucional recebido.
Não use conhecimento geral e não invente dados, regras, prazos ou procedimentos.
Se o contexto não sustentar a resposta, informe claramente que a base não possui informação suficiente."""


class ConversationNotFoundError(ValueError):
    """Raised when a student attempts to use another user's conversation."""


class QuestionService:
    """Search the knowledge base, call the LLM, and persist the audit trail."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.logs = QuestionLogRepository(session)
        self.knowledge = KnowledgeRepository(session)
        self.conversations = ConversationRepository(session)

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

    @classmethod
    def _resolve_answer(
        cls,
        question: str,
        context: str,
        found: bool,
        out_of_scope_response: str = OUT_OF_SCOPE_RESPONSE,
    ) -> tuple[str, str | None, str]:
        """Refuse deterministically when retrieval produced no approved source."""
        if not found:
            return out_of_scope_response, None, "sem_resposta"
        answer, error_detail = cls._generate_answer(question, context)
        return answer, error_detail, "erro" if error_detail else "respondida"

    def answer(
        self,
        student_code: str,
        question: str,
        search_mode: str = "like",
        conversation_key: UUID | None = None,
    ) -> AnswerResponse:
        """Search before generating a response, then save the interaction."""
        started_at = perf_counter()
        conversation = self._get_or_create_conversation(student_code, question, conversation_key)
        self.session.add(
            HistoryMessage(
                conversation_key=conversation.key,
                student_code=student_code,
                message_type=1,
                content=question,
                processing_time_ms=None,
            )
        )
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
        answer, error_detail, status = self._resolve_answer(
            question,
            context,
            found,
            ConfigurationService(self.session).out_of_scope_message(),
        )

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

        self.session.add(
            HistoryMessage(
                conversation_key=conversation.key,
                student_code=student_code,
                message_type=2,
                content=answer,
                processing_time_ms=processing_time_ms,
            )
        )
        conversation.updated_at = datetime.now(UTC)

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
            conversation_key=conversation.key,
        )

    def _get_or_create_conversation(
        self,
        student_code: str,
        question: str,
        conversation_key: UUID | None,
    ) -> Conversation:
        """Create a conversation from the first question or validate its owner."""
        if conversation_key is not None:
            conversation = self.conversations.get_for_student(conversation_key, student_code)
            if conversation is None:
                raise ConversationNotFoundError("Conversa não encontrada para o aluno autenticado.")
            return conversation

        conversation = Conversation(student_code=student_code, title=question[:255])
        self.session.add(conversation)
        self.session.flush()
        return conversation
