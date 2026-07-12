"""Create a local student account for API authentication tests."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.usuario import User
from app.repositories.usuario_repository import UserRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a student for local API tests.")
    parser.add_argument("--codigo", required=True, help="Institutional student code.")
    parser.add_argument("--nome", required=True, help="Student full name.")
    parser.add_argument("--login", required=True, help="Unique application login.")
    parser.add_argument("--senha", required=True, help="Plain password; only its hash is stored.")
    parser.add_argument("--email", default=None, help="Optional unique email address.")
    arguments = parser.parse_args()

    with SessionLocal() as session:
        users = UserRepository(session)
        if users.get_by_student_code(arguments.codigo) is not None:
            raise SystemExit(f"Já existe um aluno com o código {arguments.codigo}.")

        user = User(
            student_code=arguments.codigo,
            name=arguments.nome,
            login=arguments.login,
            email=arguments.email,
            password_hash=hash_password(arguments.senha),
            active=True,
        )
        session.add(user)
        session.commit()

    print(f"Aluno {arguments.codigo} criado com sucesso.")


if __name__ == "__main__":
    main()
