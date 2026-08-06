from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
)

from decorators import login_required


logs_bp = Blueprint(
    "logs",
    __name__,
)


@logs_bp.route("/logs")
@login_required
def logs_page():
    log_service = current_app.extensions["log_service"]

    selected_log = request.args.get(
        "source",
        "flask",
    )

    if selected_log not in log_service.allowed_logs:
        selected_log = "flask"

    return render_template(
        "logs.html",
        selected_log=selected_log,
        available_logs=log_service.allowed_logs,
        log_lines=log_service.read_log(
            selected_log
        ),
    )


@logs_bp.route("/api/logs/<log_name>")
@login_required
def api_logs(log_name: str):
    log_service = current_app.extensions["log_service"]

    if log_name not in log_service.allowed_logs:
        return jsonify({
            "error": "Journal inconnu",
        }), 404

    return jsonify({
        "source": log_name,
        "lines": log_service.read_log(log_name),
        "updated_at": datetime.now().isoformat(),
    })