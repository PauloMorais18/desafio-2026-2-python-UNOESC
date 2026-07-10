"""Question-answering routes."""

from fastapi import APIRouter, status

from app.schemas.pergunta import QuestionRequest
from app.schemas.resposta import AnswerResponse

router = APIRouter(tags=["questions"])


@router.post("/perguntar", response_model=AnswerResponse, status_code=status.HTTP_200_OK)
async def ask_question(payload: QuestionRequest) -> AnswerResponse:
    """Return a mock answer until the retrieval and LLM workflow exists."""
    # TODO: Call QuestionService, including RAG retrieval and audit logging.
    return AnswerResponse(answer=f"Mock response for: {payload.question}", found=False, processing_time_ms=0)

