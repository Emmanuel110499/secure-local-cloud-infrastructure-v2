from __future__ import annotations

from datetime import datetime, timezone

from flask import request, session


PAGES = {
    "/": {
        "title": "Accueil",
        "icon": "🏠",
    },
    "/monitoring": {
        "title": "Monitoring",
        "icon": "📈",
    },
    "/documentation": {
        "title": "Documentation",
        "icon": "📚",
    },
    "/containers": {
        "title": "Conteneurs Docker",
        "icon": "🐳",
    },
    "/infrastructure": {
        "title": "Infrastructure",
        "icon": "🖥️",
    },
    "/security": {
        "title": "Sécurité",
        "icon": "🔐",
    },
    "/audit": {
        "title": "Audit",
        "icon": "📜",
    },
    "/assistant": {
        "title": "Emma_IA",
        "icon": "🤖",
    },
}


def format_relative_time(visited_at: str) -> str:
    try:
        visited = datetime.fromisoformat(visited_at)
        now = datetime.now(timezone.utc)

        if visited.tzinfo is None:
            visited = visited.replace(tzinfo=timezone.utc)

        seconds = max(
            0,
            int((now - visited).total_seconds()),
        )
    except (TypeError, ValueError):
        return "À l’instant"

    if seconds < 45:
        return "À l’instant"

    minutes = seconds // 60

    if minutes < 60:
        return f"Il y a {minutes} min"

    hours = minutes // 60

    if hours < 24:
        return f"Il y a {hours} h"

    days = hours // 24

    if days == 1:
        return "Hier"

    return f"Il y a {days} j"


def register_recent_activity(app) -> None:
    @app.before_request
    def remember_recent_page() -> None:
        if request.method != "GET":
            return

        path = request.path.rstrip("/") or "/"
        definition = PAGES.get(path)

        if not definition:
            return

        history = session.get(
            "recent_activity",
            [],
        )

        if not isinstance(history, list):
            history = []

        history = [
            item
            for item in history
            if item.get("path") != path
        ]

        history.insert(
            0,
            {
                "path": path,
                "title": definition["title"],
                "icon": definition["icon"],
                "visited_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
        )

        session["recent_activity"] = history[:3]
        session.modified = True

    @app.context_processor
    def inject_recent_activity() -> dict:
        history = session.get(
            "recent_activity",
            [],
        )

        if not isinstance(history, list):
            history = []

        recent_pages = []

        for index, item in enumerate(history[:3]):
            recent_pages.append(
                {
                    **item,
                    "position": index + 1,
                    "relative_time": format_relative_time(
                        item.get("visited_at", "")
                    ),
                }
            )

        return {
            "recent_pages": recent_pages,
        }
