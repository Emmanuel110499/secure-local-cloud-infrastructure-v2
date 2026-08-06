import os
from pathlib import Path


class Config:
    """Configuration générale de l'application."""

    SECRET_KEY = os.getenv("SECRET_KEY")

    ADMIN_USERNAME = os.getenv(
        "ADMIN_USERNAME",
        "emmanuel",
    )

    ADMIN_PASSWORD = os.getenv(
        "ADMIN_PASSWORD",
        "",
    )

    AUDIT_FILE = Path(
        os.getenv(
            "AUDIT_FILE",
            "/app/data/audit.jsonl",
        )
    )

    ADMIN_PASSWORD_HASH = os.getenv(
        "ADMIN_PASSWORD_HASH",
        "",
    )

    PROMETHEUS_URL = os.getenv(
        "PROMETHEUS_URL",
        "http://192.168.50.20:9090",
    )

    GRAFANA_URL = os.getenv(
        "GRAFANA_URL",
        "http://192.168.50.20:3000",
    )

    ALERTMANAGER_URL = os.getenv(
        "ALERTMANAGER_URL",
        "http://192.168.50.20:9093",
    )

    CERTIFICATE_PATH = Path(
        os.getenv(
            "CERTIFICATE_PATH",
            "/security/nginx.crt",
        )
    )

    LOG_EXPORT_DIR = Path(
        os.getenv(
            "LOG_EXPORT_DIR",
            "/app/log_exports",
        )
    )

    DOCKER_ALLOWED_CONTAINERS = {
        "secure-web-app-v2",
        "cadvisor",
    }