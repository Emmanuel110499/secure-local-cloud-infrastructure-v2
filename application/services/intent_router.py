import re

INTENTS = {
    "containers": [
        "conteneur",
        "docker",
        "container",
    ],
    "services": [
        "service",
        "running",
        "exécution",
        "tourne",
    ],
    "metrics": [
        "cpu",
        "ram",
        "mémoire",
        "disque",
        "load",
    ],
    "infrastructure": [
        "ip",
        "serveur",
        "hostname",
        "machine",
    ],
    "documentation": [
        "explique",
        "comment",
        "pourquoi",
        "documentation",
        "prometheus",
        "grafana",
        "cloudflare",
    ],
}


def detect_intent(question: str) -> str:
    q = question.lower()

    for intent, words in INTENTS.items():
        for word in words:
            if re.search(r"\b" + re.escape(word) + r"\b", q):
                return intent

    return "documentation"
