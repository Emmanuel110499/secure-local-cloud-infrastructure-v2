#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="/opt/secure-local-cloud"
DEPLOYMENT_DIR="${PROJECT_DIR}/deployment"
BACKUP_DIR="/var/backups/secure-local-cloud/automatic/vps-production"
KEEP_COUNT=3

STAMP="$(date -u +%Y%m%d-%H%M%S)"
ARCHIVE="${BACKUP_DIR}/vps-production-${STAMP}.tar.gz"
CHECKSUM="${ARCHIVE}.sha256"
TEMP="${ARCHIVE}.tmp"

exec 9>/run/secure-local-cloud-backup.lock

if ! flock -n 9; then
    echo "Une sauvegarde est déjà en cours."
    exit 0
fi

platform_stopped=false

restart_platform() {
    rm -f "$TEMP"

    if [ "$platform_stopped" = true ]; then
        cd "$DEPLOYMENT_DIR"
        docker compose up -d
    fi
}

trap restart_platform EXIT

install -d -m 700 "$BACKUP_DIR"

paths=(
    "opt/secure-local-cloud"
    "var/lib/docker/volumes/secure-local-cloud_prometheus-data"
    "var/lib/docker/volumes/secure-local-cloud_grafana-data"
    "var/lib/docker/volumes/secure-local-cloud_alertmanager-data"
    "etc/nginx"
    "etc/cloudflared"
    "etc/ufw"
    "etc/ssh"
    "etc/systemd/system"
    "var/lib/tailscale"
    "usr/local/sbin"
)

cd "$DEPLOYMENT_DIR"

echo "Arrêt contrôlé de la plateforme..."
docker compose stop
platform_stopped=true

echo "Création de la sauvegarde complète..."

tar -czf "$TEMP" \
    -C / \
    "${paths[@]}"

mv "$TEMP" "$ARCHIVE"

chmod 600 "$ARCHIVE"

cd "$BACKUP_DIR"

sha256sum \
  "$(basename "$ARCHIVE")" \
  > "$CHECKSUM"

chmod 600 "$CHECKSUM"

sha256sum -c "$CHECKSUM"

echo "Application de la rétention..."

mapfile -t archives < <(
    find "$BACKUP_DIR" \
        -maxdepth 1 \
        -type f \
        -name 'vps-production-*.tar.gz' \
        -printf '%T@ %p\n' |
    sort -nr |
    cut -d' ' -f2-
)

if [ "${#archives[@]}" -gt "$KEEP_COUNT" ]; then
    for old_archive in "${archives[@]:$KEEP_COUNT}"; do
        echo "Suppression : $old_archive"

        rm -f \
            "$old_archive" \
            "${old_archive}.sha256"
    done
fi

echo "Sauvegarde créée : $ARCHIVE"
echo "Générations conservées : $KEEP_COUNT"
