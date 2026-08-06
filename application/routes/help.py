from __future__ import annotations

from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    session,
)

from decorators import login_required
from services.assistant_engine import build_assistant_response


help_bp = Blueprint(
    "help",
    __name__,
)

MAX_QUESTION_LENGTH = 500


@help_bp.get("/help")
@login_required
def help_center():
    return render_template("help_center.html")


@help_bp.get("/getting-started")
@login_required
def getting_started():
    return render_template("getting_started.html")


@help_bp.get("/faq")
@login_required
def faq():
    return render_template("faq.html")


@help_bp.get("/documentation")
@login_required
def documentation():
    return render_template("documentation.html")


@help_bp.get("/assistant")
@login_required
def assistant():
    return render_template("assistant.html")


@help_bp.post("/api/assistant")
@login_required
def assistant_api():
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "Le corps JSON est invalide."
        }), 400

    question = str(
        payload.get("question", "")
    ).strip()

    if len(question) > MAX_QUESTION_LENGTH:
        return jsonify({
            "error": "La question est trop longue."
        }), 400

    context = session.get("emma_context")

    if not isinstance(context, dict):
        context = {}

    response = build_assistant_response(
        question,
        context=context,
    )

    session["emma_context"] = {
        "last_question": question,
        "last_intent": response["intent"],
    }
    session.modified = True

    return jsonify(response)
