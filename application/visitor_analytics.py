from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import jsonify, request


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "visitor_analytics.db"


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
            CREATE TABLE IF NOT EXISTS visitor_visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visitor_id TEXT NOT NULL,
                visited_at TEXT NOT NULL,
                visit_date TEXT NOT NULL,
                country TEXT NOT NULL DEFAULT '',
                country_code TEXT NOT NULL DEFAULT '',
                city TEXT NOT NULL DEFAULT '',
                page TEXT NOT NULL DEFAULT '/'
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_visitor_visits_date
            ON visitor_visits (visit_date)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_visitor_visits_visitor
            ON visitor_visits (
                visitor_id,
                visit_date
            )
            """
        )

        connection.commit()


def clean_text(
    value: object,
    maximum_length: int,
) -> str:
    text = str(value or "").strip()

    return text[:maximum_length]


def get_statistics(
    connection: sqlite3.Connection,
) -> dict:
    today = datetime.now(
        timezone.utc
    ).date().isoformat()

    visitors_row = connection.execute(
        """
        SELECT COUNT(DISTINCT visitor_id) AS total
        FROM visitor_visits
        WHERE visit_date = ?
        """,
        (today,),
    ).fetchone()

    last_visit = connection.execute(
        """
        SELECT
            country,
            country_code,
            city,
            visited_at
        FROM visitor_visits
        ORDER BY visited_at DESC, id DESC
        LIMIT 1
        """
    ).fetchone()

    country_rows = connection.execute(
        """
        SELECT
            country,
            country_code,
            MAX(visited_at) AS last_seen
        FROM visitor_visits
        WHERE country <> ''
        GROUP BY country, country_code
        ORDER BY last_seen DESC
        LIMIT 6
        """
    ).fetchall()

    countries = [
        {
            "name": row["country"],
            "code": row["country_code"],
        }
        for row in country_rows
    ]

    return {
        "visitors_today": (
            visitors_row["total"]
            if visitors_row
            else 0
        ),
        "last_visitor": {
            "country": (
                last_visit["country"]
                if last_visit
                else ""
            ),
            "country_code": (
                last_visit["country_code"]
                if last_visit
                else ""
            ),
            "city": (
                last_visit["city"]
                if last_visit
                else ""
            ),
            "visited_at": (
                last_visit["visited_at"]
                if last_visit
                else ""
            ),
        },
        "countries": countries,
        "country_count": len(countries),
    }


def register_visitor_analytics(app) -> None:
    initialize_database()

    @app.route(
        "/api/visitor-activity",
        methods=["GET", "POST"],
    )
    def visitor_activity():
        with get_connection() as connection:
            if request.method == "POST":
                payload = request.get_json(
                    silent=True
                ) or {}

                visitor_id = clean_text(
                    payload.get("visitor_id"),
                    120,
                )

                if visitor_id:
                    now = datetime.now(
                        timezone.utc
                    )

                    visit_date = (
                        now.date().isoformat()
                    )

                    already_counted = (
                        connection.execute(
                            """
                            SELECT id
                            FROM visitor_visits
                            WHERE visitor_id = ?
                              AND visit_date = ?
                            LIMIT 1
                            """,
                            (
                                visitor_id,
                                visit_date,
                            ),
                        ).fetchone()
                    )

                    country = clean_text(
                        payload.get("country"),
                        80,
                    )

                    country_code = clean_text(
                        payload.get(
                            "country_code"
                        ),
                        8,
                    ).upper()

                    city = clean_text(
                        payload.get("city"),
                        100,
                    )

                    page = clean_text(
                        payload.get("page"),
                        200,
                    ) or "/"

                    if already_counted:
                        connection.execute(
                            """
                            UPDATE visitor_visits
                            SET
                                visited_at = ?,
                                country = ?,
                                country_code = ?,
                                city = ?,
                                page = ?
                            WHERE id = ?
                            """,
                            (
                                now.isoformat(),
                                country,
                                country_code,
                                city,
                                page,
                                already_counted["id"],
                            ),
                        )
                    else:
                        connection.execute(
                            """
                            INSERT INTO visitor_visits (
                                visitor_id,
                                visited_at,
                                visit_date,
                                country,
                                country_code,
                                city,
                                page
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                visitor_id,
                                now.isoformat(),
                                visit_date,
                                country,
                                country_code,
                                city,
                                page,
                            ),
                        )

                    connection.commit()

            return jsonify(
                {
                    "success": True,
                    **get_statistics(connection),
                }
            )
