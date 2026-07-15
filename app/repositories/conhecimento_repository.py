"""Full-text search over the institutional knowledge base."""

import re

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.conhecimento import Knowledge
from app.services.embedding_service import EmbeddingService, cosine_similarity
from app.services.configuration_service import ConfigurationService


class KnowledgeRepository:
    """Search active knowledge records by Portuguese full-text relevance."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def search(self, question: str, mode: str, limit: int | None = None) -> list[tuple[Knowledge, float]]:
        """Return relevant records using the selected search strategy."""
        limit = limit or ConfigurationService(self.session).source_limit()
        if mode == "like":
            return self._semantic_gate(question, self.search_like(question, limit))
        if mode == "embeddings":
            return self.search_embeddings(question, limit)
        return self._semantic_gate(question, self.search_full_text(question, limit))

    def _semantic_gate(
        self,
        question: str,
        matches: list[tuple[Knowledge, float]],
    ) -> list[tuple[Knowledge, float]]:
        """Allow textual matches only when their semantic relevance is sufficient."""
        if not matches:
            return []
        minimum_similarity = ConfigurationService(self.session).minimum_similarity()
        question_vector = EmbeddingService().embed_query(question)
        approved = [
            (record, cosine_similarity(question_vector, record.embedding or []))
            for record, _ in matches
            if record.embedding
        ]
        return sorted(
            (
                (record, score)
                for record, score in approved
                if score >= minimum_similarity
            ),
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
        terms = [term for term in re.findall(r"[A-Za-zÀ-ÿ0-9]+", question) if len(term) >= 4]
        if not terms:
            terms = [question]
        conditions = [
            or_(Knowledge.title.ilike(f"%{term}%"), Knowledge.content.ilike(f"%{term}%"))
            for term in terms
        ]
        statement = (
            select(Knowledge)
            .where(Knowledge.active.is_(True), or_(*conditions))
            .order_by(Knowledge.id.desc())
            .limit(limit)
        )
        return [(knowledge, 1.0) for knowledge in self.session.scalars(statement).all()]

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
