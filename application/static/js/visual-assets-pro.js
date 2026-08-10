(() => {
    "use strict";

    const currentScript = document.currentScript;
    const asset = (folder, name) => new URL(`../${folder}/${name}`, currentScript.src).href;

    const lineIcons = {
        home: '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5"/><path d="M9.5 20v-6h5v6"/>',
        monitoring: '<path d="M3 17l5-5 4 3 8-9"/><path d="M15 6h5v5"/><path d="M3 21h18"/>',
        infrastructure: '<rect x="3" y="4" width="18" height="6" rx="1.5"/><rect x="3" y="14" width="18" height="6" rx="1.5"/><path d="M7 7h.01M7 17h.01M11 7h7M11 17h7"/>',
        security: '<path d="M12 3 5 6v5c0 4.8 2.8 8.3 7 10 4.2-1.7 7-5.2 7-10V6Z"/><path d="M9 12h6M12 9v6"/>',
        audit: '<path d="M6 3h9l3 3v15H6z"/><path d="M14 3v4h4M9 11h6M9 15h6"/>',
        documentation: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v17H6.5A2.5 2.5 0 0 0 4 22Z"/><path d="M20 5.5A2.5 2.5 0 0 0 17.5 3H13v17h4.5A2.5 2.5 0 0 1 20 22Z"/>',
        assistant: '<path d="M7 8.5h10a3 3 0 0 1 3 3v5a3 3 0 0 1-3 3H9l-5 2v-10a3 3 0 0 1 3-3Z"/><path d="M9 13h.01M15 13h.01M9.5 16h5M12 8.5V5"/>',
        target: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><path d="m12 12 7-7M16 5h3v3"/>',
        clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        location: '<path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
        globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>',
        lock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/>',
        alert: '<path d="M12 3 2.8 20h18.4Z"/><path d="M12 9v5M12 17h.01"/>',
        grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
        search: '<circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/>',
        user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
        external: '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 13v7H4V6h7"/>',
        module: '<path d="m12 3 8 4.5-8 4.5-8-4.5Z"/><path d="m4 12 8 4.5 8-4.5M4 16.5 12 21l8-4.5"/>',
        wall: '<path d="M3 5h18v14H3zM3 10h18M3 15h18M8 5v5M16 5v5M6 10v5M14 10v5M10 15v4M18 15v4"/>',
        trash: '<path d="M4 7h16M9 3h6l1 4H8zM7 7l1 14h8l1-14M10 11v6M14 11v6"/>',
        status: '<circle cx="12" cy="12" r="7" fill="currentColor" stroke="none"/>',
        menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
    };

    const svg = (name) => `<svg viewBox="0 0 24 24" aria-hidden="true">${lineIcons[name] || lineIcons.grid}</svg>`;
    const image = (name, alt = "") => `<img src="${asset("brand", name)}" alt="${alt}" loading="lazy">`;

    function replaceSidebar() {
        const brand = document.querySelector(".sidebar .brand-icon");
        if (brand) {
            brand.innerHTML = svg("infrastructure");
            brand.classList.add("visual-pro-icon");
        }

        document.querySelectorAll(".sidebar .nav-item").forEach((link) => {
            const href = String(link.getAttribute("href") || "").toLowerCase();
            const icon = link.querySelector(".sidebar-colored-icon");
            if (!icon) return;

            if (href.includes("grafana")) icon.innerHTML = image("grafana.svg", "Grafana");
            else if (href.includes("prometheus")) icon.innerHTML = image("prometheus.svg", "Prometheus");
            else if (href.includes("container")) icon.innerHTML = image("docker.svg", "Docker");
            else if (href.includes("monitoring")) icon.innerHTML = svg("monitoring");
            else if (href.includes("infrastructure")) icon.innerHTML = svg("infrastructure");
            else if (href.includes("security")) icon.innerHTML = svg("security");
            else if (href.includes("audit")) icon.innerHTML = svg("audit");
            else if (href.includes("documentation")) icon.innerHTML = svg("documentation");
            else icon.innerHTML = svg("home");

            icon.classList.add("visual-pro-icon");
        });
    }

    function replaceGlobe() {
        const visual = document.querySelector(".world-presence-visual");
        if (!visual) return;
        visual.innerHTML = `<img class="world-presence-realistic" src="${asset("images", "world-presence-realistic.png")}" alt="Vue satellite de la Terre centrée sur l’Europe et l’Afrique">`;
    }

    const emojiMap = new Map([
        ["🏠", "home"], ["📈", "monitoring"], ["📊", "monitoring"],
        ["🖥️", "infrastructure"], ["🖥", "infrastructure"], ["💻", "infrastructure"],
        ["🔐", "security"], ["🛡️", "security"], ["🛡", "security"],
        ["📜", "audit"], ["📚", "documentation"], ["🤖", "assistant"],
        ["🎯", "target"], ["⏱️", "clock"], ["⏱", "clock"],
        ["📍", "location"], ["🌍", "globe"], ["🌎", "globe"],
        ["🕒", "clock"], ["🔒", "lock"], ["⚠️", "alert"], ["⚠", "alert"],
        ["☁️", "infrastructure"], ["☁", "infrastructure"],
        ["🔎", "search"], ["📖", "documentation"], ["👤", "user"],
        ["↗️", "external"], ["↗", "external"], ["🧩", "module"],
        ["🧱", "wall"], ["🗑", "trash"], ["🟢", "status"], ["☰", "menu"],
    ]);

    function replaceStandaloneEmoji() {
        const selectors = [
            ".kpi-icon", ".objective-icon", ".security-hero-icon", ".security-feature-icon",
            ".infra-main-icon", ".infra-stat span", ".platform-activity-main-icon",
            ".platform-activity-row-icon", ".emma-chat-launcher-icon", ".emma-chat-avatar",
            ".doc-icon", "#dashboard-alert-icon"
        ].join(",");

        document.querySelectorAll(selectors).forEach((node) => {
            const value = node.textContent.trim();
            if (value === "🐳") node.innerHTML = image("docker.svg", "Docker");
            else if (value === "🔥") node.innerHTML = image("prometheus.svg", "Prometheus");
            else {
                const icon = emojiMap.get(value);
                if (icon) node.innerHTML = svg(icon);
            }
            node.classList.add("visual-pro-icon");
        });
    }

    function replacePrefixedEmoji() {
        document.querySelectorAll(".doc-nav a, .login-security-note").forEach((node) => {
            const text = node.textContent.trim();
            for (const [emoji, icon] of emojiMap) {
                if (!text.startsWith(emoji)) continue;
                node.textContent = text.slice(emoji.length).trim();
                const mark = document.createElement("span");
                mark.className = "visual-pro-inline-icon";
                mark.innerHTML = svg(icon);
                node.prepend(mark);
                break;
            }
        });
    }

    function replaceAllEmojiLeaves() {
        document.querySelectorAll("body *").forEach((node) => {
            if (node.childElementCount !== 0) return;
            const value = node.textContent.trim();
            if (value === "🐳") node.innerHTML = image("docker.svg", "Docker");
            else if (value === "🔥") node.innerHTML = image("prometheus.svg", "Prometheus");
            else {
                const icon = emojiMap.get(value);
                if (!icon) return;
                node.innerHTML = svg(icon);
            }
            node.classList.add("visual-pro-icon");
        });

        const loginTitle = document.querySelector(".login-card h1");
        if (loginTitle) loginTitle.textContent = loginTitle.textContent.replace("👋", "").trim();
    }

    replaceSidebar();
    replaceGlobe();
    replaceStandaloneEmoji();
    replacePrefixedEmoji();
    replaceAllEmojiLeaves();
})();
