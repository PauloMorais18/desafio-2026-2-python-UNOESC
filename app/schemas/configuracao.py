"""Schemas for runtime application settings."""

from pydantic import BaseModel, ConfigDict, Field


class ConfigurationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    support_phone: str = Field(alias="telefoneSuporteWhatsapp")
    out_of_scope_message: str = Field(alias="mensagemForaEscopo")
    embedding_min_similarity: float = Field(alias="similaridadeMinimaEmbeddings")
    source_limit: int = Field(alias="limiteFontes")


class ConfigurationUpdate(ConfigurationResponse):
    pass
