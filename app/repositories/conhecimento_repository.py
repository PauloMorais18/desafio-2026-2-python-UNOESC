"""Full-text search over the institutional knowledge base."""

import re

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.conhecimento import Knowledge


class KnowledgeRepository:
    """Search active knowledge records by Portuguese full-text relevance."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def search(self, question: str, mode: str, limit: int = 3) -> list[tuple[Knowledge, float]]:
        """Return relevant records using the selected search strategy."""
        if mode == "like":
            return self.search_like(question, limit)
        return self.search_full_text(question, limit)

    def search_full_text(self, question: str, limit: int) -> list[tuple[Knowledge, float]]:
        """Search with PostgreSQL Full Text, also used as embeddings fallback."""
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
