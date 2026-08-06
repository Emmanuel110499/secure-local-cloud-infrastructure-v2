document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    document.body.classList.add(
        "monitoring-final-page"
    );

    function findCanvas(ids) {
        for (const id of ids) {
            const canvas = document.getElementById(id);

            if (canvas) {
                return canvas;
            }
        }

        return null;
    }

    function findCard(element) {
        if (!element) {
            return null;
        }

        return element.closest(
            ".chart-card, "
            + ".monitoring-chart-card, "
            + ".metric-chart-card, "
            + ".chart-panel, "
            + ".panel, "
            + "article, "
            + "section"
        );
    }

    const definitions = [
        {
            key: "cpu",
            title: "Utilisation CPU",
            canvas: findCanvas([
                "cpuChart",
                "cpu-chart",
            ]),
        },
        {
            key: "memory",
            title: "Utilisation mémoire",
            canvas: findCanvas([
                "memoryChart",
                "memory-chart",
            ]),
        },
        {
            key: "disk",
            title: "Utilisation disque",
            canvas: findCanvas([
                "diskChart",
                "disk-chart",
            ]),
        },
    ];

    const cards = [];

    definitions.forEach(definition => {
        const card = findCard(definition.canvas);

        if (!card) {
            console.warn(
                "Carte introuvable :",
                definition.key
            );

            return;
        }

        card.classList.add(
            "monitoring-final-chart-card",
            `monitoring-final-${definition.key}`
        );

        card.dataset.monitoringMetric =
            definition.key;

        cards.push(card);
    });

    if (cards.length) {
        const parent = cards[0].parentElement;

        if (parent) {
            parent.classList.add(
                "monitoring-final-charts-grid"
            );
        }
    }

    /*
     * Cache uniquement les anciens blocs ajoutés en double.
     * La vraie carte disque contenant diskChart est conservée.
     */
    document.querySelectorAll(
        ".disk-monitoring-section, "
        + ".monitoring-disk-chart-card"
    ).forEach(block => {
        if (!block.querySelector("#diskChart")) {
            block.remove();
        }
    });

    document.querySelectorAll(
        "h1, h2, h3, p, span"
    ).forEach(element => {
        const text = element.textContent
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();

        if (
            text === "stockage"
            && (
                element.parentElement
                    ?.classList.contains(
                        "disk-monitoring-section"
                    )
                || element.nextElementSibling
                    ?.textContent
                    ?.toLowerCase()
                    ?.includes("monitoring du disque")
            )
        ) {
            element.remove();
        }
    });

    /*
     * Identification des cartes de synthèse.
     */
    const summaryCandidates = [
        ...document.querySelectorAll(
            ".summary-card, "
            + ".metric-card, "
            + ".stat-card, "
            + ".overview-card"
        ),
    ];

    if (summaryCandidates.length) {
        const summaryParent =
            summaryCandidates[0].parentElement;

        if (summaryParent) {
            summaryParent.classList.add(
                "monitoring-final-summary-grid"
            );
        }

        summaryCandidates.forEach(card => {
            card.classList.add(
                "monitoring-final-summary-card"
            );
        });
    }

    /*
     * Boutons de période.
     */
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

    if (periodButtons.length) {
        const periodParent =
            periodButtons[0].parentElement;

        if (periodParent) {
            periodParent.classList.add(
                "monitoring-final-periods"
            );
        }
    }

    /*
     * Bouton d’export PDF propre à la page Monitoring.
     */
    if (
        !document.getElementById(
            "monitoring-export-pdf"
        )
    ) {
        const button = document.createElement(
            "button"
        );

        button.id = "monitoring-export-pdf";
        button.type = "button";
        button.className =
            "monitoring-export-pdf";

        button.innerHTML = `
            <span
                class="monitoring-export-icon"
                aria-hidden="true"
            >
                <svg viewBox="0 0 24 24">
                    <path
                        d="M6 2h8l4 4v16H6z"
                    ></path>
                    <path d="M14 2v5h5"></path>
                    <path d="M9 13h6"></path>
                    <path d="M9 17h6"></path>
                </svg>
            </span>

            <span>Exporter le monitoring</span>
        `;

        button.addEventListener(
            "click",
            () => {
                document.body.classList.add(
                    "monitoring-printing"
                );

                window.setTimeout(
                    () => window.print(),
                    150
                );
            }
        );

        window.addEventListener(
            "afterprint",
            () => {
                document.body.classList.remove(
                    "monitoring-printing"
                );
            }
        );

        const periodContainer =
            periodButtons[0]?.parentElement;

        const toolbar =
            periodContainer?.parentElement;

        if (toolbar) {
            toolbar.classList.add(
                "monitoring-final-toolbar"
            );

            toolbar.appendChild(button);
        } else {
            const main =
                document.querySelector("main")
                || document.body;

            main.insertBefore(
                button,
                main.firstChild
            );
        }
    }

    /*
     * Indicateur de criticité des cartes de synthèse.
     */
    function applyLevel(element, value) {
        if (!element) {
            return;
        }

        const numeric = Number(
            String(value)
                .replace(",", ".")
                .replace(/[^\d.]/g, "")
        );

        if (!Number.isFinite(numeric)) {
            return;
        }

        element.dataset.level =
            numeric >= 80
                ? "critical"
                : numeric >= 70
                    ? "warning"
                    : "normal";
    }

    const observedSelectors = [
        "#cpu-value",
        "#cpu-current",
        "#memory-value",
        "#memory-current",
        "#disk-value",
        "#disk-current",
        "#disk-chart-current",
        "#disk-monitoring-current",
    ];

    observedSelectors.forEach(selector => {
        const element =
            document.querySelector(selector);

        if (!element) {
            return;
        }

        applyLevel(
            element,
            element.textContent
        );

        new MutationObserver(() => {
            applyLevel(
                element,
                element.textContent
            );
        }).observe(
            element,
            {
                childList: true,
                characterData: true,
                subtree: true,
            }
        );
    });
});
