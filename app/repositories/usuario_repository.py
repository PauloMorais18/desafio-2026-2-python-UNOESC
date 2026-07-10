"""User repository extension point."""

from app.models.usuario import User


class UserRepository:
    """Encapsulate future persistence operations for users."""

    def get_by_login(self, login: str) -> User | None:
        """Find a user by login after SQLAlchemy session wiring is implemented."""
        # TODO: Query the database through an injected SQLAlchemy session.
        _ = login
        return None

