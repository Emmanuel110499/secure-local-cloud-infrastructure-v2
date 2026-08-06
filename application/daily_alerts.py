from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from flask import current_app, jsonify


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "daily_alerts.db"

DEFAULT_ALERTMANAGER_URL = "http://192.168.154.20:9093"


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10,
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS alert_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT NOT NULL,
                alertname TEXT NOT NULL DEFAULT '',
                severity TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL DEFAULT '',
                starts_at TEXT NOT NULL DEFAULT '',
                event_date TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                UNIQUE(fingerprint, starts_at)
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_alert_events_date
            ON alert_events(event_date)
            """
        )

        connection.commit()


def get_alertmanager_url() -> str:
    value = (
        current_app.config.get("ALERTMANAGER_URL")
        or os.getenv("ALERTMANAGER_URL")
        or DEFAULT_ALERTMANAGER_URL
    )

    return str(value).rstrip("/")


def is_active(alert: dict[str, Any]) -> bool:
    status = alert.get("status") or {}

    return (
        str(status.get("state", "")).lower()
        == "active"
    )


def is_telegram_receiver(
    alert: dict[str, Any],
) -> bool:
    receivers = alert.get("receivers") or []

    return any(
        "telegram"
        in str(
            receiver.get("name", "")
        ).lower()
        for receiver in receivers
        if isinstance(receiver, dict)
    )


def fetch_active_alerts() -> list[dict[str, Any]]:
    response = requests.get(
        f"{get_alertmanager_url()}/api/v2/alerts",
        timeout=5,
        headers={
            "Accept": "application/json",
        },
    )

    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, list):
        return []

    return [
        alert
        for alert in payload
        if isinstance(alert, dict)
        and is_active(alert)
        and is_telegram_receiver(alert)
    ]


def register_new_events(
    alerts: list[dict[str, Any]],
) -> None:
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()

    with get_connection() as connection:
        for alert in alerts:
            labels = alert.get("labels") or {}
            annotations = (
                alert.get("annotations") or {}
            )

            fingerprint = str(
                alert.get("fingerprint", "")
            ).strip()

            starts_at = str(
                alert.get("startsAt", "")
            ).strip()

            if not fingerprint or not starts_at:
                continue

            connection.execute(
                """
                INSERT OR IGNORE INTO alert_events (
                    fingerprint,
                    alertname,
                    severity,
                    summary,
                    starts_at,
                    event_date,
                    recorded_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fingerprint,
                    str(
                        labels.get(
                            "alertname",
                            "",
                        )
                    ),
                    str(
                        labels.get(
                            "severity",
                            "",
                        )
                    ).lower(),
                    str(
                        annotations.get(
                            "summary",
                            "",
                        )
                    ),
                    starts_at,
                    today,
                    now.isoformat(),
                ),
            )

        connection.commit()


def get_daily_statistics(
    active_alerts: list[dict[str, Any]],
) -> dict[str, Any]:
    today = datetime.now(
        timezone.utc
    ).date().isoformat()

    with get_connection() as connection:
        total_row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM alert_events
            WHERE event_date = ?
            """,
            (today,),
        ).fetchone()

        severity_rows = connection.execute(
            """
            SELECT severity, COUNT(*) AS total
            FROM alert_events
            WHERE event_date = ?
            GROUP BY severity
            """,
            (today,),
        ).fetchall()

        latest_row = connection.execute(
            """
            SELECT
                alertname,
                severity,
                summary,
                starts_at
            FROM alert_events
            WHERE event_date = ?
            ORDER BY recorded_at DESC, id DESC
            LIMIT 1
            """,
            (today,),
        ).fetchone()

    severity_counts = {
        "critical": 0,
        "warning": 0,
        "info": 0,
        "unknown": 0,
    }

    for row in severity_rows:
        severity = str(
            row["severity"] or "unknown"
        ).lower()

        if severity not in severity_counts:
            severity = "unknown"

        severity_counts[severity] = row["total"]

    latest_alert = {
        "name": "",
        "severity": "",
        "summary": "",
        "starts_at": "",
    }

    if latest_row:
        latest_alert = {
            "name": latest_row["alertname"],
            "severity": latest_row["severity"],
            "summary": latest_row["summary"],
            "starts_at": latest_row["starts_at"],
        }

    return {
        "alerts_today": (
            total_row["total"]
            if total_row
            else 0
        ),
        "active_now": len(active_alerts),
        "severity_counts": severity_counts,
        "latest_alert": latest_alert,
    }


def register_daily_alerts(app) -> None:
    initialize_database()

    @app.get("/api/daily-alerts")
    def daily_alerts():
        try:
            active_alerts = fetch_active_alerts()

            register_new_events(
                active_alerts
            )

            return jsonify(
                {
                    "success": True,
                    **get_daily_statistics(
                        active_alerts
                    ),
                    "source": "Alertmanager",
                    "receiver": "telegram",
                }
            )

        except (
            requests.RequestException,
            ValueError,
        ) as error:
            current_app.logger.warning(
                "Alertmanager indisponible : %s",
                error,
            )

            return jsonify(
                {
                    "success": False,
                    "alerts_today": 0,
                    "active_now": 0,
                    "severity_counts": {
                        "critical": 0,
                        "warning": 0,
                        "info": 0,
                        "unknown": 0,
                    },
                    "latest_alert": {
                        "name": "",
                        "severity": "",
                        "summary": "",
                        "starts_at": "",
                    },
                    "error": (
                        "Alertmanager indisponible"
                    ),
                }
            ), 503
