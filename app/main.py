"""FastAPI application entry point."""

from contextlib import asynccontextmanager
import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, configuracoes, contexto, conversas, estatisticas, health, perguntar
from app.api.dependencies import get_current_student
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.document_ingestion_service import DocumentIngestionError, DocumentIngestionService
from app.services.embedding_service import EmbeddingService, EmbeddingUnavailableError

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Make bundled context documents searchable when the API starts."""
    with SessionLocal() as session:
        try:
            indexed = DocumentIngestionService(session).index_missing(
                contexto.DOCUMENTS_DIRECTORY,
                contexto.ALLOWED_EXTENSIONS,
            )
            for document_name, chunk_count in indexed.items():
                logger.info(
                    "Documento inicial indexado: %s (%s trechos)",
                    document_name,
                    chunk_count,
                )
            embedded = EmbeddingService().populate_missing(session)
            if embedded:
                logger.info("Embeddings gerados para %s registros da base.", embedded)
        except EmbeddingUnavailableError as exc:
            session.rollback()
            logger.warning("Embeddings iniciais não gerados: %s", exc)
        except DocumentIngestionError as exc:
            session.rollback()
            logger.warning("Documento inicial não indexado: %s", exc)
        except Exception:
            session.rollback()
            logger.exception(
                "Não foi possível verificar a base inicial de documentos. "
                "Confirme se a estrutura do banco está atualizada."
            )
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Login e cadastro são públicos para permitir a obtenção do primeiro token JWT.
app.include_router(health.router, dependencies=[Depends(get_current_student)])
app.include_router(auth.router)
app.include_router(configuracoes.router)
app.include_router(contexto.router)
app.include_router(perguntar.router)
app.include_router(conversas.router)
app.include_router(estatisticas.router, dependencies=[Depends(get_current_student)])
