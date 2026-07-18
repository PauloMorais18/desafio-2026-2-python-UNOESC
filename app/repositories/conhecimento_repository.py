"""Full-text search over the institutional knowledge base."""

import re
import unicodedata
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.conhecimento import Knowledge
from app.services.embedding_service import EmbeddingService, cosine_similarity
from app.services.embedding_service import EmbeddingUnavailableError
from app.services.configuration_service import ConfigurationService


class KnowledgeRepository:
    """Search active knowledge records by Portuguese full-text relevance."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def search(self, question: str, mode: str, limit: int | None = None) -> list[tuple[Knowledge, float]]:
        """Return relevant records using the selected search strategy."""
        limit = limit or ConfigurationService(self.session).source_limit()
        if mode == "like":
            return self._semantic_gate(
                question, self.search_like(question, limit), allow_strong_textual_match=True
            )
        if mode == "embeddings":
            return self.search_embeddings(question, limit)
        return self._semantic_gate(question, self.search_full_text(question, limit))

    def search_with_fallback(
        self, question: str, preferred_mode: str, limit: int | None = None
    ) -> list[tuple[Knowledge, float]]:
        """Try the selected strategy first and complement it with the other modes."""
        limit = limit or ConfigurationService(self.session).source_limit()
        modes = [preferred_mode] + [
            mode for mode in ("like", "full_text", "embeddings") if mode != preferred_mode
        ]
        collected: dict[int, tuple[Knowledge, float]] = {}
        for mode in modes:
            try:
                matches = self.search(question, mode, limit)
            except EmbeddingUnavailableError:
                continue
            for record, score in matches:
                previous = collected.get(record.id)
                if previous is None or score > previous[1]:
                    collected[record.id] = (record, score)
        return sorted(collected.values(), key=lambda item: item[1], reverse=True)[:limit]

    def _semantic_gate(
        self,
        question: str,
        matches: list[tuple[Knowledge, float]],
        allow_strong_textual_match: bool = False,
    ) -> list[tuple[Knowledge, float]]:
        """Allow textual matches only when their semantic relevance is sufficient."""
        if not matches:
            return []
        if allow_strong_textual_match:
            strong_matches = [
                (record, textual_score)
                for record, textual_score in matches
                if textual_score >= 0.8
            ]
            if strong_matches:
                return sorted(strong_matches, key=lambda item: item[1], reverse=True)
        minimum_similarity = ConfigurationService(self.session).minimum_similarity()
        question_vector = EmbeddingService().embed_query(question)
        approved = []
        for record, textual_score in matches:
            semantic_score = cosine_similarity(question_vector, record.embedding or [])
            if semantic_score >= minimum_similarity:
                approved.append((record, semantic_score))
        return sorted(
            approved,
            key=lambda item: item[1],
            reverse=True,
        )

    def search_full_text(self, question: str, limit: int) -> list[tuple[Knowledge, float]]:
        """Search with PostgreSQL Full Text."""
        query = func.websearch_to_tsquery("portuguese", question)
        relevance = func.ts_rank_cd(Knowledge.search_document, query).label("relevance")
        statement = (
            select(Knowledge, relevance)
            .where(Knowledge.active.is_(True), Knowledge.search_document.op("@@")(query))
            .order_by(relevance.desc(), Knowledge.id.desc())
            .limit(limit)
        )
        return [(knowledge, float(score)) for knowledge, score in self.session.execute(statement).all()]

    def search_like(self, question: str, limit: int) -> list[tuple[Knowledge, float]]:
        """Search title and content with case-insensitive LIKE terms."""
        ignored_terms = {
            "como", "faco", "faço", "onde", "qual", "quais", "para", "sobre",
            "uma", "meu", "minha", "quero", "fazer", "posso", "preciso",
            "gostaria", "novamente", "detalhe", "detalhes", "detalhado",
            "detalhada", "detalhar", "melhor", "consegue", "continuar",
            "continuacao", "aluno",
        }
        terms = [
            self._remove_accents(term.lower())
            for term in re.findall(r"[A-Za-zÀ-ÿ0-9]+", question)
            if len(term) >= 4 and term.lower() not in ignored_terms
        ]
        if not terms:
            terms = [question]
        source_characters = "áàâãäéèêëíìîïóòôõöúùûüç"
        target_characters = "aaaaaeeeeiiiiooooouuuuc"
        normalized_title = func.translate(func.lower(Knowledge.title), source_characters, target_characters)
        normalized_content = func.translate(func.lower(Knowledge.content), source_characters, target_characters)
        conditions = [or_(normalized_title.contains(term), normalized_content.contains(term)) for term in terms]
        statement = (
            select(Knowledge)
            .where(Knowledge.active.is_(True), or_(*conditions))
            .order_by(Knowledge.id.desc())
            .limit(limit)
        )
        results = []
        for knowledge in self.session.scalars(statement).all():
            searchable = self._remove_accents(f"{knowledge.title} {knowledge.content}".lower())
            matched_terms = sum(searchable.count(term) for term in terms)
            textual_score = 1 - (0.2 ** matched_terms) if matched_terms else 0.0
            results.append((knowledge, textual_score))
        results.sort(key=lambda item: item[1], reverse=True)
        return results

    @staticmethod
    def _remove_accents(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        return "".join(character for character in normalized if not unicodedata.combining(character))

    def search_embeddings(self, question: str, limit: int) -> list[tuple[Knowledge, float]]:
        """Rank active knowledge chunks by semantic cosine similarity."""
        minimum_similarity = ConfigurationService(self.session).minimum_similarity()
        question_vector = EmbeddingService().embed_query(question)
        records = list(self.session.scalars(
            select(Knowledge).where(
                Knowledge.active.is_(True), Knowledge.embedding.is_not(None)
            )
        ))
        ranked = sorted(
            ((record, cosine_similarity(question_vector, record.embedding or [])) for record in records),
            key=lambda item: item[1],
            reverse=True,
        )
        return [
            (record, score)
            for record, score in ranked[:limit]
            if score >= minimum_similarity
        ]
