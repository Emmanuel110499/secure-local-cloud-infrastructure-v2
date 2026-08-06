#!/usr/bin/env bash

set -u

APP_URL="https://app.emmanuelinfra.fr"
ALERTMANAGER_URL="http://192.168.154.20:9093"
PROMETHEUS_URL="http://192.168.154.20:9090"

line() {
    printf '\n============================================================\n'
    printf '%s\n' "$1"
    printf '============================================================\n'
}

check_url() {
    local name="$1"
    local url="$2"

    code="$(
        curl -k -sS \
        -o /dev/null \
        -w '%{http_code}' \
        --max-time 10 \
        "$url" 2>/dev/null \
        || printf '000'
    )"

    printf '%-35s HTTP %s\n' "$name" "$code"
}

line "1. ÉTAT DES CONTENEURS"
docker compose ps

line "2. VALIDATION DOCKER COMPOSE"
if docker compose config -q; then
    echo "OK : docker-compose valide"
else
    echo "ERREUR : docker-compose invalide"
fi

line "3. SYNTAXE PYTHON"
python_files=(
    app.py
    daily_alerts.py
    recent_activity.py
    visitor_analytics.py
    active_alerts.py
)

for file in "${python_files[@]}"; do
    if [ -f "$file" ]; then
        if python3 -m py_compile "$file" 2>/dev/null; then
            echo "OK  : $file"
        else
            echo "KO  : $file"
        fi
    fi
done

line "4. SYNTAXE JAVASCRIPT"
js_files=(
    static/js/dashboard-v2.js
    static/js/daily-alerts.js
    static/js/recent-pages.js
    static/js/user-menu.js
    static/js/sidebar-active-navigation.js
    static/js/visitor-activity.js
    static/js/world-presence.js
    static/js/monitoring-report-print.js
)

for file in "${js_files[@]}"; do
    if [ -f "$file" ]; then
        if node --check "$file" >/dev/null 2>&1; then
            echo "OK  : $file"
        else
            echo "KO  : $file"
        fi
    fi
done

line "5. ROUTES FLASK ACTIVES"
docker compose exec -T web python3 - <<'PY'
from app import app

for rule in sorted(
    app.url_map.iter_rules(),
    key=lambda item: item.rule,
):
    methods = ",".join(
        sorted(
            method
            for method in rule.methods
            if method not in {"HEAD", "OPTIONS"}
        )
    )

    print(
        f"{methods:12} "
        f"{rule.rule:45} "
        f"{rule.endpoint}"
    )
PY

line "6. TESTS HTTP PRINCIPAUX"
check_url "Application" "$APP_URL/"
check_url "Monitoring" "$APP_URL/monitoring"
check_url "Conteneurs" "$APP_URL/containers"
check_url "Infrastructure" "$APP_URL/infrastructure"
check_url "Documentation" "$APP_URL/documentation"
check_url "Sécurité" "$APP_URL/security"
check_url "Audit" "$APP_URL/audit"

line "7. TESTS DES API"
check_url "API métriques" "$APP_URL/api/metrics"
check_url "API visiteurs" "$APP_URL/api/visitor-activity"
check_url "API alertes journalières" "$APP_URL/api/daily-alerts"
check_url "API alertes actives" "$APP_URL/api/active-alerts"
check_url "Export PDF" "$APP_URL/reports/export/pdf"

line "8. SERVICES DE SUPERVISION"
check_url "Prometheus santé" "$PROMETHEUS_URL/-/healthy"
check_url "Alertmanager santé" "$ALERTMANAGER_URL/-/healthy"
check_url "Grafana public" "https://grafana.emmanuelinfra.fr"
check_url "Prometheus public" "https://prometheus.emmanuelinfra.fr"

line "9. ALERTES ACTUELLES"
curl -sS \
    "$ALERTMANAGER_URL/api/v2/alerts" \
| python3 -c '
import json
import sys

try:
    alerts = json.load(sys.stdin)
except Exception as error:
    print("Impossible de lire les alertes :", error)
    raise SystemExit(0)

if not alerts:
    print("Aucune alerte active.")
    raise SystemExit(0)

for alert in alerts:
    labels = alert.get("labels", {})
    annotations = alert.get("annotations", {})
    status = alert.get("status", {})

    print(
        "-",
        labels.get("alertname", "Sans nom"),
        "|",
        labels.get("severity", "inconnue"),
        "|",
        status.get("state", "inconnu"),
        "|",
        annotations.get("summary", ""),
    )
