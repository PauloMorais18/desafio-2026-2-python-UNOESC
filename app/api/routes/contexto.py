"""Knowledge-context upload routes."""

from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import get_current_student

router = APIRouter(prefix="/contexto", tags=["knowledge context"])

DOCUMENTS_DIRECTORY = Path(__file__).resolve().parents[3] / "contexto" / "documentos"
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".doc", ".docx"}


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_context(
    current_student: Annotated[str, Depends(get_current_student)],
    file: Annotated[UploadFile, File(...)],
) -> dict[str, str]:
    """Store a context file for a later knowledge-base ingestion step."""
    original_name = Path(file.filename or "").name
    suffix = Path(original_name).suffix.lower()
    if not original_name or suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Envie um arquivo PDF, TXT, MD, DOC ou DOCX.")

    DOCUMENTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = DOCUMENTS_DIRECTORY / f"{uuid4().hex}{suffix}"
    destination.write_bytes(await file.read())
    await file.close()
    return {"arquivo": original_name, "armazenado_em": str(destination), "enviado_por": current_student}
