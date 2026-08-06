from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Any
import json


class HistoryService:
    """Enregistre un historique compact des métriques."""

    def __init__(
        self,
        history_path: str | Path,
        interval_minutes: int = 5,
        retention_days: int = 7,
    ) -> None:
        self.history_path = Path(history_path)
        self.interval = timedelta(
            minutes=interval_minutes
        )
        self.retention = timedelta(
            days=retention_days
        )
        self._lock = Lock()

        self.history_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.history_path.exists():
            self._write([])

    def _read(self) -> list[dict[str, Any]]:
        try:
            data = json.loads(
                self.history_path.read_text(
                    encoding="utf-8"
                )
            )

            return data if isinstance(data, list) else []
        except (
            OSError,
            json.JSONDecodeError,
        ):
            return []

    def _write(
        self,
        records: list[dict[str, Any]],
    ) -> None:
        temporary_path = self.history_path.with_suffix(
            ".tmp"
        )

        temporary_path.write_text(
            json.dumps(
                records,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        temporary_path.replace(self.history_path)

    @staticmethod
    def _parse_date(
        value: object,
    ) -> datetime | None:
        try:
            return datetime.fromisoformat(str(value))
        except (TypeError, ValueError):
            return None

    def record_if_due(
        self,
        metrics: dict[str, Any],
    ) -> bool:
        """Enregistre au maximum une mesure par intervalle."""

        now = datetime.now()

        with self._lock:
            records = self._read()

            if records:
                last_date = self._parse_date(
                    records[-1].get("timestamp")
                )

                if (
                    last_date is not None
                    and now - last_date < self.interval
                ):
                    return False

            record = {
                "timestamp": now.isoformat(
                    timespec="seconds"
                ),
                "cpu": metrics.get("cpu"),
                "memory": metrics.get("memory"),
                "disk": metrics.get("disk"),
                "containers": metrics.get(
                    "containers",
                    0,
                ),
                "targets": metrics.get("targets", 0),
                "load_1m": metrics.get("load_1m"),
                "processes": metrics.get(
                    "processes",
                    0,
                ),
                "network_receive_kbps": metrics.get(
                    "network_receive_kbps",
                    0,
                ),
                "network_transmit_kbps": metrics.get(
                    "network_transmit_kbps",
                    0,
                ),
            }

            records.append(record)

            retention_limit = now - self.retention

            records = [
                item
                for item in records
                if (
                    self._parse_date(
                        item.get("timestamp")
                    )
                    or now
                ) >= retention_limit
            ]

            self._write(records)

        return True

    def get_history(
        self,
        hours: int = 24,
    ) -> list[dict[str, Any]]:
        """Retourne les mesures récentes."""

        hours = max(1, min(hours, 168))
        limit = datetime.now() - timedelta(hours=hours)

        return [
            item
            for item in self._read()
            if (
                self._parse_date(
                    item.get("timestamp")
                )
                or datetime.min
            ) >= limit
        ]

    def get_summary(
        self,
        hours: int = 24,
    ) -> dict[str, Any]:
        records = self.get_history(hours)

        if not records:
            return {
                "period_hours": hours,
                "samples": 0,
            }

        def values(key: str) -> list[float]:
            result = []

            for item in records:
                value = item.get(key)

                if isinstance(value, (int, float)):
                    result.append(float(value))

            return result

        summary: dict[str, Any] = {
            "period_hours": hours,
            "samples": len(records),
            "first_timestamp": records[0].get(
                "timestamp"
            ),
            "last_timestamp": records[-1].get(
                "timestamp"
            ),
        }

        for key in ("cpu", "memory", "disk"):
            metric_values = values(key)

            if metric_values:
                summary[key] = {
                    "minimum": round(
                        min(metric_values),
                        1,
                    ),
                    "maximum": round(
                        max(metric_values),
                        1,
                    ),
                    "average": round(
                        sum(metric_values)
                        / len(metric_values),
                        1,
                    ),
                    "latest": round(
                        metric_values[-1],
                        1,
                    ),
                }

        return summary
