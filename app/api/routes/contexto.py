"""Knowledge-context upload, indexing, and management routes."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_student
from app.core.database import get_db_session
from app.services.document_ingestion_service import DocumentIngestionError, DocumentIngestionService

router = APIRouter(prefix="/contexto", tags=["Contexto de conhecimento"])

DOCUMENTS_DIRECTORY = Path(__file__).resolve().parents[3] / "contexto" / "documentos"
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}


def get_document_path(document_id: str) -> Path:
    """Return a safe path inside the context-documents directory."""
    candidate = (DOCUMENTS_DIRECTORY / Path(document_id).name).resolve()
    if candidate.parent != DOCUMENTS_DIRECTORY.resolve() or not candidate.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado.")
    return candidate


@router.get("/documentos", summary="Listar documentos de contexto")
async def list_documents(
    _: Annotated[str, Depends(get_current_student)],
) -> dict[str, list[dict[str, str | int]]]:
    """List files available as institutional context."""
    DOCUMENTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    documents = [
        {
            "id": path.name,
            "nome": path.name,
            "tamanho": path.stat().st_size,
            "enviadoEm": path.stat().st_mtime_ns,
        }
        for path in sorted(DOCUMENTS_DIRECTORY.iterdir(), key=lambda item: item.stat().st_mtime, reverse=True)
        if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS
    ]
    return {"documentos": documents}


@router.get("/documentos/{document_id}", summary="Visualizar documento de contexto")
async def view_document(
    document_id: str,
    _: Annotated[str, Depends(get_current_student)],
) -> FileResponse:
    """Return an uploaded document for authenticated viewing."""
    path = get_document_path(document_id)
    return FileResponse(path, filename=path.name, content_disposition_type="inline")


@router.delete(
    "/documentos/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir documento de contexto",
)
async def delete_document(
    document_id: str,
    _: Annotated[str, Depends(get_current_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> None:
    """Delete a file and deactivate all knowledge chunks that came from it."""
    path = get_document_path(document_id)
    DocumentIngestionService(session).deactivate(path.name)
    path.unlink()


@router.post("/upload", status_code=status.HTTP_201_CREATED, summary="Enviar documento de contexto")
async def upload_context(
    current_student: Annotated[str, Depends(get_current_student)],
    file: Annotated[UploadFile, File(...)],
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, str | int]:
    """Store a context file and immediately index its text for assistant retrieval."""
    original_name = Path(file.filename or "").name
    suffix = Path(original_name).suffix.lower()
    if not original_name or suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Envie um arquivo PDF, TXT, MD ou DOCX.",
        )

    DOCUMENTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = DOCUMENTS_DIRECTORY / original_name
    if destination.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um documento com esse nome. Renomeie o arquivo antes de enviá-lo.",
        )

    destination.write_bytes(await file.read())
    await file.close()
    try:
        chunks = DocumentIngestionService(session).index(destination)
    except DocumentIngestionError as exc:
        session.rollback()
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception:
        session.rollback()
        destination.unlink(missing_ok=True)
        raise

    return {
        "arquivo": original_name,
        "armazenado_em": str(destination),
        "enviado_por": current_student,
        "trechos_indexados": chunks,
    }


@router.post("/reindexar", summary="Reindexar documentos de contexto")
async def reindex_documents(
    _: Annotated[str, Depends(get_current_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, object]:
    """Index supported files already present in the context directory."""
    DOCUMENTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    service = DocumentIngestionService(session)
    indexed: list[dict[str, str | int]] = []
    errors: list[dict[str, str]] = []
    for path in sorted(DOCUMENTS_DIRECTORY.iterdir()):
        if not path.is_file() or path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        try:
            indexed.append({"arquivo": path.name, "trechos_indexados": service.index(path)})
        except DocumentIngestionError as exc:
            session.rollback()
            errors.append({"arquivo": path.name, "erro": str(exc)})
    return {"documentos_indexados": indexed, "erros": errors}
