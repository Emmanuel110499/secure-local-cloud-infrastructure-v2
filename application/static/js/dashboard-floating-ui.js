document.addEventListener("DOMContentLoaded", () => {
    const pdfButton = document.querySelector(
        ".pdf-export-button"
    );

    const assistantCandidates = [
        ...document.querySelectorAll(
            'a[href="/assistant"], '
            + 'a[href$="/assistant"], '
            + '[class*="assistant"][class*="float"], '
            + '[class*="emma"][class*="float"]'
        ),
    ];

    let assistantButton = null;

    for (const candidate of assistantCandidates) {
        const style = window.getComputedStyle(candidate);
        const rect = candidate.getBoundingClientRect();

        const isFloating =
            style.position === "fixed"
            || style.position === "sticky"
            || (
                rect.width <= 100
                && rect.height <= 100
            );

        if (
            isFloating
            && candidate !== pdfButton
        ) {
            assistantButton = candidate;
            break;
        }
    }

    if (assistantButton) {
        assistantButton.classList.add(
            "floating-ui-assistant"
        );
    }

    let scrollTimer = null;

    function handleScroll() {
        document.body.classList.add(
            "dashboard-is-scrolling"
        );

        window.clearTimeout(scrollTimer);

        scrollTimer = window.setTimeout(() => {
            document.body.classList.remove(
                "dashboard-is-scrolling"
            );
        }, 260);
    }

    window.addEventListener(
        "scroll",
        handleScroll,
        {
            passive: true,
        }
    );

    const sidebar = document.querySelector(
        ".sidebar"
    );

    if (sidebar) {
        sidebar.addEventListener(
            "scroll",
            handleScroll,
            {
                passive: true,
            }
        );
    }
});

/* Positionnement mobile du bouton Exporter au-dessus d’Emma_IA */
document.addEventListener("DOMContentLoaded", () => {
    const candidates = [
        ...document.querySelectorAll(
            'button, a, [role="button"]'
        ),
    ];

    const exportButton = candidates.find(element => {
        const text = String(
            element.textContent || ""
        )
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();

        const label = String(
            element.getAttribute("aria-label") || ""
        ).toLowerCase();

        const title = String(
            element.getAttribute("title") || ""
        ).toLowerCase();

        return (
            text.includes("exporter")
            || text.includes("export pdf")
            || label.includes("export")
            || title.includes("export")
        );
    });

    if (exportButton) {
        exportButton.classList.add(
            "mobile-export-above-emma"
        );
    }
});

/* MOBILE_ACCOUNT_RIBBON_STATE_START */

document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.querySelector(".sidebar");

    const overlay = document.querySelector(
        "#sidebar-overlay, .sidebar-overlay"
    );

    const menuButton = document.getElementById(
        "mobile-menu-button"
    );

    function menuIsOpen() {
        if (
            document.body.classList.contains("menu-is-open")
            || document.body.classList.contains("sidebar-is-open")
        ) {
            return true;
        }

        if (
            menuButton
            && menuButton.getAttribute("aria-expanded") === "true"
        ) {
            return true;
        }

        if (sidebar) {
            const openClasses = [
                "open",
                "active",
                "show",
                "visible",
                "is-open",
            ];

            if (
                openClasses.some(className =>
                    sidebar.classList.contains(className)
                )
            ) {
                return true;
            }
        }

        if (overlay) {
            const style = window.getComputedStyle(overlay);

            if (
                style.display !== "none"
                && style.visibility !== "hidden"
                && Number(style.opacity || 0) > 0.05
            ) {
                return true;
            }
        }

        return false;
    }

    function syncMenuState() {
        document.body.classList.toggle(
            "mobile-sidebar-open",
            menuIsOpen()
        );
    }

    const observer = new MutationObserver(syncMenuState);

    [sidebar, overlay, menuButton]
        .filter(Boolean)
        .forEach(element => {
            observer.observe(element, {
                attributes: true,
                attributeFilter: [
                    "class",
                    "style",
                    "hidden",
                    "aria-expanded",
                ],
            });
        });

    document.addEventListener(
        "click",
        () => window.setTimeout(syncMenuState, 80)
    );

    syncMenuState();
});

/* MOBILE_ACCOUNT_RIBBON_STATE_END */
