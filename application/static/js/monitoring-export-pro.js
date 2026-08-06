document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    function text(id, fallback = "--") {
        const element = document.getElementById(id);

        return element?.textContent?.trim() || fallback;
    }

    function chartImage(id) {
        const canvas = document.getElementById(id);

        if (!canvas) {
            return "";
        }

        try {
            return canvas.toDataURL("image/png", 1);
        } catch (error) {
            console.error(
                "Export du graphique impossible :",
                id,
                error
            );

            return "";
        }
    }

    function currentPeriod() {
        return (
            document.querySelector(
                ".cm-periods button.is-active"
            )?.textContent?.trim()
            || "24 heures"
        );
    }

    function statusClass(value) {
        const numeric = Number(
            String(value)
                .replace(",", ".")
                .replace(/[^\d.]/g, "")
        );

        if (!Number.isFinite(numeric)) {
            return "";
        }

        if (numeric >= 80) {
            return "critical";
        }

        if (numeric >= 70) {
            return "warning";
        }

        return "normal";
    }

    function metricReportCard({
        title,
        subtitle,
        current,
        minimum,
        average,
        maximum,
        image,
        className,
    }) {
        return `
            <article class="metric-card ${className}">
                <header class="metric-header">
                    <div>
                        <span class="metric-label">
                            ${subtitle}
                        </span>

                        <h2>${title}</h2>
                    </div>

                    <strong
                        class="metric-current ${statusClass(current)}"
                    >
                        ${current}
                    </strong>
                </header>

                <div class="metric-chart">
                    ${
                        image
                            ? `
                                <img
                                    src="${image}"
                                    alt="${title}"
                                >
                            `
                            : `
                                <div class="chart-unavailable">
                                    Graphique indisponible
                                </div>
                            `
                    }
                </div>

                <div class="metric-stats">
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

    function createProfessionalReport() {
        const reportWindow = window.open(
            "",
            "_blank",
            "width=1500,height=950"
        );

        if (!reportWindow) {
            alert(
                "La fenêtre d’export a été bloquée. "
                + "Autorisez les fenêtres contextuelles pour ce site."
            );

            return;
        }

        const generatedAt = new Date().toLocaleString(
            "fr-FR",
            {
                dateStyle: "long",
                timeStyle: "medium",
            }
        );

        const cpuCurrent = text("cm-current-cpu");
        const memoryCurrent = text("cm-current-memory");
        const diskCurrent = text("cm-current-disk");

        const cpuCard = metricReportCard({
            title: "Utilisation CPU",
            subtitle: "Processeur",
            current: cpuCurrent,
            minimum: text("cm-cpu-min"),
            average: text("cm-cpu-avg"),
            maximum: text("cm-cpu-max"),
            image: chartImage("cm-cpu-chart"),
            className: "cpu-card",
        });

        const memoryCard = metricReportCard({
            title: "Utilisation RAM",
            subtitle: "Mémoire",
            current: memoryCurrent,
            minimum: text("cm-memory-min"),
            average: text("cm-memory-avg"),
            maximum: text("cm-memory-max"),
            image: chartImage("cm-memory-chart"),
            className: "memory-card",
        });

        const diskCard = metricReportCard({
            title: "Utilisation disque",
            subtitle: "Stockage",
            current: diskCurrent,
            minimum: text("cm-disk-min"),
            average: text("cm-disk-avg"),
            maximum: text("cm-disk-max"),
            image: chartImage("cm-disk-chart"),
            className: "disk-card",
        });

        reportWindow.document.open();

        reportWindow.document.write(`
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <title>
        Rapport de supervision — Secure Local Cloud
    </title>

    <style>
        @page {
            size: A4 landscape;
            margin: 7mm;
        }

        * {
            box-sizing: border-box;
        }

        html,
        body {
            width: 100%;
            margin: 0;
            padding: 0;
            color: #17243c;
            background: #ffffff;
            font-family:
                Inter,
                Arial,
                Helvetica,
                sans-serif;
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
        }

        body {
            padding: 8px;
        }

        .report {
            width: 100%;
            max-width: 1280px;
            margin: 0 auto;
        }

        .report-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            min-height: 78px;
            padding: 14px 18px;
            color: #ffffff;
            background:
                radial-gradient(
                    circle at 90% 0,
                    rgba(90, 124, 255, 0.55),
                    transparent 38%
                ),
                linear-gradient(
                    135deg,
                    #0b1f43,
                    #214fb9
                );
            border-radius: 16px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 13px;
        }

        .brand-icon {
            display: grid;
            place-items: center;
            width: 46px;
            height: 46px;
            color: #ffffff;
            background:
                rgba(255, 255, 255, 0.14);
            border:
                1px solid rgba(255, 255, 255, 0.24);
            border-radius: 13px;
            font-size: 22px;
            font-weight: 900;
        }

        .brand h1 {
            margin: 0;
            font-size: 21px;
            line-height: 1.08;
        }

        .brand p {
            margin: 5px 0 0;
            color: rgba(255, 255, 255, 0.76);
            font-size: 10px;
        }

        .report-meta {
            text-align: right;
        }

        .report-meta strong {
            display: block;
            margin-bottom: 4px;
            font-size: 11px;
        }

        .report-meta span {
            display: block;
            color: rgba(255, 255, 255, 0.8);
            font-size: 9px;
            line-height: 1.55;
        }

        .overview {
            display: grid;
            grid-template-columns:
                repeat(4, minmax(0, 1fr));
            gap: 9px;
            margin: 10px 0;
        }

        
