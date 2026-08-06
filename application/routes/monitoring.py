from flask import (
    Blueprint,
    current_app,
    render_template,
)

from decorators import login_required


monitoring_bp = Blueprint(
    "monitoring",
    __name__,
)


@monitoring_bp.route("/monitoring")
@login_required
def monitoring_page():
    return render_template(
        "monitoring.html"
    )


@monitoring_bp.route("/infrastructure")
@login_required
def infrastructure_page():
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

    return render_template(
        "infrastructure.html",
        services=services,
    )