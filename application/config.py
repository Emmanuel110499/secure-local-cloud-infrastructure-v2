import os
from pathlib import Path


class Config:
    """Configuration générale de l'application."""

    SECRET_KEY = os.getenv("SECRET_KEY")

    MAX_CONTENT_LENGTH = 1024 * 1024

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

    WEB_PRIVATE_IP = os.getenv(
        "WEB_PRIVATE_IP",
        "192.168.50.10",
    )

    MONITORING_PRIVATE_IP = os.getenv(
        "MONITORING_PRIVATE_IP",
        "192.168.50.20",
    )

    NODE_EXPORTER_JOB = os.getenv(
        "NODE_EXPORTER_JOB",
        "srv-web",
    )

    CADVISOR_JOB = os.getenv(
        "CADVISOR_JOB",
        "cadvisor",
    )

    NODE_EXPORTER_INSTANCE = os.getenv(
        "NODE_EXPORTER_INSTANCE",
        f"{WEB_PRIVATE_IP}:9100",
    )

    CADVISOR_INSTANCE = os.getenv(
        "CADVISOR_INSTANCE",
        f"{WEB_PRIVATE_IP}:8080",
    )

    MONITORING_NODE_JOB = os.getenv(
        "MONITORING_NODE_JOB",
        "srv-monitoring",
    )

    MONITORING_NODE_INSTANCE = os.getenv(
        "MONITORING_NODE_INSTANCE",
        f"{MONITORING_PRIVATE_IP}:9100",
    )

    WINDOWS_EXPORTER_JOB = os.getenv(
        "WINDOWS_EXPORTER_JOB",
        "pc-windows",
    )

    WINDOWS_EXPORTER_INSTANCE = os.getenv(
        "WINDOWS_EXPORTER_INSTANCE",
        "192.168.154.1:9182",
    )

    WINDOWS_EQUIPMENT = os.getenv(
        "WINDOWS_EQUIPMENT",
        "pc-emmanuel",
    )

    EQUIPMENTS = {
        "srv-web": {
            "id": "srv-web",
            "name": "srv-web",
            "role": "Serveur applicatif",
            "os": "linux",
            "job": NODE_EXPORTER_JOB,
            "instance": NODE_EXPORTER_INSTANCE,
            "docker_job": CADVISOR_JOB,
            "docker_instance": CADVISOR_INSTANCE,
        },
        "srv-monitoring": {
            "id": "srv-monitoring",
            "name": "srv-monitoring",
            "role": "Serveur d’observabilité",
            "os": "linux",
            "job": MONITORING_NODE_JOB,
            "instance": MONITORING_NODE_INSTANCE,
        },
        "pc-emmanuel": {
            "id": "pc-emmanuel",
            "name": "PC Emmanuel",
            "role": "Poste d’administration",
            "os": "windows",
            "job": WINDOWS_EXPORTER_JOB,
            "instance": WINDOWS_EXPORTER_INSTANCE,
            "equipment_label": WINDOWS_EQUIPMENT,
        },
    }

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
