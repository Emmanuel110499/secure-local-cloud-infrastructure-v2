from __future__ import annotations

import hashlib
import html
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests
from flask import jsonify, request


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "telegram_notifications.db"
PARIS_TIMEZONE = ZoneInfo("Europe/Paris")


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
            CREATE TABLE IF NOT EXISTS telegram_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sent_at TEXT NOT NULL,
                event_date TEXT NOT NULL,
                status TEXT NOT NULL,
                alert_count INTEGER NOT NULL DEFAULT 0,
                message_hash TEXT NOT NULL,
                telegram_message_id INTEGER
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_telegram_notifications_date
            ON telegram_notifications(event_date)
            """
        )

        connection.commit()


def clean(value: object) -> str:
    return str(value or "").strip()


def severity_icon(value: object) -> str:
    severity = clean(value).lower()

    return {
        "critical": "🔴",
        "warning": "🟠",
        "info": "🔵",
    }.get(severity, "⚪")


def build_message(payload: dict[str, Any]) -> str:
    status = clean(payload.get("status")).lower()
    alerts = payload.get("alerts") or []

    if not isinstance(alerts, list):
        alerts = []

    if status == "resolved":
        header = "✅ <b>ALERTE RÉSOLUE</b>"
    else:
        header = "🚨 <b>ALERTE INFRASTRUCTURE</b>"

    sections = [header]

    for alert in alerts:
        if not isinstance(alert, dict):
            continue

        labels = alert.get("labels") or {}
        annotations = alert.get("annotations") or {}

        alertname = html.escape(
            clean(labels.get("alertname"))
            or "Alerte sans nom"
        )

        instance = html.escape(
            clean(labels.get("instance"))
            or "Non précisée"
        )

        severity = html.escape(
            clean(labels.get("severity"))
            or "Non définie"
        )

        summary = html.escape(
            clean(annotations.get("summary"))
            or "Aucun résumé"
        )

        description = html.escape(
            clean(annotations.get("description"))
            or "Aucun détail supplémentaire"
        )

        sections.append(
            "\n".join(
                [
                    "",
                    f"📌 <b>Alerte :</b> {alertname}",
                    f"🖥 <b>Instance :</b> {instance}",
                    (
                        f"{severity_icon(severity)} "
                        f"<b>Sévérité :</b> {severity}"
                    ),
                    f"📝 <b>Résumé :</b> {summary}",
                    f"🔎 <b>Détails :</b> {description}",
                ]
            )
        )

    sections.append(
        "\n📊 Message envoyé par Secure Local Cloud."
    )

    return "\n".join(sections)


def send_telegram_message(
    message: str,
) -> dict[str, Any]:
    token = clean(
        os.getenv("TELEGRAM_BOT_TOKEN")
    )

    chat_id = clean(
        os.getenv("TELEGRAM_CHAT_ID")
    )

    if not token or not chat_id:
        raise RuntimeError(
            "Configuration Telegram absente."
        )

    response = requests.post(
        (
            "https://api.telegram.org/"
            f"bot{token}/sendMessage"
        ),
        data={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        },
        timeout=10,
    )

    response.raise_for_status()

    result = response.json()

    if result.get("ok") is not True:
        raise RuntimeError(
            result.get("description")
            or "Telegram a refusé le message."
        )

    return result


def save_successful_notification(
    payload: dict[str, Any],
    message: str,
    telegram_result: dict[str, Any],
) -> None:
    now = datetime.now(PARIS_TIMEZONE)
    alerts = payload.get("alerts") or []

    result = telegram_result.get("result") or {}

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO telegram_notifications (
                sent_at,
                event_date,
                status,
                alert_count,
                message_hash,
                telegram_message_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                now.isoformat(),
                now.date().isoformat(),
                clean(payload.get("status"))
                or "unknown",
                len(alerts)
                if isinstance(alerts, list)
                else 0,
                hashlib.sha256(
                    message.encode("utf-8")
                ).hexdigest(),
                result.get("message_id"),
            ),
        )

        connection.commit()


def get_notification_stats() -> dict[str, Any]:
    today = datetime.now(
        PARIS_TIMEZONE
    ).date().isoformat()

    with get_connection() as connection:
        total_row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM telegram_notifications
            WHERE event_date = ?
            """,
            (today,),
        ).fetchone()

        latest_row = connection.execute(
            """
            SELECT
                sent_at,
                status,
                alert_count,
                telegram_message_id
            FROM telegram_notifications
            WHERE event_date = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (today,),
        ).fetchone()

    latest = None

    if latest_row:
        latest = {
            "sent_at": latest_row["sent_at"],
            "status": latest_row["status"],
            "alert_count": latest_row["alert_count"],
            "telegram_message_id": (
                latest_row["telegram_message_id"]
            ),
        }

    return {
        "today": (
            total_row["total"]
            if total_row
            else 0
        ),
        "latest": latest,
    }


def register_telegram_relay(app) -> None:
    initialize_database()

    @app.post("/api/alertmanager-telegram")
    def alertmanager_telegram():
        expected_secret = clean(
            os.getenv("ALERT_WEBHOOK_SECRET")
        )

        received_secret = clean(
            request.args.get("token")
        )

        if (
            not expected_secret
            or received_secret != expected_secret
        ):
            return jsonify(
                {
                    "success": False,
                    "error": "Accès refusé",
                }
            ), 403

        payload = request.get_json(
            silent=True
        )

        if not isinstance(payload, dict):
            return jsonify(
                {
                    "success": False,
                    "error": "Payload invalide",
                }
            ), 400

        try:
            message = build_message(payload)

            telegram_result = (
                send_telegram_message(message)
            )

            save_successful_notification(
                payload,
                message,
                telegram_result,
            )

            return jsonify(
                {
                    "success": True,
                    "telegram_message_id": (
                        telegram_result
                        .get("result", {})
                        .get("message_id")
                    ),
                }
            )

        except (
            requests.RequestException,
            RuntimeError,
        ) as error:
            app.logger.exception(
                "Échec du relais Telegram."
            )

            return jsonify(
                {
                    "success": False,
                    "error": str(error),
                }
            ), 502

    @app.get("/api/telegram-notifications")
    def telegram_notifications():
        return jsonify(
            {
                "success": True,
                **get_notification_stats(),
            }
        )
