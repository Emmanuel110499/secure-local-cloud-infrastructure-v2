(() => {
    "use strict";

    const CHART_COLORS = {
        cpu: {
            line: "#1458d4",
            fill: "rgba(20, 88, 212, 0.16)",
        },
        ram: {
            line: "#15803d",
            fill: "rgba(21, 128, 61, 0.15)",
        },
        disk: {
            line: "#ea580c",
            fill: "rgba(234, 88, 12, 0.17)",
        },
        threshold: "#dc2626",
        grid: "rgba(100, 116, 139, 0.34)",
        tick: "#334155",
        axisBorder: "rgba(71, 85, 105, 0.42)",
    };

    function getChartType(chart) {
        const canvasId = String(
            chart?.canvas?.id || ""
        ).toLowerCase();

        if (canvasId.includes("cpu")) {
            return "cpu";
        }

        if (
            canvasId.includes("ram")
            || canvasId.includes("memory")
        ) {
            return "ram";
        }

        if (canvasId.includes("disk")) {
            return "disk";
        }

        return null;
    }

    function isThresholdDataset(dataset) {
        const label = String(
            dataset?.label || ""
        ).toLowerCase();

        return (
            label.includes("seuil")
            || label.includes("threshold")
            || label.includes("75")
        );
    }

    function improveDataset(
        dataset,
        chartType
    ) {
        if (!dataset) {
            return;
        }

        if (isThresholdDataset(dataset)) {
            dataset.borderColor =
                CHART_COLORS.threshold;

            dataset.backgroundColor =
                "transparent";

            dataset.borderWidth = 2.5;
            dataset.borderDash = [9, 6];
            dataset.pointRadius = 0;
            dataset.pointHoverRadius = 0;
            dataset.fill = false;
            dataset.tension = 0;

            return;
        }

        const palette =
            CHART_COLORS[chartType];

        dataset.borderColor =
            palette.line;

        dataset.backgroundColor =
            palette.fill;

        dataset.borderWidth = 3.4;
        dataset.fill = true;
        dataset.tension = 0.28;

        dataset.pointRadius = 0;
        dataset.pointHoverRadius = 4;
        dataset.pointHoverBorderWidth = 2;
        dataset.pointHoverBorderColor =
            "#ffffff";

        dataset.pointHoverBackgroundColor =
            palette.line;

        dataset.borderJoinStyle = "round";
        dataset.borderCapStyle = "round";
    }

    function improveScale(scale) {
        if (!scale) {
            return;
        }

        scale.grid = {
            ...(scale.grid || {}),
            display: true,
            color: CHART_COLORS.grid,
            lineWidth: 1,
            drawTicks: true,
            tickLength: 5,
        };

        scale.ticks = {
            ...(scale.ticks || {}),
            color: CHART_COLORS.tick,
            font: {
                ...(
                    scale.ticks?.font || {}
                ),
                size: 12,
                weight: "600",
            },
            padding: 7,
        };

        scale.border = {
            ...(scale.border || {}),
            display: true,
            color:
                CHART_COLORS.axisBorder,
            width: 1,
        };
    }

    function improveChart(chart) {
        const chartType =
            getChartType(chart);

        if (!chartType) {
            return;
        }

        const datasets =
            chart.data?.datasets || [];

        datasets.forEach(dataset => {
            improveDataset(
                dataset,
                chartType
            );
        });

        chart.options = chart.options || {};

        chart.options.devicePixelRatio = 2;

        chart.options.animation = {
            duration: 250,
        };

        chart.options.responsive = true;
        chart.options.maintainAspectRatio =
            false;

        chart.options.plugins =
            chart.options.plugins || {};

        chart.options.plugins.legend = {
            ...(
                chart.options.plugins.legend
                || {}
            ),
            labels: {
                ...(
                    chart.options.plugins
                        ?.legend
                        ?.labels
                    || {}
                ),
                color:
                    CHART_COLORS.tick,
                font: {
                    size: 12,
                    weight: "600",
                },
            },
        };

        chart.options.plugins.tooltip = {
            ...(
                chart.options.plugins.tooltip
                || {}
            ),
            backgroundColor: "#0f172a",
            titleColor: "#ffffff",
            bodyColor: "#f8fafc",
            borderColor:
                "rgba(255,255,255,.16)",
            borderWidth: 1,
            padding: 11,
        };

        const scales =
            chart.options.scales || {};

        Object.values(scales).forEach(
            improveScale
        );

        chart.options.scales = scales;

        chart.update("none");
    }

    function improveAllCharts() {
        if (
            typeof Chart === "undefined"
            || !Chart.instances
        ) {
            return;
        }

        Object.values(
            Chart.instances
        ).forEach(improveChart);
    }

    function scheduleImprovement() {
        improveAllCharts();

        window.setTimeout(
            improveAllCharts,
            500
        );

        window.setTimeout(
            improveAllCharts,
            1500
        );
    }

    if (
        document.readyState
        === "loading"
    ) {
        document.addEventListener(
            "DOMContentLoaded",
            scheduleImprovement,
            {
                once: true,
            }
        );
    } else {
        scheduleImprovement();
    }

    window.addEventListener(
        "beforeprint",
        improveAllCharts
    );

    document.addEventListener(
        "click",
        event => {
            const exportButton =
                event.target.closest(
                    '[data-export],'
                    + '.export-button,'
                    + '#export-pdf,'
                    + '#monitoring-export'
                );

            if (exportButton) {
                improveAllCharts();
            }
        },
        true
    );

    window.setInterval(
        improveAllCharts,
        15000
    );
})();
