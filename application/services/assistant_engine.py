from __future__ import annotations

from typing import Any
import re
import unicodedata

from services.assistant_router import (
    health_analysis_answer,
    route_assistant_question,
    services_answer,
)
from services.intent_router import detect_intent
from services.knowledge_engine import search


FOLLOW_UP_MARKERS = {
    "et pourquoi",
    "pourquoi",
    "explique plus",
    "plus de details",
    "detaille",
    "et ensuite",
    "comment corriger",
    "que faire",
}

LIVE_INTENTS = {
    "containers",
    "infrastructure",
    "metrics",
    "services",
}

SUGGESTIONS = {
    "containers": [
        "Quels conteneurs sont actuellement actifs ?",
        "Analyse la santé des conteneurs.",
        "Que vérifier si un conteneur s'arrête ?",
    ],
    "metrics": [
        "Analyse le CPU, la mémoire et le disque.",
        "Le disque risque-t-il de se remplir ?",
        "Quelles métriques sont anormales ?",
    ],
    "services": [
        "Quels services sont opérationnels ?",
        "Quelle cible Prometheus est indisponible ?",
        "Explique le chemin d'une alerte.",
    ],
    "infrastructure": [
        "Quel est l’état actuel de mon infrastructure ?",
        "Analyse l’utilisation actuelle du CPU, de la RAM et du disque.",
        "Quels sont les risques de sécurité actuels ?",
    ],
    "documentation": [
        "Présente-moi toute la plateforme.",
        "Explique le rôle de Prometheus et Grafana.",
        "Quelles améliorations restent prioritaires ?",
    ],
}


