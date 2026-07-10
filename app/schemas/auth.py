"""Authentication API schemas."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credentials submitted to the future authentication workflow."""

    login: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """JWT-shaped response returned after a successful future login."""

    access_token: str
    token_type: str

