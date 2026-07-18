"""Question-answering use case backed by the local Ollama model."""

from datetime import UTC, datetime
import ast
import difflib
import operator
import re
import unicodedata
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
GENERAL_SCOPE_RESPONSE = (
    "Posso ajudar com dúvidas acadêmicas e institucionais. "
    "Para outros assuntos, faça uma pergunta relacionada à instituição."
)
SYSTEM_PROMPT = """Você é o Assistente Acadêmico da instituição.
Responda em português do Brasil, de forma direta e cordial.
Use somente fatos explicitamente escritos no contexto institucional recebido.
Não complete lacunas com conhecimento geral, suposições ou procedimentos comuns.
Não invente etapas, documentos, canais, prazos, confirmações ou recomendações.
Não diga que a pergunta contém erro e não peça esclarecimento quando a intenção estiver clara.
Diferencie matrícula inicial de rematrícula conforme a pergunta do aluno.
Quando houver procedimento no contexto, organize a resposta em etapas explicadas e objetivas.
Considere o histórico recente para interpretar perguntas de continuação, sem carregar assuntos de outras conversas.
Nunca mencione nome de arquivo, PDF, página, número de trecho, banco de dados, embedding ou mecanismo de busca.
Entregue já na primeira resposta todos os fatos relevantes recuperados para a intenção do aluno.
Se o contexto não sustentar a resposta, diga somente que a base não possui informação suficiente."""


class ConversationNotFoundError(ValueError):
    """Raised when a student attempts to use another user's conversation."""


