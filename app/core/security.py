"""JWT and password-security extension points."""

from datetime import timedelta


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Placeholder for the future JWT token generation implementation."""
    # TODO: Sign claims with configured algorithm and secret using PyJWT.
    _ = (subject, expires_delta)
    return "mock-access-token"

