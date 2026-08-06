(() => {
    "use strict";

    const pages = [
        {
            title: "Accueil",
            icon: "🏠",
            url: "/",
            description: "Vue générale de la plateforme",
            keywords: [
                "accueil",
                "home",
                "principal",
                "dashboard"
            ],
        },
        {
            title: "Tableau de bord",
            icon: "📊",
            url: "/#dashboard",
            description: "KPI, services, CPU, RAM et alertes",
            keywords: [
                "tableau",
                "kpi",
                "cpu",
                "ram",
                "mémoire",
                "alerte",
                "services"
            ],
        },
        {
            title: "Monitoring",
            icon: "📈",
            url: "/monitoring",
            description: "Métriques et graphiques de supervision",
            keywords: [
                "monitoring",
                "cpu",
                "ram",
                "disque",
                "graphique",
                "prometheus",
                "métrique"
            ],
        },
        {
            title: "Conteneurs Docker",
            icon: "🐳",
            url: "/containers",
            description: "État et ressources des conteneurs",
            keywords: [
                "docker",
                "conteneur",
                "container",
                "nginx",
                "flask",
                "cadvisor"
            ],
        },
        {
            title: "Infrastructure",
            icon: "🖥️",
            url: "/infrastructure",
            description: "Serveurs, architecture et disponibilité",
            keywords: [
                "infrastructure",
                "serveur",
                "srv-web",
                "srv-monitoring",
                "ubuntu",
                "réseau"
            ],
        },
        {
            title: "Documentation",
            icon: "📚",
            url: "/documentation",
            description: "Guides et fonctionnement du projet",
            keywords: [
                "documentation",
                "guide",
                "aide",
                "manuel",
                "projet"
            ],
        },
        {
            title: "Grafana",
            icon: "📊",
            url: "https://grafana.emmanuelinfra.fr",
            description: "Visualisation avancée des métriques",
            keywords: [
                "grafana",
                "graphique",
                "dashboard",
                "visualisation"
            ],
            external: true,
        },
        {
            title: "Prometheus",
            icon: "🔥",
            url: "https://prometheus.emmanuelinfra.fr",
            description: "Requêtes et données de supervision",
            keywords: [
                "prometheus",
                "promql",
                "target",
                "métrique",
                "alerte"
            ],
            external: true,
        },
        {
            title: "Connexion sécurisée",
            icon: "🔐",
            url: "/security",
            description: "Sécurité et protection de la plateforme",
            keywords: [
                "sécurité",
                "connexion",
                "https",
                "ssl",
                "certificat",
                "fail2ban",
                "pare-feu",
                "ufw"
            ],
        },
        {
            title: "Audit",
            icon: "📜",
            url: "/audit",
            description: "Journaux et événements de la plateforme",
            keywords: [
                "audit",
                "logs",
                "journal",
                "activité",
                "événement"
            ],
        },
        {
            title: "Emma_IA",
            icon: "🤖",
            url: "/assistant",
            description: "Assistant de la plateforme",
            keywords: [
                "emma",
                "ia",
                "assistant",
                "question",
                "aide"
            ],
        },
    ];

    function normalize(value) {
        return String(value || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();
    }

    function initialize() {
        const root =
            document.getElementById(
                "platform-search"
            );

        const input =
            document.getElementById(
                "platform-search-input"
            );

        const results =
            document.getElementById(
                "platform-search-results"
            );

        const clearButton =
            document.getElementById(
                "platform-search-clear"
            );

        if (
            !root
            || !input
            || !results
        ) {
            return;
        }

        let visibleResults = [];
        let activeIndex = -1;

        function closeResults() {
            results.hidden = true;
            input.setAttribute(
                "aria-expanded",
                "false"
            );

            activeIndex = -1;
        }

        function openResults() {
            results.hidden = false;
            input.setAttribute(
                "aria-expanded",
                "true"
            );
        }

        function navigateTo(page) {
            if (!page) {
                return;
            }

            if (page.external) {
                window.open(
                    page.url,
                    "_blank",
                    "noopener,noreferrer"
                );
            } else {
                window.location.href =
                    page.url;
            }

            closeResults();
        }

        function updateActiveResult() {
            results
                .querySelectorAll(
                    ".platform-search-result"
                )
                .forEach(
                    (element, index) => {
                        element.classList.toggle(
                            "active",
                            index === activeIndex
                        );
                    }
                );
        }

        function render(query) {
            const normalizedQuery =
                normalize(query);

            clearButton.hidden =
                normalizedQuery.length === 0;

            if (!normalizedQuery) {
                visibleResults =
                    pages.slice(0, 6);
            } else {
                visibleResults = pages
                    .map(page => {
                        const searchable =
                            normalize(
                                [
                                    page.title,
                                    page.description,
                                    ...page.keywords,
                                ].join(" ")
                            );

                        let score = 0;

                        if (
                            normalize(page.title)
                            .startsWith(
                                normalizedQuery
                            )
                        ) {
                            score += 10;
                        }

                        if (
                            searchable.includes(
                                normalizedQuery
                            )
                        ) {
                            score += 4;
                        }

                        return {
                            page,
                            score,
                        };
                    })
                    .filter(item => item.score > 0)
                    .sort(
                        (a, b) =>
                            b.score - a.score
                    )
                    .map(item => item.page)
                    .slice(0, 7);
            }

            results.replaceChildren();
            activeIndex = -1;

            if (
                visibleResults.length === 0
            ) {
                const empty =
                    document.createElement(
                        "div"
                    );

                empty.className =
                    "platform-search-empty";

                empty.textContent =
                    `Aucun résultat pour « ${query} »`;

                results.appendChild(empty);
                openResults();
                return;
            }

            visibleResults.forEach(
                (page, index) => {
                    const button =
                        document.createElement(
                            "button"
                        );

                    button.type = "button";
                    button.className =
                        "platform-search-result";

                    button.setAttribute(
                        "role",
                        "option"
                    );

                    button.innerHTML = `
                        <span
                            class="platform-search-result-icon"
                            aria-hidden="true"
                        >
                            ${page.icon}
                        </span>

                        <span
                            class="platform-search-result-content"
                        >
                            <strong>
                                ${page.title}
                            </strong>

                            <small>
                                ${page.description}
                            </small>
                        </span>
                    `;

                    button.addEventListener(
                        "click",
                        () => navigateTo(page)
                    );

                    button.addEventListener(
                        "mouseenter",
                        () => {
                            activeIndex = index;
                            updateActiveResult();
                        }
                    );

                    results.appendChild(
                        button
                    );
                }
            );

            openResults();
        }

        input.addEventListener(
            "focus",
            () => render(input.value)
        );

        input.addEventListener(
            "input",
            () => render(input.value)
        );

        input.addEventListener(
            "keydown",
            event => {
                if (
                    event.key === "ArrowDown"
                ) {
                    event.preventDefault();

                    activeIndex = Math.min(
                        activeIndex + 1,
                        visibleResults.length - 1
                    );

                    updateActiveResult();
                }

                if (
                    event.key === "ArrowUp"
                ) {
                    event.preventDefault();

                    activeIndex = Math.max(
                        activeIndex - 1,
                        0
                    );

                    updateActiveResult();
                }

                if (
                    event.key === "Enter"
                ) {
                    event.preventDefault();

                    const selected =
                        visibleResults[
                            activeIndex >= 0
                                ? activeIndex
                                : 0
                        ];

                    navigateTo(selected);
                }

                if (
                    event.key === "Escape"
                ) {
                    closeResults();
                    input.blur();
                }
            }
        );

        clearButton?.addEventListener(
            "click",
            () => {
                input.value = "";
                clearButton.hidden = true;

                input.focus();
                render("");
            }
        );

        document.addEventListener(
            "click",
            event => {
                if (
                    !root.contains(
                        event.target
                    )
                ) {
                    closeResults();
                }
            }
        );

        document.addEventListener(
            "keydown",
            event => {
                if (
                    (
                        event.ctrlKey
                        || event.metaKey
                    )
                    && event.key.toLowerCase()
                    === "k"
                ) {
                    event.preventDefault();

                    input.focus();
                    render(input.value);
                }
            }
        );
    }

    if (
        document.readyState === "loading"
    ) {
        document.addEventListener(
            "DOMContentLoaded",
            initialize,
            {
                once: true,
            }
        );
    } else {
        initialize();
    }
})();
