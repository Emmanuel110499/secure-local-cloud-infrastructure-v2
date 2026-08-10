import re
import unicodedata

INTENTS = {
    "containers": [
        "conteneur",
        "conteneurs",
        "docker",
        "container",
        "containers",
    ],
    "services": [
        "service",
        "services",
        "alerte",
        "alertes",
        "alertmanager",
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


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower())
    value = "".join(
        character
        for character in value
        if unicodedata.category(character) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def detect_intent(question: str) -> str:
    q = normalize(question)
    scores = {
        intent: 0
        for intent in INTENTS
    }

    for intent, words in INTENTS.items():
        for word in words:
            normalized_word = normalize(word)

            if re.search(
                r"\b" + re.escape(normalized_word) + r"\b",
                q,
            ):
                scores[intent] += max(
                    1,
                    len(normalized_word.split()),
                )

    best_intent = max(
        scores,
        key=scores.get,
    )

    if scores[best_intent] > 0:
        return best_intent

    return "documentation"
