from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
)

from decorators import login_required


prometheus_bp = Blueprint(
    "prometheus",
    __name__,
)


@prometheus_bp.route("/prometheus")
@login_required
def prometheus_page():

    return render_template(
        "prometheus.html"
    )


@prometheus_bp.route("/api/prometheus/targets")
@login_required
def prometheus_targets():

    prometheus = current_app.extensions[
        "prometheus_service"
    ]

    return jsonify({
        "targets": prometheus.get_targets(),
    })