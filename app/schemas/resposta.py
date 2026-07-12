"""Answer API schemas."""

from pydantic import BaseModel, Field


class KnowledgeSourceResponse(BaseModel):
    """Knowledge record used in a response."""

    id: int
    title: str
    category: str
    relevance: float


class AnswerResponse(BaseModel):
    """Output produced by the future RAG and LLM answer workflow."""

    answer: str
    found: bool
    processing_time_ms: int
    sources: list[KnowledgeSourceResponse] = Field(default_factory=list)
