"""Authenticated runtime-configuration routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_student
from app.core.database import get_db_session
from app.schemas.configuracao import ConfigurationResponse, ConfigurationUpdate
from app.services.configuration_service import ConfigurationService

router = APIRouter(prefix="/configuracoes", tags=["Configurações"])


def _response(values: dict[str, str]) -> ConfigurationResponse:
    return ConfigurationResponse(
        telefoneSuporteWhatsapp=values["telefone_suporte_whatsapp"],
        mensagemForaEscopo=values["mensagem_fora_escopo"],
        similaridadeMinimaEmbeddings=float(values["similaridade_minima_embeddings"]),
        limiteFontes=int(values["limite_fontes"]),
    )


@router.get(
    "",
    response_model=ConfigurationResponse,
    summary="Consultar configurações do assistente",
)
def get_configuration(
    _: Annotated[str, Depends(get_current_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> ConfigurationResponse:
    """Retorna suporte, mensagem de recusa, similaridade e limite de fontes."""
    return _response(ConfigurationService(session).all())


@router.put(
    "",
    response_model=ConfigurationResponse,
    summary="Atualizar configurações do assistente",
)
def update_configuration(
    payload: ConfigurationUpdate,
    _: Annotated[str, Depends(get_current_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> ConfigurationResponse:
    """Valida e salva as configurações gerais utilizadas pelo atendimento."""
    try:
        values = ConfigurationService(session).update({
            "telefone_suporte_whatsapp": payload.support_phone,
            "mensagem_fora_escopo": payload.out_of_scope_message,
            "similaridade_minima_embeddings": str(payload.embedding_min_similarity),
            "limite_fontes": str(payload.source_limit),
        })
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return _response(values)
