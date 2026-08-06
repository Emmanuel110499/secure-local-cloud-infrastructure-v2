from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()
TEMPLATES_DIR = ROOT / "templates"
ROUTES_DIR = ROOT / "routes"
SERVICES_DIR = ROOT / "services"
STATIC_DIR = ROOT / "static"
BACKUP_DIR = ROOT / "backups" / "portal-v3"
REPORT_PATH = ROOT / "portal-v3-inventory.json"

TARGET_TEMPLATES = [
    "base.html",
    "index_v2.html",
    "monitoring.html",
    "documentation.html",
    "containers.html",
    "images.html",
    "volumes.html",
    "networks.html",
    "logs.html",
    "prometheus.html",
    "infrastructure.html",
    "security.html",
    "audit.html",
    "assistant.html",
    "help_center.html",
    "getting_started.html",
    "faq.html",
    "account.html",
    "login.html",
]

TARGET_ROUTES = [
    "dashboard.py",
    "monitoring.py",
    "containers.py",
    "logs.py",
    "prometheus.py",
    "security.py",
    "audit.py",
    "help.py",
    "auth.py",
]

TARGET_SERVICES = [
    "docker_service.py",
    "log_service.py",
    "prometheus_service.py",
    "security_service.py",
    "audit_service.py",
    "account_service.py",
    "history_service.py",
    "health_score_service.py",
]


def backup_file(path: Path) -> str | None:
    if not path.is_file():
        return None

    relative = path.relative_to(ROOT)
    destination = BACKUP_DIR / relative

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(path, destination)

    return str(destination.relative_to(ROOT))


def extract_routes(content: str) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []

    pattern = re.compile(
        r'@[\w_]+\.route\(\s*'
        r'["\']([^"\']+)["\']'
        r'(.*?)\)\s*'
        r'(?:@login_required\s*)?'
        r'def\s+([a-zA-Z0-9_]+)',
        re.DOTALL,
    )

    for match in pattern.finditer(content):
        path = match.group(1)
        options = match.group(2)
        function = match.group(3)

        methods_match = re.search(
            r"methods\s*=\s*\[([^\]]+)\]",
            options,
        )

        methods = ["GET"]

        if methods_match:
            methods = re.findall(
                r'["\']([A-Z]+)["\']',
                methods_match.group(1),
            )

        results.append({
            "path": path,
            "function": function,
            "methods": methods,
        })

    post_pattern = re.compile(
        r'@[\w_]+\.post\(\s*'
        r'["\']([^"\']+)["\']\s*\)'
        r'\s*(?:@login_required\s*)?'
        r'def\s+([a-zA-Z0-9_]+)',
        re.DOTALL,
    )

    for match in post_pattern.finditer(content):
        results.append({
            "path": match.group(1),
            "function": match.group(2),
            "methods": ["POST"],
        })

    return results


def extract_template_information(
    path: Path,
) -> dict[str, object]:
    content = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    variables = sorted(set(
        re.findall(
            r"{{\s*([a-zA-Z_][\w.]*)",
            content,
        )
    ))

    loops = sorted(set(
        re.findall(
            r"{%\s*for\s+\w+\s+in\s+([a-zA-Z_][\w.]*)",
            content,
        )
    ))

    fetches = sorted(set(
        re.findall(
            r'fetch\(\s*[`"\']([^`"\']+)',
            content,
        )
    ))

    extends = re.findall(
        r'{%\s*extends\s+["\']([^"\']+)["\']',
        content,
    )

    return {
        "lines": len(content.splitlines()),
        "extends": extends,
        "variables": variables,
        "loops": loops,
        "fetches": fetches,
        "has_inline_style": "<style" in content,
        "has_inline_script": "<script" in content,
        "uses_bootstrap": "bootstrap" in content.lower(),
        "uses_portal_pages_css":
            "portal-pages.css" in content,
        "uses_portal_theme_v2":
            "portal-theme-v2.css" in content,
        "uses_dashboard_v2_css":
            "dashboard-v2.css" in content,
    }


def extract_service_methods(
    path: Path,
) -> list[str]:
    content = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    return re.findall(
        r"^\s{4}def\s+([a-zA-Z_][\w]*)\(",
        content,
        re.MULTILINE,
    )


def main() -> None:
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report: dict[str, object] = {
        "generated_at": datetime.now().isoformat(),
        "root": str(ROOT),
        "backups": [],
        "templates": {},
        "routes": {},
        "services": {},
    }

    for filename in TARGET_TEMPLATES:
        path = TEMPLATES_DIR / filename

        backup = backup_file(path)

        if backup:
            report["backups"].append(backup)

        if path.is_file():
            report["templates"][filename] = (
                extract_template_information(path)
            )
        else:
            report["templates"][filename] = {
                "missing": True,
            }

    for filename in TARGET_ROUTES:
        path = ROUTES_DIR / filename

        backup = backup_file(path)

        if backup:
            report["backups"].append(backup)

        if path.is_file():
            content = path.read_text(
                encoding="utf-8",
                errors="replace",
            )

            report["routes"][filename] = {
                "lines": len(content.splitlines()),
                "routes": extract_routes(content),
                "render_templates": sorted(set(
                    re.findall(
                        r'render_template\(\s*'
                        r'["\']([^"\']+)["\']',
                        content,
                    )
                )),
            }
        else:
            report["routes"][filename] = {
                "missing": True,
            }

    for filename in TARGET_SERVICES:
        path = SERVICES_DIR / filename

        backup = backup_file(path)

        if backup:
            report["backups"].append(backup)

        if path.is_file():
            report["services"][filename] = {
                "lines": len(
                    path.read_text(
                        encoding="utf-8",
                        errors="replace",
                    ).splitlines()
                ),
                "methods": extract_service_methods(path),
            }
        else:
            report["services"][filename] = {
                "missing": True,
            }

    for path in (
        STATIC_DIR / "css" / "dashboard-v2.css",
        STATIC_DIR / "css" / "portal-pages.css",
        STATIC_DIR / "css" / "portal-theme-v2.css",
        STATIC_DIR / "js" / "dashboard-v2.js",
    ):
        backup = backup_file(path)

        if backup:
            report["backups"].append(backup)

    REPORT_PATH.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Préparation Portal V3 terminée.")
    print(f"Sauvegardes : {BACKUP_DIR}")
    print(f"Inventaire : {REPORT_PATH}")
    print(
        "Nombre de fichiers sauvegardés :",
        len(report["backups"]),
    )


if __name__ == "__main__":
    main()
