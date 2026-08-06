document.addEventListener("DOMContentLoaded", () => {
    const countryElement =
        document.getElementById("visitor-country");

    const locationElement =
        document.getElementById("visitor-location");

    if (!countryElement || !locationElement) {
        return;
    }

    async function detectVisitorLocation() {
        const controller = new AbortController();

        const timeout = window.setTimeout(
            () => controller.abort(),
            5500
        );

        try {
            const response = await fetch(
                "https://ipapi.co/json/",
                {
                    method: "GET",
                    headers: {
                        Accept: "application/json",
                    },
                    cache: "no-store",
                    signal: controller.signal,
                }
            );

            if (!response.ok) {
                throw new Error(
                    `Erreur HTTP ${response.status}`
                );
            }

            const data = await response.json();

            if (
                data.error
                || !data.country_name
            ) {
                throw new Error(
                    data.reason
                    || "Localisation non disponible"
                );
            }

            const country =
                data.country_name;

            const countryCode =
                data.country_code
                ? data.country_code.toUpperCase()
                : "";

            const city =
                data.city
                || data.region
                || "Région non précisée";

            countryElement.textContent =
                countryCode
                    ? `${country} · ${countryCode}`
                    : country;

            locationElement.textContent =
                `${city} · Point d’accès détecté`;
        } catch (error) {
            console.warn(
                "Détection géographique indisponible :",
                error
            );

            countryElement.textContent =
                "Infrastructure mondiale";

            locationElement.textContent =
                "Localisation réseau indisponible";
        } finally {
            window.clearTimeout(timeout);
        }
    }

    detectVisitorLocation();
});
