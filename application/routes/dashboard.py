import socket
from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    session,
)

from decorators import login_required


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
)


def get_complete_services_status() -> dict:
    """Retourne l'état complet des services supervisés."""

    prometheus = current_app.extensions[
        "prometheus_service"
    ]

    security = current_app.extensions[
        "security_service"
    ]

    services = prometheus.get_service_status()

    services.update({
        "flask": True,

        "prometheus": prometheus.is_healthy(),

        "grafana": security.check_http_service(
            current_app.config["GRAFANA_URL"]
            + "/api/health"
        ),
    })

    return services


@dashboard_bp.route("/")
@login_required
def home():
    prometheus = current_app.extensions[
        "prometheus_service"
    ]

    metrics = prometheus.get_system_metrics()
    services = get_complete_services_status()

    return render_template(
        "index_v2.html",
        hostname=socket.gethostname(),
        server_ip="192.168.50.10",
        current_time=datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        ),
        metrics=metrics,
        services=services,
        infrastructure_healthy=all(
            services.values()
        ),
        logged_user=session.get("username"),
        login_time=session.get("login_time"),
    )


@dashboard_bp.route("/health")
def health():
    services = get_complete_services_status()

    return jsonify({
        "status": (
            "healthy"
            if all(services.values())
            else "degraded"
        ),
        "application": (
            "Secure Local Cloud Infrastructure V2"
        ),
        "server": socket.gethostname(),
        "services": services,
        "updated_at": datetime.now().isoformat(),
    })


@dashboard_bp.route("/api/metrics")
@login_required
def api_metrics():
    prometheus = current_app.extensions[
        "prometheus_service"
    ]

    services = get_complete_services_status()
    metrics = prometheus.get_system_metrics()

    docker_service = current_app.extensions.get(
        "docker_service"
    )

    containers = (
        docker_service.list_containers()
        if docker_service is not None
        else []
    )

    health_score_service = current_app.extensions.get(
        "health_score_service"
    )

    health = (
        health_score_service.calculate(
            metrics=metrics,
            services=services,
            containers=containers,
        )
        if health_score_service is not None
        else None
    )

    history_service = current_app.extensions.get(
        "history_service"
    )

    if history_service is not None:
        history_service.record_if_due(metrics)

    return jsonify({
        "metrics": metrics,
        "services": services,
        "health": health,
        "server": {
            "hostname": socket.gethostname(),
            "ip": "192.168.50.10",
        },
        "updated_at": datetime.now().isoformat(),
    })


@dashboard_bp.route("/api/metrics/history")
@login_required
def api_metrics_history():
    history_service = current_app.extensions.get(
        "history_service"
    )

    if history_service is None:
        return jsonify({
            "error": "Service d’historique indisponible."
        }), 503

    try:
        hours = int(request.args.get("hours", 24))
    except (TypeError, ValueError):
        hours = 24

    hours = max(1, min(hours, 168))

    return jsonify({
        "hours": hours,
        "history": history_service.get_history(hours),
        "summary": history_service.get_summary(hours),
        "updated_at": datetime.now().isoformat(),
    })


@dashboard_bp.route("/api/equipment")
@login_required
def api_equipment():
    """Catalogue et état actuel de tous les équipements."""

    prometheus = current_app.extensions["prometheus_service"]
    equipment = prometheus.get_all_equipment_metrics()

    return jsonify({
        "equipment": equipment,
        "count": len(equipment),
        "updated_at": datetime.now().isoformat(),
    })


@dashboard_bp.route("/api/equipment/<equipment_id>/metrics")
@login_required
def api_equipment_metrics(equipment_id: str):
    """KPI actuels d'un équipement configuré."""

    prometheus = current_app.extensions["prometheus_service"]
    result = prometheus.get_equipment_metrics(equipment_id)

    if result is None:
        return jsonify({
            "error": "Équipement inconnu.",
            "equipment_id": equipment_id,
        }), 404

    return jsonify({
        **result,
        "updated_at": datetime.now().isoformat(),
    })


@dashboard_bp.route("/api/health-score")
@login_required
def api_health_score():
    prometheus = current_app.extensions[
        "prometheus_service"
    ]

    docker_service = current_app.extensions[
        "docker_service"
    ]

    health_score_service = current_app.extensions[
        "health_score_service"
    ]

    metrics = prometheus.get_system_metrics()
    services = get_complete_services_status()
    containers = docker_service.list_containers()

    return jsonify(
        health_score_service.calculate(
            metrics=metrics,
            services=services,
            containers=containers,
        )
    )