.overview-card {
    display:flex;
    align-items:center;
    gap:14px;
    min-height:82px;
    padding:14px 18px;
    background:linear-gradient(145deg,#ffffff,#f7f9fd);
    border:1px solid #dce5f1;
    border-radius:14px;
}

.overview-card > div{
    display:flex;
    flex-direction:column;
    justify-content:center;
    flex:1;
    height:100%;
}

.overview-card span{
    display:block;
    margin:0 0 6px;
    color:#7c8aa5;
    font-size:10px;
    font-weight:700;
    text-transform:uppercase;
    line-height:1;
}

.overview-card strong{
    display:block;
    font-size:34px;
    font-weight:800;
    line-height:1;
    color:#16233d;
}


        .overview-icon {
            display: grid;
            place-items: center;
            flex: 0 0 35px;
            width: 35px;
            height: 35px;
            border-radius: 10px;
            font-size: 8px;
            font-weight: 900;
        }

        .overview-icon.blue {
            color: #285edb;
            background: #e9efff;
        }

        .overview-icon.green {
            color: #078f6c;
            background: #e5f8f1;
        }

        .overview-icon.orange {
            color: #c66b00;
            background: #fff1dc;
        }

        .overview-card span {
            display: block;
            margin-bottom: 3px;
            color: #7788a1;
            font-size: 7px;
            font-weight: 750;
            text-transform: uppercase;
        }

        .overview-card strong {
            color: #17243c;
            font-size: 14px;
            line-height: 1;
        }

        .overview-card strong.normal {
            color: #078f6c;
        }

        .overview-card strong.warning {
            color: #d97706;
        }

        .overview-card strong.critical {
            color: #dc2626;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns:
                repeat(3, minmax(0, 1fr));
            gap: 9px;
        }

        .metric-card {
            min-width: 0;
            overflow: hidden;
            background: #ffffff;
            border: 1px solid #dce5f1;
            border-top: 3px solid #3567e8;
            border-radius: 12px;
        }

        .memory-card {
            border-top-color: #10a87f;
        }

        .disk-card {
            border-top-color: #e9810b;
        }

        .metric-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 10px;
            padding: 9px 10px 4px;
        }

        .metric-label {
            color: #7e8fa7;
            font-size: 6px;
            font-weight: 850;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .metric-header h2 {
            margin: 4px 0 0;
            font-size: 12px;
            line-height: 1.1;
        }

        .metric-current {
            padding: 5px 7px;
            color: #315fdf;
            background: #edf3ff;
            border: 1px solid #d9e4fa;
            border-radius: 8px;
            font-size: 9px;
            white-space: nowrap;
        }

        .metric-current.normal {
            color: #078f6c;
            background: #e9f9f3;
            border-color: #ccefe2;
        }

        .metric-current.warning {
            color: #c66b00;
            background: #fff5e5;
            border-color: #f8ddb4;
        }

        .metric-current.critical {
            color: #cf252d;
            background: #fff0f1;
            border-color: #f8ced1;
        }

        .metric-chart {
            display: grid;
            place-items: center;
            height: 143px;
            padding: 1px 7px;
        }

        .metric-chart img {
            display: block;
            width: 100%;
            height: 136px;
            object-fit: contain;
        }

        .chart-unavailable {
            color: #94a3b8;
            font-size: 9px;
        }

        .metric-stats {
            display: grid;
            grid-template-columns:
                repeat(3, minmax(0, 1fr));
            gap: 5px;
            padding: 0 7px 8px;
        }

        .metric-stats div {
            padding: 6px 3px;
            text-align: center;
            background: #f6f8fc;
            border: 1px solid #e2e8f2;
            border-radius: 7px;
        }

        .metric-stats span {
            display: block;
            margin-bottom: 3px;
            color: #8292aa;
            font-size: 6px;
        }

        .metric-stats strong {
            color: #17243c;
            font-size: 8px;
        }

        .report-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 15px;
            margin-top: 8px;
            padding: 7px 2px 0;
            color: #8191a8;
            border-top: 1px solid #e4eaf2;
            font-size: 7px;
        }

        .report-footer strong {
            color: #3567e8;
        }

        @media print {
            html,
            body {
                width: 100%;
                height: auto;
            }

            body {
                padding: 0;
            }

            .report {
                max-width: none;
            }

            .report-header,
            .overview-card,
            .metric-card {
                break-inside: avoid;
                page-break-inside: avoid;
            }
        }

        /* CENTRAGE DÉFINITIF DES CARTES DE SYNTHÈSE PDF */

        .overview-card {
            display: grid !important;
            grid-template-columns: 38px minmax(0, 1fr) !important;
            align-items: center !important;
            column-gap: 11px !important;
            min-height: 64px !important;
            padding: 10px 13px !important;
        }

        .overview-icon {
            display: grid !important;
            place-items: center !important;
            align-self: center !important;
            justify-self: center !important;

            width: 38px !important;
            height: 38px !important;
            margin: 0 !important;
            padding: 0 !important;

            border-radius: 11px !important;

            font-size: 7px !important;
            font-weight: 900 !important;
            line-height: 1 !important;
            letter-spacing: 0 !important;
            text-align: center !important;
            text-transform: uppercase !important;
        }

        .overview-card > div {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: flex-start !important;

            min-width: 0 !important;
            min-height: 38px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .overview-card > div > span {
            display: block !important;
            margin: 0 0 5px !important;
            padding: 0 !important;

            color: #7788a1 !important;
            font-size: 7px !important;
            font-weight: 750 !important;
            line-height: 1 !important;
            text-transform: uppercase !important;
        }

        .overview-card > div > strong {
            display: block !important;
            margin: 0 !important;
            padding: 0 !important;

            font-size: 15px !important;
            font-weight: 900 !important;
            line-height: 1 !important;
        }

    </style>
</head>

<body>
    <main class="report">
        <header class="report-header">
            <div class="brand">
                <div class="brand-icon">
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

            <div class="report-meta">
                <strong>${generatedAt}</strong>

                <span>
                    Période analysée :
                    ${currentPeriod()}
                </span>

                <span>
                    Serveur supervisé :
                    srv-web · 192.168.50.10
                </span>
            </div>
        </header>

        <section class="overview">
            <article class="overview-card">
                <span class="overview-icon blue">
                    DATA
                </span>

                <div>
                    <span>Mesures enregistrées</span>
                    <strong>${text("cm-count")}</strong>
                </div>
            </article>

            <article class="overview-card">
                <span class="overview-icon blue">
                    CPU
                </span>

                <div>
                    <span>CPU actuel</span>
                    <strong class="${statusClass(cpuCurrent)}">
                        ${cpuCurrent}
                    </strong>
                </div>
            </article>

            <article class="overview-card">
                <span class="overview-icon green">
                    RAM
                </span>

                <div>
                    <span>RAM actuelle</span>
                    <strong class="${statusClass(memoryCurrent)}">
                        ${memoryCurrent}
                    </strong>
                </div>
            </article>

            <article class="overview-card">
                <span class="overview-icon orange">
                    SSD
                </span>

                <div>
                    <span>Disque actuel</span>
                    <strong class="${statusClass(diskCurrent)}">
                        ${diskCurrent}
                    </strong>
                </div>
            </article>
        </section>

        <section class="metrics-grid">
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
        function launchPrint() {
            const images = [
                ...document.images
            ];

            if (!images.length) {
                window.print();
                return;
            }

            let loaded = 0;

            function ready() {
                loaded += 1;

                if (loaded >= images.length) {
                    window.setTimeout(
                        () => window.print(),
                        300
                    );
                }
            }

            images.forEach(image => {
                if (image.complete) {
                    ready();
                } else {
                    image.addEventListener(
                        "load",
                        ready,
                        { once: true }
                    );

                    image.addEventListener(
                        "error",
                        ready,
                        { once: true }
                    );
                }
            });
        }

        window.addEventListener(
            "load",
            launchPrint
        );
    <\/script>
</body>
</html>
        `);

        reportWindow.document.close();
    }

    function installProfessionalExport() {
        const currentButton =
            document.getElementById("cm-export");

        if (!currentButton) {
            window.setTimeout(
                installProfessionalExport,
                300
            );

            return;
        }

        if (
            currentButton.dataset.exportMode
            === "professional"
        ) {
            return;
        }

        const replacement =
            currentButton.cloneNode(true);

        replacement.dataset.exportMode =
            "professional";

        replacement.innerHTML = `
            <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
            >
                <path d="M6 2h8l4 4v16H6z"></path>
                <path d="M14 2v5h5"></path>
                <path d="M9 13h6"></path>
                <path d="M9 17h6"></path>
            </svg>

            <span>Rapport PDF</span>
        `;

        currentButton.replaceWith(replacement);

        replacement.addEventListener(
            "click",
            createProfessionalReport
        );
    }

    window.setTimeout(
        installProfessionalExport,
        200
    );

    window.setTimeout(
        installProfessionalExport,
        800
    );
});
