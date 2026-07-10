"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Header


async def get_authorization_header(
    authorization: Annotated[str | None, Header()] = None,
) -> str | None:
    """Expose the authorization header for future JWT validation."""
    # TODO: Validate the bearer token and provide the authenticated user.
    return authorization

