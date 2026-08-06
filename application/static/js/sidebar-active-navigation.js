document.addEventListener("DOMContentLoaded", () => {
    const links = [
        ...document.querySelectorAll(
            ".sidebar .nav-item"
        ),
    ];

    const currentPath =
        window.location.pathname.replace(/\/+$/, "")
        || "/";

    const currentHash =
        window.location.hash;

    function normalizePath(value) {
        if (!value) {
            return "/";
        }

        try {
            const url = new URL(
                value,
                window.location.origin
            );

            return (
                url.pathname.replace(/\/+$/, "")
                || "/"
            );
        } catch {
            return value;
        }
    }

    function clearActive() {
        links.forEach(link => {
            link.classList.remove(
                "active",
                "is-active"
            );

            link.removeAttribute(
                "aria-current"
            );
        });
    }

    function activate(link) {
        clearActive();

        link.classList.add(
            "active",
            "is-active"
        );

        link.setAttribute(
            "aria-current",
            "page"
        );
    }

    let matchedLink = null;

    links.forEach(link => {
        const href =
            link.getAttribute("href");

        if (
            !href
            || href.startsWith("http")
            || href.startsWith("mailto:")
        ) {
            return;
        }

        const linkPath =
            normalizePath(href);

        const linkHash =
            href.includes("#")
                ? new URL(
                    href,
                    window.location.origin
                ).hash
                : "";

        const isDashboardHash =
            currentPath === "/"
            && currentHash === "#dashboard"
            && linkHash === "#dashboard";

        const isExactPage =
            currentPath === linkPath
            && !linkHash
            && !(
                currentPath === "/"
                && currentHash === "#dashboard"
            );

        if (
            isDashboardHash
            || isExactPage
        ) {
            matchedLink = link;
        }
    });

    if (matchedLink) {
        activate(matchedLink);
    }

    links.forEach(link => {
        link.addEventListener(
            "click",
            () => {
                const href =
                    link.getAttribute("href");

                if (
                    href
                    && !href.startsWith("http")
                ) {
                    activate(link);
                }
            }
        );
    });

    window.addEventListener(
        "hashchange",
        () => {
            const dashboardLink =
                document.querySelector(
                    '.sidebar .nav-item[href="#dashboard"], '
                    + '.sidebar .nav-item[href="/#dashboard"]'
                );

            const homeLink =
                document.querySelector(
                    '.sidebar .nav-item[href="/"]'
                );

            if (
                window.location.hash === "#dashboard"
                && dashboardLink
            ) {
                activate(dashboardLink);
            } else if (
                window.location.pathname === "/"
                && homeLink
            ) {
                activate(homeLink);
            }
        }
    );
});
