"""Retrieval-augmented generation orchestration boundary."""


def build_rag_context(query: str) -> str:
    """Build contextual input for an LLM after retrieval is implemented."""
    # TODO: Combine retrieved chunks with prompt templates and source metadata.
    _ = query
    return ""

