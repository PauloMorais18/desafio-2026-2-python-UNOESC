"""Generate and persist semantic vectors with the local Ollama server."""

from __future__ import annotations

from math import sqrt

from langchain_ollama import OllamaEmbeddings
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.conhecimento import Knowledge


class EmbeddingUnavailableError(RuntimeError):
    """Raised when the configured embedding model cannot be reached."""


class EmbeddingService:
    """Provide embedding generation independently from question generation."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = OllamaEmbeddings(
            model=settings.embedding_model_name,
            base_url=settings.ollama_url,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate one vector for each knowledge chunk."""
        try:
            vectors = self.client.embed_documents(texts)
        except Exception as exc:
            raise EmbeddingUnavailableError(
                "Não foi possível gerar embeddings. Verifique o Ollama e o modelo configurado."
            ) from exc
        if len(vectors) != len(texts) or any(not vector for vector in vectors):
            raise EmbeddingUnavailableError("O modelo de embeddings retornou vetores inválidos.")
        return [[float(value) for value in vector] for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        """Generate the semantic vector used to search a question."""
        try:
            vector = self.client.embed_query(text)
        except Exception as exc:
            raise EmbeddingUnavailableError(
                "A busca por embeddings está indisponível. Verifique o Ollama e o modelo configurado."
            ) from exc
        if not vector:
            raise EmbeddingUnavailableError("O modelo de embeddings retornou um vetor vazio.")
        return [float(value) for value in vector]

    def populate_missing(self, session: Session) -> int:
        """Generate vectors for active knowledge records that do not have one."""
        records = list(session.scalars(
            select(Knowledge).where(Knowledge.active.is_(True), Knowledge.embedding.is_(None))
        ))
        if not records:
            return 0
        vectors = self.embed_documents([record.content for record in records])
        for record, vector in zip(records, vectors, strict=True):
            record.embedding = vector
        session.commit()
        return len(records)


def cosine_similarity(first: list[float], second: list[float]) -> float:
    """Calculate cosine similarity between vectors of the same dimension."""
    if not first or len(first) != len(second):
        return 0.0
    first_norm = sqrt(sum(value * value for value in first))
    second_norm = sqrt(sum(value * value for value in second))
    if first_norm == 0 or second_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(first, second, strict=True)) / (first_norm * second_norm)
