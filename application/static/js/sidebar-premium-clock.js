(() => {
    "use strict";

    const timeElement = document.getElementById(
        "sidebar-local-time"
    );
    const dateElement = document.getElementById(
        "sidebar-local-date"
    );
    const dashboardTime = document.getElementById(
        "last-update"
    );

    const timeFormatter = new Intl.DateTimeFormat(
        "fr-FR",
        {
            timeZone: "Europe/Paris",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        }
    );

    const dateFormatter = new Intl.DateTimeFormat(
        "fr-FR",
        {
            timeZone: "Europe/Paris",
            weekday: "short",
            day: "2-digit",
            month: "short",
        }
    );

    const fullFormatter = new Intl.DateTimeFormat(
        "fr-FR",
        {
            timeZone: "Europe/Paris",
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        }
    );

    function updateClock() {
        const now = new Date();

        if (timeElement) {
            timeElement.textContent = timeFormatter.format(now);
        }

        if (dateElement) {
            dateElement.textContent = dateFormatter.format(now);
        }

        if (dashboardTime) {
            dashboardTime.textContent = fullFormatter.format(now);
            dashboardTime.title = "Heure locale Europe/Paris";
        }
    }

    updateClock();
    window.setInterval(updateClock, 1000);
})();
