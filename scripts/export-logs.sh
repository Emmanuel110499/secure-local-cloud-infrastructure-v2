#!/usr/bin/env bash

set -euo pipefail

EXPORT_DIR="/home/emmanuel/application/log_exports"
MAX_LINES=300

mkdir -p "$EXPORT_DIR"

docker logs secure-web-app \
    --tail "$MAX_LINES" \
    > "$EXPORT_DIR/flask.log" 2>&1 || true

sudo tail -n "$MAX_LINES" \
    /var/log/nginx/access.log \
    > "$EXPORT_DIR/nginx-access.log" 2>&1 || true

sudo tail -n "$MAX_LINES" \
    /var/log/nginx/error.log \
    > "$EXPORT_DIR/nginx-error.log" 2>&1 || true

sudo journalctl \
    -u fail2ban \
    -n "$MAX_LINES" \
    --no-pager \
    > "$EXPORT_DIR/fail2ban.log" 2>&1 || true

chmod 644 "$EXPORT_DIR"/*.log