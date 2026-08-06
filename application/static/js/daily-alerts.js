(() => {
    "use strict";

    const API_URL = "/api/daily-alerts";
    const REFRESH_DELAY = 15000;

    let currentData = null;
    let detailsPanel = null;

    function findAlertsCard() {
        const cards = [
            ...document.querySelectorAll(
                ".kpi-card, .stat-card, article"
            ),
        ];

        return cards.find(card => {
            const text = String(
                card.textContent || ""
            )
                .replace(/\s+/g, " ")
                .trim()
                .toLowerCase();

            return (
                text.includes("alertes")
                || text.includes("alerte")
            );
        }) || null;
    }

    function findNumericValue(card) {
        if (!card) {
            return null;
        }

        const selectors = [
            "[data-alert-count]",
            ".kpi-value",
            ".stat-value",
            ".metric-value",
            "strong",
        ];

        for (const selector of selectors) {
            const elements = [
                ...card.querySelectorAll(selector),
            ];

            const element = elements.find(item =>
                /^\s*\d+\s*$/.test(
                    String(item.textContent || "")
                )
            );

            if (element) {
                return element;
            }
        }

        return null;
    }

    function findSubtitle(card) {
        if (!card) {
            return null;
        }

        const candidates = [
            ...card.querySelectorAll(
                "small, span, p"
            ),
        ];

        return candidates.find(element => {
            const text = String(
                element.textContent || ""
            )
                .replace(/\s+/g, " ")
                .trim()
                .toLowerCase();

            return (
                text.includes("en cours")
                || text.includes("active")
                || text.includes("alerte")
            );
        }) || null;
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function formatDate(value) {
        if (!value) {
            return "Heure indisponible";
        }

        const date = new Date(value);

        if (
            Number.isNaN(
                date.getTime()
            )
        ) {
            return "Heure indisponible";
        }

        return new Intl.DateTimeFormat(
            "fr-FR",
            {
                hour: "2-digit",
                minute: "2-digit",
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
            }
        ).format(date);
    }

    function severityInformation(severity) {
        const value = String(
            severity || ""
        ).toLowerCase();

        if (value === "critical") {
            return {
                label: "Critique",
                icon: "🔴",
                className: "critical",
                explanation:
                    "Cette alerte nécessite une intervention rapide.",
            };
        }

        if (value === "warning") {
            return {
                label: "Avertissement",
                icon: "🟠",
                className: "warning",
                explanation:
                    "La plateforme fonctionne encore, mais une vérification est recommandée.",
            };
        }

        if (value === "info") {
            return {
                label: "Information",
                icon: "🔵",
                className: "info",
                explanation:
                    "Cette alerte est informative et ne signale pas forcément une panne.",
            };
        }

        return {
            label: "Non définie",
            icon: "⚪",
            className: "unknown",
            explanation:
                "Le niveau de gravité n’a pas été précisé.",
        };
    }

    function createDetailsPanel() {
        if (detailsPanel) {
            return detailsPanel;
        }

        detailsPanel =
            document.createElement("section");

        detailsPanel.id =
            "daily-alerts-details";

        detailsPanel.className =
            "daily-alerts-details";

        detailsPanel.hidden = true;

        detailsPanel.setAttribute(
            "aria-label",
            "Détails des alertes"
        );

        document.body.appendChild(
            detailsPanel
        );

        detailsPanel.addEventListener(
            "click",
            event => {
                event.stopPropagation();

                const closeButton =
                    event.target.closest(
                        "[data-close-alert-details]"
                    );

                if (closeButton) {
                    closeDetails();
                }
            }
        );

        return detailsPanel;
    }

    function renderDetails(data) {
        const panel =
            createDetailsPanel();

        const latest =
            data.latest_alert || {};

        const severity =
            severityInformation(
                latest.severity
            );

        const counts =
            data.severity_counts || {};

        const alertTitle =
            latest.summary
            || latest.name
            || "Aucune alerte enregistrée";

        const alertName =
            latest.name
            && latest.summary
            && latest.name !== latest.summary
                ? latest.name
                : "";

        panel.innerHTML = `
            <div class="daily-alerts-details-card">
                <header class="daily-alerts-details-header">
                    <div>
                        <span class="daily-alerts-details-eyebrow">
                            Supervision Telegram
                        </span>

                        <h2>
                            Détails des alertes
                        </h2>

                        <p>
                            Données récupérées directement depuis
                            Alertmanager.
                        </p>
                    </div>

                    <button
                        type="button"
                        class="daily-alerts-details-close"
                        data-close-alert-details
                        aria-label="Fermer les détails"
                    >
                        ✕
                    </button>
                </header>

                <div class="daily-alerts-summary-grid">
                    <div class="daily-alert-summary-card">
                        <span>📅</span>

                        <div>
                            <small>
                                Déclenchées aujourd’hui
                            </small>

                            <strong>
                                ${Number(
                                    data.alerts_today
                                ) || 0}
                            </strong>
                        </div>
                    </div>

                    <div class="daily-alert-summary-card">
                        <span>🔔</span>

                        <div>
                            <small>
                                Encore actives
                            </small>

                            <strong>
                                ${Number(
                                    data.active_now
                                ) || 0}
                            </strong>
                        </div>
                    </div>

                    <div class="daily-alert-summary-card critical">
                        <span>🔴</span>

                        <div>
                            <small>
                                Critiques
                            </small>

                            <strong>
                                ${Number(
                                    counts.critical
                                ) || 0}
                            </strong>
                        </div>
                    </div>

                    <div class="daily-alert-summary-card warning">
                        <span>🟠</span>

                        <div>
                            <small>
                                Avertissements
                            </small>

                            <strong>
                                ${Number(
                                    counts.warning
                                ) || 0}
                            </strong>
                        </div>
                    </div>
                </div>

                <article class="daily-alert-latest">
                    <div class="daily-alert-latest-heading">
                        <div>
                            <span class="daily-alert-severity ${severity.className}">
                                ${severity.icon}
                                ${severity.label}
                            </span>

                            <h3>
                                ${escapeHtml(alertTitle)}
                            </h3>

                            ${
                                alertName
                                    ? `
                                        <small>
                                            Règle :
                                            ${escapeHtml(alertName)}
                                        </small>
                                    `
                                    : ""
                            }
                        </div>

                        <time>
                            ${escapeHtml(
                                formatDate(
                                    latest.starts_at
                                )
                            )}
                        </time>
                    </div>

                    <p class="daily-alert-explanation">
                        ${escapeHtml(
                            severity.explanation
                        )}
                    </p>

                    <div class="daily-alert-definition">
                        <strong>
                            Ce que cela signifie
                        </strong>

                        <p>
                            ${
                                latest.summary
                                || latest.name
                                    ? escapeHtml(
                                        latest.summary
                                        || latest.name
                                    )
                                    : "Aucune alerte n’a encore été enregistrée aujourd’hui."
                            }
                        </p>
                    </div>
                </article>

                <footer class="daily-alerts-details-footer">
                    <span class="daily-alerts-live-dot"></span>

                    Actualisation automatique toutes les 15 secondes
                </footer>
            </div>
        `;
    }

    function positionDetails(card) {
        if (!detailsPanel || !card) {
            return;
        }

        const rect =
            card.getBoundingClientRect();

        const panelWidth =
            Math.min(
                430,
                window.innerWidth - 24
            );

        let left =
            rect.right
            - panelWidth;

        left = Math.max(
            12,
            Math.min(
                left,
                window.innerWidth
                - panelWidth
                - 12
            )
        );

        let top =
            rect.bottom + 10;

        const estimatedHeight = 480;

        if (
            top + estimatedHeight
            > window.innerHeight - 12
        ) {
            top = Math.max(
                12,
                rect.top
                - estimatedHeight
                - 10
            );
        }

        detailsPanel.style.width =
            `${panelWidth}px`;

        detailsPanel.style.left =
            `${left}px`;

        detailsPanel.style.top =
            `${top}px`;
    }

    function openDetails(card) {
        if (!currentData) {
            return;
        }

        renderDetails(
            currentData
        );

        positionDetails(card);

        detailsPanel.hidden = false;

        requestAnimationFrame(() => {
            detailsPanel.classList.add(
                "visible"
            );
        });

        document.body.classList.add(
            "daily-alerts-open"
        );
    }

    function closeDetails() {
        if (!detailsPanel) {
            return;
        }

        detailsPanel.classList.remove(
            "visible"
        );

        document.body.classList.remove(
            "daily-alerts-open"
        );

        window.setTimeout(() => {
            if (
                detailsPanel
                && !detailsPanel.classList.contains(
                    "visible"
                )
            ) {
                detailsPanel.hidden = true;
            }
        }, 180);
    }

    function updateCard(card, data) {
        const value =
            findNumericValue(card);

        const subtitle =
            findSubtitle(card);

        if (value) {
            value.textContent =
                String(
                    Number(
                        data.alerts_today
                    ) || 0
                );
        }

        if (subtitle) {
            subtitle.textContent =
                "Alertes aujourd’hui";
        }

        card.classList.add(
            "daily-alerts-clickable"
        );

        card.classList.toggle(
            "daily-alerts-active",
            Number(data.active_now) > 0
        );

        card.classList.toggle(
            "daily-alerts-clear",
            Number(data.active_now) === 0
        );

        card.setAttribute(
            "role",
            "button"
        );

        card.setAttribute(
            "tabindex",
            "0"
        );

        card.setAttribute(
            "aria-label",
            "Afficher les détails des alertes"
        );

        card.title =
            "Cliquez pour voir les alertes détaillées";

        if (!card.dataset.alertClickReady) {
            card.dataset.alertClickReady =
                "true";

            card.addEventListener(
                "click",
                event => {
                    event.stopPropagation();

                    if (
                        detailsPanel
                        && detailsPanel.classList.contains(
                            "visible"
                        )
                    ) {
                        closeDetails();
                    } else {
                        openDetails(card);
                    }
                }
            );

            card.addEventListener(
                "keydown",
                event => {
                    if (
                        event.key === "Enter"
                        || event.key === " "
                    ) {
                        event.preventDefault();
                        openDetails(card);
                    }
                }
            );
        }
    }

    async function refresh() {
        const card =
            findAlertsCard();

        if (!card) {
            return;
        }

        try {
            const response =
                await fetch(
                    `${API_URL}?t=${Date.now()}`,
                    {
                        cache: "no-store",
                        headers: {
                            Accept:
                                "application/json",
                        },
                    }
                );

            if (!response.ok) {
                throw new Error(
                    `HTTP ${response.status}`
                );
            }

            const data =
                await response.json();

            currentData = data;

            updateCard(
                card,
                data
            );

            if (
                detailsPanel
                && detailsPanel.classList.contains(
                    "visible"
                )
            ) {
                renderDetails(data);
                positionDetails(card);
            }
        } catch (error) {
            console.warn(
                "Alertes indisponibles :",
                error
            );

            card.classList.add(
                "daily-alerts-unavailable"
            );
        }
    }

    function initialize() {
        refresh();

        window.setInterval(
            refresh,
            REFRESH_DELAY
        );

        document.addEventListener(
            "click",
            event => {
                if (
                    detailsPanel
                    && !detailsPanel.contains(
                        event.target
                    )
                ) {
                    closeDetails();
                }
            }
        );

        document.addEventListener(
            "keydown",
            event => {
                if (
                    event.key === "Escape"
                ) {
                    closeDetails();
                }
            }
        );

        window.addEventListener(
            "resize",
            () => {
                const card =
                    findAlertsCard();

                if (
                    card
                    && detailsPanel
                    && detailsPanel.classList.contains(
                        "visible"
                    )
                ) {
                    positionDetails(card);
                }
            }
        );
    }

    if (
        document.readyState
        === "loading"
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
