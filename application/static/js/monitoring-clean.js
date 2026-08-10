document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    if (typeof Chart === "undefined") {
        console.error("Chart.js n'est pas disponible.");
        return;
    }

    document.body.classList.add("clean-monitoring-page");

    const state = {
        hours: 24,
        charts: {},
        timer: null,
    };

    const number = value => {
        const parsed = Number(value);
        return Number.isFinite(parsed) ? parsed : 0;
    };

    const percent = value =>
        `${number(value).toFixed(1)} %`;

    function findPageContainer() {
        return (
            document.querySelector("main")
            || document.querySelector(".page-content")
            || document.querySelector(".portal-page")
            || document.body
        );
    }

    function findMonitoringTitle() {
        return [...document.querySelectorAll("h1")].find(
            element =>
                element.textContent
                    .toLowerCase()
                    .includes("monitoring")
        );
    }

    function findMeaningfulCard(element) {
        let current = element;

        for (let level = 0; level < 7 && current; level += 1) {
            const text = current.textContent
                .replace(/\s+/g, " ")
                .trim();

            const hasHeading =
                current.querySelector("h2, h3, h4");

            const hasStats =
                /minimum|moyenne|maximum/i.test(text);

            if (hasHeading && hasStats) {
                return current;
            }

            current = current.parentElement;
        }

        return element.closest(
            "section, article, .card, .panel"
        );
    }

    function hideOldMonitoringBlocks() {
        [
            "cpuChart",
            "memoryChart",
            "diskChart",
            "cpu-chart",
            "memory-chart",
            "disk-chart",
        ].forEach(id => {
            const canvas = document.getElementById(id);

            if (!canvas) {
                return;
            }

            const card = findMeaningfulCard(canvas);

            if (card) {
                card.classList.add(
                    "clean-monitoring-old-hidden"
                );
            }
        });

        const oldTexts = [
            "Mesures enregistrées",
            "CPU moyen",
            "RAM moyenne",
            "Disque moyen",
        ];

        oldTexts.forEach(label => {
            [...document.querySelectorAll(
                "h2, h3, h4, strong, span, p"
            )]
                .filter(element =>
                    element.textContent
                        .replace(/\s+/g, " ")
                        .trim() === label
                )
                .forEach(element => {
                    const card = element.closest(
                        "article, section, "
                        + ".card, .panel, "
                        + ".summary-card, "
                        + ".metric-card, "
                        + ".stat-card"
                    );

                    if (card) {
                        card.classList.add(
                            "clean-monitoring-old-hidden"
                        );
                    }
                });
        });

        document.querySelectorAll(
            ".disk-monitoring-section, "
            + ".monitoring-disk-chart-card"
        ).forEach(element => {
            element.classList.add(
                "clean-monitoring-old-hidden"
            );
        });

        const oldPeriodButtons = [
            ...document.querySelectorAll(
                "button, a"
            ),
        ].filter(element => {
            const text = element.textContent
                .replace(/\s+/g, " ")
                .trim()
                .toLowerCase();

            return [
                "1 heure",
                "6 heures",
                "24 heures",
                "7 jours",
            ].includes(text);
        });

        oldPeriodButtons.forEach(button => {
            const wrapper = button.closest(
                "section, article, "
                + ".toolbar, .period-selector, "
                + ".history-toolbar, "
                + ".monitoring-toolbar"
            );

            if (wrapper) {
                wrapper.classList.add(
                    "clean-monitoring-old-hidden"
                );
            }
        });
    }

    function buildInterface() {
        const root = document.createElement("section");

        root.id = "clean-monitoring-dashboard";

        root.innerHTML = `
            <div class="cm-toolbar">
                <div class="cm-periods">
                    <button type="button" data-hours="1">
                        1 heure
                    </button>

                    <button type="button" data-hours="6">
                        6 heures
                    </button>

                    <button
                        type="button"
                        data-hours="24"
                        class="is-active"
                    >
                        24 heures
                    </button>

                    <button type="button" data-hours="168">
                        7 jours
                    </button>
                </div>

                <div class="cm-toolbar-right">
                    <span id="cm-status">
                        Chargement…
                    </span>

                    <div class="cm-print-choices" aria-label="Exportation et impression">
                        <a
                            href="/export/pdf"
                            class="cm-print-choice cm-pdf-download"
                            title="Télécharger le rapport PDF"
                        >
                            Télécharger PDF
                        </a>
                        <button type="button" class="cm-print-choice" data-print-orientation="portrait">
                            Imprimer vertical
                        </button>
                        <button type="button" class="cm-print-choice" data-print-orientation="landscape">
                            Imprimer horizontal
                        </button>
                    </div>
                </div>
            </div>

            <div class="cm-summary-grid">
                <article class="cm-summary-card">
                    <span class="cm-summary-icon cm-blue">
                        〽
                    </span>

                    <div>
                        <small>Mesures enregistrées</small>
                        <strong id="cm-count">--</strong>
                        <span id="cm-period-label">
                            Sur les dernières 24 heures
                        </span>
                    </div>
                </article>

                <article class="cm-summary-card">
                    <span class="cm-summary-icon cm-indigo">
                        CPU
                    </span>

                    <div>
                        <small>CPU actuel</small>
                        <strong id="cm-current-cpu">--</strong>
                        <span id="cm-cpu-state">
                            Chargement
                        </span>
                    </div>
                </article>

                <article class="cm-summary-card">
                    <span class="cm-summary-icon cm-green">
                        RAM
                    </span>

                    <div>
                        <small>RAM actuelle</small>
                        <strong id="cm-current-memory">--</strong>
                        <span id="cm-memory-state">
                            Chargement
                        </span>
                    </div>
                </article>

                <article class="cm-summary-card">
                    <span class="cm-summary-icon cm-orange">
                        SSD
                    </span>

                    <div>
                        <small>Disque actuel</small>
                        <strong id="cm-current-disk">--</strong>
                        <span id="cm-disk-state">
                            Chargement
                        </span>
                    </div>
                </article>
            </div>

            <div class="cm-chart-grid">
                <article class="cm-chart-card cm-cpu-card">
                    <header>
                        <div>
                            <span class="cm-kicker">
                                Processeur
                            </span>

                            <h2>Utilisation CPU</h2>

                            <p>
                                Charge moyenne du serveur.
                            </p>
                        </div>

                        <strong
                            id="cm-cpu-badge"
                            class="cm-value-badge"
                        >
                            --
                        </strong>
                    </header>

                    <div class="cm-chart-wrapper">
                        <canvas id="cm-cpu-chart"></canvas>
                    </div>

                    <div class="cm-stats">
                        <div>
                            <small>Minimum</small>
                            <strong id="cm-cpu-min">--</strong>
                        </div>

                        <div>
                            <small>Moyenne</small>
                            <strong id="cm-cpu-avg">--</strong>
                        </div>

                        <div>
                            <small>Maximum</small>
                            <strong id="cm-cpu-max">--</strong>
                        </div>
                    </div>
                </article>

                <article class="cm-chart-card cm-memory-card">
                    <header>
                        <div>
                            <span class="cm-kicker">
                                Mémoire
                            </span>

                            <h2>Utilisation RAM</h2>

                            <p>
                                Mémoire utilisée par le système.
                            </p>
                        </div>

                        <strong
                            id="cm-memory-badge"
                            class="cm-value-badge"
                        >
                            --
                        </strong>
                    </header>

                    <div class="cm-chart-wrapper">
                        <canvas id="cm-memory-chart"></canvas>
                    </div>

                    <div class="cm-stats">
                        <div>
                            <small>Minimum</small>
                            <strong id="cm-memory-min">--</strong>
                        </div>

                        <div>
                            <small>Moyenne</small>
                            <strong id="cm-memory-avg">--</strong>
                        </div>

                        <div>
                            <small>Maximum</small>
                            <strong id="cm-memory-max">--</strong>
                        </div>
                    </div>
                </article>

                <article class="cm-chart-card cm-disk-card">
                    <header>
                        <div>
                            <span class="cm-kicker">
                                Stockage
                            </span>

                            <h2>Utilisation disque</h2>

                            <p>
                                Espace utilisé sur la partition racine.
                            </p>
                        </div>

                        <strong
                            id="cm-disk-badge"
                            class="cm-value-badge"
                        >
                            --
                        </strong>
                    </header>

                    <div class="cm-chart-wrapper">
                        <canvas id="cm-disk-chart"></canvas>
                    </div>

                    <div class="cm-stats">
                        <div>
                            <small>Minimum</small>
                            <strong id="cm-disk-min">--</strong>
                        </div>

                        <div>
                            <small>Moyenne</small>
                            <strong id="cm-disk-avg">--</strong>
                        </div>

                        <div>
                            <small>Maximum</small>
                            <strong id="cm-disk-max">--</strong>
                        </div>
                    </div>
                </article>
            </div>

            <div class="cm-footer">
                <span>
                    <i class="cm-status-dot"></i>
                    Données issues de Prometheus et de
                    l’historique local
                </span>

                <span id="cm-updated-at">
                    Dernière actualisation : --
                </span>
            </div>

            <section class="cm-insights" aria-label="Synthèse du monitoring">
                <article class="cm-insight">
                    <small>État global</small>
                    <strong id="cm-global-state">Analyse en cours…</strong>
                </article>
                <article class="cm-insight">
                    <small>Qualité des données</small>
                    <strong id="cm-data-quality">Chargement…</strong>
                </article>
                <article class="cm-insight">
                    <small>Ressource la plus sollicitée</small>
                    <strong id="cm-highest-resource">Calcul en cours…</strong>
                </article>
                <article class="cm-insight">
                    <small>Seuils surveillés</small>
                    <strong>CPU 70 % · RAM 75 % · Disque 80 %</strong>
                </article>
            </section>
        `;

        const container = findPageContainer();
        const title = findMonitoringTitle();

        if (title) {
            let header = title.closest(
                "header, .page-header, "
                + ".portal-header, .hero"
            );

            if (!header) {
                header = title.parentElement;
            }

            header.insertAdjacentElement(
                "afterend",
                root
            );
        } else {
            container.prepend(root);
        }

        return root;
    }

    function getMetricState(metric, value) {
        if (metric === "disk") {
            if (value >= 80) {
                return {
                    text: "Alerte active",
                    level: "critical",
                };
            }

            if (value >= 70) {
                return {
                    text: "À surveiller",
                    level: "warning",
                };
            }

            return {
                text: "Normal",
                level: "normal",
            };
        }

        const warning =
            metric === "cpu" ? 70 : 75;

        if (value >= 85) {
            return {
                text: "Critique",
                level: "critical",
            };
        }

        if (value >= warning) {
            return {
                text: "À surveiller",
                level: "warning",
            };
        }

        return {
            text: "Normal",
            level: "normal",
        };
    }

    function calculate(values) {
        if (!values.length) {
            return {
                min: 0,
                max: 0,
                avg: 0,
                latest: 0,
            };
        }

        return {
            min: Math.min(...values),
            max: Math.max(...values),
            avg:
                values.reduce(
                    (sum, value) => sum + value,
                    0
                ) / values.length,
            latest: values[values.length - 1],
        };
    }

    function formatLabel(timestamp, hours) {
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

    function downsample(records, maximum = 90) {
        if (records.length <= maximum) {
            return records;
        }

        const step = records.length / maximum;

        return Array.from(
            { length: maximum },
            (_, index) =>
                records[
                    Math.min(
                        Math.floor(index * step),
                        records.length - 1
                    )
                ]
        );
    }

    function chartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 350,
            },
            interaction: {
                mode: "index",
                intersect: false,
            },
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    displayColors: false,
                    callbacks: {
                        label(context) {
                            return percent(context.raw);
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
                        color: "#8b9bb4",
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 6,
                        font: {
                            size: 10,
                        },
                    },
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: "#8b9bb4",
                        stepSize: 25,
                        callback(value) {
                            return `${value}%`;
                        },
                        font: {
                            size: 10,
                        },
                    },
                    grid: {
                        color:
                            "rgba(148,163,184,.14)",
                    },
                },
            },
        };
    }

    function renderChart({
        key,
        canvasId,
        labels,
        values,
        line,
        fill,
        threshold,
    }) {
        if (state.charts[key]) {
            state.charts[key].destroy();
        }

        const datasets = [
            {
                data: values,
                borderColor: line,
                backgroundColor: fill,
                borderWidth: 2.2,
                pointRadius: 0,
                pointHoverRadius: 4,
                tension: 0.32,
                fill: true,
            },
        ];

        if (threshold !== null) {
            datasets.push({
                data: values.map(() => threshold),
                borderColor:
                    "rgba(239,68,68,.65)",
                borderWidth: 1.4,
                borderDash: [5, 5],
                pointRadius: 0,
                fill: false,
                tension: 0,
            });
        }

        state.charts[key] = new Chart(
            document.getElementById(canvasId),
            {
                type: "line",
                data: {
                    labels,
                    datasets,
                },
                options: chartOptions(),
            }
        );
    }

    function updateMetric(metric, statistics) {
        const current = document.getElementById(
            `cm-current-${metric}`
        );

        const badge = document.getElementById(
            `cm-${metric}-badge`
        );

        const stateElement =
            document.getElementById(
                `cm-${metric}-state`
            );

        const metricState = getMetricState(
            metric,
            statistics.latest
        );

        current.textContent =
            percent(statistics.latest);

        badge.textContent =
            percent(statistics.latest);

        stateElement.textContent =
            metricState.text;

        current.dataset.level =
            metricState.level;

        badge.dataset.level =
            metricState.level;

        stateElement.dataset.level =
            metricState.level;

        document.getElementById(
            `cm-${metric}-min`
        ).textContent = percent(statistics.min);

        document.getElementById(
            `cm-${metric}-avg`
        ).textContent = percent(statistics.avg);

        document.getElementById(
            `cm-${metric}-max`
        ).textContent = percent(statistics.max);
    }

    async function fetchJson(url, timeout = 8000) {
        const controller = new AbortController();
        const timer = window.setTimeout(
            () => controller.abort(),
            timeout
        );

        try {
            const response = await fetch(url, {
                credentials: "same-origin",
                cache: "no-store",
                headers: {
                    Accept: "application/json",
                },
                signal: controller.signal,
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            return await response.json();
        } finally {
            window.clearTimeout(timer);
        }
    }

    async function loadCurrentMetrics(status, historyError) {
        try {
            const payload = await fetchJson(
                `/api/metrics?t=${Date.now()}`,
                8000
            );
            const metrics = payload.metrics || {};
            const current = {
                cpu: number(metrics.cpu),
                memory: number(metrics.memory),
                disk: number(metrics.disk),
            };

            if (
                metrics.cpu == null
                || metrics.memory == null
                || metrics.disk == null
            ) {
                throw new Error("Métriques temps réel incomplètes");
            }

            const labels = ["Maintenant", "Maintenant"];

            Object.entries(current).forEach(([metric, value]) => {
                const colors = {
                    cpu: ["#3567e8", "rgba(53,103,232,.10)", 70],
                    memory: ["#10a87f", "rgba(16,168,127,.10)", 75],
                    disk: ["#e9810b", "rgba(233,129,11,.11)", 80],
                }[metric];
                const statistics = {
                    min: value,
                    avg: value,
                    max: value,
                    latest: value,
                };

                updateMetric(metric, statistics);
                renderChart({
                    key: metric,
                    canvasId: `cm-${metric}-chart`,
                    labels,
                    values: [value, value],
                    line: colors[0],
                    fill: colors[1],
                    threshold: colors[2],
                });
            });

            document.getElementById("cm-count").textContent = "Temps réel";
            document.getElementById("cm-period-label").textContent =
                "Valeurs actuelles de Prometheus";
            document.getElementById("cm-global-state").textContent =
                "Mesures actuelles disponibles";
            document.getElementById("cm-data-quality").textContent =
                "Mode temps réel actif";
            document.getElementById("cm-highest-resource").textContent =
                Object.entries(current)
                    .sort((left, right) => right[1] - left[1])
                    .map(([name, value]) =>
                        `${name.toUpperCase()} · ${percent(value)}`
                    )[0];

            status.textContent =
                "Valeurs réelles · historique temporairement indisponible";
            document.getElementById("cm-updated-at").textContent =
                "Dernière actualisation : "
                + new Date().toLocaleTimeString("fr-FR");
        } catch (fallbackError) {
            console.error("Métriques temps réel indisponibles :", fallbackError);
            status.textContent =
                `Données indisponibles : ${historyError.message}`;
        }
    }

    async function loadHistory(hours = state.hours) {
        state.hours = hours;

        const status =
            document.getElementById("cm-status");

        status.textContent =
            "Chargement des données…";

        try {
            const payload = await fetchJson(
                `/api/metrics/history?hours=${hours}&t=${Date.now()}`,
                8000
            );

            const allRecords =
                Array.isArray(payload.history)
                    ? payload.history
                    : [];

            if (!allRecords.length) {
                throw new Error(
                    "Aucune mesure disponible"
                );
            }

            const records = downsample(allRecords);

            const labels = records.map(record =>
                formatLabel(record.timestamp, hours)
            );

            const cpu = records.map(record =>
                number(record.cpu)
            );

            const memory = records.map(record =>
                number(record.memory)
            );

            const disk = records.map(record =>
                number(record.disk)
            );

            const cpuStats = calculate(
                allRecords.map(record =>
                    number(record.cpu)
                )
            );

            const memoryStats = calculate(
                allRecords.map(record =>
                    number(record.memory)
                )
            );

            const diskStats = calculate(
                allRecords.map(record =>
                    number(record.disk)
                )
            );

            renderChart({
                key: "cpu",
                canvasId: "cm-cpu-chart",
                labels,
                values: cpu,
                line: "#3567e8",
                fill: "rgba(53,103,232,.10)",
                threshold: 70,
            });

            renderChart({
                key: "memory",
                canvasId: "cm-memory-chart",
                labels,
                values: memory,
                line: "#10a87f",
                fill: "rgba(16,168,127,.10)",
                threshold: 75,
            });

            renderChart({
                key: "disk",
                canvasId: "cm-disk-chart",
                labels,
                values: disk,
                line: "#e9810b",
                fill: "rgba(233,129,11,.11)",
                threshold: 80,
            });

            updateMetric("cpu", cpuStats);
            updateMetric("memory", memoryStats);
            updateMetric("disk", diskStats);

            const currentValues = {
                CPU: cpuStats.latest,
                RAM: memoryStats.latest,
                Disque: diskStats.latest,
            };
            const highest = Object.entries(currentValues)
                .sort((left, right) => right[1] - left[1])[0];
            const warningCount = [
                cpuStats.latest >= 70,
                memoryStats.latest >= 75,
                diskStats.latest >= 80,
            ].filter(Boolean).length;

            document.getElementById("cm-global-state").textContent =
                warningCount
                    ? `${warningCount} seuil(s) à surveiller`
                    : "Tous les indicateurs sont normaux";
            document.getElementById("cm-data-quality").textContent =
                `${allRecords.length} mesures disponibles`;
            document.getElementById("cm-highest-resource").textContent =
                `${highest[0]} · ${percent(highest[1])}`;

            document.getElementById(
                "cm-count"
            ).textContent = allRecords.length;

            const periodTexts = {
                1: "Sur la dernière heure",
                6: "Sur les 6 dernières heures",
                24: "Sur les dernières 24 heures",
                168: "Sur les 7 derniers jours",
            };

            document.getElementById(
                "cm-period-label"
            ).textContent =
                periodTexts[hours]
                || `Sur les dernières ${hours} heures`;

            status.textContent =
                `${allRecords.length} mesures chargées`;

            document.getElementById(
                "cm-updated-at"
            ).textContent =
                "Dernière actualisation : "
                + new Date().toLocaleTimeString(
                    "fr-FR",
                    {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                    }
                );

        } catch (error) {
            console.error(
                "Erreur Monitoring :",
                error
            );

            await loadCurrentMetrics(status, error);
        }
    }

    const root = buildInterface();

    hideOldMonitoringBlocks();

    /*
     * Empêche le nouveau tableau de bord d’être masqué si
     * une ancienne section parente a reçu la classe de nettoyage.
     */
    let rootAncestor = root;

    while (rootAncestor) {
        rootAncestor.classList.remove(
            "clean-monitoring-old-hidden"
        );

        rootAncestor = rootAncestor.parentElement;
    }

    root.style.display = "block";
    root.style.visibility = "visible";
    root.style.opacity = "1";

    root.querySelectorAll(
        ".cm-periods button"
    ).forEach(button => {
        button.addEventListener("click", () => {
            root.querySelectorAll(
                ".cm-periods button"
            ).forEach(item =>
                item.classList.remove("is-active")
            );

            button.classList.add("is-active");

            loadHistory(
                Number(button.dataset.hours)
            );
        });
    });

    document.getElementById(
        "cm-export"
    ).addEventListener("click", () => {
        window.print();
    });

    loadHistory(24);

    state.timer = window.setInterval(
        () => loadHistory(state.hours),
        30000
    );

    window.addEventListener("beforeunload", () => {
        window.clearInterval(state.timer);
    });
});


