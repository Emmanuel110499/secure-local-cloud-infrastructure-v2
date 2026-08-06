window.PortalV3 = (() => {
    function escapeHtml(value) {
        const element = document.createElement("div");
        element.textContent = String(value ?? "");
        return element.innerHTML;
    }

    function number(value, digits = 1) {
        const parsed = Number(value);

        return Number.isFinite(parsed)
            ? parsed.toFixed(digits)
            : "0.0";
    }

    function showToast(message, type = "success") {
        const container = document.getElementById(
            "v3-toast-container"
        );

        if (!container) {
            return;
        }

        const toast = document.createElement("div");

        toast.className = `v3-toast ${
            type === "error"
                ? "error"
                : ""
        }`;

        toast.textContent = message;
        container.appendChild(toast);

        window.setTimeout(() => {
            toast.remove();
        }, 3500);
    }

    function bindSearch({
        input,
        selector,
        getText,
        empty,
    }) {
        const field = document.querySelector(input);

        if (!field) {
            return;
        }

        function filter() {
            const query = field.value
                .trim()
                .toLowerCase()
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "");

            let visible = 0;

            document
                .querySelectorAll(selector)
                .forEach((element) => {
                    const text = (
                        getText
                            ? getText(element)
                            : element.textContent
                    )
                        .toLowerCase()
                        .normalize("NFD")
                        .replace(/[\u0300-\u036f]/g, "");

                    const matches =
                        !query
                        || text.includes(query);

                    element.hidden = !matches;

                    if (matches) {
                        visible += 1;
                    }
                });

            if (empty) {
                const emptyElement =
                    document.querySelector(empty);

                if (emptyElement) {
                    emptyElement.hidden =
                        visible !== 0;
                }
            }
        }

        field.addEventListener("input", filter);
    }

    function bindAccordions() {
        document
            .querySelectorAll(".v3-accordion-button")
            .forEach((button) => {
                button.addEventListener(
                    "click",
                    () => {
                        button.closest(
                            ".v3-accordion-item"
                        )?.classList.toggle("open");
                    }
                );
            });
    }

    document.addEventListener(
        "DOMContentLoaded",
        bindAccordions
    );

    return {
        escapeHtml,
        number,
        showToast,
        bindSearch,
    };
})();
