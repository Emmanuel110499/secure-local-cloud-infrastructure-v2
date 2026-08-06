document.addEventListener("DOMContentLoaded", () => {
    function setText(id, value, suffix = "") {
        const element = document.getElementById(id);

        if (!element) {
            return;
        }

        const number = Number(value);

        element.textContent = Number.isFinite(number)
            ? `${number}${suffix}`
            : `--${suffix}`;
    }

    async function refreshRealInfrastructure() {
        try {
            const response = await fetch(
                `/api/metrics?t=${Date.now()}`,
                {
                    cache: "no-store",
                    headers: {
                        Accept: "application/json",
                    },
                }
            );

            if (!response.ok) {
                return;
            }

            const data = await response.json();
            const metrics = data.metrics || {};
            const services = data.services || {};

            setText(
                "real-infra-cpu",
                metrics.cpu,
                " %"
            );

            setText(
                "real-infra-memory",
                metrics.memory,
                " %"
            );

            setText(
                "real-infra-disk",
                metrics.disk,
                " %"
            );

            setText(
                "emma-live-cpu",
                metrics.cpu,
                " %"
            );

            setText(
                "emma-live-memory",
                metrics.memory,
                " %"
            );

            setText(
                "emma-live-disk",
                metrics.disk,
                " %"
            );

            const serviceValues =
                Object.values(services);

            const upCount = serviceValues.filter(
                Boolean
            ).length;

            const totalCount = serviceValues.length;

            const health =
                document.getElementById(
                    "emma-live-services"
                );

            if (health) {
                health.textContent =
                    `${upCount}/${totalCount}`;
            }

            document
                .querySelectorAll(
                    "[data-real-service]"
                )
                .forEach((element) => {
                    const key =
                        element.dataset.realService;

                    const up =
                        Boolean(services[key]);

                    element.classList.toggle(
                        "down",
                        !up
                    );

                    element.title =
                        `${key} : ${
                            up
                                ? "opérationnel"
                                : "indisponible"
                        }`;
                });
        } catch (error) {
            console.error(
                "Actualisation graphique impossible :",
                error
            );
        }
    }

    document
        .querySelectorAll(
            ".emma-command-chip[data-question]"
        )
        .forEach((button) => {
            button.addEventListener("click", () => {
                const input =
                    document.getElementById(
                        "assistant-input"
                    );

                if (!input) {
                    return;
                }

                input.value =
                    button.dataset.question || "";

                input.focus();

                input.scrollIntoView({
                    behavior: "smooth",
                    block: "center",
                });
            });
        });

    refreshRealInfrastructure();

    window.setInterval(
        refreshRealInfrastructure,
        10000
    );
});
