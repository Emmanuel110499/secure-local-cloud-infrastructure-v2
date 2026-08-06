(() => {
    "use strict";

    const COOKIE_NAME = "secure_cloud_recent_pages";
    const MAX_ITEMS = 3;

    const pageDefinitions = {
        "/": {
            title: "Accueil",
            icon: "🏠",
        },
        "/monitoring": {
            title: "Monitoring",
            icon: "📈",
        },
        "/documentation": {
            title: "Documentation",
            icon: "📚",
        },
        "/containers": {
            title: "Conteneurs Docker",
            icon: "🐳",
        },
        "/infrastructure": {
            title: "Infrastructure",
            icon: "🖥️",
        },
        "/security": {
            title: "Sécurité",
            icon: "🔐",
        },
        "/audit": {
            title: "Audit",
            icon: "📜",
        },
        "/assistant": {
            title: "Emma_IA",
            icon: "🤖",
        },
    };

    function normalizePath(pathname) {
        const clean = String(pathname || "/")
            .replace(/\/+$/, "");

        return clean || "/";
    }

    function readCookie(name) {
        const prefix = `${encodeURIComponent(name)}=`;

        const part = document.cookie
            .split("; ")
            .find(item => item.startsWith(prefix));

        if (!part) {
            return "";
        }

        return decodeURIComponent(
            part.slice(prefix.length)
        );
    }

    function writeCookie(name, value) {
        document.cookie = [
            `${encodeURIComponent(name)}=${encodeURIComponent(value)}`,
            "Path=/",
            "Max-Age=2592000",
            "SameSite=Lax",
        ].join("; ");
    }

    function deleteCookie(name) {
        document.cookie = [
            `${encodeURIComponent(name)}=`,
            "Path=/",
            "Max-Age=0",
            "SameSite=Lax",
        ].join("; ");
    }

    function readHistory() {
        try {
            const raw = readCookie(COOKIE_NAME);

            if (!raw) {
                return [];
            }

            const history = JSON.parse(raw);

            return Array.isArray(history)
                ? history
                : [];
        } catch (error) {
            console.warn(
                "Historique récent illisible :",
                error
            );

            return [];
        }
    }

    function saveHistory(history) {
        writeCookie(
            COOKIE_NAME,
            JSON.stringify(history)
        );
    }

    function registerCurrentPage() {
        const currentPath = normalizePath(
            window.location.pathname
        );

        const definition =
            pageDefinitions[currentPath];

        let history = readHistory();

        if (!definition) {
            return history;
        }

        history = history.filter(
            item =>
                normalizePath(item.path)
                !== currentPath
        );

        history.unshift({
            path: currentPath,
            title: definition.title,
            icon: definition.icon,
            visitedAt: Date.now(),
        });

        history = history
            .sort(
                (a, b) =>
                    Number(b.visitedAt)
                    - Number(a.visitedAt)
            )
            .slice(0, MAX_ITEMS);

        saveHistory(history);

        return history;
    }

    function formatRelativeTime(timestamp) {
        const elapsed = Math.max(
            0,
            Date.now() - Number(timestamp || 0)
        );

        const seconds = Math.floor(
            elapsed / 1000
        );

        if (seconds < 45) {
            return "À l’instant";
        }

        const minutes = Math.floor(
            seconds / 60
        );

        if (minutes < 60) {
            return `Il y a ${minutes} min`;
        }

        const hours = Math.floor(
            minutes / 60
        );

        if (hours < 24) {
            return `Il y a ${hours} h`;
        }

        const days = Math.floor(
            hours / 24
        );

        return days === 1
            ? "Hier"
            : `Il y a ${days} j`;
    }

    function createRecentItem(item, index) {
        const link = document.createElement("a");

        link.href = item.path;
        link.className = "recent-item";
        link.dataset.visitedAt =
            String(item.visitedAt);

        const left =
            document.createElement("div");

        left.className = "recent-left";

        const icon =
            document.createElement("span");

        icon.className = "recent-icon";
        icon.textContent = item.icon || "📄";

        const content =
            document.createElement("div");

        content.className =
            "recent-item-content";

        const top =
            document.createElement("div");

        top.className = "recent-item-top";

        const title =
            document.createElement("span");

        title.className = "recent-title";
        title.textContent =
            item.title || item.path;

        top.appendChild(title);

        if (index === 0) {
            const badge =
                document.createElement("span");

            badge.className =
                "recent-current-badge";

            badge.textContent = "Plus récent";

            top.appendChild(badge);
        }

        const time =
            document.createElement("span");

        time.className = "recent-time";
        time.textContent =
            formatRelativeTime(item.visitedAt);

        content.appendChild(top);
        content.appendChild(time);

        left.appendChild(icon);
        left.appendChild(content);

        const position =
            document.createElement("span");

        position.className =
            "recent-position";

        position.textContent =
            String(index + 1);

        link.appendChild(left);
        link.appendChild(position);

        return link;
    }

    function renderHistory(history) {
        const list =
            document.getElementById(
                "recent-pages-list"
            );

        if (!list) {
            return;
        }

        list.replaceChildren();

        const sorted = [...history]
            .sort(
                (a, b) =>
                    Number(b.visitedAt)
                    - Number(a.visitedAt)
            )
            .slice(0, MAX_ITEMS);

        if (sorted.length === 0) {
            const empty =
                document.createElement("div");

            empty.className = "recent-empty";

            const title =
                document.createElement("strong");

            title.textContent =
                "Aucune activité récente";

            const description =
                document.createElement("small");

            description.textContent =
                "Ouvrez une section pour commencer l’historique.";

            empty.appendChild(title);
            empty.appendChild(description);
            list.appendChild(empty);

            return;
        }

        sorted.forEach((item, index) => {
            list.appendChild(
                createRecentItem(item, index)
            );
        });
    }

    function updateTimes() {
        document
            .querySelectorAll(
                "#recent-pages-list .recent-item"
            )
            .forEach(item => {
                const timestamp = Number(
                    item.dataset.visitedAt
                );

                const time =
                    item.querySelector(
                        ".recent-time"
                    );

                if (time && Number.isFinite(timestamp)) {
                    time.textContent =
                        formatRelativeTime(timestamp);
                }
            });
    }

    function initialize() {
        const history =
            registerCurrentPage();

        renderHistory(history);

        const clearButton =
            document.getElementById(
                "clear-recent-pages"
            );

        clearButton?.addEventListener(
            "click",
            event => {
                event.preventDefault();

                deleteCookie(COOKIE_NAME);
                renderHistory([]);
            }
        );

        window.setInterval(
            updateTimes,
            30000
        );
    }

    if (document.readyState === "loading") {
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
