(() => {
    "use strict";

    function isReportButton(element) {
        const button = element.closest(
            "button, a, [role='button']"
        );

        if (!button) {
            return null;
        }

        const text = String(
            button.textContent || ""
        )
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();

        const explicitMatch =
            button.matches(
                "#report-pdf-button, " +
                "#export-report-pdf, " +
                ".report-pdf-button, " +
                ".export-report-button, " +
                "[data-report-pdf]"
            );

        const textMatch =
            text.includes("rapport pdf")
            || text.includes("exporter le rapport");

        return explicitMatch || textMatch
            ? button
            : null;
    }

    document.addEventListener(
        "click",
        event => {
            const button =
                isReportButton(event.target);

            if (!button) {
                return;
            }

            event.preventDefault();
            event.stopPropagation();

            document.documentElement.classList.add(
                "monitoring-print-mode"
            );

            window.setTimeout(() => {
                window.print();
            }, 250);
        },
        true
    );

    window.addEventListener(
        "afterprint",
        () => {
            document.documentElement.classList.remove(
                "monitoring-print-mode"
            );
        }
    );
})();
