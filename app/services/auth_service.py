"""Authentication use-case boundary."""


class AuthService:
    """Coordinate future credential validation and JWT issuance."""

    def authenticate(self, login: str, password: str) -> str | None:
        """Return a token after planned user lookup and password verification."""
        # TODO: Use UserRepository, password hashing, and JWT security helpers.
        _ = (login, password)
        return None