'

line "10. TARGETS PROMETHEUS"
curl -sS \
    "$PROMETHEUS_URL/api/v1/targets" \
| python3 -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
    targets = payload.get("data", {}).get(
        "activeTargets",
        [],
    )
except Exception as error:
    print("Impossible de lire les targets :", error)
    raise SystemExit(0)

for target in targets:
    labels = target.get("labels", {})
    print(
        "-",
        labels.get("job", "sans-job"),
        "|",
        target.get("health", "unknown"),
        "|",
        target.get("scrapeUrl", ""),
    )
'

line "11. DERNIÈRES ERREURS DU CONTENEUR WEB"
docker compose logs \
    --tail=250 \
    web \
| grep -iE \
    'traceback|exception|error|failed|critical|warning' \
| tail -80 \
|| echo "Aucune erreur récente trouvée."

line "12. FICHIERS CSS CHARGÉS SUR L’ACCUEIL"
grep -n \
    "filename='css/" \
    templates/index_v2.html \
| sed -E \
    "s/.*filename='([^']+)'.*/- \1/" \
| sort -u

line "13. FICHIERS JAVASCRIPT CHARGÉS"
grep -n \
    "filename='js/" \
    templates/index_v2.html \
| sed -E \
    "s/.*filename='([^']+)'.*/- \1/" \
| sort -u

line "14. DOUBLONS ET ANCIENS PATCHS CSS"
printf 'Nombre de lignes dashboard-v2.css : '
wc -l < static/css/dashboard-v2.css

printf 'Blocs PREMIUM POLISH V1 : '
grep -c \
    "PREMIUM POLISH V1" \
    static/css/dashboard-v2.css \
    || true

printf 'Blocs ACTIVITÉ RÉCENTE MOBILE : '
grep -c \
    "ACTIVITÉ RÉCENTE — VERSION MOBILE" \
    static/css/dashboard-v2.css \
    || true

printf 'Utilisations de !important : '
grep -o \
    '!important' \
    static/css/dashboard-v2.css \
| wc -l

line "15. TAILLE DES FICHIERS PRINCIPAUX"
du -h \
    templates/index_v2.html \
    static/css/dashboard-v2.css \
    static/css/sidebar-premium.css \
    static/css/premium-global-polish.css \
    static/js/dashboard-v2.js \
    static/js/daily-alerts.js \
    2>/dev/null

line "16. SAUVEGARDES"
printf 'Sauvegardes templates : '
find templates/backups \
    -type f 2>/dev/null \
| wc -l

printf 'Sauvegardes CSS : '
find static/css/backups \
    -type f 2>/dev/null \
| wc -l

printf 'Sauvegardes JS : '
find static/js/backups \
    -type f 2>/dev/null \
| wc -l

printf 'Taille totale des sauvegardes : '
du -sh \
    templates/backups \
    static/css/backups \
    static/js/backups \
    2>/dev/null \
| awk '
    {
        total = total " " $1
    }
    END {
        print total
    }
'

line "17. VARIABLES SENSIBLES"
for variable in \
    SECRET_KEY \
    TELEGRAM_BOT_TOKEN \
    TELEGRAM_CHAT_ID \
    ALERTMANAGER_URL \
    PROMETHEUS_URL
do
    if grep -q "^${variable}=" .env 2>/dev/null; then
        echo "OK  : $variable=[MASQUÉ]"
    else
        echo "ABSENT : $variable"
    fi
done

line "18. RECHERCHE DE SECRETS DANS GIT"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if git ls-files | grep -qx '.env'; then
        echo "ALERTE : .env est suivi par Git"
    else
        echo "OK : .env n’est pas suivi par Git"
    fi

    git status --short
else
    echo "Ce dossier n’est pas un dépôt Git."
fi

line "19. BOUTON RAPPORT MOBILE"
grep -n -A18 -B4 \
    'mobile-export-above-emma' \
    templates/index_v2.html \
    || echo "Bouton mobile introuvable."

line "20. RAPPORT D’IMPRESSION"
for file in \
    static/css/monitoring-report-print.css \
    static/js/monitoring-report-print.js
do
    if [ -s "$file" ]; then
        echo "OK : $file"
    else
        echo "KO : $file absent ou vide"
    fi
done

line "21. RÉSUMÉ"
echo "Audit terminé."
echo "Analyse surtout les lignes KO, ABSENT, ALERTE et les codes HTTP 000/4xx/5xx."