/* =========================================================
   NETTOYAGE DÉFINITIF DES ANCIENS GRAPHIQUES
========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    function hideLegacyMonitoring() {
        const cleanDashboard = document.getElementById(
            "clean-monitoring-dashboard"
        );

        if (!cleanDashboard) {
            return;
        }

        /*
         * Tous les canvas qui n'appartiennent pas à la
         * nouvelle interface sont considérés comme anciens.
         */
        const legacyCanvases = [
            ...document.querySelectorAll("canvas"),
        ].filter(canvas => {
            return !canvas.id.startsWith("cm-");
        });

        legacyCanvases.forEach(canvas => {
            let current = canvas;

            for (let level = 0; level < 8 && current; level += 1) {
                if (
                    current === cleanDashboard
                    || current.contains(cleanDashboard)
                ) {
                    break;
                }

                const tagName = current.tagName?.toLowerCase();

                const isCandidate =
                    tagName === "article"
                    || tagName === "section"
                    || current.classList?.contains("chart-card")
                    || current.classList?.contains("chart-panel")
                    || current.classList?.contains("monitoring-chart-card")
                    || current.classList?.contains("panel")
                    || current.classList?.contains("card");

                if (isCandidate) {
                    current.classList.add(
                        "legacy-monitoring-block"
                    );

                    break;
                }

                current = current.parentElement;
            }
        });

        /*
         * Nettoyage des anciennes cartes de résumé et
         * des anciennes barres de périodes.
         */
        const legacyLabels = [
            "Mesures enregistrées",
            "CPU moyen",
            "RAM moyenne",
            "Disque moyen",
            "Utilisation CPU",
            "Utilisation mémoire",
            "Utilisation disque",
        ];

        document.querySelectorAll(
            "h2, h3, h4, strong"
        ).forEach(element => {
            if (cleanDashboard.contains(element)) {
                return;
            }

            const text = element.textContent
                .replace(/\s+/g, " ")
                .trim();

            if (!legacyLabels.includes(text)) {
                return;
            }

            const block = element.closest(
                "article, section, "
                + ".chart-card, .chart-panel, "
                + ".monitoring-chart-card, "
                + ".summary-card, .metric-card, "
                + ".stat-card, .panel, .card"
            );

            if (block && !block.contains(cleanDashboard)) {
                block.classList.add(
                    "legacy-monitoring-block"
                );
            }
        });

        /*
         * Certains anciens graphiques sont regroupés dans
         * une grande grille. On la masque si elle ne contient
         * que des blocs désormais cachés.
         */
        document.querySelectorAll(
            ".monitoring-charts, "
            + ".charts-grid, "
            + ".monitoring-grid, "
            + ".history-charts"
        ).forEach(grid => {
            if (cleanDashboard.contains(grid)) {
                return;
            }

            if (
                grid.querySelector(
                    "canvas:not([id^='cm-'])"
                )
            ) {
                grid.classList.add(
                    "legacy-monitoring-block"
                );
            }
        });
    }

    /*
     * Le tableau moderne est construit après DOMContentLoaded.
     * On laisse donc quelques millisecondes avant le nettoyage.
     */
    window.setTimeout(
        hideLegacyMonitoring,
        250
    );

    window.setTimeout(
        hideLegacyMonitoring,
        1000
    );
});


