from typing import Any

import requests


class PrometheusService:
    """Interroge Prometheus et prépare les métriques du portail."""

    def __init__(self, prometheus_url: str):
        self.prometheus_url = prometheus_url.rstrip("/")

    def query_scalar(self, query: str) -> float | None:
        """Retourne la première valeur d'une requête PromQL."""

        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": query},
                timeout=5,
            )
            response.raise_for_status()

            payload = response.json()

            if payload.get("status") != "success":
                return None

            results = payload.get(
                "data",
                {},
            ).get(
                "result",
                [],
            )

            if not results:
                return None

            return float(results[0]["value"][1])

        except (
            requests.RequestException,
            ValueError,
            TypeError,
            KeyError,
            IndexError,
        ):
            return None

    def query_vector(self, query: str) -> list[dict[str, Any]]:
        """Retourne tous les résultats d'une requête PromQL."""

    
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": query},
                timeout=5,
            )
            response.raise_for_status()

            payload = response.json()

            if payload.get("status") != "success":
                return []

            return payload.get(
                "data",
                {},
            ).get(
                "result",
                [],
            )

        except (
            requests.RequestException,
            ValueError,
            TypeError,
        ):
            return []

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

    def get_system_metrics(self) -> dict:
        """Retourne les principales métriques de srv-web."""

        cpu = self.query_scalar(
            '100 - (avg(rate('
            'node_cpu_seconds_total{'
            'job="srv-web",mode="idle"'
            '}[5m])) * 100)'
        )

        memory = self.query_scalar(
            '(1 - '
            'node_memory_MemAvailable_bytes{job="srv-web"} '
            '/ '
            'node_memory_MemTotal_bytes{job="srv-web"}'
            ') * 100'
        )

        disk = self.query_scalar(
            '100 * (1 - '
            'node_filesystem_avail_bytes{'
            'job="srv-web",'
            'mountpoint="/",'
            'fstype!~"tmpfs|overlay"'
            '} / '
            'node_filesystem_size_bytes{'
            'job="srv-web",'
            'mountpoint="/",'
            'fstype!~"tmpfs|overlay"'
            '})'
        )

        targets = self.query_scalar("sum(up)")

        containers = self.query_scalar(
            'count(container_last_seen{'
            'job="cadvisor",'
            'name!=""'
            '})'
        )

        uptime = self.query_scalar(
            'time() - node_boot_time_seconds{job="srv-web"}'
        )

        load_1m = self.query_scalar(
            'node_load1{job="srv-web"}'
        )

        processes = self.query_scalar(
            'node_procs_running{job="srv-web"}'
        )

        network_receive = self.query_scalar(
            'sum(rate(node_network_receive_bytes_total{'
            'job="srv-web",'
            'device!~"lo|docker.*|veth.*|br-.*"'
            '}[1m]))'
        )

        network_transmit = self.query_scalar(
            'sum(rate(node_network_transmit_bytes_total{'
            'job="srv-web",'
            'device!~"lo|docker.*|veth.*|br-.*"'
            '}[1m]))'
        )

        uptime_seconds = (
            int(uptime)
            if uptime is not None
            else 0
        )

        return {
            "cpu": round(cpu, 1) if cpu is not None else None,
            "memory": (
                round(memory, 1)
                if memory is not None
                else None
            ),
            "disk": (
                round(disk, 1)
                if disk is not None
                else None
            ),
            "targets": (
                int(targets)
                if targets is not None
                else 0
            ),
            "containers": (
                int(containers)
                if containers is not None
                else 0
            ),
            "uptime_seconds": uptime_seconds,
            "uptime": self.format_uptime(uptime_seconds),
            "load_1m": (
                round(load_1m, 2)
                if load_1m is not None
                else None
            ),
            "processes": (
                int(processes)
                if processes is not None
                else 0
            ),
            "network_receive_kbps": (
                round(network_receive / 1024, 1)
                if network_receive is not None
                else 0
            ),
            "network_transmit_kbps": (
                round(network_transmit / 1024, 1)
                if network_transmit is not None
                else 0
            ),
        }

    def get_targets(self) -> list[dict[str, Any]]:
        """Retourne l'état de toutes les cibles Prometheus."""

        return self.query_vector("up")


    def get_service_status(self) -> dict:
        """Retourne l'état de Node Exporter et cAdvisor."""

        node_exporter = self.query_scalar(
            'up{'
            'job="srv-web",'
            'instance="192.168.50.10:9100"'
            '}'
        )

        cadvisor = self.query_scalar(
            'up{'
            'job="cadvisor",'
            'instance="192.168.50.10:8080"'
            '}'
        )

        return {
            "node_exporter": node_exporter == 1,
            "cadvisor": cadvisor == 1,
        }

    def is_healthy(self) -> bool:
        """Vérifie que Prometheus répond."""

        try:
            response = requests.get(
                f"{self.prometheus_url}/-/healthy",
                timeout=4,
            )

            return response.status_code == 200

        except requests.RequestException:
            return False