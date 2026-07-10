"""Statistics API schemas."""

from pydantic import BaseModel


class StatisticsResponse(BaseModel):
    """Aggregate metrics to be computed from future question logs."""

    total_questions: int
    answered_questions: int
    average_processing_time_ms: float

