"""Knowledge-context upload routes."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.api.dependencies import get_current_student

router = APIRouter(prefix="/contexto", tags=["Contexto de conhecimento"])

DOCUMENTS_DIRECTORY = Path(__file__).resolve().parents[3] / "contexto" / "documentos"
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".doc", ".docx"}


def get_document_path(document_id: str) -> Path:
    """Return a safe path inside the context-documents directory."""
    candidate = (DOCUMENTS_DIRECTORY / Path(document_id).name).resolve()
    if candidate.parent != DOCUMENTS_DIRECTORY.resolve() or not candidate.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado.")
    return candidate


def public_name(path: Path) -> str:
    """Expose exactly the filename stored in the context directory."""
    return path.name


@router.get("/documentos", summary="Listar documentos de contexto")
async def list_documents(
    _: Annotated[str, Depends(get_current_student)],
) -> dict[str, list[dict[str, str | int]]]:
    """Lista os arquivos de contexto armazenados para a base de conhecimento."""
    DOCUMENTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    documents = [
        {
            "id": path.name,
            "nome": public_name(path),
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
    """Retorna um documento enviado para visualização pelo usuário autenticado."""
    path = get_document_path(document_id)
    return FileResponse(path, filename=public_name(path), content_disposition_type="inline")


@router.delete("/documentos/{document_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir documento de contexto")
async def delete_document(
    document_id: str,
    _: Annotated[str, Depends(get_current_student)],
) -> None:
    """Exclui um documento de contexto que não é mais necessário."""
    get_document_path(document_id).unlink()


@router.post("/upload", status_code=status.HTTP_201_CREATED, summary="Enviar documento de contexto")
async def upload_context(
    current_student: Annotated[str, Depends(get_current_student)],
    file: Annotated[UploadFile, File(...)],
) -> dict[str, str]:
    """Armazena um arquivo de contexto para uso posterior na base de conhecimento."""
    original_name = Path(file.filename or "").name
    suffix = Path(original_name).suffix.lower()
    if not original_name or suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Envie um arquivo PDF, TXT, MD, DOC ou DOCX.")

    DOCUMENTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = DOCUMENTS_DIRECTORY / original_name
    if destination.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um documento com esse nome. Renomeie o arquivo antes de enviá-lo.",
        )
    destination.write_bytes(await file.read())
    await file.close()
    return {"arquivo": original_name, "armazenado_em": str(destination), "enviado_por": current_student}
