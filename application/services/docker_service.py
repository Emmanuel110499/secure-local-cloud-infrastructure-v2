from datetime import datetime, timezone
from typing import Any

import docker
from docker.errors import DockerException, NotFound


class DockerService:
    """Gère les conteneurs, images, volumes et réseaux Docker."""

    def __init__(self, allowed_containers: set[str]):
        self.allowed_containers = allowed_containers

    def get_client(self):
        """Retourne un client Docker connecté au socket local."""

        try:
            client = docker.from_env()
            client.ping()
            return client

        except DockerException:
            return None

    @staticmethod
    def format_uptime(seconds: int) -> str:
        """Transforme une durée en texte lisible."""

        if seconds <= 0:
            return "Non disponible"

        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)

        parts = []

        if days:
            parts.append(f"{days} j")

        if hours:
            parts.append(f"{hours} h")

        if minutes or not parts:
            parts.append(f"{minutes} min")

        return " ".join(parts)

    def list_containers(self) -> list[dict[str, Any]]:
        """Retourne les conteneurs autorisés avec leurs statistiques."""

        client = self.get_client()

        if client is None:
            return []

        containers = []

        try:
            for container in client.containers.list(all=True):
                if container.name not in self.allowed_containers:
                    continue

                image = (
                    container.image.tags[0]
                    if container.image.tags
                    else container.image.short_id
                )

                cpu_percent = 0.0
                memory_mb = 0.0
                uptime = "Non disponible"

                if container.status == "running":
                    stats = container.stats(stream=False)

                    cpu_stats = stats.get("cpu_stats", {})
                    precpu_stats = stats.get("precpu_stats", {})

                    cpu_usage = cpu_stats.get("cpu_usage", {})
                    precpu_usage = precpu_stats.get(
                        "cpu_usage",
                        {},
                    )

                    cpu_delta = (
                        cpu_usage.get("total_usage", 0)
                        - precpu_usage.get("total_usage", 0)
                    )

                    system_delta = (
                        cpu_stats.get("system_cpu_usage", 0)
                        - precpu_stats.get(
                            "system_cpu_usage",
                            0,
                        )
                    )

                    online_cpus = cpu_stats.get(
                        "online_cpus",
                        len(
                            cpu_usage.get(
                                "percpu_usage",
                                [],
                            )
                        )
                        or 1,
                    )

                    if system_delta > 0 and cpu_delta > 0:
                        cpu_percent = (
                            cpu_delta / system_delta
                        ) * online_cpus * 100

                    memory_usage = stats.get(
                        "memory_stats",
                        {},
                    ).get(
                        "usage",
                        0,
                    )

                    memory_mb = memory_usage / 1024 / 1024

                    container.reload()

                    started_at = container.attrs.get(
                        "State",
                        {},
                    ).get(
                        "StartedAt",
                        "",
                    )

                    if started_at:
                        started = datetime.fromisoformat(
                            started_at.replace(
                                "Z",
                                "+00:00",
                            )
                        )

                        uptime_seconds = int(
                            (
                                datetime.now(timezone.utc)
                                - started
                            ).total_seconds()
                        )

                        uptime = self.format_uptime(
                            uptime_seconds
                        )

                containers.append({
                    "name": container.name,
                    "image": image,
                    "status": container.status,
                    "cpu": round(cpu_percent, 2),
                    "memory_mb": round(memory_mb, 1),
                    "uptime": uptime,
                })

        except (
            DockerException,
            KeyError,
            TypeError,
            ValueError,
        ):
            return []

        return containers

    def list_images(self) -> list[dict[str, Any]]:
        """Retourne les images Docker disponibles."""

        client = self.get_client()

        if client is None:
            return []

        images = []

        try:
            containers = client.containers.list(all=True)

            for image in client.images.list():
                tags = image.tags or ["<none>:<none>"]
                first_tag = tags[0]

                if ":" in first_tag:
                    repository, tag = first_tag.rsplit(":", 1)
                else:
                    repository = first_tag
                    tag = "latest"

                used = any(
                    container.image.id == image.id
                    for container in containers
                )

                image_size = image.attrs.get(
                    "Size",
                    0,
                )

                created = str(
                    image.attrs.get(
                        "Created",
                        "",
                    )
                )[:10]

                images.append({
                    "id": image.short_id,
                    "repository": repository,
                    "tag": tag,
                    "size_mb": round(
                        image_size / 1024 / 1024,
                        1,
                    ),
                    "created": created or "Inconnue",
                    "used": used,
                })

        except (
            DockerException,
            KeyError,
            TypeError,
            ValueError,
        ):
            return []

        return images

    def list_volumes(self) -> list[dict[str, Any]]:
        """Retourne les volumes Docker disponibles."""

        client = self.get_client()

        if client is None:
            return []

        volumes = []

        try:
            for volume in client.volumes.list():
                volumes.append({
                    "name": volume.name,
                    "driver": volume.attrs.get(
                        "Driver",
                        "",
                    ),
                    "mountpoint": volume.attrs.get(
                        "Mountpoint",
                        "",
                    ),
                    "created": str(
                        volume.attrs.get(
                            "CreatedAt",
                            "",
                        )
                    )[:19],
                })

        except (
            DockerException,
            KeyError,
            TypeError,
            ValueError,
        ):
            return []

        return volumes

    def list_networks(self) -> list[dict[str, Any]]:
        """Retourne les réseaux Docker disponibles."""

        client = self.get_client()

        if client is None:
            return []

        networks = []

        try:
            for network in client.networks.list():
                network.reload()

                containers = network.attrs.get(
                    "Containers",
                    {},
                )

                networks.append({
                    "id": network.short_id,
                    "name": network.name,
                    "driver": network.attrs.get(
                        "Driver",
                        "",
                    ),
                    "scope": network.attrs.get(
                        "Scope",
                        "",
                    ),
                    "containers": len(containers),
                })

        except (
            DockerException,
            KeyError,
            TypeError,
            ValueError,
        ):
            return []

        return networks

    def execute_action(
        self,
        container_name: str,
        action: str,
    ) -> tuple[dict[str, Any], int]:
        """Démarre, arrête ou redémarre un conteneur autorisé."""

        if container_name not in self.allowed_containers:
            return {
                "error": "Conteneur non autorisé",
            }, 403

        if action not in {"start", "stop", "restart"}:
            return {
                "error": "Action non autorisée",
            }, 400

        if (
            container_name == "secure-web-app-v2"
            and action in {"stop", "restart"}
        ):
            return {
                "error": (
                    "L'application ne peut pas arrêter "
                    "ou redémarrer son propre conteneur."
                ),
            }, 409

        client = self.get_client()

        if client is None:
            return {
                "error": "Docker est indisponible",
            }, 503

        try:
            container = client.containers.get(
                container_name
            )

            if action == "start":
                container.start()

            elif action == "stop":
                container.stop(timeout=10)

            elif action == "restart":
                container.restart(timeout=10)

            container.reload()

            return {
                "success": True,
                "container": container.name,
                "status": container.status,
                "action": action,
            }, 200

        except NotFound:
            return {
                "error": "Conteneur introuvable",
            }, 404

        except DockerException as error:
            return {
                "error": str(error),
            }, 500

    def get_logs(
        self,
        container_name: str,
        tail: int = 200,
    ) -> tuple[dict[str, Any], int]:
        """Retourne les dernières lignes des logs d'un conteneur."""

        if container_name not in self.allowed_containers:
            return {
                "error": "Conteneur non autorisé",
            }, 403

        client = self.get_client()

        if client is None:
            return {
                "error": "Docker est indisponible",
            }, 503

        try:
            container = client.containers.get(
                container_name
            )

            logs = container.logs(
                tail=tail,
                timestamps=True,
            ).decode(
                "utf-8",
                errors="replace",
            )

            return {
                "container": container.name,
                "logs": logs.splitlines(),
            }, 200

        except NotFound:
            return {
                "error": "Conteneur introuvable",
            }, 404

        except DockerException as error:
            return {
                "error": str(error),
            }, 500