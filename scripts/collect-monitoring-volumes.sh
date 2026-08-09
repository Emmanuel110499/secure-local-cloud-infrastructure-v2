#!/bin/sh
set -eu

OUTPUT_DIR=/var/lib/node_exporter/textfile_collector
OUTPUT_FILE="$OUTPUT_DIR/secure_monitoring_volumes.prom"
TEMP_FILE="$OUTPUT_FILE.tmp.$$"

install -d -m 755 -o node_exporter -g node_exporter "$OUTPUT_DIR"

{
    echo '# HELP secure_docker_volume_size_bytes Taille réellement occupée par un volume Docker.'
    echo '# TYPE secure_docker_volume_size_bytes gauge'
    for logical_name in prometheus-data grafana-data alertmanager-data
    do
        volume="monitoring_${logical_name}"
        mountpoint="/var/lib/docker/volumes/${volume}/_data"
        if [ -d "$mountpoint" ]; then
            size="$(du -sb "$mountpoint" | awk '{print $1}')"
            printf 'secure_docker_volume_size_bytes{equipment="srv-monitoring",logical_name="%s",volume="%s",mountpoint="%s"} %s\n' \
                "$logical_name" "$volume" "$mountpoint" "$size"
        fi
    done
    echo '# HELP secure_docker_volume_collector_last_success_unixtime Date de la dernière collecte réussie.'
    echo '# TYPE secure_docker_volume_collector_last_success_unixtime gauge'
    printf 'secure_docker_volume_collector_last_success_unixtime{equipment="srv-monitoring"} %s\n' "$(date +%s)"
} > "$TEMP_FILE"

chown node_exporter:node_exporter "$TEMP_FILE"
chmod 644 "$TEMP_FILE"
mv "$TEMP_FILE" "$OUTPUT_FILE"
