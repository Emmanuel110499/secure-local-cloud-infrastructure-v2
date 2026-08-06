from pathlib import Path


class LogService:
    """Lit les journaux exportés en lecture seule."""

    def __init__(self, export_directory: Path):
        self.export_directory = export_directory

        self.allowed_logs = {
            "flask": "flask.log",
            "nginx-access": "nginx-access.log",
            "nginx-error": "nginx-error.log",
            "fail2ban": "fail2ban.log",
        }

    def read_log(
        self,
        log_name: str,
        max_lines: int = 300,
    ) -> list[str]:
        """Retourne les dernières lignes d’un journal autorisé."""

        filename = self.allowed_logs.get(log_name)

        if not filename:
            return ["Journal inconnu."]

        log_path = self.export_directory / filename

        try:
            lines = log_path.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()

            return lines[-max_lines:]

        except OSError:
            return ["Journal temporairement indisponible."]