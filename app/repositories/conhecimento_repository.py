"""Knowledge repository extension point."""

from app.models.conhecimento import Knowledge


class KnowledgeRepository:
    """Encapsulate future retrieval operations for knowledge records."""

    def search(self, query: str) -> list[Knowledge]:
        """Return matching records after text/vector search is implemented."""
        # TODO: Integrate PostgreSQL and a future vector store search strategy.
        _ = query
        return []