def _normalize(value: object) -> str:
    text = unicodedata.normalize(
        "NFD",
        str(value or "").lower(),
    )
    text = "".join(
        character
        for character in text
        if unicodedata.category(character) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _is_follow_up(question: str) -> bool:
    normalized = _normalize(question)

    return (
        normalized in FOLLOW_UP_MARKERS
        or len(normalized.split()) <= 5
        and any(
            marker in normalized
            for marker in FOLLOW_UP_MARKERS
        )
    )


def _expand_question(
    question: str,
    context: dict[str, Any] | None,
) -> tuple[str, bool]:
    if not context or not _is_follow_up(question):
        return question, False

    previous = str(
        context.get("last_question", "")
    ).strip()

    if not previous:
        return question, False

    return f"{previous}. Question de suivi : {question}", True


def _direct_answer(
    question: str,
    context: dict[str, Any] | None,
) -> tuple[str | None, str | None, float]:
    """Traite les demandes prioritaires avant la recherche documentaire."""
    normalized = _normalize(question)

    asks_live_state = any(
        marker in normalized
        for marker in (
            "etat actuel",
            "statut actuel",
            "est disponible",
            "sont disponibles",
            "fonctionne actuellement",
            "fonctionnent actuellement",
            "est operationnel",
            "sont operationnels",
        )
    )

    if asks_live_state and "infrastructure" in normalized:
        return health_analysis_answer(question), "infrastructure", 0.97

    resource_terms = sum(
        term in normalized
        for term in ("cpu", "ram", "memoire", "disque")
    )
    if resource_terms >= 2 and any(
        marker in normalized
        for marker in ("analyse", "actuel", "utilisation", "etat")
    ):
        return health_analysis_answer(question), "metrics", 0.98

    if "securite" in normalized and any(
        marker in normalized
        for marker in ("risque", "actuel", "analyse", "etat")
    ):
        live_status = services_answer()
        answer = "\n".join([
            "🔐 Évaluation de sécurité actuelle",
            "",
            live_status,
            "",
            "Protections confirmées dans la configuration du projet :",
            "• application publiée par Cloudflare Tunnel ;",
            "• services de monitoring filtrés par adresse source ;",
            "• cAdvisor limité aux réseaux autorisés ;",
            "• secrets exclus des archives destinées à GitHub ;",
            "• sauvegardes automatiques contrôlées par SHA-256 ;",
            "• alertes Prometheus et Fail2ban actifs.",
            "",
            "Risques restant à surveiller :",
            "• espace disque et absence de swap sur les petites VM ;",
            "• SSH par mot de passe tant que les clés ne sont pas activées ;",
            "• dépendances et images à réexaminer régulièrement ;",
            "• sauvegardes encore locales tant qu'une copie externe n'existe pas.",
            "",
            "Cette réponse est un état opérationnel, pas un scan de vulnérabilités complet.",
        ])
        return answer, "infrastructure", 0.9

    if asks_live_state and any(
        service in normalized
        for service in (
            "prometheus",
            "cadvisor",
            "grafana",
            "service",
        )
    ):
        return services_answer(), "services", 0.98

    if "grafana" in normalized and any(
        marker in normalized
        for marker in (
            "ne repond plus",
            "ne fonctionne plus",
            "est en panne",
            "indisponible",
            "diagnostiquer",
            "verifier",
        )
    ):
        live_status = services_answer()
        answer = "\n".join([
            "🛠️ Diagnostic ciblé de Grafana",
            "",
            live_status,
            "",
            "Vérifications recommandées sur srv-monitoring :",
            "1. Vérifier l'état du conteneur Grafana.",
            "2. Lire ses derniers journaux pour identifier l'erreur.",
            "3. Tester localement l'API /api/health.",
            "4. Vérifier l'espace disque et le volume grafana-data.",
            "5. Vérifier le pare-feu du serveur de monitoring.",
            "",
            "Sur srv-monitoring :",
            "• docker compose ps grafana",
            "• docker logs --tail 100 grafana",
            "• curl -sS http://127.0.0.1:3000/api/health",
            "• df -h /",
            "",
            "Sur srv-web, si l'URL publique seule est en panne :",
            "• curl -sS http://192.168.50.20:3000/api/health",
            "• systemctl is-active cloudflared",
        ])
        return answer, "services", 0.97

    previous = _normalize((context or {}).get("last_question", ""))
    if (
        _is_follow_up(question)
        and "plateforme" in previous
        and "pourquoi" in normalized
    ) or (
        "pourquoi" in normalized
        and "deux serveurs" in normalized
    ):
        answer = (
            "L'architecture utilise deux serveurs pour séparer les rôles. "
            "srv-web expose l'application et collecte les métriques, tandis "
            "que srv-monitoring stocke, analyse et affiche la supervision. "
            "Cette séparation limite l'impact d'une panne, évite que la "
            "supervision concurrence l'application pour les ressources et "
            "permet à Prometheus de continuer à signaler clairement une "
            "indisponibilité de srv-web. Elle facilite aussi la sécurité et "
            "une future migration vers de vrais serveurs."
        )
        return answer, "infrastructure", 0.96

    return None, None, 0.0


def _documentation_answer(
    results: list[dict[str, object]],
) -> str:
    best = results[0]
    parts = [
        f"📘 {best['title']}",
        "",
        str(best["content"]).strip(),
    ]

    related = [
        result
        for result in results[1:]
        if float(result["score"])
        >= float(best["score"]) * 0.78
    ]

    if related:
        parts.extend(["", "Points liés :"])

        for result in related:
            excerpt = str(result["content"]).strip()
            first_paragraph = excerpt.split("\n\n", 1)[0].strip()
            if len(first_paragraph) > 360:
                sentences = re.split(r"(?<=[.!?])\s+", first_paragraph)
                selected: list[str] = []
                length = 0

                for sentence in sentences:
                    if selected and length + len(sentence) > 360:
                        break
                    selected.append(sentence)
                    length += len(sentence) + 1

                excerpt = " ".join(selected).strip()
            else:
                excerpt = first_paragraph
            parts.append(f"• {result['title']} : {excerpt}")

    return "\n".join(parts)


def build_assistant_response(
    question: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    original_question = str(question or "").strip()

    if not original_question:
        return {
            "answer": "Écrivez une question pour commencer.",
            "intent": "unknown",
            "confidence": 0.0,
            "sources": [],
            "suggestions": SUGGESTIONS["documentation"],
            "used_live_data": False,
            "follow_up": False,
        }

    direct_answer, direct_intent, direct_confidence = _direct_answer(
        original_question,
        context,
    )
    expanded_question, is_follow_up = _expand_question(
        original_question,
        context,
    )
    intent = direct_intent or detect_intent(expanded_question)
    used_live_data = False
    sources: list[str] = []
    confidence = 0.45

    if direct_answer:
        return {
            "answer": direct_answer,
            "intent": intent,
            "confidence": direct_confidence,
            "sources": ["Données temps réel de la plateforme"]
            if intent == "services"
            else ["Architecture documentée du projet"],
            "suggestions": SUGGESTIONS.get(
                intent,
                SUGGESTIONS["documentation"],
            ),
            "used_live_data": intent == "services",
            "follow_up": is_follow_up,
        }

    if intent in LIVE_INTENTS:
        answer = route_assistant_question(expanded_question)

        if answer:
            used_live_data = True
            sources = ["Données temps réel de la plateforme"]
            confidence = 0.92
        else:
            answer = None
    else:
        answer = None

    if not answer:
        results = search(
            expanded_question,
            limit=3,
            min_score=0.62,
        )

        if results:
            answer = _documentation_answer(results)
            sources = sorted({
                str(result["source"])
                for result in results
            })
            confidence = min(
                0.88,
                0.55 + float(results[0]["score"]) / 5,
            )

    if not answer:
        answer = route_assistant_question(expanded_question)

        if answer:
            sources = ["Moteur de connaissances du projet"]
            confidence = 0.72

    if not answer:
        answer = (
            "Je n'ai pas assez d'informations fiables pour répondre "
            "précisément. Reformulez la question en indiquant le "
            "service concerné, le symptôme observé et le moment où "
            "le problème apparaît."
        )
        confidence = 0.2

    return {
        "answer": answer,
        "intent": intent,
        "confidence": round(confidence, 2),
        "sources": sources,
        "suggestions": SUGGESTIONS.get(
            intent,
            SUGGESTIONS["documentation"],
        ),
        "used_live_data": used_live_data,
        "follow_up": is_follow_up,
    }
