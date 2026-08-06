document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;

    const sidebar =
        document.querySelector(".sidebar")
        || document.querySelector("#sidebar")
        || document.querySelector(
            "[data-sidebar]"
        );

    if (!sidebar) {
        return;
    }

    function findMenuButton() {
        const selectors = [
            ".menu-toggle",
            ".sidebar-toggle",
            "#menu-toggle",
            "#sidebar-toggle",
            ".mobile-menu-button",
            "[data-sidebar-toggle]",
            "[aria-controls='sidebar']",
        ];

        for (const selector of selectors) {
            const element =
                document.querySelector(selector);

            if (element) {
                return element;
            }
        }

        const buttons = [
            ...document.querySelectorAll(
                "button, a"
            ),
        ];

        return buttons.find((element) => {
            const text = (
                element.textContent || ""
            ).trim();

            const label = (
                element.getAttribute("aria-label")
                || ""
            ).toLowerCase();

            return (
                text === "☰"
                || text === "≡"
                || text === "⋮"
                || label.includes("menu")
                || label.includes("navigation")
            );
        }) || null;
    }

    const menuButton = findMenuButton();

    let backdrop =
        document.querySelector(
            ".dashboard-mobile-backdrop"
        );

    if (!backdrop) {
        backdrop =
            document.createElement("div");

        backdrop.className =
            "dashboard-mobile-backdrop";

        backdrop.setAttribute(
            "aria-hidden",
            "true"
        );

        document.body.appendChild(backdrop);
    }

    function isMobile() {
        return window.matchMedia(
            "(max-width: 980px)"
        ).matches;
    }

    function updateDesktopWidth() {
        if (isMobile()) {
            document.documentElement.style
                .setProperty(
                    "--detected-sidebar-width",
                    "0px"
                );

            return;
        }

        const rect =
            sidebar.getBoundingClientRect();

        const width =
            Math.max(
                0,
                Math.round(rect.width)
            );

        document.documentElement.style
            .setProperty(
                "--detected-sidebar-width",
                `${width}px`
            );
    }

    function openSidebar() {
        if (!isMobile()) {
            return;
        }

        body.classList.add("sidebar-open");

        sidebar.classList.add("is-open");

        if (menuButton) {
            menuButton.setAttribute(
                "aria-expanded",
                "true"
            );
        }

        backdrop.setAttribute(
            "aria-hidden",
            "false"
        );
    }

    function closeSidebar() {
        body.classList.remove("sidebar-open");

        sidebar.classList.remove(
            "open",
            "active",
            "is-open"
        );

        if (menuButton) {
            menuButton.setAttribute(
                "aria-expanded",
                "false"
            );
        }

        backdrop.setAttribute(
            "aria-hidden",
            "true"
        );
    }

    function toggleSidebar(event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        if (
            body.classList.contains(
                "sidebar-open"
            )
        ) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }

    if (menuButton) {
        menuButton.setAttribute(
            "aria-expanded",
            "false"
        );

        menuButton.addEventListener(
            "click",
            toggleSidebar
        );
    }

    backdrop.addEventListener(
        "click",
        closeSidebar
    );

    document.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Escape") {
                closeSidebar();
            }
        }
    );

    sidebar
        .querySelectorAll("a")
        .forEach((link) => {
            link.addEventListener(
                "click",
                () => {
                    if (isMobile()) {
                        closeSidebar();
                    }
                }
            );
        });

    const resizeObserver =
        new ResizeObserver(
            updateDesktopWidth
        );

    resizeObserver.observe(sidebar);

    window.addEventListener(
        "resize",
        () => {
            updateDesktopWidth();

            if (!isMobile()) {
                closeSidebar();
            }
        },
        {
            passive: true,
        }
    );

    window.addEventListener(
        "orientationchange",
        () => {
            window.setTimeout(
                updateDesktopWidth,
                150
            );
        }
    );

    updateDesktopWidth();
});
