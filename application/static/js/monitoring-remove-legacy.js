document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    function normalizeText(value) {
        return String(value || "")
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();
    }

    function isModernElement(element) {
        return Boolean(
            element?.closest("#clean-monitoring-dashboard")
        );
    }

    function findLegacyCard(element) {
        let current = element;

        for (let level = 0; level < 10 && current; level += 1) {
            if (
                current.id === "clean-monitoring-dashboard"
                || current.querySelector?.(
                    "#clean-monitoring-dashboard"
                )
            ) {
                return null;
            }

            const tag = current.tagName?.toLowerCase();

            const className =
                typeof current.className === "string"
                    ? current.className
                    : "";

            const candidate =
                tag === "article"
                || tag === "section"
                || /\bchart-card\b/i.test(className)
                || /\bchart-panel\b/i.test(className)
                || /\bmonitoring-card\b/i.test(className)
                || /\bmonitoring-chart\b/i.test(className)
                || /\bpanel\b/i.test(className)
                || /\bcard\b/i.test(className);

            if (candidate) {
                return current;
            }

            current = current.parentElement;
        }

        return element.parentElement;
    }

    function removeLegacyCanvasBlocks() {
        const legacyCanvasIds = new Set([
            "cpuChart",
            "memoryChart",
            "diskChart",
            "cpu-chart",
            "memory-chart",
            "disk-chart",
        ]);

        document
            .querySelectorAll("canvas")
            .forEach(canvas => {
                if (
                    canvas.id.startsWith("cm-")
                    || isModernElement(canvas)
                ) {
                    return;
                }

                if (
                    legacyCanvasIds.has(canvas.id)
                    || !canvas.id.startsWith("cm-")
                ) {
                    const card = findLegacyCard(canvas);

                    if (
                        card
                        && !isModernElement(card)
                    ) {
                        card.remove();
                    }
                }
            });
    }

    function removeLegacyTitleBlocks() {
        const legacyTitles = new Set([
            "utilisation cpu",
            "utilisation mémoire",
            "utilisation memoire",
            "utilisation disque",
            "cpu moyen",
            "ram moyenne",
            "disque moyen",
            "mesures enregistrées",
            "mesures enregistrees",
        ]);

        document
            .querySelectorAll(
                "h1, h2, h3, h4, h5, strong"
            )
            .forEach(element => {
                if (isModernElement(element)) {
                    return;
                }

                const text = normalizeText(
                    element.textContent
                );

                if (!legacyTitles.has(text)) {
                    return;
                }

                const card = findLegacyCard(element);

                if (
                    card
                    && !isModernElement(card)
                ) {
                    card.remove();
                }
            });
    }

    function removeEmptyLegacyContainers() {
        document
            .querySelectorAll(
                ".monitoring-grid, "
                + ".monitoring-charts, "
                + ".charts-grid, "
                + ".history-charts, "
                + ".chart-grid"
            )
            .forEach(container => {
                if (isModernElement(container)) {
                    return;
                }

                const visibleChildren = [
                    ...container.children,
                ].filter(child => {
                    return (
                        child.id !==
                        "clean-monitoring-dashboard"
                        && child.getBoundingClientRect()
                            .height > 2
                    );
                });

                if (!visibleChildren.length) {
                    container.remove();
                }
            });
    }

    function removeLegacyMonitoring() {
        const modernDashboard =
            document.getElementById(
                "clean-monitoring-dashboard"
            );

        if (!modernDashboard) {
            return;
        }

        removeLegacyCanvasBlocks();
        removeLegacyTitleBlocks();
        removeEmptyLegacyContainers();

        modernDashboard.hidden = false;
        modernDashboard.style.display = "";
        modernDashboard.style.visibility = "visible";
        modernDashboard.style.opacity = "1";
    }

    /*
     * Plusieurs passages car l’interface moderne et Chart.js
     * terminent leur initialisation après DOMContentLoaded.
     */
    [100, 400, 1000, 2000].forEach(delay => {
        window.setTimeout(
            removeLegacyMonitoring,
            delay
        );
    });
});
