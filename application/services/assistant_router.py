from __future__ import annotations

import re
import unicodedata

from datetime import datetime, timezone

from flask import current_app


def normalize(text: str) -> str:
    text = unicodedata.normalize(
        "NFD",
        str(text).lower(),
    )

    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    text = text.replace("-", " ")
    text = text.replace("’", " ")
    text = text.replace("'", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def contains_any(text: str, expressions: tuple[str, ...]) -> bool:
    return any(expression in text for expression in expressions)


def metrics_answer() -> str:
    prometheus = current_app.extensions.get(
        "prometheus_service"
    )

    if prometheus is None:
        return "Les métriques Prometheus sont indisponibles."

    metrics = prometheus.get_system_metrics()

    def percent(key: str) -> str:
        value = metrics.get(key)

        if value is None:
            return "non disponible"

        return f"{value} %"

    lines = [
        "📊 État actuel des ressources",
        "",
        f"• CPU : {percent('cpu')}",
        f"• RAM : {percent('memory')}",
        f"• Disque : {percent('disk')}",
        (
            "• Charge système : "
            f"{metrics.get('load_1m', 'non disponible')}"
        ),
        (
            "• Processus actifs : "
            f"{metrics.get('processes', 0)}"
        ),
        (
            "• Uptime : "
            f"{metrics.get('uptime', 'non disponible')}"
        ),
        (
            "• Réseau reçu : "
            f"{metrics.get('network_receive_kbps', 0)} Ko/s"
        ),
        (
            "• Réseau envoyé : "
            f"{metrics.get('network_transmit_kbps', 0)} Ko/s"
        ),
    ]

    return "\n".join(lines)


def containers_answer(question: str) -> str:
    docker_service = current_app.extensions.get(
        "docker_service"
    )

    if docker_service is None:
        return "Le service Docker est indisponible."

    containers = docker_service.list_containers()

    if not containers:
        return "Aucun conteneur Docker n’est actuellement détecté."

    normalized = normalize(question)

    if contains_any(
        normalized,
        (
            "consomme le plus",
            "plus de memoire",
            "plus de ram",
            "plus de cpu",
        ),
    ):
        if contains_any(normalized, ("memoire", "ram")):
            container = max(
                containers,
                key=lambda item: float(
                    item.get("memory_mb", 0) or 0
                ),
            )

            return (
                "🐳 Conteneur utilisant le plus de mémoire\n\n"
                f"• Nom : {container.get('name', 'inconnu')}\n"
                f"• Mémoire : "
                f"{container.get('memory_mb', 0)} Mo\n"
                f"• CPU : {container.get('cpu', 0)} %\n"
                f"• État : "
                f"{container.get('status', 'inconnu')}"
            )

        container = max(
            containers,
            key=lambda item: float(
                item.get("cpu", 0) or 0
            ),
        )

        return (
            "🐳 Conteneur utilisant le plus de CPU\n\n"
            f"• Nom : {container.get('name', 'inconnu')}\n"
            f"• CPU : {container.get('cpu', 0)} %\n"
            f"• Mémoire : "
            f"{container.get('memory_mb', 0)} Mo\n"
            f"• État : {container.get('status', 'inconnu')}"
        )

    running = [
        container
        for container in containers
        if str(
            container.get("status", "")
        ).lower() in {"running", "up", "active"}
    ]

    lines = [
        (
            f"🐳 {len(running)} conteneur(s) actif(s) "
            f"sur {len(containers)} détecté(s)"
        ),
        "",
    ]

    for container in containers:
        status = str(
            container.get("status", "inconnu")
        ).lower()

        is_running = status in {
            "running",
            "up",
            "active",
        }

        lines.extend([
            (
                f"{'✅' if is_running else '❌'} "
                f"{container.get('name', 'inconnu')}"
            ),
            f"   Image : {container.get('image', 'inconnue')}",
            f"   État : {status}",
            (
                f"   CPU : {container.get('cpu', 0)} % | "
                f"RAM : {container.get('memory_mb', 0)} Mo"
            ),
            (
                f"   Uptime : "
                f"{container.get('uptime', 'non disponible')}"
            ),
            "",
        ])

    return "\n".join(lines).rstrip()


def services_answer() -> str:
    prometheus = current_app.extensions.get(
        "prometheus_service"
    )
    security = current_app.extensions.get(
        "security_service"
    )

    statuses: dict[str, str] = {
        "Application Flask": "up",
    }

    if prometheus is not None:
        service_status = prometheus.get_service_status_detailed()

        statuses["Node Exporter"] = service_status.get(
            "node_exporter",
            "unknown",
        )
        statuses["cAdvisor"] = service_status.get(
            "cadvisor",
            "unknown",
        )
        statuses["Prometheus"] = prometheus.get_health_status()
    else:
        statuses["Node Exporter"] = "unknown"
        statuses["cAdvisor"] = "unknown"
        statuses["Prometheus"] = "unknown"

    if security is not None:
        grafana_url = current_app.config.get(
            "GRAFANA_URL",
            "http://127.0.0.1:3000",
        )

        statuses["Grafana"] = security.check_http_service_status(
            grafana_url.rstrip("/") + "/api/health"
        )
    else:
        statuses["Grafana"] = "unknown"

    lines = [
        "🖥️ Services actuellement supervisés",
        "",
    ]

    labels = {
        "up": ("✅", "opérationnel"),
        "down": ("❌", "indisponible"),
        "unknown": ("⚪", "état inconnu"),
    }

    for name, status in statuses.items():
        icon, label = labels.get(
            status,
            labels["unknown"],
        )
        lines.append(
            f"{icon} {name} : {label}"
        )

    operational = sum(
        status == "up"
        for status in statuses.values()
    )
    down = sum(
        status == "down"
        for status in statuses.values()
    )
    unknown = sum(
        status == "unknown"
        for status in statuses.values()
    )

    lines.extend([
        "",
        (
            f"{operational}/{len(statuses)} service(s) "
            "sont opérationnels."
        ),
        f"Indisponibles : {down} | Inconnus : {unknown}",
        (
            "Contrôle effectué le "
            + datetime.now(timezone.utc).strftime(
                "%d/%m/%Y à %H:%M:%S UTC"
            )
            + "."
        ),
    ])

    return "\n".join(lines)


def infrastructure_answer() -> str:
    prometheus = current_app.extensions.get(
        "prometheus_service"
    )

    metrics = (
        prometheus.get_system_metrics()
        if prometheus is not None
        else {}
    )

    lines = [
        "🏗️ Infrastructure principale",
        "",
        "• Serveur : srv-web",
        (
            "• Adresse IP : "
            + current_app.config["WEB_PRIVATE_IP"]
        ),
        "• Système : Ubuntu Server 24.04 LTS",
        (
            "• Uptime : "
            f"{metrics.get('uptime', 'non disponible')}"
        ),
        (
            "• CPU : "
            f"{metrics.get('cpu', 'non disponible')} %"
        ),
        (
            "• RAM : "
            f"{metrics.get('memory', 'non disponible')} %"
        ),
        (
            "• Disque : "
            f"{metrics.get('disk', 'non disponible')} %"
        ),
    ]

    return "\n".join(lines)


def platform_answer() -> str:
    return "\n".join([
        "☁️ Secure Local Cloud Infrastructure",
        "",
        (
            "Cette plateforme centralise la supervision "
            "d’une infrastructure Docker sécurisée."
        ),
        "",
        "Elle permet notamment de :",
        "• surveiller le CPU, la RAM, le disque et le réseau ;",
        "• vérifier l’état des services ;",
        "• suivre les conteneurs Docker ;",
        "• consulter les métriques avec Prometheus ;",
        "• visualiser les données avec Grafana ;",
        "• analyser les ressources avec Node Exporter et cAdvisor ;",
        "• protéger les accès avec Cloudflare Zero Trust ;",
        "• consulter l’historique et les informations de sécurité.",
        "",
        (
            "Emma_IA utilise les données réelles de la plateforme "
            "et la documentation locale pour vous assister."
        ),
    ])




def architecture_answer() -> str:
    return "\n".join([
        "🏗️ Architecture de la plateforme",
        "",
        "L’infrastructure est organisée autour de deux serveurs :",
        "",
        (
            "• srv-web — "
            + current_app.config["WEB_PRIVATE_IP"]
        ),
        "  Héberge l’application Flask, Docker, Node Exporter et cAdvisor.",
        "",
        (
            "• srv-monitoring — "
            + current_app.config["MONITORING_PRIVATE_IP"]
        ),
        "  Héberge Prometheus, Grafana et Alertmanager.",
        "",
        "Fonctionnement général :",
        "",
        "1. Node Exporter collecte les métriques système du serveur.",
        "2. cAdvisor collecte les métriques des conteneurs Docker.",
        "3. Prometheus récupère et stocke ces métriques.",
        "4. Grafana les transforme en tableaux de bord.",
        "5. Alertmanager gère les alertes de supervision.",
        "6. Flask centralise les informations dans cette interface.",
        "7. Cloudflare Zero Trust protège les accès externes.",
    ])


def prometheus_grafana_answer() -> str:
    return "\n".join([
        "📊 Prometheus et Grafana",
        "",
        "Prometheus collecte et stocke les métriques sous forme "
        "de séries temporelles.",
        "",
        "Il récupère notamment les données provenant de :",
        "• Node Exporter pour les ressources système ;",
        "• cAdvisor pour les conteneurs Docker.",
        "",
        "Grafana utilise ensuite les données de Prometheus pour "
        "créer des graphiques et des tableaux de bord.",
        "",
        "En résumé :",
        "• Prometheus collecte et stocke ;",
        "• Grafana affiche et visualise.",
    ])


def zero_trust_answer() -> str:
    return "\n".join([
        "🔐 Cloudflare Zero Trust",
        "",
        "Cloudflare Zero Trust protège les interfaces sensibles "
        "de la plateforme, notamment Grafana et Prometheus.",
        "",
        "Avant d’autoriser l’accès, Cloudflare vérifie l’identité "
        "de l’utilisateur.",
        "",
        "Dans cette infrastructure, l’utilisateur doit fournir "
        "une adresse e-mail autorisée et valider un code temporaire.",
        "",
        "Cela évite d’exposer directement les outils de supervision "
        "sur Internet et limite l’accès aux personnes autorisées.",
    ])


def health_analysis_answer(question: str) -> str:
    prometheus = current_app.extensions.get(
        "prometheus_service"
    )
    docker_service = current_app.extensions.get(
        "docker_service"
    )

    metrics = (
        prometheus.get_system_metrics()
        if prometheus is not None
        else {}
    )

    containers = (
        docker_service.list_containers()
        if docker_service is not None
        else []
    )

    cpu = metrics.get("cpu")
    memory = metrics.get("memory")
    disk = metrics.get("disk")
    load = metrics.get("load_1m")
    uptime = metrics.get(
        "uptime",
        "non disponible",
    )

    normalized = normalize(question)

    problems: list[str] = []
    recommendations: list[str] = []

    if cpu is not None:
        if cpu >= 90:
            problems.append(
                f"Le CPU est critique à {cpu} %."
            )
            recommendations.append(
                "Identifier le processus ou le conteneur "
                "qui consomme le plus de CPU."
            )
        elif cpu >= 75:
            problems.append(
                f"Le CPU est élevé à {cpu} %."
            )
            recommendations.append(
                "Surveiller la charge et vérifier les "
                "conteneurs les plus actifs."
            )

    if memory is not None:
        if memory >= 90:
            problems.append(
                f"La mémoire est critique à {memory} %."
            )
            recommendations.append(
                "Vérifier les processus et conteneurs "
                "utilisant le plus de mémoire."
            )
        elif memory >= 75:
            problems.append(
                f"La mémoire est élevée à {memory} %."
            )

    if disk is not None:
        if disk >= 90:
            problems.append(
                f"Le disque est presque saturé à {disk} %."
            )
            recommendations.append(
                "Nettoyer les anciens logs, images Docker "
                "et volumes inutilisés."
            )
        elif disk >= 80:
            problems.append(
                f"L’utilisation du disque est élevée à {disk} %."
            )

    stopped = []

    for container in containers:
        status = str(
            container.get("status", "")
        ).lower()

        if status not in {
            "running",
            "up",
            "active",
        }:
            stopped.append(
                container.get("name", "inconnu")
            )

    if stopped:
        problems.append(
            "Conteneur(s) non opérationnel(s) : "
            + ", ".join(stopped)
            + "."
        )
        recommendations.append(
            "Consulter les logs Docker avant tout redémarrage."
        )

    if containers:
        top_cpu = max(
            containers,
            key=lambda item: float(
                item.get("cpu", 0) or 0
            ),
        )

        top_memory = max(
            containers,
            key=lambda item: float(
                item.get("memory_mb", 0) or 0
            ),
        )
    else:
        top_cpu = None
        top_memory = None

    lines = [
        "🧠 Analyse de l’infrastructure",
        "",
        "Métriques actuelles :",
        (
            f"• CPU : "
            f"{cpu if cpu is not None else 'non disponible'} %"
        ),
        (
            f"• RAM : "
            f"{memory if memory is not None else 'non disponible'} %"
        ),
        (
            f"• Disque : "
            f"{disk if disk is not None else 'non disponible'} %"
        ),
        f"• Charge système : {load}",
        f"• Uptime : {uptime}",
    ]

    if top_cpu is not None:
        lines.extend([
            "",
            (
                "Conteneur utilisant le plus de CPU : "
                f"{top_cpu.get('name', 'inconnu')} "
                f"({top_cpu.get('cpu', 0)} %)"
            ),
            (
                "Conteneur utilisant le plus de mémoire : "
                f"{top_memory.get('name', 'inconnu')} "
                f"({top_memory.get('memory_mb', 0)} Mo)"
            ),
        ])

    lines.append("")

    if problems:
        lines.append("⚠️ Problèmes ou points de vigilance :")

        for problem in problems:
            lines.append(f"• {problem}")
    else:
        lines.extend([
            "✅ Aucun problème critique détecté.",
            (
                "Les valeurs CPU, RAM, disque et Docker "
                "sont actuellement dans des limites normales."
            ),
        ])

    if recommendations:
        lines.extend([
            "",
            "🔧 Recommandations :",
        ])

        for recommendation in recommendations:
            lines.append(f"• {recommendation}")

    if contains_any(
        normalized,
        (
            "commande",
            "commandes",
            "que faire",
            "comment corriger",
            "diagnostic",
        ),
    ):
        lines.extend([
            "",
            "Commandes de diagnostic proposées :",
            "• docker stats --no-stream",
            "• docker ps -a",
            "• docker logs <nom_du_conteneur> --tail 100",
            "• top",
            "• free -h",
            "• df -h",
        ])

    return "\n".join(lines)


def sre_advisor_answer(question: str) -> str:
    prometheus = current_app.extensions.get(
        "prometheus_service"
    )

    docker_service = current_app.extensions.get(
        "docker_service"
    )

    metrics = (
        prometheus.get_system_metrics()
        if prometheus is not None
        else {}
    )

    containers = (
        docker_service.list_containers()
        if docker_service is not None
        else []
    )

    cpu = metrics.get("cpu")
    memory = metrics.get("memory")
    disk = metrics.get("disk")
    load = metrics.get("load_1m")
    processes = metrics.get("processes", 0)

    normalized = normalize(question)

    findings: list[str] = []
    risks: list[str] = []
    recommendations: list[str] = []
    commands: list[str] = []

    if cpu is not None:
        if cpu >= 90:
            findings.append(
                f"Le CPU est critique à {cpu} %."
            )
            risks.append(
                "Ralentissement de l’application et "
                "risque de saturation du serveur."
            )
            recommendations.append(
                "Identifier immédiatement le processus "
                "ou le conteneur responsable."
            )
            commands.extend([
                "top",
                "ps aux --sort=-%cpu | head",
                "docker stats --no-stream",
            ])

        elif cpu >= 75:
            findings.append(
                f"Le CPU est élevé à {cpu} %."
            )
            risks.append(
                "Dégradation possible des performances "
                "si la charge continue d’augmenter."
            )
            recommendations.append(
                "Surveiller la tendance et vérifier les "
                "conteneurs les plus consommateurs."
            )
            commands.extend([
                "top",
                "docker stats --no-stream",
            ])
        else:
            findings.append(
                f"Le CPU est normal à {cpu} %."
            )

    if memory is not None:
        if memory >= 90:
            findings.append(
                f"La mémoire est critique à {memory} %."
            )
            risks.append(
                "Risque de swap, lenteur importante "
                "ou arrêt de processus."
            )
            recommendations.append(
                "Rechercher les processus et conteneurs "
                "utilisant le plus de mémoire."
            )
            commands.extend([
                "free -h",
                "ps aux --sort=-%mem | head",
                "docker stats --no-stream",
            ])

        elif memory >= 75:
            findings.append(
                f"La mémoire est élevée à {memory} %."
            )
            recommendations.append(
                "Vérifier les processus les plus gourmands."
            )
            commands.extend([
                "free -h",
                "ps aux --sort=-%mem | head",
            ])
        else:
            findings.append(
                f"La mémoire est normale à {memory} %."
            )

    if disk is not None:
        if disk >= 90:
            findings.append(
                f"Le disque est critique à {disk} %."
            )
            risks.append(
                "Risque d’échec des écritures, logs "
                "incomplets et arrêt de services."
            )
            recommendations.append(
                "Nettoyer les logs, images Docker "
                "et volumes inutilisés."
            )
            commands.extend([
                "df -h",
                "du -sh /var/log/* | sort -h",
                "docker system df",
            ])

        elif disk >= 80:
            findings.append(
                f"Le disque est élevé à {disk} %."
            )
            recommendations.append(
                "Prévoir un nettoyage ou une extension "
                "du stockage."
            )
            commands.extend([
                "df -h",
                "docker system df",
            ])
        else:
            findings.append(
                f"Le disque est normal à {disk} %."
            )

    stopped = []

    for container in containers:
        status = str(
            container.get("status", "")
        ).lower()

        if status not in {
            "running",
            "up",
            "active",
        }:
            stopped.append(
                str(container.get("name", "inconnu"))
            )

    if stopped:
        findings.append(
            "Conteneurs non opérationnels : "
            + ", ".join(stopped)
            + "."
        )
        risks.append(
            "Une partie de la plateforme peut être indisponible."
        )
        recommendations.append(
            "Analyser les logs avant de redémarrer les conteneurs."
        )
        commands.extend([
            "docker ps -a",
            "docker logs <nom_du_conteneur> --tail 100",
        ])

    if containers:
        top_cpu = max(
            containers,
            key=lambda item: float(
                item.get("cpu", 0) or 0
            ),
        )

        top_memory = max(
            containers,
            key=lambda item: float(
                item.get("memory_mb", 0) or 0
            ),
        )
    else:
        top_cpu = None
        top_memory = None

    if not risks:
        risks.append(
            "Aucun risque critique détecté actuellement."
        )

    if not recommendations:
        recommendations.append(
            "Continuer la supervision et conserver "
            "un historique des métriques."
        )

    lines = [
        "🛠️ Conseiller SRE",
        "",
        "Constats :",
        *[
            f"• {finding}"
            for finding in findings
        ],
        "",
        "Risques :",
        *[
            f"• {risk}"
            for risk in risks
        ],
        "",
        "Recommandations :",
        *[
            f"• {recommendation}"
            for recommendation in recommendations
        ],
    ]

    if top_cpu is not None:
        lines.extend([
            "",
            "Conteneurs les plus consommateurs :",
            (
                "• CPU : "
                f"{top_cpu.get('name', 'inconnu')} "
                f"({top_cpu.get('cpu', 0)} %)"
            ),
            (
                "• Mémoire : "
                f"{top_memory.get('name', 'inconnu')} "
                f"({top_memory.get('memory_mb', 0)} Mo)"
            ),
        ])

    if contains_any(
        normalized,
        (
            "commande",
            "commandes",
            "que dois je verifier",
            "que verifier",
            "diagnostic",
            "corriger",
            "solution",
            "que faire",
        ),
    ):
        unique_commands = list(
            dict.fromkeys(commands)
        )

        if not unique_commands:
            unique_commands = [
                "top",
                "free -h",
                "df -h",
                "docker ps -a",
                "docker stats --no-stream",
            ]

        lines.extend([
            "",
            "Commandes recommandées :",
            *[
                f"• {command}"
                for command in unique_commands
            ],
        ])

    lines.extend([
        "",
        (
            "Résumé système : "
            f"charge={load}, processus={processes}"
        ),
    ])

    return "\n".join(lines)

def route_assistant_question(question: str) -> str | None:
    normalized = normalize(question)

    if not normalized:
        return "Écrivez une question pour commencer."

    if contains_any(
        normalized,
        (
            "infrastructure est elle saine",
            "infrastructure saine",
            "etat global",
            "analyse l infrastructure",
            "analyse de l infrastructure",
            "analyse mon infrastructure",
            "analyse complete de l infrastructure",
            "analyse complete",
            "y a t il un probleme",
            "probleme de cpu",
            "cpu est eleve",
            "cpu eleve",
            "pourquoi mon cpu",
            "probleme de memoire",
            "memoire elevee",
            "ram elevee",
            "disque sature",
            "diagnostic infrastructure",
            "diagnostic de l infrastructure",
            "diagnostic complet de l infrastructure",
            "fais un diagnostic",
            "faire un diagnostic",
            "analyse complete",
            "diagnostic du serveur",
            "que faire si le cpu",
            "comment corriger le cpu",
        ),
    ):
        return health_analysis_answer(question)

    if contains_any(
        normalized,
        (
            "conseiller sre",
            "analyse sre",
            "avis sre",
            "que me recommandes tu",
            "quelles recommandations",
            "quels risques",
            "risques vois tu",
            "que dois je verifier",
            "que verifier",
            "quelles commandes lancer",
            "commandes de diagnostic",
            "pourquoi le cpu est eleve",
            "pourquoi mon cpu est eleve",
            "pourquoi la ram est elevee",
            "pourquoi ma memoire est elevee",
            "comment corriger le probleme",
            "comment resoudre le probleme",
            "que faire maintenant",
            "diagnostic sre",
        ),
    ):
        return sre_advisor_answer(question)

    # Questions proposées dans l’interface
    if contains_any(
        normalized,
        (
            "expliquer la plateforme",
            "explique la plateforme",
            "explique moi la plateforme",
            "explique moi cette plateforme",
            "presentation de la plateforme",
            "a quoi sert la plateforme",
            "a quoi sert cette plateforme",
            "que fait la plateforme",
            "comment fonctionne la plateforme",
            "presente moi le projet",
            "presente le projet",
            "presentation du projet",
            "presentation de cette plateforme",
            "presente cette plateforme",
            "decris cette plateforme",
            "decris le projet",
            "quel est le projet",
            "objectif du projet",
            "objectif de la plateforme",
        ),
    ):
        return platform_answer()

    if contains_any(
        normalized,
        (
            "expliquer l architecture",
            "explique l architecture",
            "explique moi l architecture",
            "architecture de la plateforme",
            "architecture du projet",
            "comment est organisee l infrastructure",
            "comment fonctionne cette infrastructure",
            "comment fonctionne l infrastructure",
            "fonctionnement de l infrastructure",
            "explique le fonctionnement",
            "comment fonctionne le projet",
            "architecture",
            "decris l architecture",
            "explique l infrastructure",
        ),
    ):
        return architecture_answer()

    if contains_any(
        normalized,
        (
            "etat des services",
            "services en cours",
            "services actifs",
            "services operationnels",
            "services disponibles",
            "quels services",
            "statut des services",
            "services tournent",
            "services fonctionnent",
        ),
    ):
        return services_answer()

    if contains_any(
        normalized,
        (
            "conteneurs actifs",
            "combien de conteneurs",
            "conteneurs docker",
            "liste des conteneurs",
            "quel conteneur",
            "container docker",
            "containers docker",
        ),
    ):
        return containers_answer(question)

    if contains_any(
        normalized,
        (
            "prometheus ou grafana",
            "prometheus et grafana",
            "difference entre prometheus et grafana",
            "role de prometheus et grafana",
        ),
    ):
        return prometheus_grafana_answer()

    if contains_any(
        normalized,
        (
            "expliquer zero trust",
            "explique zero trust",
            "cloudflare zero trust",
            "pourquoi zero trust",
            "a quoi sert zero trust",
        ),
    ):
        return zero_trust_answer()

    if contains_any(
        normalized,
        (
            "adresse ip",
            "ip du serveur",
            "hostname",
            "nom du serveur",
            "infrastructure principale",
            "information serveur",
        ),
    ):
        return infrastructure_answer()

    if contains_any(
        normalized,
        (
            "utilisation cpu",
            "utilisation ram",
            "utilisation memoire",
            "espace disque",
            "metriques actuelles",
            "etat des ressources",
            "charge systeme",
            "ressources systeme",
            "cpu et ram",
        ),
    ):
        return metrics_answer()

    return None
