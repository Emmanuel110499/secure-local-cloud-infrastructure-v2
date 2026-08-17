from time import time
from typing import Any

import requests


class PrometheusService:
    """Interroge Prometheus et prépare les métriques du portail."""

    def __init__(
        self,
        prometheus_url: str,
        *,
        node_exporter_job: str,
        cadvisor_job: str,
        node_exporter_instance: str,
        cadvisor_instance: str,
        equipments: dict[str, dict[str, str]] | None = None,
    ):
        self.prometheus_url = prometheus_url.rstrip("/")
        self.node_exporter_job = node_exporter_job
        self.cadvisor_job = cadvisor_job
        self.node_exporter_instance = node_exporter_instance
        self.cadvisor_instance = cadvisor_instance
        self.equipments = equipments or {
            "vps-production": {
                "id": "vps-production",
                "name": "VPS Production",
                "role": "Hébergement et observabilité",
                "os": "linux",
                "job": node_exporter_job,
                "instance": node_exporter_instance,
                "docker_job": cadvisor_job,
                "docker_instance": cadvisor_instance,
                "monitored": True,
            }
        }

    @staticmethod
    def _metric_value(value: float | None, digits: int = 1):
        return round(value, digits) if value is not None else None

    def _first_scalar(self, *queries: str) -> float | None:
        """Essaie plusieurs noms de métriques compatibles exporter."""

        for query in queries:
            value = self.query_scalar(query)
            if value is not None:
                return value
        return None

    @staticmethod
    def _labels(equipment: dict[str, str]) -> str:
        return (
            f'job="{equipment["job"]}",'
            f'instance="{equipment["instance"]}"'
        )

    def get_equipment_catalog(self) -> list[dict[str, Any]]:
        """Retourne le catalogue public, sans information sensible."""

        return [
            {
                "id": item["id"],
                "name": item["name"],
                "role": item["role"],
                "os": item["os"],
                "monitored": item.get("monitored", True),
            }
            for item in self.equipments.values()
        ]

    def get_equipment_metrics(self, equipment_id: str) -> dict[str, Any] | None:
        """Retourne les KPI actuels d'un équipement Linux ou Windows."""

        equipment = self.equipments.get(equipment_id)
        if equipment is None:
            return None

        if not equipment.get("monitored", True):
            return {
                "equipment": {
                    "id": equipment["id"],
                    "name": equipment["name"],
                    "role": equipment["role"],
                    "os": equipment["os"],
                    "monitored": False,
                },
                "state": "disconnected",
                "metrics": {},
            }

        labels = self._labels(equipment)
        availability = self.query_scalar(f'up{{{labels}}}')

        if equipment["os"] == "windows":
            metrics = self._get_windows_metrics(equipment, labels)
        else:
            metrics = self._get_linux_metrics(equipment, labels)

        if availability is None:
            state = "unknown"
        else:
            state = "up" if availability == 1 else "down"

        return {
            "equipment": {
                "id": equipment["id"],
                "name": equipment["name"],
                "role": equipment["role"],
                "os": equipment["os"],
                "monitored": equipment.get("monitored", True),
            },
            "state": state,
            "metrics": metrics,
        }

    def get_all_equipment_metrics(self) -> list[dict[str, Any]]:
        return [
            result
            for equipment_id in self.equipments
            if (result := self.get_equipment_metrics(equipment_id)) is not None
        ]

    def get_equipment_history(
        self,
        equipment_id: str,
        hours: int = 24,
    ) -> dict[str, Any] | None:
        """Retourne les séries CPU, RAM et disque d'un équipement."""

        equipment = self.equipments.get(equipment_id)
        if equipment is None:
            return None

        if not equipment.get("monitored", True):
            return {
                "equipment": {
                    "id": equipment["id"],
                    "name": equipment["name"],
                    "role": equipment["role"],
                    "os": equipment["os"],
                    "monitored": False,
                },
                "hours": max(1, min(int(hours), 168)),
                "series": {"cpu": [], "memory": [], "disk": []},
            }

        hours = max(1, min(int(hours), 168))
        labels = self._labels(equipment)

        if equipment["os"] == "windows":
            queries = {
                "cpu": (
                    '100 - (avg(rate(windows_cpu_time_total{'
                    f'{labels},mode="idle"'
                    '}[5m])) * 100)'
                ),
                "memory": (
                    '100 * (1 - windows_memory_available_bytes{'
                    f'{labels}'
                    '} / windows_memory_physical_total_bytes{'
                    f'{labels}'
                    '})'
                ),
                "disk": (
                    '100 * (1 - windows_logical_disk_free_bytes{'
                    f'{labels},volume="C:"'
                    '} / windows_logical_disk_size_bytes{'
                    f'{labels},volume="C:"'
                    '})'
                ),
            }
        else:
            queries = {
                "cpu": (
                    '100 - (avg(rate(node_cpu_seconds_total{'
                    f'{labels},mode="idle"'
                    '}[5m])) * 100)'
                ),
                "memory": (
                    '(1 - node_memory_MemAvailable_bytes{'
                    f'{labels}'
                    '} / node_memory_MemTotal_bytes{'
                    f'{labels}'
                    '}) * 100'
                ),
                "disk": (
                    '100 * (1 - node_filesystem_avail_bytes{'
                    f'{labels},mountpoint="/",fstype!~"tmpfs|overlay"'
                    '} / node_filesystem_size_bytes{'
                    f'{labels},mountpoint="/",fstype!~"tmpfs|overlay"'
                    '})'
                ),
            }

        end = int(time())
        start = end - hours * 3600
        step = max(60, hours * 60)

        return {
            "equipment": {
                "id": equipment["id"],
                "name": equipment["name"],
                "role": equipment["role"],
                "os": equipment["os"],
            },
            "hours": hours,
            "series": {
                name: self.query_range(query, start, end, step)
                for name, query in queries.items()
            },
        }

    def get_global_history(self, hours: int = 24) -> dict[str, Any]:
        """Agrège les historiques des équipements pour la vue globale."""

        histories = [
            history
            for equipment_id in self.equipments
            if (history := self.get_equipment_history(equipment_id, hours))
        ]

        aggregated: dict[str, list[dict[str, float]]] = {}
        for metric in ("cpu", "memory", "disk"):
            available = [
                history["series"].get(metric, [])
                for history in histories
                if history["series"].get(metric)
            ]
            length = min((len(series) for series in available), default=0)
            aggregated[metric] = [
                {
                    "timestamp": available[0][index]["timestamp"],
                    "value": round(
                        sum(series[index]["value"] for series in available)
                        / len(available),
                        2,
                    ),
                }
                for index in range(length)
            ]

        return {
            "equipment": {
                "id": "global",
                "name": "Vue globale",
                "role": "État consolidé de l’infrastructure",
                "os": "multi",
            },
            "hours": max(1, min(int(hours), 168)),
            "series": aggregated,
        }

    def _get_linux_metrics(
        self,
        equipment: dict[str, str],
        labels: str,
    ) -> dict[str, Any]:
        cpu = self.query_scalar(
            '100 - (avg(rate(node_cpu_seconds_total{'
            f'{labels},mode="idle"'
            '}[5m])) * 100)'
        )
        memory = self.query_scalar(
            '(1 - node_memory_MemAvailable_bytes{'
            f'{labels}'
            '} / node_memory_MemTotal_bytes{'
            f'{labels}'
            '}) * 100'
        )
        disk = self.query_scalar(
            '100 * (1 - node_filesystem_avail_bytes{'
            f'{labels},mountpoint="/",fstype!~"tmpfs|overlay"'
            '} / node_filesystem_size_bytes{'
            f'{labels},mountpoint="/",fstype!~"tmpfs|overlay"'
            '})'
        )
        uptime = self.query_scalar(
            f'time() - node_boot_time_seconds{{{labels}}}'
        )
        receive = self.query_scalar(
            'sum(rate(node_network_receive_bytes_total{'
            f'{labels},device!~"lo|docker.*|veth.*|br-.*"'
            '}[1m]))'
        )
        transmit = self.query_scalar(
            'sum(rate(node_network_transmit_bytes_total{'
            f'{labels},device!~"lo|docker.*|veth.*|br-.*"'
            '}[1m]))'
        )
        load = self.query_scalar(f'node_load1{{{labels}}}')
        processes = self.query_scalar(f'node_procs_running{{{labels}}}')
        disk_total = self.query_scalar(
            f'node_filesystem_size_bytes{{{labels},mountpoint="/",fstype!~"tmpfs|overlay"}}'
        )
        disk_available = self.query_scalar(
            f'node_filesystem_avail_bytes{{{labels},mountpoint="/",fstype!~"tmpfs|overlay"}}'
        )

        result = self._common_metrics(
            cpu, memory, disk, uptime, receive, transmit
        )
        result.update({
            "load_1m": self._metric_value(load, 2),
            "processes": int(processes) if processes is not None else None,
            "disk_total_bytes": disk_total,
            "disk_available_bytes": disk_available,
        })

        docker_job = equipment.get("docker_job")
        docker_instance = equipment.get("docker_instance")
        if docker_job and docker_instance:
            containers = self.query_scalar(
                'count(container_last_seen{'
                f'job="{docker_job}",instance="{docker_instance}",name!=""'
                '})'
            )
            result["containers"] = (
                int(containers) if containers is not None else None
            )
        if equipment["id"] in ("vps-production", "srv-monitoring"):
            result["volumes"] = self._get_monitoring_volumes()
        return result

    def _get_monitoring_volumes(self) -> list[dict[str, Any]]:
        """Lit les tailles réelles publiées par le collecteur textfile."""

        rows = []
        for item in self.query_vector(
            'secure_docker_volume_size_bytes{equipment=~"vps-production|srv-monitoring"}'
        ):
            try:
                labels = item.get("metric", {})
                rows.append({
                    "name": labels.get("logical_name") or labels.get("volume"),
                    "docker_name": labels.get("volume"),
                    "mountpoint": labels.get("mountpoint", "Volume Docker"),
                    "used_bytes": float(item["value"][1]),
                })
            except (TypeError, ValueError, KeyError, IndexError):
                continue
        return sorted(rows, key=lambda row: row["name"] or "")

    def _get_windows_metrics(
        self,
        equipment: dict[str, str],
        labels: str,
    ) -> dict[str, Any]:
        cpu = self.query_scalar(
            '100 - (avg(rate(windows_cpu_time_total{'
            f'{labels},mode="idle"'
            '}[5m])) * 100)'
        )
        memory = self._first_scalar(
            '100 * (1 - windows_memory_available_bytes{'
            f'{labels}'
            '} / windows_memory_physical_total_bytes{'
            f'{labels}'
            '})',
            '100 * (1 - windows_memory_physical_free_bytes{'
            f'{labels}'
            '} / windows_memory_physical_total_bytes{'
            f'{labels}'
            '})',
            '100 * (1 - windows_memory_available_bytes{'
            f'{labels}'
            '} / windows_cs_physical_memory_bytes{'
            f'{labels}'
            '})',
            '100 * (1 - windows_os_physical_memory_free_bytes{'
            f'{labels}'
            '} / windows_cs_physical_memory_bytes{'
            f'{labels}'
            '})',
        )
        disk = self.query_scalar(
            '100 * (1 - windows_logical_disk_free_bytes{'
            f'{labels},volume="C:"'
            '} / windows_logical_disk_size_bytes{'
            f'{labels},volume="C:"'
            '})'
        )
        uptime = self._first_scalar(
            f'time() - windows_system_system_up_time{{{labels}}}',
            f'time() - windows_os_system_up_time{{{labels}}}',
        )
        receive = self.query_scalar(
            f'sum(rate(windows_net_bytes_received_total{{{labels}}}[1m]))'
        )
        transmit = self.query_scalar(
            f'sum(rate(windows_net_bytes_sent_total{{{labels}}}[1m]))'
        )
        disk_total = self.query_scalar(
            f'windows_logical_disk_size_bytes{{{labels},volume="C:"}}'
        )
        disk_available = self.query_scalar(
            f'windows_logical_disk_free_bytes{{{labels},volume="C:"}}'
        )
        result = self._common_metrics(
            cpu, memory, disk, uptime, receive, transmit
        )
        battery_label = equipment.get("equipment_label", equipment["id"])
        battery = self.query_scalar(
            'secure_windows_battery_charge_percent{'
            f'equipment="{battery_label}"'
            '}'
        )
        ac_power = self.query_scalar(
            'secure_windows_battery_on_ac_power{'
            f'equipment="{battery_label}"'
            '}'
        )
        collector_time = self.query_scalar(
            'secure_windows_battery_collector_last_success_unixtime{'
            f'equipment="{battery_label}"'
            '}'
        )
        collector_age = self.query_scalar(
            'time() - secure_windows_battery_collector_last_success_unixtime{'
            f'equipment="{battery_label}"'
            '}'
        )
        result["battery"] = {
            "charge_percent": self._metric_value(battery),
            "on_ac_power": (
                bool(ac_power) if ac_power is not None else None
            ),
            "collector_last_success_unixtime": collector_time,
            "collector_age_seconds": self._metric_value(collector_age, 0),
        }
        result["disk_total_bytes"] = disk_total
        result["disk_available_bytes"] = disk_available
        return result

    def _common_metrics(
        self,
        cpu: float | None,
        memory: float | None,
        disk: float | None,
        uptime: float | None,
        receive: float | None,
        transmit: float | None,
    ) -> dict[str, Any]:
        uptime_seconds = int(uptime) if uptime is not None else 0
        return {
            "cpu": self._metric_value(cpu),
            "memory": self._metric_value(memory),
            "disk": self._metric_value(disk),
            "uptime_seconds": uptime_seconds if uptime is not None else None,
            "uptime": (
                self.format_uptime(uptime_seconds)
                if uptime is not None
                else "Non disponible"
            ),
            "network_receive_kbps": (
                self._metric_value(receive / 1024)
                if receive is not None else None
            ),
            "network_transmit_kbps": (
                self._metric_value(transmit / 1024)
                if transmit is not None else None
            ),
        }

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

    def query_range(
        self,
        query: str,
        start: int,
        end: int,
        step: int,
    ) -> list[dict[str, float]]:
        """Retourne une série Prometheus normalisée pour les graphiques."""

        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query_range",
                params={
                    "query": query,
                    "start": start,
                    "end": end,
                    "step": step,
                },
                timeout=8,
            )
            response.raise_for_status()
            payload = response.json()
            results = payload.get("data", {}).get("result", [])
            if payload.get("status") != "success" or not results:
                return []
            return [
                {"timestamp": float(point[0]), "value": round(float(point[1]), 2)}
                for point in results[0].get("values", [])
            ]
        except (
            requests.RequestException,
            ValueError,
            TypeError,
            KeyError,
            IndexError,
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
            f'job="{self.node_exporter_job}",mode="idle"'
            '}[5m])) * 100)'
        )

        memory = self.query_scalar(
            '(1 - '
            'node_memory_MemAvailable_bytes{'
            f'job="{self.node_exporter_job}"'
            '} '
            '/ '
            'node_memory_MemTotal_bytes{'
            f'job="{self.node_exporter_job}"'
            '}'
            ') * 100'
        )

        disk = self.query_scalar(
            '100 * (1 - '
            'node_filesystem_avail_bytes{'
            f'job="{self.node_exporter_job}",'
            'mountpoint="/",'
            'fstype!~"tmpfs|overlay"'
            '} / '
            'node_filesystem_size_bytes{'
            f'job="{self.node_exporter_job}",'
            'mountpoint="/",'
            'fstype!~"tmpfs|overlay"'
            '})'
        )

        targets = self.query_scalar("sum(up)")

        containers = self.query_scalar(
            'count(container_last_seen{'
            f'job="{self.cadvisor_job}",'
            'name!=""'
            '})'
        )

        uptime = self.query_scalar(
            'time() - node_boot_time_seconds{'
            f'job="{self.node_exporter_job}"'
            '}'
        )

        load_1m = self.query_scalar(
            'node_load1{'
            f'job="{self.node_exporter_job}"'
            '}'
        )

        processes = self.query_scalar(
            'node_procs_running{'
            f'job="{self.node_exporter_job}"'
            '}'
        )

        network_receive = self.query_scalar(
            'sum(rate(node_network_receive_bytes_total{'
            f'job="{self.node_exporter_job}",'
            'device!~"lo|docker.*|veth.*|br-.*"'
            '}[1m]))'
        )

        network_transmit = self.query_scalar(
            'sum(rate(node_network_transmit_bytes_total{'
            f'job="{self.node_exporter_job}",'
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
            f'job="{self.node_exporter_job}",'
            f'instance="{self.node_exporter_instance}"'
            '}'
        )

        cadvisor = self.query_scalar(
            'up{'
            f'job="{self.cadvisor_job}",'
            f'instance="{self.cadvisor_instance}"'
            '}'
        )

        return {
            "node_exporter": node_exporter == 1,
            "cadvisor": cadvisor == 1,
        }

    def get_service_status_detailed(self) -> dict[str, str]:
        """Distingue une cible UP, DOWN et impossible à vérifier."""

        def state(value: float | None) -> str:
            if value is None:
                return "unknown"
            return "up" if value == 1 else "down"

        node_exporter = self.query_scalar(
            'up{'
            f'job="{self.node_exporter_job}",'
            f'instance="{self.node_exporter_instance}"'
            '}'
        )
        cadvisor = self.query_scalar(
            'up{'
            f'job="{self.cadvisor_job}",'
            f'instance="{self.cadvisor_instance}"'
            '}'
        )

        return {
            "node_exporter": state(node_exporter),
            "cadvisor": state(cadvisor),
        }

    def get_health_status(self) -> str:
        """Retourne up, down ou unknown pour Prometheus."""

        try:
            response = requests.get(
                f"{self.prometheus_url}/-/healthy",
                timeout=4,
            )
        except requests.RequestException:
            return "unknown"

        return "up" if response.status_code == 200 else "down"

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
