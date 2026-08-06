from services.health_score_service import HealthScoreService
from services.account_service import AccountService
from services.audit_service import AuditService
from services.docker_service import DockerService
from services.log_service import LogService
from services.history_service import HistoryService
from services.prometheus_service import PrometheusService
from services.security_service import SecurityService


def initialize_services(app):
    """Initialise les services de l'application."""

    app.extensions["health_score_service"] = (
        HealthScoreService()
    )

    app.extensions["prometheus_service"] = PrometheusService(
        app.config["PROMETHEUS_URL"],
        node_exporter_job=app.config["NODE_EXPORTER_JOB"],
        cadvisor_job=app.config["CADVISOR_JOB"],
        node_exporter_instance=app.config["NODE_EXPORTER_INSTANCE"],
        cadvisor_instance=app.config["CADVISOR_INSTANCE"],
        equipments=app.config["EQUIPMENTS"],
    )

    app.extensions["docker_service"] = DockerService(
        app.config["DOCKER_ALLOWED_CONTAINERS"]
    )

    app.extensions["log_service"] = LogService(
        app.config["LOG_EXPORT_DIR"]
    )

    app.extensions["security_service"] = SecurityService(
        certificate_path=app.config["CERTIFICATE_PATH"],
        alertmanager_url=app.config["ALERTMANAGER_URL"],
    )

    app.extensions["audit_service"] = AuditService(
        app.config["AUDIT_FILE"]
    )


    app.extensions["account_service"] = AccountService(
        credentials_path="data/auth/credentials.json",
        default_username=app.config["ADMIN_USERNAME"],
        default_password=app.config.get(
            "ADMIN_PASSWORD",
            "",
        ),
        default_password_hash=app.config.get(
            "ADMIN_PASSWORD_HASH",
            "",
        ),
    )
    app.extensions["history_service"] = HistoryService(
        "data/history/metrics_history.json",
        interval_minutes=5,
        retention_days=7,
    )
