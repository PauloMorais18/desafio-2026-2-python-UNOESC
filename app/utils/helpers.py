"""General helper extension points."""


def normalize_text(value: str) -> str:
    """Normalize text according to future domain-specific conventions."""
    # TODO: Define normalization rules required by the knowledge ingestion pipeline.
    return value.strip()

