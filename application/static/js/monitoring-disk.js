document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("diskChart");
    const currentValue = document.getElementById(
        "disk-monitoring-current"
    );

    if (!canvas) {
        console.error("Canvas diskChart introuvable.");
        return;
    }

    if (typeof Chart === "undefined") {
        console.error("Chart.js n’est pas chargé.");
        return;
    }

    const labels = [];
    const diskValues = [];
    const alertThreshold = [];

    const diskChart = new Chart(
        canvas,
        {
            type: "line",
            data: {
                labels,
                datasets: [
                    {
                        label: "Disque utilisé",
                        data: diskValues,
                        borderColor: "#f59e0b",
                        backgroundColor:
                            "rgba(245, 158, 11, 0.14)",
                        borderWidth: 3,
                        fill: true,
                        tension: 0.35,
                        pointRadius: 2,
                    },
                    {
                        label: "Seuil d’alerte 80 %",
                        data: alertThreshold,
                        borderColor: "#ef4444",
                        borderWidth: 2,
                        borderDash: [7, 7],
                        pointRadius: 0,
                        fill: false,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: "index",
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: "bottom",
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback(value) {
                                return value + " %";
                            },
                        },
                    },
                },
            },
        }
    );

    async function refreshDiskMonitoring() {
        try {
            const response = await fetch(
                "/api/metrics?t=" + Date.now(),
                {
                    cache: "no-store",
                }
            );

            if (!response.ok) {
                throw new Error(
                    "API métriques indisponible"
                );
            }

            const data = await response.json();
            const metrics = data.metrics || data;

            const disk = Number(metrics.disk) || 0;

            labels.push(
                new Date().toLocaleTimeString(
                    "fr-FR",
                    {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                    }
                )
            );

            diskValues.push(disk);
            alertThreshold.push(80);

            while (labels.length > 20) {
                labels.shift();
                diskValues.shift();
                alertThreshold.shift();
            }

            if (!currentValue) {
                return;
            }

            currentValue.textContent =
                disk.toFixed(1) + " %";

            currentValue.dataset.level =
                disk >= 80
                    ? "critical"
                    : disk >= 70
                        ? "warning"
                        : "normal";

            diskChart.update();

        } catch (error) {
            console.error(
                "Erreur monitoring disque :",
                error
            );

            currentValue.textContent =
                "Indisponible";
        }
    }

    refreshDiskMonitoring();

    window.setInterval(
        refreshDiskMonitoring,
        5000
    );
});
