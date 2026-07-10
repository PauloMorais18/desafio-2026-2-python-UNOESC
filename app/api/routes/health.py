"""Health-check route."""

from fastapi import APIRouter, status

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Return a mock health status until dependency checks are implemented."""
    # TODO: Check database, vector store, and local LLM availability.
    return {"status": "ok"}

