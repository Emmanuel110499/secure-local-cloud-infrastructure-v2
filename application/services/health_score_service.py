from __future__ import annotations

from typing import Any


class HealthScoreService:
    """Calcule la santé globale de l'infrastructure sur 100."""

    @staticmethod
    def _metric_penalty(
        value: Any,
        warning: float,
        critical: float,
        maximum_penalty: int,
    ) -> int:
        if not isinstance(value, (int, float)):
            return 0

        if value >= critical:
            return maximum_penalty

        if value >= warning:
            progress = (
                (value - warning)
                / max(critical - warning, 1)
            )

            return round(
                maximum_penalty * (0.45 + progress * 0.55)
            )

        return 0

    def calculate(
        self,
        metrics: dict[str, Any],
        services: dict[str, bool],
        containers: list[dict[str, Any]],
    ) -> dict[str, Any]:
        score = 100
        findings: list[str] = []

        cpu_penalty = self._metric_penalty(
            metrics.get("cpu"),
            warning=75,
            critical=90,
            maximum_penalty=18,
        )

        memory_penalty = self._metric_penalty(
            metrics.get("memory"),
            warning=75,
            critical=90,
            maximum_penalty=18,
        )

        disk_penalty = self._metric_penalty(
            metrics.get("disk"),
            warning=80,
            critical=92,
            maximum_penalty=18,
        )

        score -= cpu_penalty
        score -= memory_penalty
        score -= disk_penalty

        if cpu_penalty:
            findings.append(
                f"Utilisation CPU élevée : "
                f"{metrics.get('cpu')} %."
            )

        if memory_penalty:
            findings.append(
                f"Utilisation mémoire élevée : "
                f"{metrics.get('memory')} %."
            )

        if disk_penalty:
            findings.append(
                f"Utilisation disque élevée : "
                f"{metrics.get('disk')} %."
            )

        unavailable_services = [
            name
            for name, status in services.items()
            if not status
        ]

        service_penalty = min(
            len(unavailable_services) * 12,
            36,
        )

        score -= service_penalty

        if unavailable_services:
            findings.append(
                "Services indisponibles : "
                + ", ".join(unavailable_services)
                + "."
            )

        stopped_containers = []

        for container in containers:
            status = str(
                container.get("status", "")
            ).lower()

            if status not in {
                "running",
                "up",
                "active",
            }:
                stopped_containers.append(
                    str(container.get("name", "inconnu"))
                )

        container_penalty = min(
            len(stopped_containers) * 10,
            20,
        )

        score -= container_penalty
        score = max(0, min(100, score))

        if stopped_containers:
            findings.append(
                "Conteneurs arrêtés : "
                + ", ".join(stopped_containers)
                + "."
            )

        if score >= 90:
            level = "excellent"
            label = "Infrastructure saine"
        elif score >= 75:
            level = "good"
            label = "Infrastructure stable"
        elif score >= 55:
            level = "warning"
            label = "Vigilance requise"
        else:
            level = "critical"
            label = "Incident critique"

        if not findings:
            findings.append(
                "Aucun incident critique détecté."
            )

        return {
            "score": score,
            "level": level,
            "label": label,
            "findings": findings,
            "details": {
                "cpu_penalty": cpu_penalty,
                "memory_penalty": memory_penalty,
                "disk_penalty": disk_penalty,
                "service_penalty": service_penalty,
                "container_penalty": container_penalty,
                "unavailable_services": unavailable_services,
                "stopped_containers": stopped_containers,
            },
        }
