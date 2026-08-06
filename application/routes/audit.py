from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
)

from decorators import login_required


audit_bp = Blueprint(
    "audit",
    __name__,
)


@audit_bp.route("/audit")
@login_required
def audit_page():
    audit_service = current_app.extensions[
        "audit_service"
    ]

    return render_template(
        "audit.html",
        actions=audit_service.list_actions(),
    )


@audit_bp.route("/api/audit")
@login_required
def api_audit():
    audit_service = current_app.extensions[
        "audit_service"
    ]

    actions = audit_service.list_actions()

    return jsonify({
        "count": len(actions),
        "actions": actions,
        "updated_at": datetime.now().isoformat(),
    })