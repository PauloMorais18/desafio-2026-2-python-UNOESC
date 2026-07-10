"""Statistics routes."""

from fastapi import APIRouter, status

from app.schemas.estatisticas import StatisticsResponse

router = APIRouter(tags=["statistics"])


@router.get("/estatisticas", response_model=StatisticsResponse, status_code=status.HTTP_200_OK)
async def get_statistics() -> StatisticsResponse:
    """Return placeholder aggregate values until reporting is implemented."""
    # TODO: Obtain aggregated metrics from StatisticsService.
    return StatisticsResponse(total_questions=0, answered_questions=0, average_processing_time_ms=0.0)

