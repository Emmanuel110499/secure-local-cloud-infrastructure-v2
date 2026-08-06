
document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    const menuButton = document.getElementById(
        "mobile-menu-button"
    );
    const overlay = document.getElementById(
        "sidebar-overlay"
    );

    function openMenu() {
        if (!sidebar || !menuButton || !overlay) {
            return;
        }

        sidebar.classList.add("mobile-open");
        overlay.classList.add("visible");
        menuButton.hidden = true;
        menuButton.style.display = "none";
        document.body.classList.add("menu-is-open");
    }

    function closeMenu() {
        if (!sidebar || !menuButton || !overlay) {
            return;
        }

        sidebar.classList.remove("mobile-open");
        overlay.classList.remove("visible");
        menuButton.hidden = false;
        menuButton.style.display = "";
        document.body.classList.remove("menu-is-open");
    }

    if (menuButton) {
        menuButton.addEventListener("click", (event) => {
            event.preventDefault();
            openMenu();
        });
    }

    if (overlay) {
        overlay.addEventListener("click", closeMenu);
    }

    if (sidebar) {
        sidebar.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                if (window.innerWidth <= 820) {
                    closeMenu();
                }
            });
        });
    }

    window.addEventListener("resize", () => {
        if (window.innerWidth > 820) {
            closeMenu();
        }
    });

    const initial =
        window.dashboardInitialData || {};

    const historySize = 30;

    function nowLabel() {
        return new Date().toLocaleTimeString(
            "fr-FR",
            {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
            }
        );
    }

    function createInitialHistory(value) {
        const base = Number(value) || 0;

        return Array.from(
            { length: historySize },
            (_, index) => {
                const variation =
                    Math.sin(index / 3) * 0.7;

                return Math.max(
                    0,
                    Math.min(100, base + variation)
                );
            }
        );
    }

    function createGradient(
        context,
        topColor,
        bottomColor
    ) {
        const gradient =
            context.createLinearGradient(
                0,
                0,
                0,
                240
            );

        gradient.addColorStop(0, topColor);
        gradient.addColorStop(1, bottomColor);

        return gradient;
    }

    function createMetricChart({
        canvasId,
        initialValue,
        borderColor,
        gradientTop,
        gradientBottom,
    }) {
        const canvas =
            document.getElementById(canvasId);

        if (!canvas) {
            console.error(
                `Canvas introuvable : ${canvasId}`
            );
            return null;
        }

        if (typeof Chart === "undefined") {
            console.error(
                "Chart.js n'est pas chargé."
            );
            return null;
        }

        const context = canvas.getContext("2d");

        const gradient = createGradient(
            context,
            gradientTop,
            gradientBottom
        );

        const values =
            createInitialHistory(initialValue);

        const labels = Array.from(
            { length: historySize },
            () => ""
        );

        labels[labels.length - 1] = nowLabel();

        return new Chart(canvas, {
            type: "line",
            data: {
                labels,
                datasets: [{
                    data: values,
                    borderColor,
                    backgroundColor: gradient,
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.38,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    pointHoverBackgroundColor:
                        borderColor,
                    pointHoverBorderColor: "#ffffff",
                    pointHoverBorderWidth: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 450,
                    easing: "easeOutQuart",
                },
                interaction: {
                    intersect: false,
                    mode: "index",
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        backgroundColor: "#0f172a",
                        titleColor: "#ffffff",
                        bodyColor: "#e2e8f0",
                        displayColors: false,
                        callbacks: {
                            label: (context) =>
                                `${Number(
                                    context.raw
                                ).toFixed(1)} %`,
                        },
                    },
                },
                scales: {
                    x: {
                        display: false,
                        grid: {
                            display: false,
                        },
                        border: {
                            display: false,
                        },
                    },
                    y: {
                        beginAtZero: true,
                        suggestedMax: 100,
                        ticks: {
                            stepSize: 20,
                            callback: (value) =>
                                `${value}%`,
                            color: "#94a3b8",
                            font: {
                                size: 10,
                            },
                        },
                        grid: {
                            color: "#e9eef5",
                        },
                        border: {
                            display: false,
                        },
                    },
                },
            },
        });
    }

    const cpuChart = createMetricChart({
        canvasId: "cpu-chart",
        initialValue: initial.cpu,
        borderColor: "#2563eb",
        gradientTop:
            "rgba(37, 99, 235, 0.28)",
        gradientBottom:
            "rgba(37, 99, 235, 0.01)",
    });

    const memoryChart = createMetricChart({
        canvasId: "memory-chart",
        initialValue: initial.memory,
        borderColor: "#10b981",
        gradientTop:
            "rgba(16, 185, 129, 0.25)",
        gradientBottom:
            "rgba(16, 185, 129, 0.01)",
    });

    function formatPercent(value) {
        const number = Number(value);

        return Number.isFinite(number)
            ? `${number.toFixed(1)}%`
            : "N/A";
    }

    function pushChartValue(chart, value) {
        if (!chart) {
            return;
        }

        const number = Number(value) || 0;
        const dataset =
            chart.data.datasets[0].data;
        const labels = chart.data.labels;

        dataset.push(number);
        labels.push(nowLabel());

        if (dataset.length > historySize) {
            dataset.shift();
            labels.shift();
        }

        chart.update();
    }

    function setText(id, value) {
        const element =
            document.getElementById(id);

        if (element) {
            element.textContent = value;
        }
    }


    function updateDashboardAlert(metrics, services = {}) {
        const alertBox = document.getElementById(
            "dashboard-alert"
        );
        const alertText = document.getElementById(
            "dashboard-alert-text"
        );
        const alertIcon = document.getElementById(
            "dashboard-alert-icon"
        );

        if (!alertBox || !alertText) {
            return;
        }

        const cpu = Number(metrics.cpu) || 0;
        const memory = Number(metrics.memory) || 0;
        const disk = Number(metrics.disk) || 0;

        const unavailableServices = Object.entries(
            services
        )
            .filter(([, status]) => !status)
            .map(([name]) => (
                name
                    .replaceAll("_", " ")
                    .replace(/\b\w/g, (letter) =>
                        letter.toUpperCase()
                    )
            ));

        alertBox.className = "dashboard-alert hidden";

        if (unavailableServices.length > 0) {
            alertBox.classList.add("danger");

            if (alertIcon) {
                alertIcon.textContent = "🚨";
            }

            alertText.textContent =
                `Service(s) indisponible(s) : ${
                    unavailableServices.join(", ")
                }`;

            return;
        }

        if (cpu >= 85) {
            alertBox.classList.add("danger");

            if (alertIcon) {
                alertIcon.textContent = "🔥";
            }

            alertText.textContent =
                `CPU critique : ${cpu.toFixed(1)} %`;

            return;
        }

        if (memory >= 90) {
            alertBox.classList.add("danger");

            if (alertIcon) {
                alertIcon.textContent = "🧠";
            }

            alertText.textContent =
                `Mémoire critique : ${memory.toFixed(1)} %`;

            return;
        }

        if (disk >= 85) {
            alertBox.classList.add("warning");

            if (alertIcon) {
                alertIcon.textContent = "💾";
            }

            alertText.textContent =
                `Espace disque élevé : ${disk.toFixed(1)} %`;

            return;
        }

        if (alertIcon) {
            alertIcon.textContent = "✅";
        }

        alertText.textContent =
            "Infrastructure opérationnelle";
    }


    function updateHealthScore(health) {
        if (!health) {
            return;
        }

        const card = document.getElementById(
            "global-health-card"
        );

        const scoreElement = document.getElementById(
            "global-health-score"
        );

        const labelElement = document.getElementById(
            "global-health-label"
        );

        const detailElement = document.getElementById(
            "global-health-detail"
        );

        if (!card) {
            return;
        }

        const allowedLevels = [
            "excellent",
            "good",
            "warning",
            "critical",
        ];

        const level = allowedLevels.includes(
            health.level
        )
            ? health.level
            : "warning";

        card.classList.remove(
            "health-excellent",
            "health-good",
            "health-warning",
            "health-critical"
        );

        card.classList.add(
            `health-${level}`
        );

        const score = Number(health.score);

        if (scoreElement) {
            scoreElement.textContent =
                Number.isFinite(score)
                    ? Math.round(score)
                    : "--";
        }

        if (labelElement) {
            labelElement.textContent =
                health.label || "État inconnu";
        }

        if (detailElement) {
            const findings = Array.isArray(
                health.findings
            )
                ? health.findings
                : [];

            detailElement.textContent =
                findings[0]
                || "Aucun incident détecté";
        }
    }

    async function refreshDashboard() {
        try {
            const response = await fetch(
                `/api/metrics?t=${Date.now()}`,
                {
                    cache: "no-store",
                    headers: {
                        Accept: "application/json",
                    },
                }
            );

            if (!response.ok) {
                console.error(
                    "API metrics indisponible :",
                    response.status
                );
                return;
            }

            const payload = await response.json();

            updateHealthScore(
                payload.health
            );

            const metrics = payload.metrics || {};

            updateDashboardAlert(
                metrics,
                payload.services || {}
            );

            setText(
                "cpu-value",
                formatPercent(metrics.cpu)
            );

            setText(
                "memory-value",
                formatPercent(metrics.memory)
            );

            setText(
                "containers-value",
                metrics.containers ?? 0
            );

            setText(
                "cpu-chart-label",
                formatPercent(metrics.cpu)
            );

            setText(
                "memory-chart-label",
                formatPercent(metrics.memory)
            );

            setText(
                "docker-donut-value",
                metrics.containers ?? 0
            );

            setText(
                "docker-running-value",
                metrics.containers ?? 0
            );

            setText(
                "docker-total-value",
                metrics.containers ?? 0
            );

            pushChartValue(
                cpuChart,
                metrics.cpu
            );

            pushChartValue(
                memoryChart,
                metrics.memory
            );

            if (payload.updated_at) {
                setText(
                    "last-update",
                    new Date(
                        payload.updated_at
                    ).toLocaleString("fr-FR")
                );
            }
        } catch (error) {
            console.error(
                "Actualisation impossible :",
                error
            );
        }
    }


    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function renderDockerContainers(containers) {
        const tbody = document.getElementById(
            "docker-table-body"
        );

        if (!tbody) {
            return;
        }

        if (!Array.isArray(containers) || !containers.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6">
                        Aucun conteneur détecté.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = containers.map((container) => {
            const status = String(
                container.status || ""
            ).toLowerCase();

            const isRunning =
                status.includes("running")
                || status === "up"
                || status === "active";

            return `
                <tr>
                    <td class="container-name">
                        ${escapeHtml(container.name)}
                    </td>

                    <td class="container-image">
                        ${escapeHtml(container.image)}
                    </td>

                    <td>
                        ${Number(container.cpu || 0).toFixed(2)} %
                    </td>

                    <td>
                        ${Number(container.memory_mb || 0).toFixed(1)} MB
                    </td>

                    <td>
                        ${escapeHtml(container.uptime || "N/A")}
                    </td>

                    <td>
                        <span
                            class="container-status ${
                                isRunning
                                    ? "running"
                                    : "stopped"
                            }"
                        >
                            <span
                                class="container-status-dot"
                            ></span>

                            ${
                                isRunning
                                    ? "Running"
                                    : "Stopped"
                            }
                        </span>
                    </td>
                </tr>
            `;
        }).join("");
    }

    async function refreshDockerContainers() {
        try {
            const response = await fetch(
                `/api/docker/containers?t=${Date.now()}`,
                {
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

            renderDockerContainers(
                payload.containers || []
            );
        } catch (error) {
            console.error(
                "Actualisation Docker impossible :",
                error
            );
        }
    }

    setTimeout(refreshDockerContainers, 800);
    setInterval(refreshDockerContainers, 10000);

    setTimeout(refreshDashboard, 1500);
    setInterval(refreshDashboard, 10000);
});



