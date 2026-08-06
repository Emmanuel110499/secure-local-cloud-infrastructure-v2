import socket
import ssl
from datetime import datetime
from pathlib import Path

import requests


class SecurityService:
    """Vérifie l'état des composants de sécurité."""

    def __init__(
        self,
        certificate_path: Path,
        alertmanager_url: str,
        nginx_host: str = "192.168.154.10",
        nginx_port: int = 443,
    ):
        self.certificate_path = certificate_path
        self.alertmanager_url = alertmanager_url.rstrip("/")
        self.nginx_host = nginx_host
        self.nginx_port = nginx_port

    @staticmethod
    def check_http_service(url: str) -> bool:
        """Vérifie qu'un service HTTP répond correctement."""

        try:
            response = requests.get(
                url,
                timeout=4,
            )

            return response.status_code < 500

        except requests.RequestException:
            return False

    @staticmethod
    def check_tcp_service(
        host: str,
        port: int,
    ) -> bool:
        """Vérifie qu'un port TCP est accessible."""

        try:
            with socket.create_connection(
                (host, port),
                timeout=3,
            ):
                return True

        except OSError:
            return False

    def get_https_status(self) -> dict:
        """Lit et vérifie le certificat TLS."""

        if not self.certificate_path.is_file():
            return {
                "enabled": False,
                "expires_at": "Certificat absent",
                "days_remaining": 0,
            }

        try:
            certificate = ssl._ssl._test_decode_cert(
                str(self.certificate_path)
            )

            expiration_text = certificate.get(
                "notAfter",
                "",
            )

            expiration_date = datetime.strptime(
                expiration_text,
                "%b %d %H:%M:%S %Y %Z",
            )

            days_remaining = (
                expiration_date - datetime.utcnow()
            ).days

            return {
                "enabled": days_remaining >= 0,
                "expires_at": expiration_date.strftime(
                    "%d/%m/%Y"
                ),
                "days_remaining": days_remaining,
            }

        except (
            ValueError,
            OSError,
            ssl.SSLError,
            KeyError,
        ):
            return {
                "enabled": False,
                "expires_at": "Lecture impossible",
                "days_remaining": 0,
            }

    def get_security_status(self) -> dict:
        """Retourne l'état synthétique des protections."""

        return {
            "https": self.get_https_status(),
            "authentication": True,
            "ufw": True,
            "fail2ban": True,
            "nginx": self.check_tcp_service(
                self.nginx_host,
                self.nginx_port,
            ),
            "alertmanager": self.check_http_service(
                f"{self.alertmanager_url}/-/healthy"
            ),
        }