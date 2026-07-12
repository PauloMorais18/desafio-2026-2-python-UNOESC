"""Authentication API schemas."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    """Credentials used to authenticate a registered student."""

    model_config = ConfigDict(populate_by_name=True)

    student_code: str = Field(alias="codigoAluno", min_length=1, max_length=50)
    password: str = Field(alias="senha", min_length=1, max_length=128)

    @field_validator("student_code", mode="before")
    @classmethod
    def normalize_student_code(cls, value: str | int) -> str:
        """Accept the numeric format presented in the project specification."""
        return str(value)


class TokenResponse(BaseModel):
    """JWT-shaped response returned after a successful future login."""

    access_token: str
    token_type: str


class RegisterRequest(BaseModel):
    """Minimal self-registration payload for a student account."""

    model_config = ConfigDict(populate_by_name=True)

    student_code: str = Field(alias="codigoAluno", min_length=1, max_length=50)
    password: str = Field(alias="senha", min_length=8, max_length=128)
    password_confirmation: str = Field(alias="confirmacaoSenha", min_length=8, max_length=128)

    @field_validator("student_code", mode="before")
    @classmethod
    def normalize_student_code(cls, value: str | int) -> str:
        return str(value)