class QuestionService:
    """Search the knowledge base, call the LLM, and persist the audit trail."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.logs = QuestionLogRepository(session)
        self.knowledge = KnowledgeRepository(session)
        self.conversations = ConversationRepository(session)

    @classmethod
    def _generate_answer(
        cls, question: str, context: str, conversation_history: str = ""
    ) -> tuple[str, str | None]:
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
                            f"Histórico recente desta conversa:\n"
                            f"{conversation_history or 'Sem mensagens anteriores.'}\n\n"
                            f"Pergunta atual do aluno: {question}"
                        )
                    ),
                ]
            )
            content = response.content
            answer = content.strip() if isinstance(content, str) else str(content).strip()
            if not answer:
                raise ValueError("O modelo retornou uma resposta vazia.")
            if not cls._answer_is_grounded(answer, context):
                contextual_question = f"{conversation_history}\n{question}".strip()
                return cls._extract_grounded_answer(contextual_question, context), None
            return answer, None
        except Exception as exc:
            return OLLAMA_UNAVAILABLE_RESPONSE, f"{type(exc).__name__}: {exc}"

    @classmethod
    def _contextualize_question(
        cls, question: str, previous_messages: list[HistoryMessage]
    ) -> str:
        """Resolve short follow-ups against the latest user turn in this chat only."""
        if cls._requires_institutional_context(question) or not previous_messages:
            return question
        normalized = cls._normalize_text(question)
        words = set(normalized.split())
        follow_up_terms = {
            "mais", "detalhe", "detalhes", "detalhado", "detalhada", "explica",
            "explique", "isso", "essa", "esse", "tambem", "ainda", "consegue",
            "continue", "continuar", "aprofundar",
        }
        is_follow_up = bool(words & follow_up_terms) or normalized.startswith("e ")
        if not is_follow_up:
            return question
        previous_user_message = next(
            (
                message.content
                for message in reversed(previous_messages)
                if message.message_type == 1
                and cls._requires_institutional_context(message.content)
            ),
            None,
        )
        if previous_user_message is None:
            return question
        return f"{previous_user_message}. Continuação do aluno: {question}"

    @staticmethod
    def _format_conversation_history(
        previous_messages: list[HistoryMessage], limit: int = 6
    ) -> str:
        """Format only the current conversation's recent turns for the local model."""
        lines = []
        for message in previous_messages[-limit:]:
            role = "Aluno" if message.message_type == 1 else "Assistente"
            lines.append(f"{role}: {message.content}")
        return "\n".join(lines)
    @classmethod
    def _answer_is_grounded(cls, answer: str, context: str) -> bool:
        """Reject verbose or weakly supported generations from small local models."""
        if len(answer) > 900:
            return False
        normalized_answer = cls._normalize_text(answer)
        if (
            "trecho" in normalized_answer
            or re.search(r"\bpagina\s+\d+", normalized_answer)
            or ".pdf" in answer.lower()
            or "base_de_conhecimento" in answer.lower()
        ):
            return False
        ignored = {
            "como", "para", "pela", "pelo", "com", "uma", "voce", "deve",
            "pode", "caso", "sobre", "seus", "suas", "mais", "apos", "antes",
        }
        answer_terms = {
            term for term in cls._normalize_text(answer).split()
            if len(term) >= 4 and term not in ignored
        }
        if not answer_terms:
            return False
        context_terms = set(cls._normalize_text(context).split())
        return len(answer_terms & context_terms) / len(answer_terms) >= 0.75

    @classmethod
    def _format_institutional_procedure(cls, question: str, context: str) -> str | None:
        """Turn procedures explicitly present in the PDF into explained steps."""
        normalized_question = cls._normalize_institutional_query(question)
        question_terms = set(normalized_question.split())
        procedural_terms = {
            "como", "fazer", "realizar", "passo", "quero", "rematricula",
            "detalhe", "detalhes", "detalhado", "detalhada",
        }
        if not question_terms & procedural_terms:
            return None
        normalized_context = cls._normalize_text(context)
        steps: list[tuple[str, str]] = []
        missing_details = ""

        if "rematricula" in question_terms:
            if "rematricula ocorre semestralmente conforme calendario academico" in normalized_context:
                steps.append((
                    "Período da rematrícula",
                    "A rematrícula é semestral e deve seguir o calendário acadêmico.",
                ))
            if "aluno seleciona disciplinas" in normalized_context:
                steps.append((
                    "Seleção das disciplinas",
                    "Escolha as disciplinas que farão parte da nova grade.",
                ))
            if "verifica conflitos de horario" in normalized_context:
                steps.append((
                    "Conferência de horários",
                    "Verifique se as disciplinas escolhidas possuem conflitos de horário.",
                ))
            if "confirma a grade" in normalized_context:
                steps.append((
                    "Confirmação da grade",
                    "Revise e confirme a grade selecionada.",
                ))
            if "finaliza o processo" in normalized_context:
                steps.append((
                    "Finalização",
                    "Finalize o processo depois de conferir as disciplinas e os horários.",
                ))
            missing_details = (
                "A base institucional não informa o endereço do sistema nem datas "
                "específicas. As datas devem ser consultadas no calendário acadêmico."
            )
        elif "matricula" in question_terms:
            if "matricula inicial e realizada online" in normalized_context:
                steps.append((
                    "Início online",
                    "A matrícula inicial é realizada online.",
                ))
            if "entrega da documentacao exigida" in normalized_context:
                steps.append((
                    "Documentação",
                    "A conclusão da matrícula depende da entrega da documentação exigida.",
                ))
            if "confirmacao do contrato academico" in normalized_context:
                steps.append((
                    "Contrato acadêmico",
                    "Também é necessário confirmar o contrato acadêmico.",
                ))
            missing_details = (
                "A base institucional não identifica o portal, não lista os documentos "
                "exigidos e não apresenta prazos específicos."
            )

        if not steps:
            return None
        numbered_steps = "\n".join(
            f"{index}. {title}: {detail}"
            for index, (title, detail) in enumerate(steps, start=1)
        )
        subject = "a rematrícula" if "rematricula" in question_terms else "a matrícula inicial"
        return (
            f"Para realizar {subject}, siga estas orientações:\n"
            f"{numbered_steps}\n\n{missing_details}"
        )
    @classmethod
    def _extract_grounded_answer(cls, question: str, context: str) -> str:
        """Build a safe answer from the most relevant sentences in the source."""
        procedural_answer = cls._format_institutional_procedure(question, context)
        if procedural_answer is not None:
            return procedural_answer
        normalized_question = cls._normalize_institutional_query(question)
        ignored = {
            "como", "faco", "para", "quero", "fazer", "minha", "meu", "uma",
            "posso", "preciso", "novamente", "onde", "qual", "quais",
            "minha", "minhas", "meus", "seus", "suas", "mais", "detalhes",
        }
        query_terms = {
            term for term in normalized_question.split()
            if len(term) >= 4 and term not in ignored
        }
        compact_context = re.sub(r"\s+", " ", context).strip()
        sentences = []
        for raw_sentence in re.split(r"(?<=[.!?])\s+", compact_context):
            sentence = raw_sentence.strip()
            sentence = re.sub(
                r"^[^:\n]{0,220}(?:—|-)\s*trecho\s+\d+:\s*",
                "",
                sentence,
                flags=re.IGNORECASE,
            )
            sentence = re.sub(r"^P.gina\s+\d+\s*", "", sentence, flags=re.IGNORECASE)
            sentence = re.sub(
                r"^(?:\d+\.\s*)?(?:Matrícula e Rematrícula|Secretaria Acadêmica|"
                r"Portal do Aluno|Biblioteca|Financeiro|FAQ Institucional\s+"
                r"Perguntas frequentes:)\s+",
                "",
                sentence,
                flags=re.IGNORECASE,
            )
            normalized_sentence = cls._normalize_text(sentence)
            is_metadata = any(
                marker in normalized_sentence
                for marker in (
                    "base de conhecimento universidade ficticia",
                    "esta secao descreve procedimentos internos",
                    "mecanismos de busca semantica rag",
                    "informacoes aqui apresentadas sao exemplificativas",
                )
            )
            if (
                len(sentence) >= 20
                and not sentence.endswith("?")
                and not is_metadata
            ):
                sentences.append(sentence)
        ranked = []
        for index, sentence in enumerate(sentences):
            sentence_words = cls._normalize_text(sentence).split()
            hits = sum(
                any(
                    term == word
                    or (
                        len(term) >= 4
                        and len(word) >= 4
                        and term[: min(5, len(term))] == word[: min(5, len(term))]
                    )
                    for word in sentence_words
                )
                for term in query_terms
            )
            if hits:
                density = hits / max(1, len(sentence_words))
                ranked.append((hits, density, index, sentence))
        if not ranked:
            return "A base de conhecimento não possui informação suficiente para responder com segurança."
        ordered = sorted(
            ranked, key=lambda item: (-item[0], -item[1], item[2])
        )
        selected = []
        seen = set()
        for _, _, index, sentence in ordered[:4]:
            normalized_sentence = cls._normalize_text(sentence)
            if normalized_sentence not in seen:
                selected.append((index, cls._repair_extracted_text(sentence)))
                seen.add(normalized_sentence)
        selected.sort(key=lambda item: item[0])
        facts = "\n".join(f"- {sentence}" for _, sentence in selected)
        return f"De acordo com a base de conhecimento:\n{facts}"
    @staticmethod
    def _repair_extracted_text(text: str) -> str:
        """Repair known replacement-character artifacts from the bundled PDF font."""
        replacements = {
            "frequ�ncia": "frequência", "hist�rico": "histórico",
            "declara��es": "declarações", "solicita��es": "solicitações",
            "acad�micas": "acadêmicas", "acad�mico": "acadêmico",
            "empr�stimos": "empréstimos", "renova��o": "renovação",
            "normaliza��o": "normalização", "cient�fica": "científica",
            "coordena��o": "coordenação", "negocia��o": "negociação",
            "matr�cula": "matrícula", "rematr�cula": "rematrícula",
            "documenta��o": "documentação", "confirma��o": "confirmação",
            "hor�rio": "horário", "institui��o": "instituição",
            "informa��es": "informações", "n�o": "não",
        }
        for corrupted, repaired in replacements.items():
            text = text.replace(corrupted, repaired)
        return text
    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text.lower())
        without_accents = "".join(character for character in normalized if not unicodedata.combining(character))
        return re.sub(r"[^a-z0-9 ]+", " ", without_accents).strip()

    @classmethod
    def _direct_conversation_response(cls, question: str) -> str | None:
        """Answer simple social interactions without consulting institutional documents."""
        text = cls._normalize_text(question)
        if re.fullmatch(r"(oi|ola|opa|e ai|bom dia|boa tarde|boa noite)( tudo bem)?", text):
            return "Olá! Como posso ajudar com sua dúvida acadêmica?"
        if re.fullmatch(r"(obrigado|obrigada|valeu|agradeco|muito obrigado|muito obrigada)", text):
            return "Por nada! Se precisar, posso ajudar com outra dúvida acadêmica."
        if re.fullmatch(r"(tchau|ate logo|ate mais|falou|boa noite)", text):
            return "Até mais! Estou à disposição quando precisar."
        if re.fullmatch(r"(tenho uma duvida|estou com uma duvida|posso fazer uma pergunta)", text):
            return "Claro! Pode enviar sua dúvida."
        calculation = cls._safe_calculation_response(question)
        if calculation is not None:
            return calculation
        return None

    @staticmethod
    def _safe_calculation_response(question: str) -> str | None:
        """Answer basic arithmetic without using institutional context or arbitrary code."""
        expression_match = re.search(r"(-?\d+(?:[.,]\d+)?(?:\s*[+\-*/]\s*-?\d+(?:[.,]\d+)?)+)", question)
        if expression_match is None:
            return None
        expression = expression_match.group(1).replace(",", ".")
        operations = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }

        def evaluate(node: ast.AST) -> float:
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return float(node.value)
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                value = evaluate(node.operand)
                return value if isinstance(node.op, ast.UAdd) else -value
            if isinstance(node, ast.BinOp) and type(node.op) in operations:
                return operations[type(node.op)](evaluate(node.left), evaluate(node.right))
            raise ValueError("Expressão não permitida.")

        try:
            result = evaluate(ast.parse(expression, mode="eval"))
        except (SyntaxError, ValueError, ZeroDivisionError, OverflowError):
            return None
        if abs(result) > 1_000_000_000:
            return None
        formatted = str(int(result)) if result.is_integer() else f"{result:.6f}".rstrip("0").rstrip(".")
        return f"O resultado de {expression} é {formatted}."

    @classmethod
    def _requires_institutional_context(cls, question: str) -> bool:
        """Identify questions that should be answered from institutional documents."""
        text = cls._normalize_institutional_query(question)
        words = set(text.split())
        return bool(words & cls._institutional_terms())

    @staticmethod
    def _institutional_terms() -> set[str]:
        return {
            "academico", "aluno", "aula", "biblioteca", "boleto", "bolsa",
            "calendario", "campus", "certificado", "chamada", "coordenacao",
            "curso", "diploma", "disciplina", "documento", "estagio", "faculdade",
            "falta", "frequencia", "horario", "inscricao", "instituicao", "materia",
            "matricula", "mensalidade", "nota", "portal", "professor", "prova",
            "rematricula", "secretaria", "trabalho", "universidade", "vestibular",
            "pagamento", "financeiro", "parcelamento", "comprovante",
        }

    @classmethod
    def _normalize_institutional_query(cls, question: str) -> str:
        """Normalize accents and correct close misspellings of known academic terms."""
        text = cls._normalize_text(question)
        intent_aliases = {
            "me inscrever novamente": "rematricula",
            "inscrever novamente": "rematricula",
            "fazer a inscricao novamente": "rematricula",
            "fazer inscricao novamente": "rematricula",
            "renovar a matricula": "rematricula",
            "renovar matricula": "rematricula",
            "refazer a matricula": "rematricula",
            "refazer matricula": "rematricula",
            "matricular novamente": "rematricula",
            "nova matricula": "rematricula",
        }
        for alias, canonical_term in intent_aliases.items():
            text = text.replace(alias, canonical_term)
        words = text.split()
        institutional_terms = cls._institutional_terms()
        corrected = []
        for word in words:
            if word in institutional_terms or len(word) < 5:
                corrected.append(word)
                continue
            match = difflib.get_close_matches(word, institutional_terms, n=1, cutoff=0.82)
            corrected.append(match[0] if match else word)
        return " ".join(corrected)

    @classmethod
    def _resolve_answer(
        cls,
        question: str,
        context: str,
        found: bool,
        out_of_scope_response: str = OUT_OF_SCOPE_RESPONSE,
        direct_response: str | None = None,
        requires_institutional_context: bool = True,
        conversation_history: str = "",
    ) -> tuple[str, str | None, str]:
        """Refuse deterministically when retrieval produced no approved source."""
        if direct_response is not None:
            return direct_response, None, "respondida"
        if not found:
            return out_of_scope_response, None, "sem_resposta"
        answer, error_detail = cls._generate_answer(question, context, conversation_history)
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
        previous_messages = (
            self.conversations.messages_for_student(conversation.key, student_code)
            if conversation_key is not None
            else []
        )
        conversation_history = self._format_conversation_history(previous_messages)
        retrieval_question = self._contextualize_question(question, previous_messages)
        self.session.add(
            HistoryMessage(
                conversation_key=conversation.key,
                student_code=student_code,
                message_type=1,
                content=question,
                processing_time_ms=None,
            )
        )
        direct_response = self._direct_conversation_response(question)
        normalized_question = self._normalize_institutional_query(retrieval_question)
        requires_institutional_context = self._requires_institutional_context(normalized_question)
        matches = []
        if direct_response is None:
            candidates = self.knowledge.search_with_fallback(
                normalized_question, search_mode
            )
            if retrieval_question.strip() != normalized_question:
                candidates += self.knowledge.search_with_fallback(
                    retrieval_question, search_mode
                )
            by_id: dict[int, tuple[Knowledge, float]] = {}
            for knowledge, relevance in candidates:
                previous = by_id.get(knowledge.id)
                if previous is None or relevance > previous[1]:
                    by_id[knowledge.id] = (knowledge, relevance)
            source_limit = ConfigurationService(self.session).source_limit()
            matches = sorted(
                by_id.values(), key=lambda item: item[1], reverse=True
            )[:source_limit]
            topic_terms = set(normalized_question.split()) & self._institutional_terms()
            requested_details = {
                term for term in ("telefone", "prazo", "endereco")
                if term in normalized_question.split()
            }
            aligned_matches = []
            query_content_terms = {
                term for term in normalized_question.split()
                if len(term) >= 4
                and term not in {
                    "como", "onde", "qual", "quais", "voce", "esta", "estou",
                    "quero", "fazer", "minha", "meu", "para", "sobre", "mais",
                }
            }
            for knowledge, relevance in matches:
                searchable = self._normalize_text(
                    f"{knowledge.title} {knowledge.content}"
                )
                has_topic = not topic_terms or any(
                    term in searchable
                    or (len(term) >= 5 and term[:5] in searchable)
                    for term in topic_terms
                )
                has_requested_detail = not requested_details or all(
                    detail in searchable for detail in requested_details
                )
                has_lexical_evidence = bool(topic_terms) or any(
                    term in searchable
                    or (len(term) >= 5 and term[:5] in searchable)
                    for term in query_content_terms
                )
                if has_topic and has_requested_detail and has_lexical_evidence:
                    aligned_matches.append((knowledge, relevance))
            matches = aligned_matches
        found = bool(matches)
        requires_institutional_context = requires_institutional_context or found
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
            "\n\n".join(knowledge.content for knowledge, _ in matches)
            if found
            else "Nenhum contexto institucional relevante foi encontrado para esta pergunta."
        )
        configuration = ConfigurationService(self.session)
        answer, error_detail, status = self._resolve_answer(
            retrieval_question,
            context,
            found,
            configuration.out_of_scope_message(),
            direct_response,
            requires_institutional_context,
            conversation_history,
        )
        financial_terms = {"pagamento", "financeiro", "parcelamento", "comprovante"}
        if (
            found
            and error_detail is None
            and financial_terms & set(normalized_question.split())
            and "setor responsavel" in self._normalize_text(context)
        ):
            phone = configuration.get("telefone_suporte_whatsapp")
            answer = (
                f"{answer}\n\nPara informações específicas sobre pagamento, "
                f"entre em contato com o suporte pelo WhatsApp: {phone}"
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
