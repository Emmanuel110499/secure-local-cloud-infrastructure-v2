from services.assistant_router import route_assistant_question
from services.knowledge_engine import (
    build_documentation_answer,
    search,
)
from services.intent_router import detect_intent
import unicodedata
import json
import os
import re
from difflib import SequenceMatcher
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
)

from decorators import login_required

STOP_WORDS = {
    "a", "au", "aux", "avec", "ce", "ces", "cest", "c", "dans",
    "de", "des", "du", "elle", "en", "est", "et", "ils", "je",
    "la", "le", "les", "leur", "lui", "ma", "mais", "mes", "mon",
    "ne", "nos", "notre", "nous", "on", "ou", "par", "pas", "pour",
    "que", "quel", "quelle", "quels", "quelles", "qui", "quoi",
    "sa", "se", "ses", "son", "sur", "ta", "tes", "toi", "ton",
    "tu", "un", "une", "vos", "votre", "vous", "comment",
    "pourquoi", "explique", "expliquer", "sert", "servent"
}


help_bp = Blueprint(
    "help",
    __name__,
)

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

KNOWLEDGE_PATH = os.path.join(
    BASE_DIR,
    "knowledge",
    "project_knowledge.json",
)


def load_knowledge() -> dict[str, Any]:
    try:
        with open(
            KNOWLEDGE_PATH,
            "r",
            encoding="utf-8",
        ) as knowledge_file:
            return json.load(knowledge_file)
    except (OSError, json.JSONDecodeError):
        return {}


KNOWLEDGE = load_knowledge()


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower())

    value = "".join(
        character
        for character in value
        if unicodedata.category(character) != "Mn"
    )

    value = re.sub(r"[^a-z0-9\s_-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value

def extract_words(value: str) -> set[str]:
    normalized = normalize_text(value)

    return {
        word
        for word in normalized.split()
        if len(word) > 1 and word not in STOP_WORDS
    }

def service_is_reachable(
    url: str,
    timeout: int = 3,
) -> bool:
    try:
        with urlopen(url, timeout=timeout) as response:
            return 200 <= response.status < 500
    except URLError:
        return False


def get_live_services() -> dict[str, bool]:
    return {
        "grafana": service_is_reachable(
            "http://192.168.50.20:3000/login"
        ),
        "prometheus": service_is_reachable(
            "http://192.168.50.20:9090/-/healthy"
        ),
        "application": service_is_reachable(
            "http://127.0.0.1:5000/login"
        ),
    }


def get_containers_summary() -> str:
    docker_service = current_app.extensions.get(
        "docker_service"
    )

    if docker_service is None:
        return (
            "Le service Docker n’est pas disponible "
            "dans l’application."
        )

    containers = docker_service.list_containers()

    if not containers:
        return "Aucun conteneur Docker n’a été détecté."

    running = []
    stopped = []

    for container in containers:
        name = container.get(
            "name",
            container.get("id", "inconnu"),
        )

        state = str(
            container.get(
                "state",
                container.get("status", ""),
            )
        ).lower()

        if (
            "running" in state
            or state == "up"
            or state == "active"
        ):
            running.append(name)
        else:
            stopped.append(name)

    parts = [
        f"{len(containers)} conteneur(s) détecté(s)."
    ]

    if running:
        parts.append(
            "Actifs : " + ", ".join(running) + "."
        )

    if stopped:
        parts.append(
            "Arrêtés ou non sains : "
            + ", ".join(stopped)
            + "."
        )

    return " ".join(parts)


def live_answer(question: str) -> str | None:
    normalized = normalize_text(question)

    if any(
        phrase in normalized
        for phrase in (
            "etat des services",
            "statut des services",
            "services fonctionnent",
            "services sont up",
            "tout fonctionne",
        )
    ):
        services = get_live_services()

        labels = {
            "application": "Application Flask",
            "grafana": "Grafana",
            "prometheus": "Prometheus",
        }

        details = []

        for service_name, is_up in services.items():
            state = "UP" if is_up else "DOWN"

            details.append(
                f"{labels[service_name]} : {state}"
            )

        return "État actuel : " + " | ".join(details)

    if any(
        phrase in normalized
        for phrase in (
            "conteneurs actifs",
            "conteneurs docker",
            "container actifs",
            "quels conteneurs",
            "combien de conteneurs",
        )
    ):
        return get_containers_summary()

    if "grafana" in normalized and any(
        word in normalized
        for word in (
            "up",
            "down",
            "fonctionne",
            "disponible",
            "etat",
            "statut",
        )
    ):
        status = service_is_reachable(
            "http://192.168.50.20:3000/login"
        )

        return (
            "Grafana répond actuellement correctement."
            if status
            else "Grafana ne répond pas actuellement."
        )

    if "prometheus" in normalized and any(
        word in normalized
        for word in (
            "up",
            "down",
            "fonctionne",
            "disponible",
            "etat",
            "statut",
        )
    ):
        status = service_is_reachable(
            "http://192.168.50.20:9090/-/healthy"
        )

        return (
            "Prometheus est actuellement opérationnel."
            if status
            else "Prometheus ne répond pas actuellement."
        )

    return None


def knowledge_answer(question: str) -> str | None:
    return build_documentation_answer(question)




def documentation_answer(question: str) -> str | None:
    results = search(
        question,
        limit=3,
        min_score=0.25,
    )

    if not results:
        return None

    best = results[0]

    answer_parts = [
        f"📘 {best['title']}",
        "",
        str(best["content"]).strip(),
    ]

    sources = [str(best["source"])]

    for result in results[1:]:
        if float(result["score"]) < (
            float(best["score"]) * 0.72
        ):
            continue

        if result["source"] not in sources:
            sources.append(str(result["source"]))

    source_lines = "\n".join(
        f"✓ {source}"
        for source in sources
    )

    answer_parts.extend([
        "",
        "────────────────────",
        "📚 Documentation utilisée",
        source_lines,
    ])

    return "\n".join(answer_parts)


def generate_assistant_answer(question: str) -> str:
    question = question.strip()

    if not question:
        return "Écrivez une question pour commencer."

    routed_answer = route_assistant_question(question)

    if routed_answer:
        return routed_answer

    direct_answer = live_answer(question)

    if direct_answer:
        return direct_answer

    project_answer = knowledge_answer(question)

    if project_answer:
        return project_answer

    docs_answer = documentation_answer(question)

    if docs_answer:
        return docs_answer

    return (
        "Je n’ai pas trouvé une réponse suffisamment précise "
        "dans mes données ou dans la documentation. "
        "Vous pouvez me questionner sur Docker, les services, "
        "le CPU, la RAM, le disque, l’adresse IP, Prometheus, "
        "Grafana, Cloudflare ou l’architecture."
    )


@help_bp.route("/help")
@login_required
def help_center():
    return render_template("help_center.html")


@help_bp.route("/getting-started")
@login_required
def getting_started():
    return render_template("getting_started.html")


@help_bp.route("/faq")
@login_required
def faq():
    return render_template("faq.html")


@help_bp.route("/documentation")
@login_required
def documentation():
    return render_template("documentation.html")


@help_bp.route("/assistant")
@login_required
def assistant():
    return render_template("assistant.html")


@help_bp.post("/api/assistant")
@login_required
def assistant_api():
    payload = request.get_json(silent=True) or {}

    question = str(
        payload.get("question", "")
    ).strip()

    if len(question) > 500:
        return jsonify({
            "error": "La question est trop longue."
        }), 400

    answer = generate_assistant_answer(question)

    return jsonify({
        "answer": answer,
    })
