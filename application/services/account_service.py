from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Any
import json
import os

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)


class AccountService:
    """Gère les identifiants administrateur de façon persistante."""

    def __init__(
        self,
        credentials_path: str | Path,
        default_username: str,
        default_password: str = "",
        default_password_hash: str = "",
    ) -> None:
        self.credentials_path = Path(credentials_path)
        self._lock = Lock()

        self.credentials_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.credentials_path.exists():
            password_hash = default_password_hash

            if not password_hash and default_password:
                password_hash = generate_password_hash(
                    default_password
                )

            self._write({
                "username": default_username,
                "password_hash": password_hash,
            })

    def _read(self) -> dict[str, Any]:
        try:
            payload = json.loads(
                self.credentials_path.read_text(
                    encoding="utf-8"
                )
            )

            return payload if isinstance(payload, dict) else {}
        except (
            OSError,
            json.JSONDecodeError,
        ):
            return {}

    def _write(self, payload: dict[str, Any]) -> None:
        temporary = self.credentials_path.with_suffix(
            ".tmp"
        )

        temporary.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        temporary.replace(self.credentials_path)

        try:
            os.chmod(self.credentials_path, 0o600)
        except OSError:
            pass

    def get_username(self) -> str:
        return str(
            self._read().get("username", "")
        ).strip()

    def verify_password(self, password: str) -> bool:
        password_hash = str(
            self._read().get("password_hash", "")
        )

        if not password_hash:
            return False

        try:
            return check_password_hash(
                password_hash,
                password,
            )
        except ValueError:
            return False

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> bool:
        return (
            username == self.get_username()
            and self.verify_password(password)
        )

    def update_username(
        self,
        new_username: str,
    ) -> None:
        new_username = new_username.strip()

        if len(new_username) < 3:
            raise ValueError(
                "L’identifiant doit contenir au moins 3 caractères."
            )

        with self._lock:
            payload = self._read()
            payload["username"] = new_username
            self._write(payload)

    def update_password(
        self,
        new_password: str,
    ) -> None:
        if len(new_password) < 8:
            raise ValueError(
                "Le mot de passe doit contenir au moins 8 caractères."
            )

        with self._lock:
            payload = self._read()
            payload["password_hash"] = generate_password_hash(
                new_password
            )
            self._write(payload)
