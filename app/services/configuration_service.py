"""Read and validate global options stored in the database."""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.configuracao import ApplicationSetting

DEFAULT_SETTINGS = {
    "telefone_suporte_whatsapp": "554935512034",
    "mensagem_fora_escopo": (
        "Não encontrei informações sobre esse assunto na base de conhecimento institucional. "
        "Entre em contato com o suporte pelo WhatsApp: {telefone}"
    ),
    "similaridade_minima_embeddings": "0.65",
    "limite_fontes": "3",
}


class ConfigurationService:
    """Provide typed access to the application configuration table."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def all(self) -> dict[str, str]:
        """Return every supported option, completed with safe defaults."""
        values = dict(DEFAULT_SETTINGS)
        rows = self.session.execute(
            select(ApplicationSetting.key, ApplicationSetting.value).where(
                ApplicationSetting.key.in_(DEFAULT_SETTINGS)
            )
        ).all()
        values.update({key: value for key, value in rows})
        return values

    def get(self, key: str) -> str:
        """Return one option or its application default."""
        value = self.session.scalar(
            select(ApplicationSetting.value).where(ApplicationSetting.key == key)
        )
        return value if value is not None else DEFAULT_SETTINGS[key]

    def update(self, values: dict[str, str]) -> dict[str, str]:
        """Validate and persist the supported editable options."""
        validated = self._validate(values)
        existing = {
            row.key: row
            for row in self.session.scalars(
                select(ApplicationSetting).where(ApplicationSetting.key.in_(validated))
            )
        }
        descriptions = {
            "telefone_suporte_whatsapp": "Número do suporte com código do país e DDD",
            "mensagem_fora_escopo": "Mensagem usada quando não existe fonte confiável",
            "similaridade_minima_embeddings": "Similaridade mínima aceita entre 0 e 1",
            "limite_fontes": "Quantidade máxima de fontes enviadas ao modelo",
        }
        for key, value in validated.items():
            if key in existing:
                existing[key].value = value
            else:
                self.session.add(ApplicationSetting(
                    key=key, value=value, description=descriptions[key]
                ))
        self.session.commit()
        return self.all()

    @staticmethod
    def _validate(values: dict[str, str]) -> dict[str, str]:
        unknown = set(values) - set(DEFAULT_SETTINGS)
        if unknown:
            raise ValueError(f"Configuração não permitida: {', '.join(sorted(unknown))}")
        validated = {key: str(value).strip() for key, value in values.items()}
        phone = validated.get("telefone_suporte_whatsapp")
        if phone is not None and not re.fullmatch(r"\d{10,15}", phone):
            raise ValueError("O telefone deve conter somente país, DDD e número, com 10 a 15 dígitos.")
        message = validated.get("mensagem_fora_escopo")
        if message is not None and (not message or len(message) > 500):
            raise ValueError("A mensagem deve possuir entre 1 e 500 caracteres.")
        similarity = validated.get("similaridade_minima_embeddings")
        if similarity is not None:
            try:
                numeric_similarity = float(similarity)
            except ValueError as exc:
                raise ValueError("A similaridade mínima deve ser numérica.") from exc
            if not 0 <= numeric_similarity <= 1:
                raise ValueError("A similaridade mínima deve ficar entre 0 e 1.")
            validated["similaridade_minima_embeddings"] = str(numeric_similarity)
        source_limit = validated.get("limite_fontes")
        if source_limit is not None:
            try:
                numeric_limit = int(source_limit)
            except ValueError as exc:
                raise ValueError("O limite de fontes deve ser um número inteiro.") from exc
            if not 1 <= numeric_limit <= 10:
                raise ValueError("O limite de fontes deve ficar entre 1 e 10.")
            validated["limite_fontes"] = str(numeric_limit)
        return validated

    def out_of_scope_message(self) -> str:
        """Build the refusal guidance with the configured support phone."""
        phone = self.get("telefone_suporte_whatsapp")
        template = self.get("mensagem_fora_escopo")
        return template.replace("{telefone}", phone)

    def minimum_similarity(self) -> float:
        return float(self.get("similaridade_minima_embeddings"))

    def source_limit(self) -> int:
        return int(self.get("limite_fontes"))
