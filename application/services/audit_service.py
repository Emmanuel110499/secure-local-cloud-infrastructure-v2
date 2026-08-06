import json
from datetime import datetime
from pathlib import Path
from typing import Any


class AuditService:
    """Enregistre et lit l'historique des actions administratives."""

    def __init__(self, audit_file: Path):
        self.audit_file = audit_file
        self.audit_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def record_action(
        self,
        user: str,
        resource: str,
        action: str,
        success: bool,
        details: str = "",
    ) -> None:
        """Ajoute une action au journal d'audit."""

        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "resource": resource,
            "action": action,
            "success": success,
            "details": details,
        }

        try:
            with self.audit_file.open(
                "a",
                encoding="utf-8",
            ) as file:
                file.write(
                    json.dumps(
                        entry,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        except OSError:
            pass

    def list_actions(
        self,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        """Retourne les actions les plus récentes."""

        if not self.audit_file.is_file():
            return []

        actions = []

        try:
            lines = self.audit_file.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()

            for line in lines[-limit:]:
                try:
                    actions.append(
                        json.loads(line)
                    )
                except json.JSONDecodeError:
                    continue

        except OSError:
            return []

        actions.reverse()

        return actions