/* =========================================================
   EXPORT PROFESSIONNEL DU MONITORING
========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    function valueOf(id) {
        return (
            document.getElementById(id)
                ?.textContent
                ?.trim()
            || "--"
        );
    }

    function canvasImage(id) {
        const canvas = document.getElementById(id);

        if (!canvas) {
            return "";
        }

        try {
            return canvas.toDataURL(
                "image/png",
                1
            );
        } catch (error) {
            console.error(
                "Impossible d'exporter le graphique :",
                id,
                error
            );

            return "";
        }
    }

    function metricCard({
        title,
        current,
        minimum,
        average,
        maximum,
        chart,
        accentClass,
    }) {
        return `
            <article class="report-metric ${accentClass}">
                <header>
                    <div>
                        <small>RESSOURCE SYSTÈME</small>
                        <h2>${title}</h2>
                    </div>

                    <strong>${current}</strong>
                </header>

                <div class="report-chart">
                    ${
                        chart
                            ? `<img src="${chart}" alt="${title}">`
                            : `<p>Graphique indisponible</p>`
                    }
                </div>

                <div class="report-stats">
                    <div>
                        <span>Minimum</span>
                        <strong>${minimum}</strong>
                    </div>

                    <div>
                        <span>Moyenne</span>
                        <strong>${average}</strong>
                    </div>

                    <div>
                        <span>Maximum</span>
                        <strong>${maximum}</strong>
                    </div>
                </div>
            </article>
        `;
    }

    function exportMonitoringReport() {
        const reportWindow = window.open(
            "",
            "_blank",
            "width=1400,height=900"
        );

        if (!reportWindow) {
            alert(
                "Le navigateur a bloqué la fenêtre d’export. "
                + "Autorisez les fenêtres contextuelles pour ce site."
            );

            return;
        }

        const selectedPeriod =
            document.querySelector(
                ".cm-periods button.is-active"
            )?.textContent?.trim()
            || "24 heures";

        const measures = valueOf("cm-count");
        const generatedAt =
            new Date().toLocaleString("fr-FR");

        const cpuCard = metricCard({
            title: "Utilisation CPU",
            current: valueOf("cm-current-cpu"),
            minimum: valueOf("cm-cpu-min"),
            average: valueOf("cm-cpu-avg"),
            maximum: valueOf("cm-cpu-max"),
            chart: canvasImage("cm-cpu-chart"),
            accentClass: "report-cpu",
        });

        const memoryCard = metricCard({
            title: "Utilisation RAM",
            current: valueOf("cm-current-memory"),
            minimum: valueOf("cm-memory-min"),
            average: valueOf("cm-memory-avg"),
            maximum: valueOf("cm-memory-max"),
            chart: canvasImage("cm-memory-chart"),
            accentClass: "report-memory",
        });

        const diskCard = metricCard({
            title: "Utilisation disque",
            current: valueOf("cm-current-disk"),
            minimum: valueOf("cm-disk-min"),
            average: valueOf("cm-disk-avg"),
            maximum: valueOf("cm-disk-max"),
            chart: canvasImage("cm-disk-chart"),
            accentClass: "report-disk",
        });

        reportWindow.document.open();

        reportWindow.document.write(`
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">

    <title>
        Rapport Monitoring — Secure Local Cloud
    </title>

    <style>
        @page {
            size: A4 landscape;
            margin: 9mm;
        }

        * {
            box-sizing: border-box;
        }

        html,
        body {
            margin: 0;
            padding: 0;
            background: #ffffff;
            color: #17243c;
            font-family:
                Inter,
                Arial,
                Helvetica,
                sans-serif;
        }

        body {
            padding: 10px;
        }

        .report {
            width: 100%;
        }

        .report-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            margin-bottom: 14px;
            padding: 14px 18px;
            background:
                linear-gradient(
                    135deg,
                    #102349,
                    #1f4db8
                );
            color: #ffffff;
            border-radius: 16px;
        }

        .report-brand {
            display: flex;
            align-items: center;
            gap: 13px;
        }

        .report-logo {
            display: grid;
            place-items: center;
            width: 48px;
            height: 48px;
            background:
                rgba(255, 255, 255, 0.13);
            border:
                1px solid rgba(255, 255, 255, 0.22);
            border-radius: 13px;
            font-size: 22px;
        }

        .report-header h1 {
            margin: 0;
            font-size: 22px;
            line-height: 1.1;
        }

        .report-header p {
            margin: 5px 0 0;
            color: rgba(255, 255, 255, 0.77);
            font-size: 11px;
        }

        .report-date {
            text-align: right;
            font-size: 10px;
            line-height: 1.6;
        }

        .report-date strong {
            display: block;
            font-size: 11px;
        }

        .report-overview {
            display: grid;
            grid-template-columns:
                repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin-bottom: 13px;
        }

        .overview-card {
            min-height: 70px;
            padding: 11px 13px;
            background: #f7f9fd;
            border: 1px solid #dce5f1;
            border-radius: 12px;
        }

        .overview-card span {
            display: block;
            margin-bottom: 5px;
            color: #73839b;
            font-size: 9px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .overview-card strong {
            color: #17243c;
            font-size: 18px;
        }

        .overview-card.disk strong {
            color: #dc2626;
        }

        .report-grid {
            display: grid;
            grid-template-columns:
                repeat(3, minmax(0, 1fr));
            gap: 10px;
        }

        .report-metric {
            min-width: 0;
            overflow: hidden;
            background: #ffffff;
            border: 1px solid #dce5f1;
            border-top: 3px solid #3567e8;
            border-radius: 13px;
        }

        .report-memory {
            border-top-color: #10a87f;
        }

        .report-disk {
            border-top-color: #e9810b;
        }

        .report-metric header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 10px;
            padding: 11px 12px 5px;
        }

        .report-metric header small {
            color: #8292aa;
            font-size: 7px;
            font-weight: 800;
            letter-spacing: 0.06em;
        }

        .report-metric header h2 {
            margin: 4px 0 0;
            font-size: 13px;
        }

        .report-metric header > strong {
            padding: 5px 8px;
            background: #f0f5ff;
            border-radius: 8px;
            font-size: 11px;
        }

        .report-memory header > strong {
            color: #078f6c;
            background: #e9f9f3;
        }

        .report-disk header > strong {
            color: #dc2626;
            background: #fff0f1;
        }

        .report-chart {
            display: grid;
            place-items: center;
            height: 165px;
            padding: 4px 9px;
        }

        .report-chart img {
            display: block;
            max-width: 100%;
            width: 100%;
            max-height: 155px;
            object-fit: contain;
        }

        .report-chart p {
            color: #94a3b8;
            font-size: 10px;
        }

        .report-stats {
            display: grid;
            grid-template-columns:
                repeat(3, minmax(0, 1fr));
            gap: 6px;
            padding: 0 9px 10px;
        }

        .report-stats div {
            padding: 7px 4px;
            text-align: center;
            background: #f7f9fd;
            border: 1px solid #e3e9f2;
            border-radius: 8px;
        }

        .report-stats span {
            display: block;
            margin-bottom: 3px;
            color: #8292aa;
            font-size: 7px;
        }

        .report-stats strong {
            font-size: 9px;
        }

        .report-footer {
            display: flex;
            justify-content: space-between;
            gap: 15px;
            margin-top: 11px;
            padding: 8px 3px 0;
            color: #8090a7;
            border-top: 1px solid #e3e9f2;
            font-size: 8px;
        }

        .report-footer strong {
            color: #3567e8;
        }

        @media print {
            body {
                padding: 0;
            }

            .report-header,
            .overview-card,
            .report-metric {
                break-inside: avoid;
            }
        }
    </style>
</head>

<body>
    <main class="report">
        <header class="report-header">
            <div class="report-brand">
                <div class="report-logo">
                    ▥
                </div>

                <div>
                    <h1>
                        Rapport de supervision
                    </h1>

                    <p>
                        Secure Local Cloud Infrastructure
                    </p>
                </div>
            </div>

            <div class="report-date">
                <strong>
                    ${generatedAt}
                </strong>

                Période analysée :
                ${selectedPeriod}
            </div>
        </header>

        <section class="report-overview">
            <article class="overview-card">
                <span>Mesures enregistrées</span>
                <strong>${measures}</strong>
            </article>

            <article class="overview-card">
                <span>CPU actuel</span>
                <strong>
                    ${valueOf("cm-current-cpu")}
                </strong>
            </article>

            <article class="overview-card">
                <span>RAM actuelle</span>
                <strong>
                    ${valueOf("cm-current-memory")}
                </strong>
            </article>

            <article class="overview-card disk">
                <span>Disque actuel</span>
                <strong>
                    ${valueOf("cm-current-disk")}
                </strong>
            </article>
        </section>

        <section class="report-grid">
            ${cpuCard}
            ${memoryCard}
            ${diskCard}
        </section>

        <footer class="report-footer">
            <span>
                Données issues de Prometheus et de
                l’historique local.
            </span>

            <span>
                Généré par
                <strong>
                    Secure Local Cloud Infrastructure
                </strong>
            </span>
        </footer>
    </main>

    <script>
        window.addEventListener(
            "load",
            () => {
                window.setTimeout(
                    () => window.print(),
                    500
                );
            }
        );
    <\/script>
</body>
</html>
        `);

        reportWindow.document.close();
    }

    window.setTimeout(() => {
        const oldButton =
            document.getElementById("cm-export");

        if (!oldButton) {
            return;
        }

        /*
         * Remplacement du bouton pour supprimer
         * l'ancien événement window.print().
         */
        const newButton =
            oldButton.cloneNode(true);

        oldButton.replaceWith(newButton);

        newButton.addEventListener(
            "click",
            exportMonitoringReport
        );
    }, 300);
});


