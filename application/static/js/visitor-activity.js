document.addEventListener(
    "DOMContentLoaded",
    () => {
        const visitorsToday =
            document.getElementById(
                "platform-visitors-today"
            );

        const lastCountry =
            document.getElementById(
                "platform-last-country"
            );

        const lastCity =
            document.getElementById(
                "platform-last-city"
            );

        const lastTime =
            document.getElementById(
                "platform-last-time"
            );

        const countryList =
            document.getElementById(
                "platform-country-list"
            );

        const countryCount =
            document.getElementById(
                "platform-country-count"
            );

        const lastActivity =
            document.getElementById(
                "platform-last-activity"
            );

        if (
            !visitorsToday
            || !lastCountry
            || !lastCity
        ) {
            return;
        }

        function getVisitorId() {
            const storageKey =
                "secure_cloud_visitor_id";

            let visitorId =
                localStorage.getItem(
                    storageKey
                );

            if (!visitorId) {
                visitorId =
                    window.crypto?.randomUUID?.()
                    || (
                        Date.now().toString(36)
                        + "-"
                        + Math.random()
                            .toString(36)
                            .slice(2)
                    );

                localStorage.setItem(
                    storageKey,
                    visitorId
                );
            }

            return visitorId;
        }

        function flagFromCode(code) {
            const normalized =
                String(code || "")
                    .trim()
                    .toUpperCase();

            if (
                normalized.length !== 2
            ) {
                return "🌍";
            }

            return normalized
                .split("")
                .map(character =>
                    String.fromCodePoint(
                        127397
                        + character.charCodeAt(0)
                    )
                )
                .join("");
        }

        function relativeTime(
            isoDate
        ) {
            if (!isoDate) {
                return "À l’instant";
            }

            const date =
                new Date(isoDate);

            const seconds =
                Math.max(
                    0,
                    Math.floor(
                        (
                            Date.now()
                            - date.getTime()
                        )
                        / 1000
                    )
                );

            if (seconds < 60) {
                return "À l’instant";
            }

            const minutes =
                Math.floor(
                    seconds / 60
                );

            if (minutes < 60) {
                return `Il y a ${minutes} min`;
            }

            const hours =
                Math.floor(
                    minutes / 60
                );

            if (hours < 24) {
                return `Il y a ${hours} h`;
            }

            const days =
                Math.floor(
                    hours / 24
                );

            return `Il y a ${days} j`;
        }

        function displayStatistics(
            statistics
        ) {
            visitorsToday.textContent =
                String(
                    statistics.visitors_today
                    ?? 0
                );

            const visitor =
                statistics.last_visitor
                || {};

            const visitorFlag =
                flagFromCode(
                    visitor.country_code
                );

            lastCountry.textContent =
                visitor.country
                    ? `${visitorFlag} ${visitor.country}`
                    : "Localisation indisponible";

            lastCity.textContent =
                visitor.city
                    ? visitor.city
                    : "Ville non disponible";

            const timeText =
                relativeTime(
                    visitor.visited_at
                );

            if (lastTime) {
                lastTime.textContent =
                    timeText;
            }

            if (lastActivity) {
                lastActivity.textContent =
                    timeText;
            }

            const countries =
                Array.isArray(
                    statistics.countries
                )
                    ? statistics.countries
                    : [];

            if (countryList) {
                countryList.textContent =
                    countries.length
                        ? countries
                            .map(country => {
                                const flag =
                                    flagFromCode(
                                        country.code
                                    );

                                return (
                                    `${flag} `
                                    + country.name
                                );
                            })
                            .join(" · ")
                        : "Aucun pays enregistré";
            }

            if (countryCount) {
                countryCount.textContent =
                    String(
                        statistics.country_count
                        ?? countries.length
                    );
            }
        }

        async function getLocation() {
            const controller =
                new AbortController();

            const timeout =
                window.setTimeout(
                    () =>
                        controller.abort(),
                    6000
                );

            try {
                const response =
                    await fetch(
                        "https://ipwho.is/",
                        {
                            cache:
                                "no-store",
                            signal:
                                controller.signal,
                        }
                    );

                if (!response.ok) {
                    throw new Error(
                        `HTTP ${response.status}`
                    );
                }

                const location =
                    await response.json();

                if (
                    location.success
                    === false
                ) {
                    throw new Error(
                        location.message
                        || "Localisation refusée"
                    );
                }

                return {
                    country:
                        location.country
                        || "",
                    country_code:
                        location.country_code
                        || "",
                    city:
                        location.city
                        || location.region
                        || "",
                };
            } catch (error) {
                console.warn(
                    "Localisation indisponible :",
                    error
                );

                return {
                    country: "",
                    country_code: "",
                    city: "",
                };
            } finally {
                window.clearTimeout(
                    timeout
                );
            }
        }

        async function registerVisit() {
            visitorsToday.textContent =
                "…";

            lastCountry.textContent =
                "Localisation en cours…";

            lastCity.textContent =
                "Recherche de la ville…";

            try {
                const location =
                    await getLocation();

                const response =
                    await fetch(
                        "/api/visitor-activity",
                        {
                            method: "POST",
                            headers: {
                                "Content-Type":
                                    "application/json",
                                Accept:
                                    "application/json",
                            },
                            cache:
                                "no-store",
                            body:
                                JSON.stringify({
                                    visitor_id:
                                        getVisitorId(),
                                    country:
                                        location.country,
                                    country_code:
                                        location.country_code,
                                    city:
                                        location.city,
                                    page:
                                        window.location.pathname,
                                }),
                        }
                    );

                if (!response.ok) {
                    throw new Error(
                        `HTTP ${response.status}`
                    );
                }

                const statistics =
                    await response.json();

                displayStatistics(
                    statistics
                );
            } catch (error) {
                console.error(
                    "Activité visiteurs indisponible :",
                    error
                );

                visitorsToday.textContent =
                    "--";

                lastCountry.textContent =
                    "Données indisponibles";

                lastCity.textContent =
                    "Réessayez dans quelques instants";

                if (countryList) {
                    countryList.textContent =
                        "Données indisponibles";
                }

                if (countryCount) {
                    countryCount.textContent =
                        "--";
                }
            }
        }

        registerVisit();
    }
);
