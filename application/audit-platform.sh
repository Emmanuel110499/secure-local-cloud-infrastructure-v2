#!/usr/bin/env bash

set -u

PROJECT_DIR="$(pwd)"
REPORT="$PROJECT_DIR/platform-audit-$(date +%F-%H%M%S).txt"

exec > >(tee "$REPORT") 2>&1

section() {
    printf "\n\n============================================================\n"
    printf "%s\n" "$1"
    printf "============================================================\n"
}

section "1. INFORMATIONS GÉNÉRALES"

echo "Date          : $(date)"
echo "Serveur       : $(hostname)"
echo "Utilisateur   : $(whoami)"
echo "Projet        : $PROJECT_DIR"
echo "Espace disque :"
df -h "$PROJECT_DIR" 2>/dev/null || true

echo
echo "Mémoire :"
free -h 2>/dev/null || true

echo
echo "Temps actif :"
uptime 2>/dev/null || true


section "2. ÉTAT GIT"

if [ -d .git ]; then
    git status --short
    echo
    git branch --show-current
    git log -1 --oneline
else
    echo "Aucun dépôt Git détecté."
fi


section "3. STRUCTURE DU PROJET"

find . \
    -maxdepth 2 \
    -type f \
    ! -path "./.git/*" \
    ! -path "./backups/*" \
    ! -path "./templates/backups/*" \
    ! -path "./static/js/backups/*" \
    ! -path "./static/css/backups/*" \
    | sort

echo
echo "Nombre de fichiers Python :"
find . -type f -name "*.py" \
    ! -path "./backups/*" \
    | wc -l

echo "Nombre de templates actifs :"
find templates -maxdepth 1 -type f -name "*.html" \
    | wc -l

echo "Nombre de fichiers CSS actifs :"
find static/css -maxdepth 1 -type f -name "*.css" \
    | wc -l

echo "Nombre de fichiers JS actifs :"
find static/js -maxdepth 1 -type f -name "*.js" \
    | wc -l


section "4. VÉRIFICATION PYTHON"

PYTHON_FILES="$(
    find . \
        -maxdepth 3 \
        -type f \
        -name "*.py" \
        ! -path "./backups/*" \
        ! -name "*.before-*"
)"

python3 -m compileall -q \
    $(printf "%s\n" "$PYTHON_FILES") \
    && echo "Syntaxe Python : OK" \
    || echo "Syntaxe Python : ERREURS DÉTECTÉES"


section "5. IMPORT RÉEL DE L’APPLICATION FLASK"

docker compose exec -T web python3 - <<'PY' 2>&1 || true
try:
    import app

    flask_app = app.app

    print("Application :", flask_app.name)
    print("Debug       :", flask_app.debug)
    print("Secret key  :", "définie" if flask_app.secret_key else "ABSENTE")
    print("Routes      :", len(list(flask_app.url_map.iter_rules())))

    print("\nRoutes enregistrées :")

    for rule in sorted(
        flask_app.url_map.iter_rules(),
        key=lambda item: str(item),
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
            f"{str(rule):45} "
            f"{rule.endpoint}"
        )

except Exception as error:
    print("ERREUR IMPORT FLASK :", repr(error))
PY


section "6. DOCKER"

docker compose config --quiet \
    && echo "docker-compose : syntaxe OK" \
    || echo "docker-compose : ERREUR"

echo
docker compose ps

echo
echo "Images :"
docker compose images 2>/dev/null || true

echo
echo "Santé des conteneurs :"
docker inspect \
    $(docker compose ps -q) \
    --format '{{.Name}} | {{.State.Status}} | health={{if .State.Health}}{{.State.Health.Status}}{{else}}non défini{{end}}' \
    2>/dev/null || true


section "7. JOURNAUX DU CONTENEUR WEB"

docker compose logs \
    --tail=250 \
    web \
    | grep -iE \
    "error|exception|traceback|critical|warning|failed|timeout|refused" \
    || echo "Aucune erreur évidente dans les 250 dernières lignes."


section "8. FICHIERS STATIQUES CHARGÉS"

echo "CSS inclus dans index_v2.html :"
grep -nE "filename=['\"]css/" \
    templates/index_v2.html \
    || true

echo
echo "JavaScript inclus dans index_v2.html :"
grep -nE "filename=['\"]js/" \
    templates/index_v2.html \
    || true


section "9. SYNTAXE JAVASCRIPT"

JS_ERRORS=0

