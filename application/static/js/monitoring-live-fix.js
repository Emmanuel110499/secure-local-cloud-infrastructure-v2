document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    if (typeof Chart === "undefined") {
        console.error(
            "Monitoring : Chart.js n'est pas chargé."
        );
        return;
    }

    const state = {
        hours: 24,
        refreshTimer: null,
    };

    function number(value) {
        const parsed = Number(value);
        return Number.isFinite(parsed) ? parsed : 0;
    }

    function formatPercent(value) {
        return number(value).toFixed(1) + " %";
    }

    function setText(selectors, value) {
        for (const selector of selectors) {
            const element = document.querySelector(selector);

            if (element) {
                element.textContent = value;
            }
        }
    }

    function setMetricLevel(selectors, value) {
        const metric = number(value);

        for (const selector of selectors) {
            const element = document.querySelector(selector);

            if (!element) {
                continue;
            }

            element.dataset.level =
                metric >= 80
                    ? "critical"
                    : metric >= 70
                        ? "warning"
                        : "normal";
        }
    }

    function formatTimestamp(timestamp, hours) {
        const date = new Date(timestamp);

        if (Number.isNaN(date.getTime())) {
            return "";
        }

        if (hours >= 48) {
            return date.toLocaleString(
                "fr-FR",
                {
                    day: "2-digit",
                    month: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                }
            );
        }

        return date.toLocaleTimeString(
            "fr-FR",
            {
                hour: "2-digit",
                minute: "2-digit",
            }
        );
    }

    function chartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false,
            },
            animation: {
                duration: 250,
            },
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    callbacks: {
                        label(context) {
                            return (
                                context.dataset.label
                                + " : "
                                + formatPercent(context.raw)
                            );
                        },
                    },
                },
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                    },
                    ticks: {
                        color: "#94a3b8",
                        autoSkip: true,
                        maxRotation: 0,
                        maxTicksLimit: 7,
                    },
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: "#94a3b8",
                        callback(value) {
                            return value + " %";
                        },
                    },
                    grid: {
                        color: "rgba(148, 163, 184, 0.13)",
                    },
                },
            },
        };
    }

    function findCanvas(ids) {
        for (const id of ids) {
            const element = document.getElementById(id);

            if (element instanceof HTMLCanvasElement) {
                return element;
            }
        }

        return null;
    }

    function updateOrCreateChart({
        ids,
        labels,
        values,
        label,
        borderColor,
        backgroundColor,
        threshold = null,
    }) {
        const canvas = findCanvas(ids);

        if (!canvas) {
            console.warn(
                "Monitoring : canvas introuvable :",
                ids.join(", ")
            );
            return;
        }

        let chart = Chart.getChart(canvas);

        const datasets = [
            {
                label,
                data: values,
                borderColor,
                backgroundColor,
                borderWidth: 2.4,
                pointRadius: values.length > 40 ? 0 : 2,
                pointHoverRadius: 4,
                tension: 0.32,
                fill: true,
            },
        ];

        if (threshold !== null) {
            datasets.push({
                label: "Seuil d’alerte",
                data: values.map(() => threshold),
                borderColor: "rgba(220, 38, 38, 0.76)",
                borderWidth: 1.5,
                borderDash: [6, 6],
                pointRadius: 0,
                fill: false,
                tension: 0,
            });
        }

        if (!chart) {
            chart = new Chart(
                canvas,
                {
                    type: "line",
                    data: {
                        labels,
                        datasets,
                    },
                    options: chartOptions(),
                }
            );

            return;
        }

        chart.data.labels = labels;
        chart.data.datasets = datasets;
        chart.options = chartOptions();
        chart.update("none");
    }

    function calculateSummary(records, key) {
        const values = records
            .map(record => number(record[key]))
            .filter(value => Number.isFinite(value));

        if (!values.length) {
            return {
                minimum: 0,
                maximum: 0,
                average: 0,
                latest: 0,
            };
        }

        const total = values.reduce(
            (sum, value) => sum + value,
            0
        );

        return {
            minimum: Math.min(...values),
            maximum: Math.max(...values),
            average: total / values.length,
            latest: values[values.length - 1],
        };
    }

    function updateSummary(key, summary) {
        const mappings = {
            cpu: {
                min: [
                    "#cpu-min",
                    "[data-summary='cpu-min']",
                ],
                avg: [
                    "#cpu-average",
                    "#cpu-avg",
                    "[data-summary='cpu-average']",
                ],
                max: [
                    "#cpu-max",
                    "[data-summary='cpu-max']",
                ],
            },
            memory: {
                min: [
                    "#memory-min",
                    "[data-summary='memory-min']",
                ],
                avg: [
                    "#memory-average",
                    "#memory-avg",
                    "[data-summary='memory-average']",
                ],
                max: [
                    "#memory-max",
                    "[data-summary='memory-max']",
                ],
            },
            disk: {
                min: [
                    "#disk-min",
                    "[data-summary='disk-min']",
                ],
                avg: [
                    "#disk-average",
                    "#disk-avg",
                    "[data-summary='disk-average']",
                ],
                max: [
                    "#disk-max",
                    "[data-summary='disk-max']",
                ],
            },
        };

        const target = mappings[key];

        if (!target) {
            return;
        }

        setText(target.min, formatPercent(summary.minimum));
        setText(target.avg, formatPercent(summary.average));
        setText(target.max, formatPercent(summary.maximum));
    }

    function updateCurrentValues(record) {
        const cpu = number(record.cpu);
        const memory = number(record.memory);
        const disk = number(record.disk);

        setText(
            [
                "#cpu-value",
                "#cpu-current",
                "[data-current-metric='cpu']",
            ],
            formatPercent(cpu)
        );

        setText(
            [
                "#memory-value",
                "#memory-current",
                "[data-current-metric='memory']",
            ],
            formatPercent(memory)
        );

        setText(
            [
                "#disk-value",
                "#disk-current",
                "#disk-chart-current",
                "#disk-monitoring-current",
                "[data-current-metric='disk']",
            ],
            formatPercent(disk)
        );

        setMetricLevel(
            [
                "#cpu-value",
                "#cpu-current",
            ],
            cpu
        );

        setMetricLevel(
            [
                "#memory-value",
                "#memory-current",
            ],
            memory
        );

        setMetricLevel(
            [
                "#disk-value",
                "#disk-current",
                "#disk-chart-current",
                "#disk-monitoring-current",
            ],
            disk
        );
    }

    async function loadHistory(hours = state.hours) {
        state.hours = hours;

        const statusElements = document.querySelectorAll(
            "#history-status, "
            + "#monitoring-status, "
            + "[data-history-status]"
        );

        statusElements.forEach(element => {
            element.textContent =
                "Chargement des données réelles…";
        });

        try {
            const response = await fetch(
                `/api/metrics/history?hours=${hours}&t=${Date.now()}`,
                {
                    method: "GET",
                    credentials: "same-origin",
                    cache: "no-store",
                    headers: {
                        Accept: "application/json",
                    },
                }
            );

            if (!response.ok) {
                throw new Error(
                    `API historique : HTTP ${response.status}`
                );
            }

            const payload = await response.json();
            const records = Array.isArray(payload.history)
                ? payload.history
                : [];

            if (!records.length) {
                throw new Error(
                    "Aucune mesure disponible pour cette période."
                );
            }

            const labels = records.map(record =>
                formatTimestamp(record.timestamp, hours)
            );

            const cpuValues = records.map(record =>
                number(record.cpu)
            );

            const memoryValues = records.map(record =>
                number(record.memory)
            );

            const diskValues = records.map(record =>
                number(record.disk)
            );

            updateOrCreateChart({
                ids: [
                    "cpuChart",
                    "cpu-chart",
                ],
                labels,
                values: cpuValues,
                label: "CPU",
                borderColor: "#2563eb",
                backgroundColor:
                    "rgba(37, 99, 235, 0.10)",
                threshold: 70,
            });

            updateOrCreateChart({
                ids: [
                    "memoryChart",
                    "memory-chart",
                ],
                labels,
                values: memoryValues,
                label: "Mémoire",
                borderColor: "#16a34a",
                backgroundColor:
                    "rgba(22, 163, 74, 0.10)",
                threshold: 75,
            });

            updateOrCreateChart({
                ids: [
                    "diskChart",
                    "disk-chart",
                ],
                labels,
                values: diskValues,
                label: "Disque",
                borderColor: "#d97706",
                backgroundColor:
                    "rgba(217, 119, 6, 0.11)",
                threshold: 80,
            });

            const latest = records[records.length - 1];
            updateCurrentValues(latest);

            const responseSummary =
                payload.summary || {};

            updateSummary(
                "cpu",
                responseSummary.cpu
                || calculateSummary(records, "cpu")
            );

            updateSummary(
                "memory",
                responseSummary.memory
                || calculateSummary(records, "memory")
            );

            updateSummary(
                "disk",
                responseSummary.disk
                || calculateSummary(records, "disk")
            );

            statusElements.forEach(element => {
                element.textContent =
                    `${records.length} mesures réelles chargées`;
            });

            const updatedAt = document.querySelector(
                "#history-updated-at, "
                + "#monitoring-updated-at, "
                + "[data-history-updated-at]"
            );

            if (updatedAt) {
                updatedAt.textContent =
                    "Actualisé le "
                    + new Date().toLocaleString("fr-FR");
            }

        } catch (error) {
            console.error(
                "Erreur historique monitoring :",
                error
            );

            statusElements.forEach(element => {
                element.textContent =
                    "Impossible de charger l’historique : "
                    + error.message;
            });
        }
    }

    async function loadCurrentMetrics() {
        try {
            const response = await fetch(
                `/api/metrics?t=${Date.now()}`,
                {
                    credentials: "same-origin",
                    cache: "no-store",
                    headers: {
                        Accept: "application/json",
                    },
                }
            );

            if (!response.ok) {
                return;
            }

            const payload = await response.json();
            const metrics = payload.metrics || payload;

            updateCurrentValues(metrics);

        } catch (error) {
            console.error(
                "Erreur métriques temps réel :",
                error
            );
        }
    }

    function readHours(button) {
        const raw =
            button.dataset.hours
            || button.dataset.period
            || button.dataset.range
            || button.value
            || button.textContent;

        const normalized = String(raw)
            .trim()
            .toLowerCase();

        if (
            normalized.includes("7")
            && (
                normalized.includes("jour")
                || normalized.includes("day")
                || normalized.includes("d")
            )
        ) {
            return 168;
        }

        const match = normalized.match(/\d+/);

        if (!match) {
            return 24;
        }

        return Math.max(
            1,
            Math.min(Number(match[0]), 168)
        );
    }

    const periodButtons = [
        ...document.querySelectorAll(
            "[data-hours], "
            + "[data-period], "
            + "[data-range], "
            + ".period-button, "
            + ".history-period, "
            + ".monitoring-period-button"
        ),
    ];

    periodButtons.forEach(button => {
        button.addEventListener(
            "click",
            event => {
                event.preventDefault();

                periodButtons.forEach(item => {
                    item.classList.remove(
                        "active",
                        "is-active"
                    );
                });

                button.classList.add("is-active");

                loadHistory(
                    readHours(button)
                );
            }
        );
    });

    loadHistory(24);
    loadCurrentMetrics();

    state.refreshTimer = window.setInterval(
        () => {
            loadCurrentMetrics();
            loadHistory(state.hours);
        },
        30000
    );

    window.addEventListener(
        "beforeunload",
        () => {
            window.clearInterval(
                state.refreshTimer
            );
        }
    );
});
