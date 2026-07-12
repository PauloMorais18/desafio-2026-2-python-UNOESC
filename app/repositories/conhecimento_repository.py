"""Full-text search over the institutional knowledge base."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.conhecimento import Knowledge


class KnowledgeRepository:
    """Search active knowledge records by Portuguese full-text relevance."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def search(self, question: str, limit: int = 3) -> list[tuple[Knowledge, float]]:
        """Return the most relevant active records for a submitted question."""
        query = func.websearch_to_tsquery("portuguese", question)
        relevance = func.ts_rank_cd(Knowledge.search_document, query).label("relevance")
        statement = (
            select(Knowledge, relevance)
            .where(Knowledge.active.is_(True), Knowledge.search_document.op("@@")(query))
            .order_by(relevance.desc(), Knowledge.id.desc())
            .limit(limit)
        )
        return [(knowledge, float(score)) for knowledge, score in self.session.execute(statement).all()]
