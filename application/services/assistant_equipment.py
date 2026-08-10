from __future__ import annotations

import re
import unicodedata
from typing import Any

from flask import current_app


EQUIPMENT_ALIASES = {
    "srv-web": ("srv web", "serveur web", "serveur applicatif"),
    "srv-monitoring": (
        "srv monitoring",
        "serveur monitoring",
        "serveur de monitoring",
        "serveur d observabilite",
    ),
    "pc-emmanuel": (
        "pc emmanuel",
        "mon pc",
        "ordinateur",
        "poste d administration",
        "pc windows",
    ),
}


def _normalize(value: object) -> str:
    text = unicodedata.normalize("NFD", str(value or "").lower())
    text = "".join(
        character
        for character in text
        if unicodedata.category(character) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _equipment_id(question: str) -> str | None:
    normalized = _normalize(question)
    for equipment_id, aliases in EQUIPMENT_ALIASES.items():
        if any(alias in normalized for alias in aliases):
            return equipment_id
    return None


def _value(value: Any, suffix: str = "") -> str:
    if value is None:
        return "non disponible"
    return f"{value}{suffix}"


def _service():
    return current_app.extensions.get("prometheus_service")


def _equipment_answer(equipment_id: str) -> str | None:
    service = _service()
    if service is None:
        return "Les données Prometheus sont actuellement indisponibles."

    result = service.get_equipment_metrics(equipment_id)
    if not result:
        return None

    equipment = result["equipment"]
    metrics = result["metrics"]
    state = {
        "up": "opérationnel",
        "down": "indisponible",
        "unknown": "état inconnu",
    }.get(result.get("state"), "état inconnu")

    lines = [
        f"État actuel de {equipment['name']}",
        "",
        f"• Rôle : {equipment['role']}",
        f"• Système : {equipment['os'].title()}",
        f"• État : {state}",
        f"• CPU : {_value(metrics.get('cpu'), ' %')}",
        f"• RAM : {_value(metrics.get('memory'), ' %')}",
        f"• Disque : {_value(metrics.get('disk'), ' %')}",
        (
            "• Réseau reçu : "
            + _value(metrics.get("network_receive_kbps"), " Ko/s")
        ),
        f"• Uptime : {metrics.get('uptime', 'non disponible')}",
    ]

    battery = metrics.get("battery") or {}
    if battery:
        power = battery.get("on_ac_power")
        lines.extend([
            f"• Batterie : {_value(battery.get('charge_percent'), ' %')}",
            (
                "• Alimentation : "
                + (
                    "branché au secteur"
                    if power is True
                    else "sur batterie"
                    if power is False
                    else "non disponible"
                )
            ),
        ])

    return "\n".join(lines)


def _comparison_answer() -> str:
    service = _service()
    if service is None:
        return "Les données Prometheus sont actuellement indisponibles."

    results = service.get_all_equipment_metrics()
    lines = ["Comparaison actuelle des équipements", ""]
    for result in results:
        equipment = result["equipment"]
        metrics = result["metrics"]
        state = {
            "up": "opérationnel",
            "down": "indisponible",
            "unknown": "état inconnu",
        }.get(result.get("state"), "état inconnu")
        lines.append(
            f"• {equipment['name']} — "
            f"CPU {_value(metrics.get('cpu'), ' %')} | "
            f"RAM {_value(metrics.get('memory'), ' %')} | "
            f"Disque {_value(metrics.get('disk'), ' %')} | "
            f"état {state}"
        )

    comparable = [
        (result["equipment"]["name"], key, result["metrics"].get(key))
        for result in results
        for key in ("cpu", "memory", "disk")
        if result["metrics"].get(key) is not None
    ]
    if comparable:
        name, key, value = max(comparable, key=lambda item: float(item[2]))
        labels = {"cpu": "CPU", "memory": "RAM", "disk": "disque"}
        numeric_value = float(value)
        if numeric_value >= 90:
            severity = "Alerte critique"
        elif numeric_value >= 80:
            severity = "Vigilance élevée"
        elif numeric_value >= 70:
            severity = "À surveiller"
        else:
            severity = "Situation normale"
        lines.extend([
            "",
            f"{severity} : {name}, {labels[key]} à {value} %.",
        ])
    return "\n".join(lines)


def _battery_answer() -> str:
    service = _service()
    if service is None:
        return "Les données Prometheus sont actuellement indisponibles."
    result = service.get_equipment_metrics("pc-emmanuel")
    battery = (result or {}).get("metrics", {}).get("battery") or {}
    if battery.get("charge_percent") is None:
        return "La métrique de batterie du PC n’est pas disponible."

    power = battery.get("on_ac_power")
    return "\n".join([
        "Batterie du PC Emmanuel",
        "",
        f"• Charge : {battery['charge_percent']} %",
        (
            "• Alimentation : "
            + ("secteur" if power is True else "batterie" if power is False else "inconnue")
        ),
        (
            "• Dernière collecte : il y a "
            f"{_value(battery.get('collector_age_seconds'), ' seconde(s)')}"
        ),
    ])


def _volumes_answer() -> str:
    service = _service()
    if service is None:
        return "Les données Prometheus sont actuellement indisponibles."
    result = service.get_equipment_metrics("srv-monitoring")
    volumes = (result or {}).get("metrics", {}).get("volumes") or []
    if not volumes:
        return "Aucune métrique de volume persistant n’est disponible."

    lines = ["Volumes persistants de srv-monitoring", ""]
    for volume in volumes:
        size_gib = float(volume.get("used_bytes", 0)) / 1024**3
        lines.append(f"• {volume.get('name', 'volume')} : {size_gib:.2f} Gio utilisés")
    lines.extend([
        "",
        "Ces volumes conservent les données de Prometheus, Grafana et Alertmanager après le redémarrage des conteneurs.",
    ])
    return "\n".join(lines)


def equipment_question_answer(question: str) -> str | None:
    normalized = _normalize(question)

    if "batterie" in normalized:
        return _battery_answer()

    if "volume" in normalized or "stockage persistant" in normalized:
        return _volumes_answer()

    if any(word in normalized for word in ("compare", "comparaison", "le plus", "plus sollicite")):
        return _comparison_answer()

    equipment_id = _equipment_id(question)
    if equipment_id and any(
        word in normalized
        for word in ("etat", "sante", "cpu", "ram", "memoire", "disque", "ressource", "metrique")
    ):
        return _equipment_answer(equipment_id)

    if any(
        phrase in normalized
        for phrase in ("quel equipement", "equipement en difficulte", "equipement a un probleme")
    ):
        return _comparison_answer()

    return None
