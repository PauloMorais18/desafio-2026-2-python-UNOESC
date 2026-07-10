"""Authentication routes."""

from fastapi import APIRouter, status

from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(tags=["authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest) -> TokenResponse:
    """Return a mock token; credential verification will be added later."""
    # TODO: Delegate authentication to AuthService and issue a JWT.
    _ = payload
    return TokenResponse(access_token="mock-access-token", token_type="bearer")

