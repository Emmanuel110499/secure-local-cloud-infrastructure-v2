document.addEventListener("DOMContentLoaded", () => {
    const revealSelectors = [
        ".v3-stat-card",
        ".v3-resource-card",
        ".v3-guide-card",
        ".portal-card",
        ".chart-card",
        ".server-card",
        ".security-control",
        ".assistant-side-card",
        ".audit-entry",
        ".container-card",
        ".topology-node",
        ".node",
        ".card",
    ];

    const elements = document.querySelectorAll(
        revealSelectors.join(",")
    );

    elements.forEach((element, index) => {
        element.classList.add("v4-reveal");

        element.style.animationDelay =
            `${Math.min(index * 35, 420)}ms`;
    });

    /* Corrige les images ou logos qui ne chargent pas */
    document.querySelectorAll("img").forEach((image) => {
        image.addEventListener("error", () => {
            if (image.dataset.v4Fallback === "true") {
                return;
            }

            image.dataset.v4Fallback = "true";

            const fallback =
                document.createElement("span");

            fallback.className =
                "v4-image-fallback";

            const alt = String(
                image.alt
                || image.dataset.name
                || "LOGO"
            )
                .trim()
                .slice(0, 3)
                .toUpperCase();

            fallback.textContent = alt || "IT";

            image.replaceWith(fallback);
        });
    });

    /* Animation des valeurs numériques */
    const numberElements = document.querySelectorAll(
        [
            ".metric-value",
            ".summary-value",
            ".v3-stat-card strong",
            ".audit-summary-card strong",
            "[data-cpu]",
            "[data-ram]",
            "[data-disk]",
            "[data-containers]",
        ].join(",")
    );

    numberElements.forEach((element) => {
        if (element.dataset.v4Animated === "true") {
            return;
        }

        const original = element.textContent.trim();

        const match = original.match(
            /^(-?\d+(?:[.,]\d+)?)(.*)$/
        );

        if (!match) {
            return;
        }

        const target = Number(
            match[1].replace(",", ".")
        );

        if (!Number.isFinite(target)) {
            return;
        }

        const suffix = match[2] || "";
        const decimals =
            match[1].includes(".")
            || match[1].includes(",")
                ? 1
                : 0;

        element.dataset.v4Animated = "true";

        const duration = 720;
        const start = performance.now();

        function update(now) {
            const progress = Math.min(
                (now - start) / duration,
                1
            );

            const eased =
                1 - Math.pow(1 - progress, 3);

            const value = target * eased;

            element.textContent =
                value.toFixed(decimals)
                + suffix;

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    });

    /* Ajoute une barre de progression aux métriques en pourcentage */
    const percentSelectors = [
        "[data-cpu]",
        "[data-ram]",
        "[data-disk]",
        ".metric-value",
    ];

    document
        .querySelectorAll(
            percentSelectors.join(",")
        )
        .forEach((element) => {
            const value = Number.parseFloat(
                element.textContent
                    .replace(",", ".")
            );

            if (
                !Number.isFinite(value)
                || value < 0
                || value > 100
                || element.parentElement?.querySelector(
                    ":scope > .v4-progress-track"
                )
            ) {
                return;
            }

            const track =
                document.createElement("div");

            track.className =
                "v4-progress-track";

            const progress =
                document.createElement("div");

            progress.className =
                "v4-progress-value";

            track.appendChild(progress);

            element.parentElement?.appendChild(track);

            requestAnimationFrame(() => {
                progress.style.width =
                    `${Math.min(value, 100)}%`;
            });
        });

    /* Effet de profondeur suivant la souris sur PC */
    if (
        window.matchMedia(
            "(pointer: fine)"
        ).matches
    ) {
        const interactiveCards =
            document.querySelectorAll(
                [
                    ".v3-resource-card",
                    ".v3-guide-card",
                    ".security-control",
                    ".container-card",
                    ".server-card",
                ].join(",")
            );

        interactiveCards.forEach((card) => {
            card.addEventListener(
                "mousemove",
                (event) => {
                    const rect =
                        card.getBoundingClientRect();

                    const x =
                        event.clientX - rect.left;

                    const y =
                        event.clientY - rect.top;

                    const rotateY =
                        ((x / rect.width) - 0.5) * 2;

                    const rotateX =
                        ((y / rect.height) - 0.5) * -2;

                    card.style.transform =
                        `perspective(900px) `
                        + `rotateX(${rotateX}deg) `
                        + `rotateY(${rotateY}deg) `
                        + `translateY(-4px)`;
                }
            );

            card.addEventListener(
                "mouseleave",
                () => {
                    card.style.transform = "";
                }
            );
        });
    }
});
