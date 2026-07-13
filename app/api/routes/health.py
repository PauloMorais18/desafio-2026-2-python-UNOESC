"""Health-check route."""

from fastapi import APIRouter, status

router = APIRouter(tags=["Saúde da API"])


@router.get("/health", status_code=status.HTTP_200_OK, summary="Verificar saúde da API")
async def health_check() -> dict[str, str]:
    """Retorna o status básico da API enquanto verificações de dependências não são adicionadas."""
    # TODO: Check database, vector store, and local LLM availability.
    return {"status": "ok"}