/* =========================================================
   NETTOYAGE DÉFINITIF DES ANCIENS GRAPHIQUES
========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    function hideLegacyMonitoring() {
        const cleanDashboard = document.getElementById(
            "clean-monitoring-dashboard"
        );

        if (!cleanDashboard) {
            return;
        }

        /*
         * Tous les canvas qui n'appartiennent pas à la
         * nouvelle interface sont considérés comme anciens.
         */
        const legacyCanvases = [
            ...document.querySelectorAll("canvas"),
        ].filter(canvas => {
            return !canvas.id.startsWith("cm-");
        });

        legacyCanvases.forEach(canvas => {
            let current = canvas;

            for (let level = 0; level < 8 && current; level += 1) {
                if (
                    current === cleanDashboard
                    || current.contains(cleanDashboard)
                ) {
                    break;
                }

                const tagName = current.tagName?.toLowerCase();

                const isCandidate =
                    tagName === "article"
                    || tagName === "section"
                    || current.classList?.contains("chart-card")
                    || current.classList?.contains("chart-panel")
                    || current.classList?.contains("monitoring-chart-card")
                    || current.classList?.contains("panel")
                    || current.classList?.contains("card");

                if (isCandidate) {
                    current.classList.add(
                        "legacy-monitoring-block"
                    );

                    break;
                }

                current = current.parentElement;
            }
        });

        /*
         * Nettoyage des anciennes cartes de résumé et
         * des anciennes barres de périodes.
         */
        const legacyLabels = [
            "Mesures enregistrées",
            "CPU moyen",
            "RAM moyenne",
            "Disque moyen",
            "Utilisation CPU",
            "Utilisation mémoire",
            "Utilisation disque",
        ];

        document.querySelectorAll(
            "h2, h3, h4, strong"
        ).forEach(element => {
            if (cleanDashboard.contains(element)) {
                return;
            }

            const text = element.textContent
                .replace(/\s+/g, " ")
                .trim();

            if (!legacyLabels.includes(text)) {
                return;
            }

            const block = element.closest(
                "article, section, "
                + ".chart-card, .chart-panel, "
                + ".monitoring-chart-card, "
                + ".summary-card, .metric-card, "
                + ".stat-card, .panel, .card"
            );

            if (block && !block.contains(cleanDashboard)) {
                block.classList.add(
                    "legacy-monitoring-block"
                );
            }
        });

        /*
         * Certains anciens graphiques sont regroupés dans
         * une grande grille. On la masque si elle ne contient
         * que des blocs désormais cachés.
         */
        document.querySelectorAll(
            ".monitoring-charts, "
            + ".charts-grid, "
            + ".monitoring-grid, "
            + ".history-charts"
        ).forEach(grid => {
            if (cleanDashboard.contains(grid)) {
                return;
            }

            if (
                grid.querySelector(
                    "canvas:not([id^='cm-'])"
                )
            ) {
                grid.classList.add(
                    "legacy-monitoring-block"
                );
            }
        });
    }

    /*
     * Le tableau moderne est construit après DOMContentLoaded.
     * On laisse donc quelques millisecondes avant le nettoyage.
     */
    window.setTimeout(
        hideLegacyMonitoring,
        250
    );

    window.setTimeout(
        hideLegacyMonitoring,
        1000
    );
});