for file in static/js/*.js; do
    [ -f "$file" ] || continue

    if node --check "$file" >/dev/null 2>&1; then
        echo "OK    $file"
    else
        echo "ERREUR $file"
        node --check "$file" 2>&1
        JS_ERRORS=$((JS_ERRORS + 1))
    fi
done

echo
echo "Nombre de fichiers JS en erreur : $JS_ERRORS"


section "10. DOUBLONS ET ACCUMULATION CSS"

echo "Taille des principaux CSS :"
du -h static/css/*.css 2>/dev/null \
    | sort -h \
    | tail -20

echo
echo "Nombre de règles !important dans dashboard-v2.css :"
grep -o "!important" static/css/dashboard-v2.css 2>/dev/null \
    | wc -l

echo
echo "Marqueurs de correctifs répétés :"
grep -hE "^/\*.*(FIX|FINAL|PREMIUM|MOBILE|CORRECTIF|HARMONISATION)" \
    static/css/*.css \
    | sort \
    | uniq -c \
    | sort -nr \
    | head -30


section "11. IDENTIFIANTS HTML DUPLIQUÉS"

python3 - <<'PY'
from collections import Counter
from pathlib import Path
import re

path = Path("templates/index_v2.html")
html = path.read_text(encoding="utf-8")

identifiers = re.findall(
    r'\bid=["\']([^"\']+)["\']',
    html,
)

duplicates = {
    name: count
    for name, count in Counter(identifiers).items()
    if count > 1
}

if duplicates:
    print("IDs dupliqués :")

    for name, count in sorted(duplicates.items()):
        print(f"- {name}: {count}")
else:
    print("Aucun ID HTML dupliqué dans index_v2.html.")
PY


section "12. RÉFÉRENCES STATIQUES MANQUANTES"

python3 - <<'PY'
from pathlib import Path
import re

templates = Path("templates")
static = Path("static")

missing = []

pattern = re.compile(
    r"filename\s*=\s*['\"]([^'\"]+)['\"]"
)

for template in templates.glob("*.html"):
    text = template.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    for filename in pattern.findall(text):
        target = static / filename

        if not target.exists():
            missing.append(
                (template.name, filename)
            )

if missing:
    print("Fichiers statiques manquants :")

    for template, filename in missing:
        print(f"- {template}: {filename}")
else:
    print("Toutes les références statiques détectées existent.")
PY


section "13. VARIABLES D’ENVIRONNEMENT"

if [ -f .env ]; then
    grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env \
        | sed 's/=.*/=[MASQUÉ]/'
else
    echo "Fichier .env absent."
fi

echo
echo "Variables sensibles suivies par Git :"

if [ -d .git ]; then
    git ls-files \
        | grep -E \
        '(^|/)\.env$|token|secret|credential|password' \
        || echo "Aucun fichier sensible évident suivi."
fi


section "14. RECHERCHE DE SECRETS EXPOSÉS"

grep -RniE \
    'bot[0-9]{6,}:[A-Za-z0-9_-]{20,}|TELEGRAM_BOT_TOKEN=.+|SECRET_KEY=.+|ADMIN_PASSWORD=.+|api[_-]?key[" ]*[:=][" ]*[^ ]+' \
    . \
    --exclude-dir=.git \
    --exclude-dir=backups \
    --exclude-dir=__pycache__ \
    --exclude=".env" \
    --exclude="*.db" \
    || echo "Aucun secret évident trouvé hors .env."


section "15. PERMISSIONS"

echo "Fichiers accessibles en écriture à tous :"

find . \
    -type f \
    -perm -0002 \
    ! -path "./.git/*" \
    ! -path "./backups/*" \
    -print \
    || true

echo
echo "Permissions de .env :"

if [ -f .env ]; then
    stat -c "%A %a %U:%G %n" .env
fi

echo
echo "Permissions des bases SQLite :"

find data \
    -maxdepth 1 \
    -type f \
    -name "*.db" \
    -exec stat -c "%A %a %U:%G %n" {} \; \
    2>/dev/null || true


section "16. ENDPOINTS DU PORTAIL"

for endpoint in \
    "/" \
    "/login" \
    "/monitoring" \
    "/containers" \
    "/infrastructure" \
    "/documentation" \
    "/security" \
    "/audit" \
    "/api/daily-alerts" \
    "/api/active-alerts" \
    "/api/visitor-activity"
