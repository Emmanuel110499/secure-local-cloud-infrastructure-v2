from flask import (
    Blueprint,
    current_app,
    render_template,
)

from decorators import login_required


security_bp = Blueprint(
    "security",
    __name__,
)


@security_bp.route("/security")
@login_required
def security_page():

    security_service = current_app.extensions[
        "security_service"
    ]

    return render_template(
        "security.html",
        security=security_service.get_security_status(),
    )