/* =========================================================
   EXPORT PROFESSIONNEL DU MONITORING
========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    function valueOf(id) {
        return (
            document.getElementById(id)
                ?.textContent
                ?.trim()
            || "--"
        );
    }

    function canvasImage(id) {
        const canvas = document.getElementById(id);

        if (!canvas) {
            return "";
        }

        try {
            return canvas.toDataURL(
                "image/png",
                1
            );
        } catch (error) {
            console.error(
                "Impossible d'exporter le graphique :",
                id,
                error
            );

            return "";
        }
    }

    function metricCard({
        title,
        current,
        minimum,
        average,
        maximum,
        chart,
        accentClass,
    }) {
        return `
            <article class="report-metric ${accentClass}">
                <header>
                    <div>
                        <small>RESSOURCE SYSTÈME</small>
                        <h2>${title}</h2>
                    </div>

                    <strong>${current}</strong>
                </header>

                <div class="report-chart">
                    ${
                        chart
                            ? `<img src="${chart}" alt="${title}">`
                            : `<p>Graphique indisponible</p>`
                    }
                </div>

                <div class="report-stats">
                    <div>
                        <span>Minimum</span>
                        <strong>${minimum}</strong>
                    </div>

                    <div>
                        <span>Moyenne</span>
                        <strong>${average}</strong>
                    </div>

                    <div>
                        <span>Maximum</span>
                        <strong>${maximum}</strong>
                    </div>
                </div>
            </article>
        `;
    }

    function exportMonitoringReport() {
        const reportWindow = window.open(
            "",
            "_blank",
            "width=1400,height=900"
        );

        if (!reportWindow) {
            alert(
                "Le navigateur a bloqué la fenêtre d’export. "
                + "Autorisez les fenêtres contextuelles pour ce site."
            );

            return;
        }

        const selectedPeriod =
            document.querySelector(
                ".cm-periods button.is-active"
            )?.textContent?.trim()
            || "24 heures";

        const measures = valueOf("cm-count");
        const generatedAt =
            new Date().toLocaleString("fr-FR");

        const cpuCard = metricCard({
            title: "Utilisation CPU",
            current: valueOf("cm-current-cpu"),
            minimum: valueOf("cm-cpu-min"),
            average: valueOf("cm-cpu-avg"),
            maximum: valueOf("cm-cpu-max"),
            chart: canvasImage("cm-cpu-chart"),
            accentClass: "report-cpu",
        });

        const memoryCard = metricCard({
            title: "Utilisation RAM",
            current: valueOf("cm-current-memory"),
            minimum: valueOf("cm-memory-min"),
            average: valueOf("cm-memory-avg"),
            maximum: valueOf("cm-memory-max"),
            chart: canvasImage("cm-memory-chart"),
            accentClass: "report-memory",
        });

        const diskCard = metricCard({
            title: "Utilisation disque",
            current: valueOf("cm-current-disk"),
            minimum: valueOf("cm-disk-min"),
            average: valueOf("cm-disk-avg"),
            maximum: valueOf("cm-disk-max"),
            chart: canvasImage("cm-disk-chart"),
            accentClass: "report-disk",
        });

        reportWindow.document.open();

        reportWindow.document.write(`
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">

    <title>
        Rapport Monitoring — Secure Local Cloud
    </title>

    <style>
        @page {
            size: A4 landscape;
            margin: 9mm;
        }

        * {
            box-sizing: border-box;
        }

        html,
        body {
            margin: 0;
            padding: 0;
            background: #ffffff;
            color: #17243c;
            font-family:
                Inter,
                Arial,
                Helvetica,
                sans-serif;
        }

        body {
            padding: 10px;
        }

        .report {
            width: 100%;
        }

        .report-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            margin-bottom: 14px;
            padding: 14px 18px;
            background:
                linear-gradient(
                    135deg,
                    #102349,
                    #1f4db8
                );
            color: #ffffff;
            border-radius: 16px;
        }

        .report-brand {
            display: flex;
            align-items: center;
            gap: 13px;
        }

        .report-logo {
            display: grid;
            place-items: center;
            width: 48px;
            height: 48px;
            background:
                rgba(255, 255, 255, 0.13);
            border:
                1px solid rgba(255, 255, 255, 0.22);
            border-radius: 13px;
            font-size: 22px;
        }

        .report-header h1 {
            margin: 0;
            font-size: 22px;
            line-height: 1.1;
        }

        .report-header p {
            margin: 5px 0 0;
            color: rgba(255, 255, 255, 0.77);
            font-size: 11px;
        }

        .report-date {
            text-align: right;
            font-size: 10px;
            line-height: 1.6;
        }

        .report-date strong {
            display: block;
            font-size: 11px;
        }

        .report-overview {
            display: grid;
            grid-template-columns:
                repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin-bottom: 13px;
        }

        .overview-card {
            min-height: 70px;
            padding: 11px 13px;
            background: #f7f9fd;
            border: 1px solid #dce5f1;
            border-radius: 12px;
        }

        .overview-card span {
            display: block;
            margin-bottom: 5px;
            color: #73839b;
            font-size: 9px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .overview-card strong {
            color: #17243c;
            font-size: 18px;
        }

        .overview-card.disk strong {
            color: #dc2626;
        }

        .report-grid {
            display: grid;
            grid-template-columns:
                repeat(3, minmax(0, 1fr));
            gap: 10px;
        }

        .report-metric {
            min-width: 0;
            overflow: hidden;
            background: #ffffff;
            border: 1px solid #dce5f1;
            border-top: 3px solid #3567e8;
            border-radius: 13px;
        }

        .report-memory {
            border-top-color: #10a87f;
        }

        .report-disk {
            border-top-color: #e9810b;
        }

        .report-metric header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 10px;
            padding: 11px 12px 5px;
        }

        .report-metric header small {
            color: #8292aa;
            font-size: 7px;
            font-weight: 800;
            letter-spacing: 0.06em;
        }

        .report-metric header h2 {
            margin: 4px 0 0;
            font-size: 13px;
        }

        .report-metric header > strong {
            padding: 5px 8px;
            background: #f0f5ff;
            border-radius: 8px;
            font-size: 11px;
        }

        .report-memory header > strong {
            color: #078f6c;
            background: #e9f9f3;
        }

        .report-disk header > strong {
            color: #dc2626;
            background: #fff0f1;
        }

        .report-chart {
            display: grid;
            place-items: center;
            height: 165px;
            padding: 4px 9px;
        }

        .report-chart img {
            display: block;
            max-width: 100%;
            width: 100%;
            max-height: 155px;
            object-fit: contain;
        }

        .report-chart p {
            color: #94a3b8;
            font-size: 10px;
        }

        .report-stats {
            display: grid;
            grid-template-columns:
                repeat(3, minmax(0, 1fr));
            gap: 6px;
            padding: 0 9px 10px;
        }

        .report-stats div {
            padding: 7px 4px;
            text-align: center;
            background: #f7f9fd;
            border: 1px solid #e3e9f2;
            border-radius: 8px;
        }

        .report-stats span {
            display: block;
            margin-bottom: 3px;
            color: #8292aa;
            font-size: 7px;
        }

        .report-stats strong {
            font-size: 9px;
        }

        .report-footer {
            display: flex;
            justify-content: space-between;
            gap: 15px;
            margin-top: 11px;
            padding: 8px 3px 0;
            color: #8090a7;
            border-top: 1px solid #e3e9f2;
            font-size: 8px;
        }

        .report-footer strong {
            color: #3567e8;
        }

        @media print {
            body {
                padding: 0;
            }

            .report-header,
            .overview-card,
            .report-metric {
                break-inside: avoid;
            }
        }
    </style>
</head>

<body>
    <main class="report">
        <header class="report-header">
            <div class="report-brand">
                <div class="report-logo">
                    ▥
                </div>

                <div>
                    <h1>
                        Rapport de supervision
                    </h1>

                    <p>
                        Secure Local Cloud Infrastructure
                    </p>
                </div>
            </div>

            <div class="report-date">
                <strong>
                    ${generatedAt}
                </strong>

                Période analysée :
                ${selectedPeriod}
            </div>
        </header>

        <section class="report-overview">
            <article class="overview-card">
                <span>Mesures enregistrées</span>
                <strong>${measures}</strong>
            </article>

            <article class="overview-card">
                <span>CPU actuel</span>
                <strong>
                    ${valueOf("cm-current-cpu")}
                </strong>
            </article>

            <article class="overview-card">
                <span>RAM actuelle</span>
                <strong>
                    ${valueOf("cm-current-memory")}
                </strong>
            </article>

            <article class="overview-card disk">
                <span>Disque actuel</span>
                <strong>
                    ${valueOf("cm-current-disk")}
                </strong>
            </article>
        </section>

        <section class="report-grid">
            ${cpuCard}
            ${memoryCard}
            ${diskCard}
        </section>

        <footer class="report-footer">
            <span>
                Données issues de Prometheus et de
                l’historique local.
            </span>

            <span>
                Généré par
                <strong>
                    Secure Local Cloud Infrastructure
                </strong>
            </span>
        </footer>
    </main>

    <script>
        window.addEventListener(
            "load",
            () => {
                window.setTimeout(
                    () => window.print(),
                    500
                );
            }
        );
    <\/script>
</body>
</html>
        `);

        reportWindow.document.close();
    }

    window.setTimeout(() => {
        const oldButton =
            document.getElementById("cm-export");

        if (!oldButton) {
            return;
        }

        /*
         * Remplacement du bouton pour supprimer
         * l'ancien événement window.print().
         */
        const newButton =
            oldButton.cloneNode(true);

        oldButton.replaceWith(newButton);

        newButton.addEventListener(
            "click",
            exportMonitoringReport
        );
    }, 300);
});
