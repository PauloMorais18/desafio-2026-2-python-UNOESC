"""Answer API schemas."""

from pydantic import BaseModel


class AnswerResponse(BaseModel):
    """Output produced by the future RAG and LLM answer workflow."""

    answer: str
    found: bool
    processing_time_ms: int