do
    code="$(
        curl -ksS \
            -o /dev/null \
            -w '%{http_code}' \
            "https://app.emmanuelinfra.fr${endpoint}" \
            || echo "ERR"
    )"

    printf "%-35s %s\n" "$endpoint" "$code"
done


section "17. EN-TÊTES HTTP DE SÉCURITÉ"

curl -ksSI \
    https://app.emmanuelinfra.fr/ \
    | grep -iE \
    'HTTP/|server:|strict-transport-security|content-security-policy|x-frame-options|x-content-type-options|referrer-policy|permissions-policy|set-cookie' \
    || true


section "18. CERTIFICAT TLS"

echo | openssl s_client \
    -connect app.emmanuelinfra.fr:443 \
    -servername app.emmanuelinfra.fr \
    2>/dev/null \
    | openssl x509 \
        -noout \
        -subject \
        -issuer \
        -dates \
        2>/dev/null \
    || echo "Impossible de lire le certificat."


section "19. SERVICES DE SUPERVISION"

check_service() {
    name="$1"
    url="$2"

    result="$(
        curl -sS \
            --max-time 5 \
            -o /dev/null \
            -w '%{http_code}' \
            "$url" \
            2>/dev/null \
        || echo "ERR"
    )"

    printf "%-20s %-55s %s\n" \
        "$name" \
        "$url" \
        "$result"
}

check_service \
    "Application" \
    "http://127.0.0.1:5001/"

check_service \
    "Prometheus" \
    "http://192.168.154.20:9090/-/healthy"

check_service \
    "Alertmanager" \
    "http://192.168.154.20:9093/-/healthy"

check_service \
    "Grafana" \
    "https://grafana.emmanuelinfra.fr/api/health"

check_service \
    "cAdvisor" \
    "http://127.0.0.1:8080/healthz"


section "20. ALERTES ACTUELLES"

curl -sS \
    --max-time 5 \
    http://192.168.154.20:9093/api/v2/alerts \
    | python3 -c '
import json
import sys

try:
    alerts = json.load(sys.stdin)
except Exception as error:
    print("JSON invalide :", error)
    raise SystemExit(0)

print("Nombre d alertes :", len(alerts))

for alert in alerts:
    labels = alert.get("labels", {})
    annotations = alert.get("annotations", {})
    status = alert.get("status", {})

    print(
        "-",
        labels.get("alertname", "sans nom"),
        "|",
        labels.get("severity", "inconnue"),
        "|",
        status.get("state", "inconnu"),
        "|",
        annotations.get("summary", ""),
    )
' 2>/dev/null || echo "Alertmanager indisponible."


section "21. BASES SQLITE"

find data \
    -maxdepth 1 \
    -type f \
    -name "*.db" \
    -print 2>/dev/null

for database in data/*.db; do
    [ -f "$database" ] || continue

    echo
    echo "--- $database ---"

    sqlite3 "$database" \
        "PRAGMA integrity_check;" \
        2>/dev/null \
        || echo "sqlite3 absent ou base illisible."

    sqlite3 "$database" \
        ".tables" \
        2>/dev/null \
        || true
done


section "22. FICHIERS VOLUMINEUX"

find . \
    -type f \
    ! -path "./.git/*" \
    -printf "%s %p\n" \
    | sort -nr \
    | head -25 \
    | awk '
        {
            size=$1/1024/1024;
            $1="";
            printf "%.2f MB%s\n", size, $0
        }
    '


section "23. SAUVEGARDES ACCUMULÉES"

for directory in \
    backups \
    templates/backups \
    static/js/backups \
    static/css/backups
do
    if [ -d "$directory" ]; then
        count="$(
            find "$directory" \
                -type f \
                | wc -l
        )"

        size="$(
            du -sh "$directory" \
                2>/dev/null \
                | awk '{print $1}'
        )"

        echo "$directory : $count fichier(s), $size"
    fi
done


section "24. RÉSUMÉ AUTOMATIQUE"

echo "Rapport créé : $REPORT"
echo
echo "Points à examiner prioritairement :"
echo "- erreurs Python ou JavaScript ;"
echo "- routes Flask absentes ou en erreur ;"
echo "- fichiers statiques manquants ;"
echo "- secrets ou permissions trop ouvertes ;"
echo "- en-têtes HTTP de sécurité absents ;"
echo "- services Prometheus/Grafana/Alertmanager indisponibles ;"
echo "- accumulation de CSS, JS et sauvegardes."

